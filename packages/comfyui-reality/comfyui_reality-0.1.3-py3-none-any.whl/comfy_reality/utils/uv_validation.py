"""UV orientation validation utilities for ComfyReality."""

import json
import tempfile
import zipfile
from pathlib import Path
from typing import Any

import numpy as np
import torch
from PIL import Image

try:
    from pxr import Usd, UsdGeom

    USD_AVAILABLE = True
except ImportError:
    USD_AVAILABLE = False


class UVOrientationValidator:
    """Validates UV orientation in USDZ files."""

    def __init__(self):
        self.corner_colors = {
            "top_left": (0, 255, 0),  # Green
            "top_right": (255, 0, 0),  # Red
            "bottom_left": (0, 0, 255),  # Blue
            "bottom_right": (255, 255, 0),  # Yellow
        }

    def validate_usdz_structure(self, usdz_path: Path) -> dict[str, Any]:
        """Validate basic USDZ file structure."""
        try:
            if not usdz_path.exists():
                return {"valid": False, "error": "File does not exist"}

            if usdz_path.stat().st_size == 0:
                return {"valid": False, "error": "File is empty"}

            # Check if it's a valid zip file
            try:
                with zipfile.ZipFile(usdz_path, "r") as zip_file:
                    file_list = zip_file.namelist()

                    # Check for required components
                    usd_files = [f for f in file_list if f.endswith(".usd") or f.endswith(".usda")]
                    texture_files = [f for f in file_list if f.endswith((".png", ".jpg", ".jpeg"))]

                    if not usd_files:
                        return {"valid": False, "error": "No USD file found"}

                    if not texture_files:
                        return {"valid": False, "error": "No texture file found"}

                    return {
                        "valid": True,
                        "usd_files": usd_files,
                        "texture_files": texture_files,
                        "total_files": len(file_list),
                        "file_size_mb": usdz_path.stat().st_size / (1024 * 1024),
                    }

            except zipfile.BadZipFile:
                return {"valid": False, "error": "Invalid zip file"}

        except Exception as e:
            return {"valid": False, "error": f"Validation error: {e!s}"}

    def extract_texture_from_usdz(self, usdz_path: Path) -> Image.Image | None:
        """Extract the main texture from a USDZ file."""
        try:
            with zipfile.ZipFile(usdz_path, "r") as zip_file:
                texture_files = [f for f in zip_file.namelist() if f.endswith((".png", ".jpg", ".jpeg"))]

                if not texture_files:
                    return None

                # Use the first texture file
                texture_file = texture_files[0]

                with zip_file.open(texture_file) as texture_data:
                    return Image.open(texture_data).copy()

        except Exception:
            return None

    def validate_corner_markers(self, image: Image.Image, tolerance: int = 50) -> dict[str, Any]:
        """Validate corner markers in an image to check UV orientation."""
        if image.mode != "RGB":
            image = image.convert("RGB")

        width, height = image.size
        corner_size = min(width, height) // 8  # Check 1/8 of the image size

        # Extract corner regions
        corners = {
            "top_left": image.crop((0, 0, corner_size, corner_size)),
            "top_right": image.crop((width - corner_size, 0, width, corner_size)),
            "bottom_left": image.crop((0, height - corner_size, corner_size, height)),
            "bottom_right": image.crop((width - corner_size, height - corner_size, width, height)),
        }

        results = {}

        for corner_name, corner_image in corners.items():
            expected_color = self.corner_colors[corner_name]

            # Calculate average color of the corner region
            corner_array = np.array(corner_image)
            avg_color = np.mean(corner_array, axis=(0, 1))

            # Check if the average color is close to expected
            color_diff = np.abs(avg_color - np.array(expected_color))
            max_diff = np.max(color_diff)

            results[corner_name] = {
                "expected_color": expected_color,
                "actual_color": tuple(avg_color.astype(int)),
                "color_difference": max_diff,
                "matches": max_diff < tolerance,
            }

        # Overall validation
        all_match = all(r["matches"] for r in results.values())

        return {"valid": all_match, "corner_results": results, "tolerance": tolerance}

    def validate_uv_orientation_from_usdz(self, usdz_path: Path) -> dict[str, Any]:
        """Complete UV orientation validation from USDZ file."""
        # First validate file structure
        structure_result = self.validate_usdz_structure(usdz_path)
        if not structure_result["valid"]:
            return structure_result

        # Extract texture
        texture = self.extract_texture_from_usdz(usdz_path)
        if texture is None:
            return {"valid": False, "error": "Could not extract texture from USDZ"}

        # Validate corner markers
        corner_result = self.validate_corner_markers(texture)

        return {
            "valid": corner_result["valid"],
            "file_structure": structure_result,
            "texture_validation": corner_result,
            "texture_size": texture.size,
        }

    def extract_uv_coordinates(self, usdz_path: Path) -> list[tuple[float, float]] | None:
        """Extract UV coordinates from USDZ file using USD libraries."""
        if not USD_AVAILABLE:
            return None

        try:
            # Extract USDZ to temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)

                with zipfile.ZipFile(usdz_path, "r") as zip_file:
                    zip_file.extractall(temp_path)

                # Find USD file
                usd_files = list(temp_path.glob("*.usd")) + list(temp_path.glob("*.usda"))
                if not usd_files:
                    return None

                usd_file = usd_files[0]

                # Open USD stage
                stage = Usd.Stage.Open(str(usd_file))
                if not stage:
                    return None

                # Find mesh geometry
                for prim in stage.Traverse():
                    if prim.IsA(UsdGeom.Mesh):
                        mesh = UsdGeom.Mesh(prim)

                        # Get texture coordinates
                        primvar = mesh.GetPrimvar("st")
                        if primvar:
                            uvs_attr = primvar.GetAttr()
                            uvs = uvs_attr.Get()

                            if uvs:
                                return [(float(uv[0]), float(uv[1])) for uv in uvs]

                return None

        except Exception:
            return None

    def generate_validation_report(self, usdz_files: list[Path], output_path: Path | None = None) -> dict[str, Any]:
        """Generate a comprehensive validation report for multiple USDZ files."""
        results = []

        for usdz_file in usdz_files:
            if not usdz_file.exists():
                results.append({"file": str(usdz_file), "valid": False, "error": "File not found"})
                continue

            validation_result = self.validate_uv_orientation_from_usdz(usdz_file)
            validation_result["file"] = str(usdz_file)
            results.append(validation_result)

        # Generate summary
        total_files = len(results)
        valid_files = sum(1 for r in results if r.get("valid", False))

        report = {
            "timestamp": str(Path(__file__).stat().st_mtime),
            "summary": {
                "total_files": total_files,
                "valid_files": valid_files,
                "invalid_files": total_files - valid_files,
                "success_rate": valid_files / total_files if total_files > 0 else 0,
            },
            "file_results": results,
            "validation_criteria": {
                "corner_markers": {
                    "top_left": "Green (0, 255, 0)",
                    "top_right": "Red (255, 0, 0)",
                    "bottom_left": "Blue (0, 0, 255)",
                    "bottom_right": "Yellow (255, 255, 0)",
                },
                "tolerance": 50,
                "expected_uv_origin": "Bottom-left (0, 0)",
                "expected_uv_max": "Top-right (1, 1)",
            },
        }

        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as f:
                json.dump(report, f, indent=2)

        return report


