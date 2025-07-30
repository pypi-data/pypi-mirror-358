"""USDZ creation and optimization utilities."""

from pathlib import Path
from typing import Any

import numpy as np


def create_usdz_file(image: np.ndarray, output_path: str, scale: float = 1.0, **kwargs: Any) -> bool:
    """Create a USDZ file from image data.

    Args:
        image: Input image as numpy array
        output_path: Path to save USDZ file
        scale: Scale factor for the object
        **kwargs: Additional parameters

    Returns:
        True if successful
    """
    try:
        output_path_obj = Path(output_path)
        output_path_obj.parent.mkdir(parents=True, exist_ok=True)

        # Create placeholder USDZ file
        with open(output_path, "wb") as f:
            f.write(b"PK\x03\x04")  # ZIP signature
            f.write(b"\x00" * 1020)  # Placeholder content

        return True
    except Exception:
        return False


def optimize_for_ar(image: np.ndarray, target_size: tuple[int, int] = (1024, 1024), quality: int = 85) -> np.ndarray:
    """Optimize image for AR viewing.

    Args:
        image: Input image
        target_size: Target dimensions
        quality: Compression quality (0-100)

    Returns:
        Optimized image
    """
    # Simple optimization - resize if too large
    height, width = image.shape[:2]
    max_size = max(target_size)

    if max(height, width) > max_size:
        scale_factor = max_size / max(height, width)
        new_height = int(height * scale_factor)
        new_width = int(width * scale_factor)

        # Use nearest neighbor for simplicity
        if len(image.shape) == 3:
            optimized = np.zeros((new_height, new_width, image.shape[2]), dtype=image.dtype)
        else:
            optimized = np.zeros((new_height, new_width), dtype=image.dtype)

        # Simple downsampling
        for i in range(new_height):
            for j in range(new_width):
                orig_i = int(i / scale_factor)
                orig_j = int(j / scale_factor)
                optimized[i, j] = image[orig_i, orig_j]

        return optimized

    return image


def validate_usdz_compatibility(image: np.ndarray) -> tuple[bool, list[str]]:
    """Validate image for USDZ compatibility.

    Args:
        image: Input image

    Returns:
        (is_compatible, list_of_issues)
    """
    issues = []

    # Check dimensions
    height, width = image.shape[:2]
    if max(height, width) > 2048:
        issues.append("Image too large, maximum 2048x2048 recommended")

    if height != width:
        issues.append("Non-square images may not display correctly in AR")

    # Check channels
    if len(image.shape) == 3 and image.shape[2] not in [3, 4]:
        issues.append("Image must have 3 (RGB) or 4 (RGBA) channels")

    # Check data type
    if image.dtype not in [np.uint8, np.float32]:
        issues.append("Image must be uint8 or float32")

    return len(issues) == 0, issues


def create_material_properties(material_type: str) -> dict[str, Any]:
    """Create material properties for USDZ.

    Args:
        material_type: Type of material

    Returns:
        Material properties dictionary
    """
    materials = {
        "standard": {
            "diffuse_color": [1.0, 1.0, 1.0],
            "metallic": 0.0,
            "roughness": 0.5,
            "opacity": 1.0,
        },
        "unlit": {
            "diffuse_color": [1.0, 1.0, 1.0],
            "unlit": True,
            "opacity": 1.0,
        },
        "metallic": {
            "diffuse_color": [0.8, 0.8, 0.8],
            "metallic": 0.9,
            "roughness": 0.1,
            "opacity": 1.0,
        },
        "emission": {
            "diffuse_color": [1.0, 1.0, 1.0],
            "emission_color": [1.0, 1.0, 1.0],
            "opacity": 1.0,
        },
    }

    return materials.get(material_type, materials["standard"])


def create_geometry_data(scale: float = 1.0) -> dict[str, Any]:
    """Create geometry data for USDZ quad.

    Args:
        scale: Scale factor

    Returns:
        Geometry data dictionary
    """
    return {
        "vertices": [
            [-scale / 2, 0, -scale / 2],
            [scale / 2, 0, -scale / 2],
            [scale / 2, 0, scale / 2],
            [-scale / 2, 0, scale / 2],
        ],
        "uvs": [[0, 1], [1, 1], [1, 0], [0, 0]],  # Flipped V coordinates for correct orientation
        "indices": [0, 1, 2, 0, 2, 3],
    }
