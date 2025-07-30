"""Tests for utility modules."""

import tempfile
from pathlib import Path

import numpy as np
import pytest
import torch
from PIL import Image

from comfy_reality.utils.image_utils import apply_mask, create_alpha_channel, postprocess_image, preprocess_image, resize_image
from comfy_reality.utils.usdz_utils import (
    create_geometry_data,
    create_material_properties,
    create_usdz_file,
    optimize_for_ar,
    validate_usdz_compatibility,
)
from comfy_reality.utils.validation import (
    validate_ar_requirements,
    validate_image_tensor,
    validate_mask_tensor,
    validate_usdz,
    validate_workflow,
)


class TestImageUtils:
    """Test suite for image utilities."""

    @pytest.fixture
    def numpy_image(self):
        """Create sample numpy image."""
        return np.random.randint(0, 255, (256, 256, 3), dtype=np.uint8)

    @pytest.fixture
    def torch_image_hwc(self):
        """Create sample torch image in HWC format."""
        return torch.rand(256, 256, 3)

    @pytest.fixture
    def torch_image_chw(self):
        """Create sample torch image in CHW format."""
        return torch.rand(3, 256, 256)

    @pytest.fixture
    def pil_image(self):
        """Create sample PIL image."""
        return Image.fromarray(np.random.randint(0, 255, (256, 256, 3), dtype=np.uint8))

    def test_preprocess_image_numpy(self, numpy_image):
        """Test preprocessing numpy image."""
        result = preprocess_image(numpy_image)

        assert isinstance(result, torch.Tensor)
        assert result.dim() == 4  # BCHW
        assert result.shape == (1, 3, 256, 256)
        assert 0 <= result.min() <= result.max() <= 1

    def test_preprocess_image_torch_hwc(self, torch_image_hwc):
        """Test preprocessing torch image in HWC format."""
        result = preprocess_image(torch_image_hwc)

        assert isinstance(result, torch.Tensor)
        assert result.dim() == 4  # BCHW
        assert result.shape == (1, 3, 256, 256)

    def test_preprocess_image_torch_chw(self, torch_image_chw):
        """Test preprocessing torch image in CHW format."""
        result = preprocess_image(torch_image_chw)

        assert isinstance(result, torch.Tensor)
        assert result.dim() == 4  # BCHW
        assert result.shape == (1, 3, 256, 256)

    def test_preprocess_image_pil(self, pil_image):
        """Test preprocessing PIL image."""
        result = preprocess_image(pil_image)

        assert isinstance(result, torch.Tensor)
        assert result.dim() == 4  # BCHW
        assert result.shape == (1, 3, 256, 256)

    def test_postprocess_image(self):
        """Test postprocessing image tensor."""
        # Create BCHW tensor
        tensor = torch.rand(1, 3, 128, 128)
        result = postprocess_image(tensor)

        assert isinstance(result, np.ndarray)
        assert result.shape == (128, 128, 3)
        assert result.dtype == np.uint8
        assert 0 <= result.min() <= result.max() <= 255

    def test_postprocess_image_chw(self):
        """Test postprocessing CHW image tensor."""
        tensor = torch.rand(3, 64, 64)
        result = postprocess_image(tensor)

        assert isinstance(result, np.ndarray)
        assert result.shape == (64, 64, 3)
        assert result.dtype == np.uint8

    def test_resize_image(self):
        """Test image resizing."""
        image = torch.rand(3, 256, 256)
        resized = resize_image(image, (128, 128))

        assert isinstance(resized, torch.Tensor)
        assert resized.shape == (3, 128, 128)

    def test_resize_image_batch(self):
        """Test image resizing with batch dimension."""
        image = torch.rand(2, 3, 256, 256)
        resized = resize_image(image, (512, 512))

        assert isinstance(resized, torch.Tensor)
        assert resized.shape == (2, 3, 512, 512)

    def test_create_alpha_channel(self):
        """Test alpha channel creation."""
        mask = torch.rand(256, 256)
        alpha = create_alpha_channel(mask)

        assert isinstance(alpha, torch.Tensor)
        assert alpha.shape == (256, 256)
        assert alpha.dtype == torch.float32

    def test_create_alpha_channel_3d(self):
        """Test alpha channel creation from 3D mask."""
        mask = torch.rand(256, 256, 1)
        alpha = create_alpha_channel(mask)

        assert isinstance(alpha, torch.Tensor)
        assert alpha.shape == (256, 256)

    def test_apply_mask_rgb(self):
        """Test applying mask to RGB image."""
        image = torch.rand(3, 256, 256)
        mask = torch.rand(256, 256)

        result = apply_mask(image, mask)

        assert isinstance(result, torch.Tensor)
        assert result.shape == (4, 256, 256)  # RGBA

    def test_apply_mask_rgba(self):
        """Test applying mask to RGBA image."""
        image = torch.rand(4, 256, 256)
        mask = torch.rand(256, 256)

        result = apply_mask(image, mask)

        assert isinstance(result, torch.Tensor)
        assert result.shape == (4, 256, 256)  # RGBA

    def test_apply_mask_batch(self):
        """Test applying mask with batch dimensions."""
        image = torch.rand(1, 3, 256, 256)
        mask = torch.rand(1, 256, 256)

        result = apply_mask(image, mask)

        assert isinstance(result, torch.Tensor)
        assert result.shape == (4, 256, 256)


