"""Spatial Positioner Node for ComfyUI Reality."""

from typing import Any

import numpy as np

from ..exceptions import ARGeometryError
from .base import BaseARNode


class SpatialPositioner(BaseARNode):
    """Position and scale 3D objects in AR space.

    This node handles precise 3D positioning, rotation, and scaling for AR objects
    with support for world-space coordinates, anchor points, and relative positioning.
    """

    @classmethod
    def INPUT_TYPES(cls) -> dict[str, Any]:
        """Define the input parameters for the node."""
        return {
            "required": {
                "position_x": (
                    "FLOAT",
                    {"default": 0.0, "min": -10.0, "max": 10.0, "step": 0.01},
                ),
                "position_y": (
                    "FLOAT",
                    {"default": 0.0, "min": -10.0, "max": 10.0, "step": 0.01},
                ),
                "position_z": (
                    "FLOAT",
                    {"default": 0.0, "min": -10.0, "max": 10.0, "step": 0.01},
                ),
                "scale": (
                    "FLOAT",
                    {"default": 1.0, "min": 0.001, "max": 100.0, "step": 0.01},
                ),
            },
            "optional": {
                "rotation_x": (
                    "FLOAT",
                    {"default": 0.0, "min": -360.0, "max": 360.0, "step": 1.0},
                ),
                "rotation_y": (
                    "FLOAT",
                    {"default": 0.0, "min": -360.0, "max": 360.0, "step": 1.0},
                ),
                "rotation_z": (
                    "FLOAT",
                    {"default": 0.0, "min": -360.0, "max": 360.0, "step": 1.0},
                ),
                "anchor_point": (
                    ["center", "bottom", "top", "front", "back", "left", "right"],
                    {"default": "center"},
                ),
                "coordinate_system": (
                    ["world", "local", "parent"],
                    {"default": "world"},
                ),
                "reference_object": ("SPATIAL_TRANSFORM",),
                "relative_positioning": ("BOOLEAN", {"default": False}),
                "auto_ground_snap": ("BOOLEAN", {"default": True}),
                "collision_bounds": (
                    ["none", "box", "sphere", "mesh"],
                    {"default": "box"},
                ),
            },
        }

    RETURN_TYPES = ("SPATIAL_TRANSFORM", "MATRIX4X4", "BOUNDS")
    RETURN_NAMES = ("transform", "transform_matrix", "bounding_box")
    FUNCTION = "create_spatial_transform"
    CATEGORY = "📐 ComfyReality/Spatial"
    DESCRIPTION = "Position and scale 3D objects in AR space"

    def create_spatial_transform(
        self,
        position_x: float,
        position_y: float,
        position_z: float,
        scale: float,
        rotation_x: float = 0.0,
        rotation_y: float = 0.0,
        rotation_z: float = 0.0,
        anchor_point: str = "center",
        coordinate_system: str = "world",
        reference_object=None,
        relative_positioning: bool = False,
        auto_ground_snap: bool = True,
        collision_bounds: str = "box",
    ):
        """Create spatial transformation data for AR positioning."""
        try:
            # Validate inputs using base class methods
            self.validate_numeric_parameter(position_x, "position_x", min_val=-1000.0, max_val=1000.0)
            self.validate_numeric_parameter(position_y, "position_y", min_val=-1000.0, max_val=1000.0)
            self.validate_numeric_parameter(position_z, "position_z", min_val=-1000.0, max_val=1000.0)
            self.validate_numeric_parameter(scale, "scale", min_val=0.001, max_val=100.0)
            self.validate_numeric_parameter(rotation_x, "rotation_x", min_val=-3600.0, max_val=3600.0)
            self.validate_numeric_parameter(rotation_y, "rotation_y", min_val=-3600.0, max_val=3600.0)
            self.validate_numeric_parameter(rotation_z, "rotation_z", min_val=-3600.0, max_val=3600.0)
            self.validate_string_parameter(
                anchor_point,
                "anchor_point",
                valid_values=[
                    "center",
                    "bottom",
                    "top",
                    "front",
                    "back",
                    "left",
                    "right",
                ],
            )
            self.validate_string_parameter(
                coordinate_system,
                "coordinate_system",
                valid_values=["world", "local", "parent"],
            )
            self.validate_string_parameter(
                collision_bounds,
                "collision_bounds",
                valid_values=["none", "box", "sphere", "mesh"],
            )

            self.log_processing_info(
                "Spatial Transform",
                position=[position_x, position_y, position_z],
                scale=scale,
                anchor=anchor_point,
            )

            # Build transformation matrix
            transform_matrix = self._build_transform_matrix(
                position_x,
                position_y,
                position_z,
                rotation_x,
                rotation_y,
                rotation_z,
                scale,
                anchor_point,
            )

            # Handle relative positioning
            if relative_positioning and reference_object is not None:
                transform_matrix = self._apply_relative_transform(transform_matrix, reference_object)

            # Auto ground snapping
            if auto_ground_snap:
                transform_matrix = self._snap_to_ground(transform_matrix)

            # Create spatial transform data
            spatial_transform = {
                "position": [position_x, position_y, position_z],
                "rotation": [rotation_x, rotation_y, rotation_z],
                "scale": scale,
                "anchor_point": anchor_point,
                "coordinate_system": coordinate_system,
                "matrix": transform_matrix.tolist(),
            }

            # Calculate bounding box
            bounds = self._calculate_bounds(transform_matrix, scale, collision_bounds)

            result = (spatial_transform, transform_matrix, bounds)
            self.validate_return_types(result, self.RETURN_TYPES)

            self.log_result_info("Spatial Transform", success=True, scale=scale)
            return result

        except Exception as e:
            self.log_result_info("Spatial Transform", success=False, error=str(e))
            raise ARGeometryError(f"Spatial transform failed: {e}") from e

    def _build_transform_matrix(self, tx, ty, tz, rx, ry, rz, scale, anchor):
        """Build 4x4 transformation matrix."""
        # Placeholder: construct transformation matrix
        matrix = np.eye(4, dtype=np.float32)

        # Apply scale
        matrix[0, 0] = scale
        matrix[1, 1] = scale
        matrix[2, 2] = scale

        # Apply rotation (simplified)
        # TODO: Implement proper rotation matrix construction

        # Apply translation
        matrix[0, 3] = tx
        matrix[1, 3] = ty
        matrix[2, 3] = tz

        return matrix

    def _apply_relative_transform(self, matrix, reference):
        """Apply relative positioning to another object."""
        # TODO: Implement relative positioning logic
        return matrix

    def _snap_to_ground(self, matrix):
        """Snap object to ground plane."""
        # TODO: Implement ground snapping logic
        return matrix

    def _calculate_bounds(self, matrix, scale, bounds_type):
        """Calculate object bounding box."""
        # Placeholder bounding box calculation
        bounds = {
            "type": bounds_type,
            "min": [-scale, -scale, -scale],
            "max": [scale, scale, scale],
            "center": [matrix[0, 3], matrix[1, 3], matrix[2, 3]],
        }
        return bounds
