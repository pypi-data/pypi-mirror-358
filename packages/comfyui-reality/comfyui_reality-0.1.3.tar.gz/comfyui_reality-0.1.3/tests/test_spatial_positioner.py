"""Tests for SpatialPositioner node."""

import numpy as np
import pytest

from comfy_reality.nodes.spatial_positioner import SpatialPositioner


class TestSpatialPositioner:
    """Test suite for SpatialPositioner."""

    @pytest.fixture
    def positioner(self):
        """Create positioner instance."""
        return SpatialPositioner()

    def test_input_types(self, positioner):
        """Test INPUT_TYPES class method."""
        input_types = positioner.INPUT_TYPES()

        assert isinstance(input_types, dict)
        assert "required" in input_types
        assert "optional" in input_types

        # Check required inputs
        required = input_types["required"]
        assert "position_x" in required
        assert "position_y" in required
        assert "position_z" in required
        assert "scale" in required

        # Check optional inputs
        optional = input_types["optional"]
        assert "rotation_x" in optional
        assert "rotation_y" in optional
        assert "rotation_z" in optional
        assert "anchor_point" in optional
        assert "coordinate_system" in optional

    def test_class_attributes(self, positioner):
        """Test class attributes."""
        assert positioner.RETURN_TYPES == ("SPATIAL_TRANSFORM", "MATRIX4X4", "BOUNDS")
        assert positioner.RETURN_NAMES == ("transform", "transform_matrix", "bounding_box")
        assert positioner.FUNCTION == "create_spatial_transform"
        assert positioner.CATEGORY == "📐 ComfyReality/Spatial"
        assert isinstance(positioner.DESCRIPTION, str)

    def test_create_spatial_transform_basic(self, positioner):
        """Test basic spatial transform creation."""
        result = positioner.create_spatial_transform(position_x=0.0, position_y=0.0, position_z=0.0, scale=1.0)

        assert isinstance(result, tuple)
        assert len(result) == 3

        transform, matrix, bounds = result
        assert isinstance(transform, dict)
        assert isinstance(matrix, np.ndarray)
        assert isinstance(bounds, dict)

    def test_transform_data_structure(self, positioner):
        """Test spatial transform data structure."""
        result = positioner.create_spatial_transform(
            position_x=1.0,
            position_y=2.0,
            position_z=3.0,
            scale=1.5,
            rotation_x=10.0,
            rotation_y=20.0,
            rotation_z=30.0,
            anchor_point="center",
        )

        transform, _, _ = result

        # Check required fields
        assert "position" in transform
        assert "rotation" in transform
        assert "scale" in transform
        assert "anchor_point" in transform
        assert "coordinate_system" in transform
        assert "matrix" in transform

        # Check data types and values
        assert transform["position"] == [1.0, 2.0, 3.0]
        assert transform["rotation"] == [10.0, 20.0, 30.0]
        assert transform["scale"] == 1.5
        assert transform["anchor_point"] == "center"
        assert isinstance(transform["matrix"], list)

    def test_matrix_dimensions(self, positioner):
        """Test transformation matrix dimensions."""
        result = positioner.create_spatial_transform(position_x=0.0, position_y=0.0, position_z=0.0, scale=1.0)

        _, matrix, _ = result

        # Should be 4x4 transformation matrix
        assert matrix.shape == (4, 4)
        assert matrix.dtype == np.float32 or matrix.dtype == np.float64

    @pytest.mark.parametrize("anchor", ["center", "bottom", "top", "front", "back", "left", "right"])
    def test_all_anchor_points(self, positioner, anchor):
        """Test all anchor point options."""
        result = positioner.create_spatial_transform(position_x=0.0, position_y=0.0, position_z=0.0, scale=1.0, anchor_point=anchor)

        assert isinstance(result, tuple)
        assert len(result) == 3

        transform, _, _ = result
        assert transform["anchor_point"] == anchor

    @pytest.mark.parametrize("coord_sys", ["world", "local", "parent"])
    def test_all_coordinate_systems(self, positioner, coord_sys):
        """Test all coordinate system options."""
        result = positioner.create_spatial_transform(position_x=0.0, position_y=0.0, position_z=0.0, scale=1.0, coordinate_system=coord_sys)

        assert isinstance(result, tuple)
        assert len(result) == 3

        transform, _, _ = result
        assert transform["coordinate_system"] == coord_sys

    @pytest.mark.parametrize("collision", ["none", "box", "sphere", "mesh"])
    def test_all_collision_bounds(self, positioner, collision):
        """Test all collision bounds options."""
        result = positioner.create_spatial_transform(position_x=0.0, position_y=0.0, position_z=0.0, scale=1.0, collision_bounds=collision)

        assert isinstance(result, tuple)
        assert len(result) == 3

        _, _, bounds = result
        # Bounds should be affected by collision type
        assert isinstance(bounds, dict)

    def test_different_scales(self, positioner):
        """Test different scale values."""
        scales = [0.1, 0.5, 1.0, 2.0, 5.0, 10.0]

        for scale in scales:
            result = positioner.create_spatial_transform(position_x=0.0, position_y=0.0, position_z=0.0, scale=scale)

            assert isinstance(result, tuple)
            assert len(result) == 3

            transform, matrix, _ = result
            assert transform["scale"] == scale
            assert isinstance(matrix, np.ndarray)

    def test_rotation_values(self, positioner):
        """Test different rotation values."""
        rotations = [
            (0.0, 0.0, 0.0),
            (90.0, 0.0, 0.0),
            (0.0, 90.0, 0.0),
            (0.0, 0.0, 90.0),
            (45.0, 45.0, 45.0),
            (180.0, 180.0, 180.0),
            (360.0, 360.0, 360.0),
        ]

        for rot_x, rot_y, rot_z in rotations:
            result = positioner.create_spatial_transform(
                position_x=0.0, position_y=0.0, position_z=0.0, scale=1.0, rotation_x=rot_x, rotation_y=rot_y, rotation_z=rot_z
            )

            assert isinstance(result, tuple)
            assert len(result) == 3

            transform, _, _ = result
            assert transform["rotation"] == [rot_x, rot_y, rot_z]

    def test_position_values(self, positioner):
        """Test different position values."""
        positions = [
            (0.0, 0.0, 0.0),
            (1.0, 2.0, 3.0),
            (-1.0, -2.0, -3.0),
            (10.0, 0.0, -5.0),
            (0.5, 0.25, 0.75),
        ]

        for pos_x, pos_y, pos_z in positions:
            result = positioner.create_spatial_transform(position_x=pos_x, position_y=pos_y, position_z=pos_z, scale=1.0)

            assert isinstance(result, tuple)
            assert len(result) == 3

            transform, _, _ = result
            assert transform["position"] == [pos_x, pos_y, pos_z]

    def test_relative_positioning(self, positioner):
        """Test relative positioning feature."""
        # Create reference object (simplified)
        reference_obj = {"position": [1.0, 1.0, 1.0], "rotation": [0.0, 0.0, 0.0], "scale": 1.0}

        result = positioner.create_spatial_transform(
            position_x=1.0, position_y=0.0, position_z=0.0, scale=1.0, reference_object=reference_obj, relative_positioning=True
        )

        assert isinstance(result, tuple)
        assert len(result) == 3

        transform, matrix, bounds = result
        assert isinstance(transform, dict)
        assert isinstance(matrix, np.ndarray)
        assert isinstance(bounds, dict)

    def test_auto_ground_snap(self, positioner):
        """Test auto ground snapping feature."""
        # Test with ground snap enabled
        result_snap = positioner.create_spatial_transform(
            position_x=0.0,
            position_y=5.0,  # High Y position
            position_z=0.0,
            scale=1.0,
            auto_ground_snap=True,
        )

        # Test with ground snap disabled
        result_no_snap = positioner.create_spatial_transform(
            position_x=0.0,
            position_y=5.0,  # Same high Y position
            position_z=0.0,
            scale=1.0,
            auto_ground_snap=False,
        )

        assert isinstance(result_snap, tuple)
        assert isinstance(result_no_snap, tuple)

        transform_snap, _, _ = result_snap
        transform_no_snap, _, _ = result_no_snap

        # Ground snap should affect Y position
        assert isinstance(transform_snap, dict)
        assert isinstance(transform_no_snap, dict)

    def test_bounding_box_structure(self, positioner):
        """Test bounding box data structure."""
        result = positioner.create_spatial_transform(
            position_x=0.0,
            position_y=0.0,
            position_z=0.0,
            scale=2.0,  # Larger scale should affect bounds
        )

        _, _, bounds = result

        # Check bounding box structure
        assert isinstance(bounds, dict)
        # Should contain min/max or center/size information
        assert len(bounds) > 0

    def test_extreme_values(self, positioner):
        """Test with extreme parameter values."""
        # Test extreme positions
        result = positioner.create_spatial_transform(
            position_x=1000.0,
            position_y=-1000.0,
            position_z=500.0,
            scale=0.001,  # Very small scale
            rotation_x=720.0,  # Multiple rotations
            rotation_y=-360.0,
            rotation_z=1080.0,
        )

        assert isinstance(result, tuple)
        assert len(result) == 3

        transform, matrix, bounds = result
        assert isinstance(transform, dict)
        assert isinstance(matrix, np.ndarray)
        assert isinstance(bounds, dict)

    def test_matrix_identity(self, positioner):
        """Test that identity transform produces expected matrix."""
        result = positioner.create_spatial_transform(
            position_x=0.0, position_y=0.0, position_z=0.0, scale=1.0, rotation_x=0.0, rotation_y=0.0, rotation_z=0.0
        )

        _, matrix, _ = result

        # Check that transformation matrix is reasonable
        assert isinstance(matrix, np.ndarray)
        assert matrix.shape == (4, 4)
        # Last row should be [0, 0, 0, 1] for homogeneous coordinates
        assert np.allclose(matrix[3, :], [0, 0, 0, 1])