class TestUSDZUtils:
    """Test suite for USDZ utilities."""

    @pytest.fixture
    def sample_image(self):
        """Create sample image."""
        return np.random.randint(0, 255, (512, 512, 3), dtype=np.uint8)

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    def test_create_usdz_file(self, sample_image, temp_dir):
        """Test USDZ file creation."""
        output_path = temp_dir / "test.usdz"

        success = create_usdz_file(sample_image, str(output_path))

        assert success is True
        assert output_path.exists()
        assert output_path.stat().st_size > 0

    def test_create_usdz_file_with_scale(self, sample_image, temp_dir):
        """Test USDZ file creation with scale parameter."""
        output_path = temp_dir / "test_scale.usdz"

        success = create_usdz_file(sample_image, str(output_path), scale=2.0)

        assert success is True
        assert output_path.exists()

    def test_create_usdz_file_invalid_path(self, sample_image):
        """Test USDZ file creation with invalid path."""
        success = create_usdz_file(sample_image, "/invalid/path/test.usdz")

        assert success is False

    def test_optimize_for_ar_no_resize(self, sample_image):
        """Test AR optimization without resizing."""
        optimized = optimize_for_ar(sample_image, (1024, 1024))

        # Should return same image since it's within limits
        assert np.array_equal(optimized, sample_image)

    def test_optimize_for_ar_with_resize(self):
        """Test AR optimization with resizing."""
        large_image = np.random.randint(0, 255, (3000, 2000, 3), dtype=np.uint8)
        optimized = optimize_for_ar(large_image, (1024, 1024))

        assert isinstance(optimized, np.ndarray)
        assert max(optimized.shape[:2]) <= 1024
        assert optimized.shape[2] == 3  # Channels preserved

    def test_optimize_for_ar_grayscale(self):
        """Test AR optimization with grayscale image."""
        gray_image = np.random.randint(0, 255, (2000, 2000), dtype=np.uint8)
        optimized = optimize_for_ar(gray_image, (1024, 1024))

        assert isinstance(optimized, np.ndarray)
        assert max(optimized.shape[:2]) <= 1024
        assert len(optimized.shape) == 2  # Still grayscale

    def test_validate_usdz_compatibility_valid(self, sample_image):
        """Test USDZ compatibility validation with valid image."""
        is_compatible, issues = validate_usdz_compatibility(sample_image)

        assert isinstance(is_compatible, bool)
        assert isinstance(issues, list)

    def test_validate_usdz_compatibility_too_large(self):
        """Test USDZ compatibility validation with oversized image."""
        large_image = np.random.randint(0, 255, (3000, 3000, 3), dtype=np.uint8)
        is_compatible, issues = validate_usdz_compatibility(large_image)

        assert is_compatible is False
        assert any("too large" in issue.lower() for issue in issues)

    def test_validate_usdz_compatibility_non_square(self):
        """Test USDZ compatibility validation with non-square image."""
        rect_image = np.random.randint(0, 255, (512, 1024, 3), dtype=np.uint8)
        is_compatible, issues = validate_usdz_compatibility(rect_image)

        assert is_compatible is False
        assert any("square" in issue.lower() for issue in issues)

    def test_validate_usdz_compatibility_wrong_channels(self):
        """Test USDZ compatibility validation with wrong number of channels."""
        wrong_channels = np.random.randint(0, 255, (512, 512, 2), dtype=np.uint8)
        is_compatible, issues = validate_usdz_compatibility(wrong_channels)

        assert is_compatible is False
        assert any("channels" in issue.lower() for issue in issues)

    def test_create_material_properties(self):
        """Test material properties creation."""
        materials = ["standard", "unlit", "metallic", "emission"]

        for material in materials:
            props = create_material_properties(material)

            assert isinstance(props, dict)
            assert "diffuse_color" in props
            assert "opacity" in props
            assert len(props["diffuse_color"]) == 3

    def test_create_material_properties_unknown(self):
        """Test material properties creation with unknown type."""
        props = create_material_properties("unknown_material")
        standard_props = create_material_properties("standard")

        assert props == standard_props

    def test_create_geometry_data(self):
        """Test geometry data creation."""
        geometry = create_geometry_data(2.0)

        assert isinstance(geometry, dict)
        assert "vertices" in geometry
        assert "uvs" in geometry
        assert "indices" in geometry

        assert len(geometry["vertices"]) == 4
        assert len(geometry["uvs"]) == 4
        assert len(geometry["indices"]) == 6

    def test_create_geometry_data_different_scales(self):
        """Test geometry data creation with different scales."""
        scales = [0.5, 1.0, 2.0, 5.0]

        for scale in scales:
            geometry = create_geometry_data(scale)

            # Check that vertices scale correctly
            vertices = geometry["vertices"]
            expected_extent = scale / 2

            for vertex in vertices:
                assert abs(vertex[0]) == expected_extent
                assert abs(vertex[2]) == expected_extent


