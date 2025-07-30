"""Integration tests for ComfyReality AR workflows."""

import pytest
import torch

from comfy_reality.exceptions import AROptimizationError
from comfy_reality.nodes.ar_optimizer import AROptimizer
from comfy_reality.nodes.material_composer import MaterialComposer
from comfy_reality.nodes.spatial_positioner import SpatialPositioner
from comfy_reality.nodes.usdz_exporter import USDZExporter
from comfy_reality.utils.image_utils import postprocess_image
from comfy_reality.utils.validation import validate_ar_requirements, validate_workflow


class TestARWorkflow:
    """Test complete AR content creation workflow."""

    @pytest.fixture
    def sample_image(self):
        """Create sample image tensor."""
        return torch.rand(1, 3, 512, 512)

    @pytest.fixture
    def sample_mask(self):
        """Create sample mask tensor."""
        return torch.rand(1, 512, 512)

    @pytest.fixture
    def optimizer(self):
        """Create AR optimizer."""
        return AROptimizer()

    @pytest.fixture
    def positioner(self):
        """Create spatial positioner."""
        return SpatialPositioner()

    @pytest.fixture
    def material_composer(self):
        """Create material composer."""
        return MaterialComposer()

    @pytest.fixture
    def exporter(self):
        """Create USDZ exporter."""
        return USDZExporter()

    def test_optimize_and_export_workflow(self, sample_image, optimizer, exporter):
        """Test AR optimization + export workflow."""
        # Step 1: Optimize for AR
        optimized_result = optimizer.optimize_for_ar(
            sample_image, target_platform="universal", optimization_level="balanced", max_texture_size=1024, compression_format="auto"
        )

        assert isinstance(optimized_result, tuple)
        optimized_image = optimized_result[0]
        assert isinstance(optimized_image, torch.Tensor)

        # Step 2: Export to USDZ
        export_result = exporter.export_usdz(optimized_image, "optimized_test", optimization_level="mobile")

        assert isinstance(export_result, tuple)
        usdz_path = export_result[0]
        assert isinstance(usdz_path, str)
        assert usdz_path.endswith(".usdz")

    def test_positioning_and_export_workflow(self, sample_image, positioner, exporter):
        """Test spatial positioning + export workflow."""
        # Step 1: Position in 3D space
        position_result = positioner.create_spatial_transform(
            position_x=0.0, position_y=0.0, position_z=0.0, scale=1.0, rotation_x=0.0, rotation_y=0.0, rotation_z=0.0, anchor_point="center"
        )

        assert isinstance(position_result, tuple)
        # positioned_data = position_result[0]  # Not used in export

        # Step 2: Export with positioning data
        export_result = exporter.export_usdz(sample_image, "positioned_test", scale=1.5, physics_enabled=True)

        assert isinstance(export_result, tuple)
        usdz_path = export_result[0]
        assert isinstance(usdz_path, str)
        assert usdz_path.endswith(".usdz")

    def test_material_and_export_workflow(self, sample_image, material_composer, exporter):
        """Test material composition + export workflow."""
        # Step 1: Compose material
        material_result = material_composer.compose_material(
            albedo=sample_image,
            material_name="test_material",
            material_type="standard",
            metallic_factor=0.2,
            roughness_factor=0.8,
            emission_strength=0.0,
            opacity=1.0,
            normal_strength=1.0,
        )

        assert isinstance(material_result, tuple)
        # material_data = material_result[0]  # Not used in export

        # Step 2: Export with material
        export_result = exporter.export_usdz(sample_image, "material_test", material_type="standard")

        assert isinstance(export_result, tuple)
        usdz_path = export_result[0]
        assert isinstance(usdz_path, str)
        assert usdz_path.endswith(".usdz")

    def test_complete_ar_pipeline(self, sample_image, sample_mask, optimizer, positioner, material_composer, exporter):
        """Test complete AR content creation pipeline."""
        # Step 1: Optimize for AR
        optimized_result = optimizer.optimize_for_ar(
            sample_image, target_platform="universal", optimization_level="balanced", max_texture_size=1024, compression_format="auto"
        )
        optimized_image = optimized_result[0]

        # Step 2: Position in space
        position_result = positioner.create_spatial_transform(position_x=0.0, position_y=0.5, position_z=0.0, scale=1.2)
        # positioned_data = position_result[0]  # Not used in export

        # Step 3: Compose material
        material_result = material_composer.compose_material(
            albedo=optimized_image, material_name="metallic_material", material_type="metallic", metallic_factor=0.8, roughness_factor=0.2
        )
        # material_data = material_result[0]  # Not used in export

        # Step 4: Export to USDZ
        export_result = exporter.export_usdz(
            optimized_image,
            "complete_pipeline_test",
            mask=sample_mask,
            scale=1.2,
            material_type="metallic",
            optimization_level="balanced",
            physics_enabled=True,
        )

        assert isinstance(export_result, tuple)
        usdz_path = export_result[0]
        assert isinstance(usdz_path, str)
        assert usdz_path.endswith(".usdz")

    @pytest.mark.slow
    def test_high_quality_ar_workflow(self, sample_image, optimizer, exporter):
        """Test high-quality AR workflow (marked as slow)."""
        # Create high-resolution image
        hq_image = torch.rand(1, 3, 2048, 2048)

        # Optimize for quality
        optimized_result = optimizer.optimize_for_ar(
            hq_image, target_platform="universal", optimization_level="conservative", max_texture_size=2048, compression_format="auto"
        )
        optimized_image = optimized_result[0]

        # Export with quality settings
        export_result = exporter.export_usdz(
            optimized_image, "hq_ar_test", optimization_level="quality", material_type="standard", physics_enabled=True
        )

        assert isinstance(export_result, tuple)
        usdz_path = export_result[0]
        assert isinstance(usdz_path, str)
        assert usdz_path.endswith(".usdz")

    def test_different_platforms_workflow(self, sample_image, optimizer, exporter):
        """Test workflow with different target platforms."""
        platforms = ["ios", "android", "universal"]

        for platform in platforms:
            # Optimize for platform
            optimized_result = optimizer.optimize_for_ar(
                sample_image, target_platform=platform, optimization_level="balanced", max_texture_size=1024, compression_format="auto"
            )
            optimized_image = optimized_result[0]

            # Export with platform-specific settings
            export_result = exporter.export_usdz(optimized_image, f"platform_{platform}_test", optimization_level="mobile")

            assert isinstance(export_result, tuple)
            usdz_path = export_result[0]
            assert isinstance(usdz_path, str)
            assert usdz_path.endswith(".usdz")