def create_uv_test_texture(width: int = 512, height: int = 512) -> torch.Tensor:
    """Create a test texture with UV orientation markers."""
    image = torch.zeros(1, height, width, 3)

    # Add gradient background
    for y in range(height):
        for x in range(width):
            image[0, y, x, 0] = x / (width - 1)  # Red gradient left to right
            image[0, y, x, 1] = y / (height - 1)  # Green gradient top to bottom
            image[0, y, x, 2] = 0.2  # Constant blue

    # Add corner markers
    corner_size = min(width, height) // 8

    # Top-Left: Green
    image[0, :corner_size, :corner_size] = torch.tensor([0.0, 1.0, 0.0])

    # Top-Right: Red
    image[0, :corner_size, -corner_size:] = torch.tensor([1.0, 0.0, 0.0])

    # Bottom-Left: Blue
    image[0, -corner_size:, :corner_size] = torch.tensor([0.0, 0.0, 1.0])

    # Bottom-Right: Yellow
    image[0, -corner_size:, -corner_size:] = torch.tensor([1.0, 1.0, 0.0])

    return image


def save_test_texture(tensor: torch.Tensor, output_path: Path):
    """Save a test texture tensor as an image file."""
    # Convert tensor to PIL Image
    if tensor.dim() == 4:  # BHWC
        tensor = tensor.squeeze(0)  # Remove batch dimension

    # Convert to numpy and scale to 0-255
    image_np = (tensor.numpy() * 255).astype(np.uint8)

    # Convert to PIL Image
    image = Image.fromarray(image_np)

    # Save
    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(output_path)


# Example usage
if __name__ == "__main__":
    # Create validator
    validator = UVOrientationValidator()

    # Create test texture
    test_texture = create_uv_test_texture()

    # Save test texture
    save_test_texture(test_texture, Path("test_texture_with_markers.png"))

    print("Created test texture with UV orientation markers")