class TestValidation:
    """Test suite for validation utilities."""

    @pytest.fixture
    def valid_workflow(self):
        """Create valid workflow data."""
        return {
            "nodes": [{"id": "1", "type": "AROptimizer"}, {"id": "2", "type": "SpatialPositioner"}, {"id": "3", "type": "USDZExporter"}],
            "connections": [{"from_node": "1", "to_node": "2", "from_output": "optimized_image", "to_input": "image"}],
        }

    @pytest.fixture
    def temp_usdz_file(self):
        """Create temporary USDZ file."""
        with tempfile.NamedTemporaryFile(suffix=".usdz", delete=False) as f:
            f.write(b"PK\x03\x04")  # ZIP signature
            f.write(b"\x00" * 100)  # Some content
            temp_path = f.name

        yield temp_path

        # Cleanup
        Path(temp_path).unlink(missing_ok=True)

    def test_validate_workflow_valid(self, valid_workflow):
        """Test workflow validation with valid data."""
        is_valid, errors = validate_workflow(valid_workflow)

        assert is_valid is True
        assert len(errors) == 0

    def test_validate_workflow_missing_nodes(self):
        """Test workflow validation with missing nodes."""
        invalid_workflow = {"connections": []}

        is_valid, errors = validate_workflow(invalid_workflow)

        assert is_valid is False
        assert any("nodes" in error for error in errors)

    def test_validate_workflow_missing_connections(self):
        """Test workflow validation with missing connections."""
        invalid_workflow = {"nodes": []}

        is_valid, errors = validate_workflow(invalid_workflow)

        assert is_valid is False
        assert any("connections" in error for error in errors)

    def test_validate_workflow_invalid_node_type(self):
        """Test workflow validation with invalid node type."""
        invalid_workflow = {"nodes": [{"id": "1", "type": "InvalidNodeType"}], "connections": []}

        is_valid, errors = validate_workflow(invalid_workflow)

        assert is_valid is False
        assert any("Invalid node type" in error for error in errors)

    def test_validate_workflow_missing_node_fields(self):
        """Test workflow validation with missing node fields."""
        invalid_workflow = {
            "nodes": [{"id": "1"}],  # Missing type
            "connections": [],
        }

        is_valid, errors = validate_workflow(invalid_workflow)

        assert is_valid is False
        assert any("Missing required field" in error for error in errors)

    def test_validate_usdz_valid_file(self, temp_usdz_file):
        """Test USDZ validation with valid file."""
        is_valid, issues = validate_usdz(temp_usdz_file)

        assert is_valid is True
        assert len(issues) == 0

    def test_validate_usdz_nonexistent_file(self):
        """Test USDZ validation with nonexistent file."""
        is_valid, issues = validate_usdz("nonexistent.usdz")

        assert is_valid is False
        assert any("does not exist" in issue for issue in issues)

    def test_validate_usdz_wrong_extension(self, temp_usdz_file):
        """Test USDZ validation with wrong extension."""
        wrong_ext_path = temp_usdz_file.replace(".usdz", ".zip")
        Path(temp_usdz_file).rename(wrong_ext_path)

        is_valid, issues = validate_usdz(wrong_ext_path)

        assert is_valid is False
        assert any("extension" in issue for issue in issues)

        # Cleanup
        Path(wrong_ext_path).unlink()

    def test_validate_usdz_empty_file(self):
        """Test USDZ validation with empty file."""
        with tempfile.NamedTemporaryFile(suffix=".usdz", delete=False) as f:
            temp_path = f.name  # Create empty file

        is_valid, issues = validate_usdz(temp_path)

        assert is_valid is False
        assert any("empty" in issue for issue in issues)

        # Cleanup
        Path(temp_path).unlink()

    def test_validate_image_tensor_valid(self):
        """Test image tensor validation with valid tensor."""
        valid_tensor = torch.rand(1, 3, 256, 256)
        is_valid, issues = validate_image_tensor(valid_tensor)

        assert is_valid is True
        assert len(issues) == 0

    def test_validate_image_tensor_wrong_type(self):
        """Test image tensor validation with wrong type."""
        is_valid, issues = validate_image_tensor("not a tensor")

        assert is_valid is False
        assert any("torch.Tensor" in issue for issue in issues)

    def test_validate_image_tensor_wrong_dimensions(self):
        """Test image tensor validation with wrong dimensions."""
        wrong_dims = torch.rand(256, 256)  # 2D instead of 3D/4D
        is_valid, issues = validate_image_tensor(wrong_dims)

        assert is_valid is False
        assert any("dimensions" in issue for issue in issues)

    def test_validate_image_tensor_wrong_channels(self):
        """Test image tensor validation with wrong number of channels."""
        wrong_channels = torch.rand(1, 7, 256, 256)  # 7 channels
        is_valid, issues = validate_image_tensor(wrong_channels)

        assert is_valid is False
        assert any("channels" in issue for issue in issues)

    def test_validate_image_tensor_wrong_range(self):
        """Test image tensor validation with wrong value range."""
        wrong_range = torch.rand(1, 3, 256, 256) * 2  # Values > 1
        is_valid, issues = validate_image_tensor(wrong_range)

        assert is_valid is False
        assert any("range" in issue for issue in issues)

    def test_validate_mask_tensor_valid(self):
        """Test mask tensor validation with valid tensor."""
        valid_mask = torch.rand(256, 256)
        is_valid, issues = validate_mask_tensor(valid_mask)

        assert is_valid is True
        assert len(issues) == 0

    def test_validate_mask_tensor_wrong_type(self):
        """Test mask tensor validation with wrong type."""
        is_valid, issues = validate_mask_tensor(np.array([1, 2, 3]))

        assert is_valid is False
        assert any("torch.Tensor" in issue for issue in issues)

    def test_validate_ar_requirements_square_image(self):
        """Test AR requirements validation with square image."""
        square_image = np.random.randint(0, 255, (512, 512, 3), dtype=np.uint8)
        meets_req, recommendations = validate_ar_requirements(square_image)

        assert isinstance(meets_req, bool)
        assert isinstance(recommendations, list)

    def test_validate_ar_requirements_extreme_aspect_ratio(self):
        """Test AR requirements validation with extreme aspect ratio."""
        extreme_image = np.random.randint(0, 255, (100, 1000, 3), dtype=np.uint8)
        meets_req, recommendations = validate_ar_requirements(extreme_image)

        assert meets_req is False
        assert any("aspect ratio" in rec.lower() for rec in recommendations)

    def test_validate_ar_requirements_low_resolution(self):
        """Test AR requirements validation with low resolution."""
        low_res_image = np.random.randint(0, 255, (128, 128, 3), dtype=np.uint8)
        meets_req, recommendations = validate_ar_requirements(low_res_image)

        assert meets_req is False
        assert any("resolution" in rec.lower() for rec in recommendations)

    def test_validate_ar_requirements_high_resolution(self):
        """Test AR requirements validation with high resolution."""
        high_res_image = np.random.randint(0, 255, (4096, 4096, 3), dtype=np.uint8)
        meets_req, recommendations = validate_ar_requirements(high_res_image)

        assert meets_req is False
        assert any("performance" in rec.lower() for rec in recommendations)

    @pytest.mark.parametrize("channels", [1, 3, 4])
    def test_validate_image_tensor_valid_channels(self, channels):
        """Test image tensor validation with different valid channel counts."""
        if channels == 1:
            tensor = torch.rand(1, 1, 256, 256)
        else:
            tensor = torch.rand(1, channels, 256, 256)

        is_valid, issues = validate_image_tensor(tensor)
        assert is_valid is True
        assert len(issues) == 0