class TestWorkflowValidation:
    """Test workflow validation for AR content creation."""

    @pytest.fixture
    def optimizer(self):
        """Create AR optimizer."""
        return AROptimizer()

    def test_validate_ar_workflow(self):
        """Test validation of AR workflow definition."""
        workflow = {
            "nodes": [
                {"id": "optimizer", "type": "AROptimizer", "params": {"target_platform": "universal", "optimization_level": "balanced"}},
                {"id": "positioner", "type": "SpatialPositioner", "params": {"scale": 1.0}},
                {"id": "exporter", "type": "USDZExporter", "params": {"filename": "ar_content", "material_type": "standard"}},
            ],
            "connections": [
                {"from_node": "optimizer", "to_node": "positioner", "from_output": "optimized_image", "to_input": "image"},
                {"from_node": "positioner", "to_node": "exporter", "from_output": "positioned_data", "to_input": "image"},
            ],
        }

        is_valid, errors = validate_workflow(workflow)
        assert is_valid is True
        assert len(errors) == 0

    def test_validate_ar_requirements(self, optimizer):
        """Test AR requirements validation throughout workflow."""
        # Generate test image
        test_image = torch.rand(1, 3, 1024, 1024)

        # Optimize for AR
        optimized_result = optimizer.optimize_for_ar(
            test_image, target_platform="universal", optimization_level="balanced", max_texture_size=1024, compression_format="auto"
        )
        optimized_image = optimized_result[0]

        # Convert to numpy for validation
        image_np = postprocess_image(optimized_image)

        # Validate AR requirements
        meets_req, recommendations = validate_ar_requirements(image_np)

        # Should meet requirements after optimization
        assert isinstance(meets_req, bool)
        assert isinstance(recommendations, list)


class TestDataFlow:
    """Test data flow between AR nodes."""

    @pytest.fixture
    def sample_image(self):
        """Create sample image tensor."""
        return torch.rand(1, 3, 512, 512)

    @pytest.fixture
    def optimizer(self):
        """Create AR optimizer."""
        return AROptimizer()

    @pytest.fixture
    def exporter(self):
        """Create USDZ exporter."""
        return USDZExporter()

    def test_tensor_format_consistency(self, sample_image, optimizer, exporter):
        """Test that tensor formats are consistent between nodes."""
        # Optimize image
        optimized_result = optimizer.optimize_for_ar(
            sample_image, target_platform="universal", optimization_level="balanced", max_texture_size=1024, compression_format="auto"
        )
        optimized_image = optimized_result[0]

        # Verify optimizer output format
        assert isinstance(optimized_image, torch.Tensor)
        assert optimized_image.dim() == 4  # BCHW
        assert optimized_image.shape[0] == 1  # Batch size
        assert optimized_image.shape[1] == 3  # RGB channels

        # Export to USDZ
        export_result = exporter.export_usdz(optimized_image, "format_test")

        # Should succeed without format errors
        assert isinstance(export_result, tuple)
        assert len(export_result) == 1

    def test_different_input_formats(self, optimizer, exporter):
        """Test nodes handle different input formats correctly."""
        # Test different image formats
        formats = [
            torch.rand(1, 3, 256, 256),  # BCHW
            torch.rand(3, 256, 256),  # CHW
        ]

        for i, image_format in enumerate(formats):
            # Optimization should handle different formats
            optimized_result = optimizer.optimize_for_ar(
                image_format, target_platform="universal", optimization_level="balanced", max_texture_size=1024, compression_format="auto"
            )
            optimized_image = optimized_result[0]

            # Export should handle optimizer output
            export_result = exporter.export_usdz(optimized_image, f"format_test_{i}")

            assert isinstance(export_result, tuple)


class TestErrorHandling:
    """Test error handling in AR workflows."""

    @pytest.fixture
    def optimizer(self):
        """Create AR optimizer."""
        return AROptimizer()

    @pytest.fixture
    def exporter(self):
        """Create USDZ exporter."""
        return USDZExporter()

    def test_invalid_input_handling(self, optimizer, exporter):
        """Test handling of invalid inputs."""
        # Test optimizer with invalid image
        with pytest.raises(AROptimizationError):
            optimizer.optimize_for_ar(
                "not an image", target_platform="universal", optimization_level="balanced", max_texture_size=1024, compression_format="auto"
            )

        # Test exporter with invalid image
        result = exporter.export_usdz("not an image", "test")
        assert isinstance(result, tuple)
        assert "failed" in result[0].lower()

    def test_extreme_parameters(self, optimizer):
        """Test handling of extreme parameter values."""
        test_image = torch.rand(1, 3, 256, 256)

        # Test with extreme optimization settings
        result = optimizer.optimize_for_ar(
            test_image,
            target_platform="universal",
            optimization_level="aggressive",
            max_texture_size=256,  # Very small
            compression_format="auto",
        )

        assert isinstance(result, tuple)
        assert len(result) == 3
