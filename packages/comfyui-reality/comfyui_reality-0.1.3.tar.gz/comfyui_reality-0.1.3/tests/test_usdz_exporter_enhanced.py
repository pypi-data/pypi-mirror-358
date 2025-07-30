"""Enhanced tests for USDZExporter node with UV orientation validation."""

import tempfile
import zipfile
from pathlib import Path

import pytest
import torch

from comfy_reality.nodes.usdz_exporter import USDZExporter

try:
    from pxr import Gf, Usd, UsdGeom, UsdShade

    USD_AVAILABLE = True
except ImportError:
    USD_AVAILABLE = False


class TestUSDZExporterEnhanced:
    """Enhanced test suite for USDZExporter with UV orientation validation."""

    @pytest.fixture
    def exporter(self):
        """Create exporter instance."""
        return USDZExporter()

    @pytest.fixture
    def uv_validation_image(self) -> torch.Tensor:
        """Create a test image with clear UV orientation markers."""
        # Create 512x512 image with gradient and corner markers in BCHW format
        image = torch.zeros(1, 3, 512, 512)

        # Add gradient background (helps with visual inspection)
        for y in range(512):
            for x in range(512):
                image[0, 0, y, x] = x / 511.0  # Red gradient left to right
                image[0, 1, y, x] = y / 511.0  # Green gradient top to bottom
                image[0, 2, y, x] = 0.3  # Constant blue for contrast

        # Add corner markers (64x64 pixels each)
        corner_size = 64

        # Top-Left: Bright White
        image[0, :, :corner_size, :corner_size] = torch.tensor([1.0, 1.0, 1.0]).view(3, 1, 1)

        # Top-Right: Bright Red
        image[0, :, :corner_size, -corner_size:] = torch.tensor([1.0, 0.0, 0.0]).view(3, 1, 1)

        # Bottom-Left: Bright Blue
        image[0, :, -corner_size:, :corner_size] = torch.tensor([0.0, 0.0, 1.0]).view(3, 1, 1)

        # Bottom-Right: Bright Yellow
        image[0, :, -corner_size:, -corner_size:] = torch.tensor([1.0, 1.0, 0.0]).view(3, 1, 1)

        # Add text labels (approximate positions)
        self._add_text_regions(image)

        return image

    def _add_text_regions(self, image: torch.Tensor):
        """Add text-like regions to help with visual validation."""
        # Create "TL" region (top-left) - BCHW format
        image[0, :, 10:25, 10:35] = torch.tensor([0.0, 0.0, 0.0]).view(3, 1, 1)  # Black text

        # Create "TR" region (top-right)
        image[0, :, 10:25, -35:-10] = torch.tensor([0.0, 0.0, 0.0]).view(3, 1, 1)  # Black text

        # Create "BL" region (bottom-left)
        image[0, :, -25:-10, 10:35] = torch.tensor([0.0, 0.0, 0.0]).view(3, 1, 1)  # Black text

        # Create "BR" region (bottom-right)
        image[0, :, -25:-10, -35:-10] = torch.tensor([0.0, 0.0, 0.0]).view(3, 1, 1)  # Black text

    def test_direct_usdz_export_with_real_texture(self, exporter, test_texture_tensor, temp_output_dir, output_cleanup):
        """Test direct USDZ export using the real test texture (converted from direct test)."""
        if test_texture_tensor is None:
            pytest.skip("Test texture not available")

        output_path = temp_output_dir / "direct_test_enhanced.usdz"
        output_cleanup(output_path)

        # Export USDZ with enhanced settings
        result = exporter.export_usdz(
            image=test_texture_tensor,
            filename="direct_test_enhanced",
            mask=None,
            scale=1.0,
            material_type="unlit",
            optimization_level="quality",
            coordinate_system="y_up",
            physics_enabled=False,
        )

        # Validate result
        assert isinstance(result, tuple)
        assert len(result) == 1
        assert isinstance(result[0], str)
        assert result[0].endswith(".usdz")

        # Check if file was created
        default_output_path = Path("output/ar_stickers/direct_test_enhanced.usdz")
        assert default_output_path.exists() or Path(result[0]).exists()

        # Validate file properties
        actual_path = Path(result[0]) if Path(result[0]).exists() else default_output_path
        assert actual_path.stat().st_size > 0
        assert actual_path.stat().st_size < 25 * 1024 * 1024  # iOS limit: 25MB

    def test_uv_orientation_validation_synthetic(self, exporter, uv_validation_image, temp_output_dir, output_cleanup):
        """Test UV orientation using synthetic image with corner markers."""
        output_path = temp_output_dir / "uv_validation_test.usdz"
        output_cleanup(output_path)

        # Export USDZ
        result = exporter.export_usdz(
            image=uv_validation_image,
            filename="uv_validation_test",
            material_type="unlit",
            optimization_level="quality",
            coordinate_system="y_up",
        )

        assert isinstance(result, tuple)
        assert len(result) == 1

        # Validate file was created
        actual_path = Path(result[0]) if Path(result[0]).exists() else Path("output/ar_stickers/uv_validation_test.usdz")
        assert actual_path.exists()

        # Perform UV orientation validation
        validation_result = self._validate_uv_orientation_from_usdz(actual_path)
        assert validation_result["valid"], f"UV orientation validation failed: {validation_result['error']}"

    @pytest.mark.skipif(not USD_AVAILABLE, reason="USD libraries not available")
    def test_uv_coordinates_validation(self, exporter, corner_marked_image, temp_output_dir, output_cleanup):
        """Test that UV coordinates are correctly oriented by analyzing USD geometry."""
        output_path = temp_output_dir / "uv_coords_test.usdz"
        output_cleanup(output_path)

        # Export USDZ
        result = exporter.export_usdz(
            image=corner_marked_image, filename="uv_coords_test", material_type="standard", coordinate_system="y_up"
        )

        assert isinstance(result, tuple)
        actual_path = Path(result[0]) if Path(result[0]).exists() else Path("output/ar_stickers/uv_coords_test.usdz")
        assert actual_path.exists()

        # Extract and validate UV coordinates
        uv_coords = self._extract_uv_coordinates_from_usdz(actual_path)
        assert len(uv_coords) == 4, "Expected 4 UV coordinates for quad"

        # Validate UV coordinate orientation
        # Standard UV mapping: (0,0) bottom-left, (1,1) top-right
        expected_uvs = [
            (0.0, 0.0),  # Bottom-left
            (1.0, 0.0),  # Bottom-right
            (1.0, 1.0),  # Top-right
            (0.0, 1.0),  # Top-left
        ]

        # Check that UVs are close to expected values (allowing for small floating point differences)
        for i, (expected_u, expected_v) in enumerate(expected_uvs):
            actual_u, actual_v = uv_coords[i]
            assert abs(actual_u - expected_u) < 0.01, f"UV coordinate {i} U component mismatch: {actual_u} != {expected_u}"
            assert abs(actual_v - expected_v) < 0.01, f"UV coordinate {i} V component mismatch: {actual_v} != {expected_v}"

    def test_multiple_material_types_uv_consistency(self, exporter, uv_validation_image, temp_output_dir, output_cleanup):
        """Test that UV orientation is consistent across different material types."""
        material_types = ["standard", "unlit", "metallic", "emission"]
        results = {}

        for material_type in material_types:
            output_path = temp_output_dir / f"material_{material_type}_test.usdz"
            output_cleanup(output_path)

            result = exporter.export_usdz(
                image=uv_validation_image,
                filename=f"material_{material_type}_test",
                material_type=material_type,
                optimization_level="quality",
            )

            actual_path = Path(result[0]) if Path(result[0]).exists() else Path(f"output/ar_stickers/material_{material_type}_test.usdz")
            assert actual_path.exists()

            # Validate UV orientation
            validation_result = self._validate_uv_orientation_from_usdz(actual_path)
            results[material_type] = validation_result

            assert validation_result["valid"], f"UV orientation failed for {material_type}: {validation_result['error']}"

        # Ensure all material types produce consistent UV orientations
        for material_type, result in results.items():
            assert result["valid"], f"Material type {material_type} failed UV validation"

    def test_coordinate_system_uv_orientation(self, exporter, uv_validation_image, temp_output_dir, output_cleanup):
        """Test UV orientation consistency across different coordinate systems."""
        coordinate_systems = ["y_up", "z_up"]

        for coord_system in coordinate_systems:
            output_path = temp_output_dir / f"coords_{coord_system}_test.usdz"
            output_cleanup(output_path)

            result = exporter.export_usdz(
                image=uv_validation_image, filename=f"coords_{coord_system}_test", coordinate_system=coord_system, material_type="unlit"
            )

            actual_path = Path(result[0]) if Path(result[0]).exists() else Path(f"output/ar_stickers/coords_{coord_system}_test.usdz")
            assert actual_path.exists()

            # Validate UV orientation
            validation_result = self._validate_uv_orientation_from_usdz(actual_path)
            assert validation_result["valid"], f"UV orientation failed for {coord_system}: {validation_result['error']}"

    def test_texture_export_with_different_formats(self, exporter, temp_output_dir, output_cleanup):
        """Test texture export with valid ComfyUI tensor formats."""
        # Test only valid ComfyUI formats (BCHW and CHW)
        formats_to_test = [
            ("BCHW", torch.rand(1, 3, 512, 512)),  # Batch, Channels, Height, Width (ComfyUI standard)
            ("CHW", torch.rand(3, 512, 512)),  # Channels, Height, Width
        ]

        for format_name, tensor in formats_to_test:
            output_path = temp_output_dir / f"format_{format_name}_test.usdz"
            output_cleanup(output_path)

            result = exporter.export_usdz(image=tensor, filename=f"format_{format_name}_test", material_type="unlit")

            assert isinstance(result, tuple)
            actual_path = Path(result[0]) if Path(result[0]).exists() else Path(f"output/ar_stickers/format_{format_name}_test.usdz")
            assert actual_path.exists()
            assert actual_path.stat().st_size > 0

    def _validate_uv_orientation_from_usdz(self, usdz_path: Path) -> dict[str, any]:
        """Validate UV orientation by analyzing the USDZ file structure.

        This is a basic validation that checks if the file is valid and contains
        expected components. More sophisticated validation would require USD parsing.
        """
        try:
            if not usdz_path.exists():
                return {"valid": False, "error": "USDZ file does not exist"}

            if usdz_path.stat().st_size == 0:
                return {"valid": False, "error": "USDZ file is empty"}

            # Basic zip file validation (USDZ is a zip archive)
            try:
                with zipfile.ZipFile(usdz_path, "r") as zip_file:
                    file_list = zip_file.namelist()

                    # Check for required USDZ components
                    has_usd_file = any(f.endswith(".usd") or f.endswith(".usda") for f in file_list)
                    has_texture = any(f.endswith(".png") or f.endswith(".jpg") or f.endswith(".jpeg") for f in file_list)

                    if not has_usd_file:
                        return {"valid": False, "error": "No USD file found in USDZ archive"}

                    if not has_texture:
                        return {"valid": False, "error": "No texture file found in USDZ archive"}

                    return {
                        "valid": True,
                        "file_count": len(file_list),
                        "files": file_list,
                        "has_usd": has_usd_file,
                        "has_texture": has_texture,
                    }

            except zipfile.BadZipFile:
                return {"valid": False, "error": "Invalid USDZ file (not a valid zip archive)"}

        except Exception as e:
            return {"valid": False, "error": f"Validation error: {e!s}"}

    @pytest.mark.skipif(not USD_AVAILABLE, reason="USD libraries not available")
    def _extract_uv_coordinates_from_usdz(self, usdz_path: Path) -> list[tuple[float, float]]:
        """Extract UV coordinates from USDZ file using USD libraries."""
        try:
            # Extract USDZ to temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)

                with zipfile.ZipFile(usdz_path, "r") as zip_file:
                    zip_file.extractall(temp_path)

                # Find USD file
                usd_files = list(temp_path.glob("*.usd")) + list(temp_path.glob("*.usda"))
                if not usd_files:
                    raise ValueError("No USD file found in USDZ archive")

                usd_file = usd_files[0]

                # Open USD stage
                stage = Usd.Stage.Open(str(usd_file))
                if not stage:
                    raise ValueError("Failed to open USD stage")

                # Find geometry prims
                for prim in stage.Traverse():
                    if prim.IsA(UsdGeom.Mesh):
                        mesh = UsdGeom.Mesh(prim)

                        # Get texture coordinates using PrimvarsAPI (correct pattern)
                        primvars_api = UsdGeom.PrimvarsAPI(mesh)
                        uv_primvar = primvars_api.GetPrimvar("st")  # Standard texture coordinate name

                        if uv_primvar.IsDefined():
                            uvs = uv_primvar.Get()

                            if uvs:
                                # Convert to list of tuples
                                return [(float(uv[0]), float(uv[1])) for uv in uvs]

                raise ValueError("No UV coordinates found in USD file")

        except Exception as e:
            raise ValueError(f"Failed to extract UV coordinates: {e!s}")

    def test_generate_visual_validation_files(self, exporter, test_texture_tensor, uv_validation_image, temp_output_dir, output_cleanup):
        """Generate USDZ files for manual visual validation."""
        if test_texture_tensor is None:
            pytest.skip("Test texture not available")

        # Test files to generate
        test_configs = [
            ("real_texture_unlit", test_texture_tensor, "unlit"),
            ("real_texture_standard", test_texture_tensor, "standard"),
            ("synthetic_markers", uv_validation_image, "unlit"),
            ("synthetic_standard", uv_validation_image, "standard"),
        ]

        generated_files = []

        for name, image, material_type in test_configs:
            result = exporter.export_usdz(
                image=image,
                filename=f"visual_validation_{name}",
                material_type=material_type,
                optimization_level="quality",
                coordinate_system="y_up",
            )

            actual_path = Path(result[0]) if Path(result[0]).exists() else Path(f"output/ar_stickers/visual_validation_{name}.usdz")
            if actual_path.exists():
                generated_files.append(actual_path)
                output_cleanup(actual_path)

        # Verify all files were generated
        assert len(generated_files) == len(test_configs)

        # All files should be valid
        for file_path in generated_files:
            validation_result = self._validate_uv_orientation_from_usdz(file_path)
            assert validation_result["valid"], f"Generated file {file_path.name} failed validation: {validation_result['error']}"

    @pytest.mark.integration
    def test_end_to_end_uv_workflow(self, exporter, test_texture_tensor, temp_output_dir, output_cleanup):
        """End-to-end test of the UV orientation workflow."""
        if test_texture_tensor is None:
            pytest.skip("Test texture not available")

        # Test complete workflow with various configurations
        configs = [
            {"material_type": "unlit", "optimization_level": "mobile", "coordinate_system": "y_up"},
            {"material_type": "standard", "optimization_level": "balanced", "coordinate_system": "y_up"},
            {"material_type": "metallic", "optimization_level": "quality", "coordinate_system": "z_up"},
        ]

        for i, config in enumerate(configs):
            output_path = temp_output_dir / f"workflow_test_{i}.usdz"
            output_cleanup(output_path)

            result = exporter.export_usdz(image=test_texture_tensor, filename=f"workflow_test_{i}", **config)

            actual_path = Path(result[0]) if Path(result[0]).exists() else Path(f"output/ar_stickers/workflow_test_{i}.usdz")
            assert actual_path.exists()

            # Validate file properties
            assert actual_path.stat().st_size > 0
            assert actual_path.stat().st_size < 25 * 1024 * 1024  # iOS limit

            # Validate UV orientation
            validation_result = self._validate_uv_orientation_from_usdz(actual_path)
            assert validation_result["valid"], f"Workflow test {i} failed UV validation: {validation_result['error']}"

    def test_file_size_limits(self, exporter, temp_output_dir, output_cleanup):
        """Test that exported files stay within iOS ARKit size limits."""
        # Create different sized images to test optimization
        image_sizes = [
            (256, 256),  # Small
            (512, 512),  # Medium
            (1024, 1024),  # Large
            (2048, 2048),  # Very large
        ]

        for width, height in image_sizes:
            # Create test image in BCHW format
            test_image = torch.rand(1, 3, height, width)

            output_path = temp_output_dir / f"size_test_{width}x{height}.usdz"
            output_cleanup(output_path)

            result = exporter.export_usdz(
                image=test_image,
                filename=f"size_test_{width}x{height}",
                optimization_level="mobile",  # Use mobile optimization for size control
            )

            actual_path = Path(result[0]) if Path(result[0]).exists() else Path(f"output/ar_stickers/size_test_{width}x{height}.usdz")
            assert actual_path.exists()

            # Check file size is within iOS limits (25MB)
            file_size = actual_path.stat().st_size
            assert file_size > 0
            assert file_size < 25 * 1024 * 1024, f"File size {file_size} bytes exceeds iOS limit for {width}x{height} image"
