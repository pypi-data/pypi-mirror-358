"""Tests for USDZExporter node."""

import tempfile
from pathlib import Path

import numpy as np
import pytest
import torch

from comfy_reality.nodes.usdz_exporter import USDZExporter


class TestUSDZExporter:
    """Test suite for USDZExporter."""

    @pytest.fixture
    def exporter(self):
        """Create exporter instance."""
        return USDZExporter()

    @pytest.fixture
    def sample_image(self):
        """Create a sample image tensor in BCHW format."""
        return torch.rand(1, 3, 512, 512)

    @pytest.fixture
    def sample_mask(self):
        """Create a sample mask tensor."""
        return torch.rand(1, 512, 512)

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    def test_input_types(self, exporter):
        """Test INPUT_TYPES class method."""
        input_types = exporter.INPUT_TYPES()

        assert isinstance(input_types, dict)
        assert "required" in input_types
        assert "optional" in input_types

        # Check required inputs
        required = input_types["required"]
        assert "image" in required
        assert "filename" in required

        # Check optional inputs
        optional = input_types["optional"]
        assert "mask" in optional
        assert "scale" in optional
        assert "material_type" in optional
        assert "optimization_level" in optional
        assert "coordinate_system" in optional
        assert "physics_enabled" in optional

    def test_class_attributes(self, exporter):
        """Test class attributes."""
        assert exporter.RETURN_TYPES == ("STRING",)
        assert exporter.RETURN_NAMES == ("usdz_path",)
        assert exporter.FUNCTION == "export_usdz"
        assert exporter.CATEGORY == "📦 ComfyReality/Export"
        assert isinstance(exporter.DESCRIPTION, str)

    def test_export_usdz_basic(self, exporter, sample_image, temp_dir):
        """Test basic USDZ export."""
        # Temporarily change output directory for testing
        original_method = exporter.export_usdz

        def mock_export_usdz(*args, **kwargs):
            result = original_method(*args, **kwargs)
            # Check if file was created in default location
            default_path = Path("output/ar_stickers/test_sticker.usdz")
            if default_path.exists():
                return (str(default_path),)
            return result

        exporter.export_usdz = mock_export_usdz

        result = exporter.export_usdz(sample_image, "test_sticker")

        assert isinstance(result, tuple)
        assert len(result) == 1
        assert isinstance(result[0], str)
        assert result[0].endswith(".usdz")

    def test_export_usdz_with_mask(self, exporter, sample_image, sample_mask):
        """Test USDZ export with mask."""
        result = exporter.export_usdz(sample_image, "test_with_mask", mask=sample_mask)

        assert isinstance(result, tuple)
        assert len(result) == 1

    def test_export_usdz_with_all_options(self, exporter, sample_image, sample_mask):
        """Test USDZ export with all optional parameters."""
        result = exporter.export_usdz(
            image=sample_image,
            filename="test_full_options",
            mask=sample_mask,
            scale=2.0,
            material_type="metallic",
            optimization_level="quality",
            coordinate_system="z_up",
            physics_enabled=True,
        )

        assert isinstance(result, tuple)
        assert len(result) == 1

    @pytest.mark.parametrize("material", ["standard", "unlit", "metallic", "emission"])
    def test_all_material_types(self, exporter, sample_image, material):
        """Test all material types."""
        result = exporter.export_usdz(sample_image, f"test_{material}", material_type=material)

        assert isinstance(result, tuple)
        assert len(result) == 1

    @pytest.mark.parametrize("level", ["mobile", "balanced", "quality"])
    def test_all_optimization_levels(self, exporter, sample_image, level):
        """Test all optimization levels."""
        result = exporter.export_usdz(sample_image, f"test_{level}", optimization_level=level)

        assert isinstance(result, tuple)
        assert len(result) == 1

    @pytest.mark.parametrize("coord", ["y_up", "z_up"])
    def test_coordinate_systems(self, exporter, sample_image, coord):
        """Test different coordinate systems."""
        result = exporter.export_usdz(sample_image, f"test_{coord}", coordinate_system=coord)

        assert isinstance(result, tuple)
        assert len(result) == 1

    def test_sanitize_filename(self, exporter):
        """Test filename sanitization."""
        # Test invalid characters
        assert exporter._sanitize_filename("test<>file") == "test__file"
        assert exporter._sanitize_filename('test:"file') == "test__file"
        assert exporter._sanitize_filename("test/\\file") == "test__file"

        # Test length limit
        long_name = "a" * 150
        sanitized = exporter._sanitize_filename(long_name)
        assert len(sanitized) <= 100

        # Test empty filename
        assert exporter._sanitize_filename("") == "ar_sticker"
        assert exporter._sanitize_filename("   ") == "ar_sticker"

        # Test valid filename
        assert exporter._sanitize_filename("valid_filename") == "valid_filename"

    def test_tensor_to_numpy(self, exporter):
        """Test tensor to numpy conversion."""
        # Test 4D tensor (BCHW format)
        tensor_4d = torch.rand(1, 3, 256, 256)
        result = exporter.tensor_to_numpy(tensor_4d)
        assert isinstance(result, np.ndarray)
        assert result.shape == (256, 256, 3)

        # Test 3D tensor (CHW format)
        tensor_3d = torch.rand(3, 256, 256)
        result = exporter.tensor_to_numpy(tensor_3d)
        assert isinstance(result, np.ndarray)
        assert result.shape == (256, 256, 3)

        # Test None input
        result = exporter.tensor_to_numpy(None)
        assert result is None

    def test_optimize_for_ar(self, exporter):
        """Test AR optimization."""
        # Test image that needs resizing
        large_image = np.random.randint(0, 255, (3000, 3000, 3), dtype=np.uint8)
        optimized, mask_opt = exporter._optimize_for_ar(large_image, None, "mobile")

        assert isinstance(optimized, np.ndarray)
        assert mask_opt is None

        # Test image that doesn't need resizing
        small_image = np.random.randint(0, 255, (512, 512, 3), dtype=np.uint8)
        optimized, mask_opt = exporter._optimize_for_ar(small_image, None, "quality")

        assert np.array_equal(optimized, small_image)

        # Test with mask
        mask = np.random.rand(512, 512).astype(np.float32)
        optimized, mask_opt = exporter._optimize_for_ar(small_image, mask, "balanced")

        assert isinstance(mask_opt, np.ndarray)

    def test_create_geometry(self, exporter):
        """Test geometry creation."""
        image = np.random.randint(0, 255, (256, 256, 3), dtype=np.uint8)
        geometry = exporter._create_geometry(image, 2.0)

        assert isinstance(geometry, dict)
        assert "vertices" in geometry
        assert "uvs" in geometry
        assert "indices" in geometry

        # Check vertices
        vertices = geometry["vertices"]
        assert len(vertices) == 4  # Quad
        assert all(len(v) == 3 for v in vertices)  # 3D coordinates

        # Check UVs
        uvs = geometry["uvs"]
        assert len(uvs) == 4
        assert all(len(uv) == 2 for uv in uvs)  # 2D coordinates

        # Check indices
        indices = geometry["indices"]
        assert len(indices) == 6  # Two triangles

    def test_create_material(self, exporter):
        """Test material creation."""
        # Test all material types
        materials = ["standard", "unlit", "metallic", "emission"]

        for mat_type in materials:
            material = exporter._create_material(mat_type)

            assert isinstance(material, dict)
            assert "diffuse_color" in material
            assert "opacity" in material

            # Check specific properties
            if mat_type == "unlit":
                assert material.get("unlit") is True
            elif mat_type == "metallic":
                assert "metallic" in material
                assert "roughness" in material
            elif mat_type == "emission":
                assert "emission_color" in material

        # Test unknown material type (should default to standard)
        default_material = exporter._create_material("unknown")
        standard_material = exporter._create_material("standard")
        assert default_material == standard_material

    def test_create_usdz_file(self, exporter, temp_dir):
        """Test USDZ file creation."""
        image = np.random.randint(0, 255, (256, 256, 3), dtype=np.uint8)
        mask = np.random.rand(256, 256).astype(np.float32)
        output_path = str(temp_dir / "test.usdz")

        success = exporter._create_usdz_file(
            image_np=image,
            mask_np=mask,
            output_path=output_path,
            scale=1.0,
            material_type="standard",
            coordinate_system="y_up",
            physics_enabled=False,
        )

        assert success is True
        assert Path(output_path).exists()

        # Check file is not empty
        assert Path(output_path).stat().st_size > 0

    def test_create_usdz_file_error_handling(self, exporter):
        """Test USDZ file creation error handling."""
        image = np.random.randint(0, 255, (256, 256, 3), dtype=np.uint8)
        invalid_path = "/invalid/path/test.usdz"

        success = exporter._create_usdz_file(
            image_np=image,
            mask_np=None,
            output_path=invalid_path,
            scale=1.0,
            material_type="standard",
            coordinate_system="y_up",
            physics_enabled=False,
        )

        assert success is False

    def test_empty_filename_handling(self, exporter, sample_image):
        """Test handling of empty filename."""
        # Test empty string
        result = exporter.export_usdz(sample_image, "")
        assert isinstance(result, tuple)

        # Test whitespace-only string
        result = exporter.export_usdz(sample_image, "   ")
        assert isinstance(result, tuple)

    def test_different_image_formats(self, exporter):
        """Test export with different image tensor formats."""
        # Test CHW format
        image_chw = torch.rand(3, 512, 512)
        result = exporter.export_usdz(image_chw, "test_chw")
        assert isinstance(result, tuple)

        # Test BCHW format
        image_bchw = torch.rand(1, 3, 512, 512)
        result = exporter.export_usdz(image_bchw, "test_bchw")
        assert isinstance(result, tuple)

    def test_scale_parameter(self, exporter, sample_image):
        """Test different scale values."""
        scales = [0.1, 0.5, 1.0, 2.0, 5.0, 10.0]

        for scale in scales:
            result = exporter.export_usdz(sample_image, f"test_scale_{scale}", scale=scale)
            assert isinstance(result, tuple)
            assert len(result) == 1

    def test_physics_enabled(self, exporter, sample_image):
        """Test physics enabled/disabled."""
        # Test with physics enabled
        result = exporter.export_usdz(sample_image, "test_physics_on", physics_enabled=True)
        assert isinstance(result, tuple)

        # Test with physics disabled
        result = exporter.export_usdz(sample_image, "test_physics_off", physics_enabled=False)
        assert isinstance(result, tuple)

    @pytest.mark.slow
    def test_large_image_export(self, exporter):
        """Test export with large image (marked as slow)."""
        large_image = torch.rand(1, 3, 2048, 2048)

        result = exporter.export_usdz(
            large_image,
            "test_large_image",
            optimization_level="mobile",  # Use mobile optimization for speed
        )

        assert isinstance(result, tuple)
        assert len(result) == 1
        assert result[0].endswith(".usdz")

    def test_directory_creation(self, exporter, sample_image, temp_dir):
        """Test that output directories are created."""
        # This test verifies the directory creation logic
        result = exporter.export_usdz(sample_image, "test_dir_creation")

        # The default output directory should exist
        output_dir = Path("output/ar_stickers")
        assert output_dir.exists()
