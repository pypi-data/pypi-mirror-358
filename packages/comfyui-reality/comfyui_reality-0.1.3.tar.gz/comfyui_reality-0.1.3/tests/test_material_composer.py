"""Tests for MaterialComposer node."""

import pytest
import torch

from comfy_reality.nodes.material_composer import MaterialComposer


class TestMaterialComposer:
    """Test suite for MaterialComposer."""

    @pytest.fixture
    def material_composer(self):
        """Create material composer instance."""
        return MaterialComposer()

    @pytest.fixture
    def sample_albedo(self):
        """Create sample albedo texture."""
        return torch.rand(1, 3, 512, 512)

    @pytest.fixture
    def sample_normal(self):
        """Create sample normal map."""
        return torch.rand(1, 3, 512, 512)

    @pytest.fixture
    def sample_roughness(self):
        """Create sample roughness map."""
        return torch.rand(1, 1, 512, 512)

    def test_input_types(self, material_composer):
        """Test INPUT_TYPES class method."""
        input_types = material_composer.INPUT_TYPES()

        assert isinstance(input_types, dict)
        assert "required" in input_types
        assert "optional" in input_types

        # Check required inputs
        required = input_types["required"]
        assert "albedo" in required
        assert "material_name" in required
        assert "material_type" in required

        # Check optional inputs
        optional = input_types["optional"]
        assert "normal_map" in optional
        assert "roughness_map" in optional
        assert "metallic_map" in optional
        assert "emission_map" in optional
        assert "opacity_map" in optional
        assert "roughness_factor" in optional
        assert "metallic_factor" in optional

    def test_class_attributes(self, material_composer):
        """Test class attributes."""
        assert material_composer.RETURN_TYPES == ("MATERIAL", "MATERIAL_PREVIEW", "MATERIAL_PROPERTIES")
        assert material_composer.RETURN_NAMES == ("material", "preview_render", "properties")
        assert material_composer.FUNCTION == "compose_material"
        assert material_composer.CATEGORY == "🎨 ComfyReality/Materials"
        assert isinstance(material_composer.DESCRIPTION, str)

    def test_compose_material_basic(self, material_composer, sample_albedo):
        """Test basic material composition."""
        result = material_composer.compose_material(albedo=sample_albedo, material_name="test_material", material_type="standard")

        assert isinstance(result, tuple)
        assert len(result) == 3

        material, preview, properties = result
        assert isinstance(material, dict)
        assert isinstance(preview, torch.Tensor)
        assert isinstance(properties, dict)

    @pytest.mark.parametrize("mat_type", ["standard", "unlit", "metallic", "emission", "glass", "subsurface"])
    def test_all_material_types(self, material_composer, sample_albedo, mat_type):
        """Test all material types."""
        result = material_composer.compose_material(albedo=sample_albedo, material_name=f"test_{mat_type}", material_type=mat_type)

        assert isinstance(result, tuple)
        assert len(result) == 3

        material, preview, properties = result
        assert isinstance(material, dict)
        assert properties["material_type"] == mat_type

    def test_compose_with_all_textures(self, material_composer, sample_albedo, sample_normal, sample_roughness):
        """Test material composition with all texture maps."""
        # Create additional texture maps
        metallic_map = torch.rand(1, 1, 512, 512)
        emission_map = torch.rand(1, 3, 512, 512)
        opacity_map = torch.rand(1, 1, 512, 512)
        occlusion_map = torch.rand(1, 1, 512, 512)

        result = material_composer.compose_material(
            albedo=sample_albedo,
            material_name="full_material",
            material_type="standard",
            normal_map=sample_normal,
            roughness_map=sample_roughness,
            metallic_map=metallic_map,
            emission_map=emission_map,
            opacity_map=opacity_map,
            occlusion_map=occlusion_map,
        )

        assert isinstance(result, tuple)
        assert len(result) == 3

        material, preview, properties = result
        assert isinstance(material, dict)
        assert isinstance(preview, torch.Tensor)
        assert isinstance(properties, dict)

    def test_compose_with_all_factors(self, material_composer, sample_albedo):
        """Test material composition with all factor parameters."""
        result = material_composer.compose_material(
            albedo=sample_albedo,
            material_name="factor_test",
            material_type="metallic",
            roughness_factor=0.2,
            metallic_factor=0.8,
            emission_strength=1.5,
            opacity=0.9,
            normal_strength=0.8,
            uv_tiling=2.0,
            double_sided=True,
            ar_optimized=True,
        )

        assert isinstance(result, tuple)
        assert len(result) == 3

        material, preview, properties = result
        assert isinstance(material, dict)
        assert properties["roughness_factor"] == 0.2
        assert properties["metallic_factor"] == 0.8
        assert properties["emission_strength"] == 1.5
        assert properties["opacity"] == 0.9
        assert properties["double_sided"] is True
        assert properties["ar_optimized"] is True

    def test_material_data_structure(self, material_composer, sample_albedo):
        """Test material data structure."""
        result = material_composer.compose_material(albedo=sample_albedo, material_name="structure_test", material_type="standard")

        material, _, _ = result

        # Check required material fields
        assert "name" in material
        assert "type" in material
        assert "albedo" in material
        assert "properties" in material

        # Check data types
        assert isinstance(material["name"], str)
        assert isinstance(material["type"], str)
        assert isinstance(material["properties"], dict)

    def test_properties_data_structure(self, material_composer, sample_albedo):
        """Test material properties data structure."""
        result = material_composer.compose_material(
            albedo=sample_albedo, material_name="props_test", material_type="standard", roughness_factor=0.5, metallic_factor=0.1
        )

        _, _, properties = result

        # Check required property fields
        assert "material_type" in properties
        assert "roughness_factor" in properties
        assert "metallic_factor" in properties
        assert "emission_strength" in properties
        assert "opacity" in properties
        assert "ar_optimized" in properties

        # Check data types
        assert isinstance(properties["material_type"], str)
        assert isinstance(properties["roughness_factor"], (int, float))
        assert isinstance(properties["metallic_factor"], (int, float))
        assert isinstance(properties["emission_strength"], (int, float))
        assert isinstance(properties["opacity"], (int, float))
        assert isinstance(properties["ar_optimized"], bool)

    def test_preview_generation(self, material_composer, sample_albedo):
        """Test material preview generation."""
        result = material_composer.compose_material(albedo=sample_albedo, material_name="preview_test", material_type="standard")

        _, preview, _ = result

        # Check preview tensor properties
        assert isinstance(preview, torch.Tensor)
        assert preview.dim() >= 3  # At least HWC
        assert preview.shape[-1] == 3  # RGB channels

    def test_different_albedo_formats(self, material_composer):
        """Test composition with different albedo formats."""
        # Test different tensor formats
        formats = [
            torch.rand(1, 3, 256, 256),  # BCHW
            torch.rand(3, 256, 256),  # CHW
            torch.rand(256, 256, 3),  # HWC
        ]

        for i, albedo_format in enumerate(formats):
            result = material_composer.compose_material(albedo=albedo_format, material_name=f"format_test_{i}", material_type="standard")

            assert isinstance(result, tuple)
            assert len(result) == 3

    def test_extreme_factor_values(self, material_composer, sample_albedo):
        """Test with extreme factor values."""
        # Test minimum values
        result_min = material_composer.compose_material(
            albedo=sample_albedo,
            material_name="extreme_min",
            material_type="standard",
            roughness_factor=0.0,
            metallic_factor=0.0,
            emission_strength=0.0,
            opacity=0.1,
            normal_strength=0.0,
            uv_tiling=0.1,
        )

        assert isinstance(result_min, tuple)
        assert len(result_min) == 3

        # Test maximum values
        result_max = material_composer.compose_material(
            albedo=sample_albedo,
            material_name="extreme_max",
            material_type="emission",
            roughness_factor=1.0,
            metallic_factor=1.0,
            emission_strength=10.0,
            opacity=1.0,
            normal_strength=2.0,
            uv_tiling=10.0,
        )

        assert isinstance(result_max, tuple)
        assert len(result_max) == 3

    def test_ar_optimization_flag(self, material_composer, sample_albedo):
        """Test AR optimization flag effects."""
        # Test with AR optimization enabled
        result_ar = material_composer.compose_material(
            albedo=sample_albedo, material_name="ar_optimized", material_type="standard", ar_optimized=True
        )

        # Test with AR optimization disabled
        result_no_ar = material_composer.compose_material(
            albedo=sample_albedo, material_name="not_ar_optimized", material_type="standard", ar_optimized=False
        )

        assert isinstance(result_ar, tuple)
        assert isinstance(result_no_ar, tuple)

        _, _, props_ar = result_ar
        _, _, props_no_ar = result_no_ar

        assert props_ar["ar_optimized"] is True
        assert props_no_ar["ar_optimized"] is False

    def test_double_sided_flag(self, material_composer, sample_albedo):
        """Test double-sided material flag."""
        result = material_composer.compose_material(
            albedo=sample_albedo, material_name="double_sided_test", material_type="standard", double_sided=True
        )

        _, _, properties = result
        assert properties["double_sided"] is True

    def test_uv_tiling_values(self, material_composer, sample_albedo):
        """Test different UV tiling values."""
        tiling_values = [0.5, 1.0, 2.0, 4.0, 0.25, 8.0]

        for tiling in tiling_values:
            result = material_composer.compose_material(
                albedo=sample_albedo, material_name=f"tiling_{tiling}", material_type="standard", uv_tiling=tiling
            )

            assert isinstance(result, tuple)
            assert len(result) == 3

            _, _, properties = result
            assert properties["uv_tiling"] == tiling

    def test_invalid_inputs(self, material_composer):
        """Test handling of invalid inputs."""
        # Test with invalid albedo
        with pytest.raises((ValueError, RuntimeError, TypeError, AttributeError)):
            material_composer.compose_material(albedo="not a tensor", material_name="invalid_test", material_type="standard")

        # Test with empty material name
        with pytest.raises((ValueError, AssertionError)):
            material_composer.compose_material(albedo=torch.rand(1, 3, 256, 256), material_name="", material_type="standard")

    def test_glass_material_specific(self, material_composer, sample_albedo):
        """Test glass material specific properties."""
        result = material_composer.compose_material(
            albedo=sample_albedo,
            material_name="glass_test",
            material_type="glass",
            roughness_factor=0.0,  # Smooth glass
            opacity=0.3,  # Transparent
        )

        material, preview, properties = result
        assert properties["material_type"] == "glass"
        assert properties["opacity"] == 0.3
        assert isinstance(material, dict)
        assert isinstance(preview, torch.Tensor)

    def test_emission_material_specific(self, material_composer, sample_albedo):
        """Test emission material specific properties."""
        emission_map = torch.rand(1, 3, 512, 512)

        result = material_composer.compose_material(
            albedo=sample_albedo, material_name="emission_test", material_type="emission", emission_map=emission_map, emission_strength=5.0
        )

        material, preview, properties = result
        assert properties["material_type"] == "emission"
        assert properties["emission_strength"] == 5.0
        assert isinstance(material, dict)
        assert isinstance(preview, torch.Tensor)
