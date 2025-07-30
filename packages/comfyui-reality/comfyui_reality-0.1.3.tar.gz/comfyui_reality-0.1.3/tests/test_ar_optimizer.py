"""Tests for AROptimizer node."""

import pytest
import torch

from comfy_reality.exceptions import AROptimizationError
from comfy_reality.nodes.ar_optimizer import AROptimizer


class TestAROptimizer:
    """Test suite for AROptimizer."""

    @pytest.fixture
    def optimizer(self):
        """Create optimizer instance."""
        return AROptimizer()

    @pytest.fixture
    def sample_image(self):
        """Create a sample image tensor."""
        return torch.rand(1, 3, 512, 512)

    def test_input_types(self, optimizer):
        """Test INPUT_TYPES class method."""
        input_types = optimizer.INPUT_TYPES()

        assert isinstance(input_types, dict)
        assert "required" in input_types
        assert "optional" in input_types

        # Check required inputs
        required = input_types["required"]
        assert "image" in required
        assert "target_platform" in required
        assert "optimization_level" in required
        assert "max_texture_size" in required
        assert "compression_format" in required

        # Check optional inputs
        optional = input_types["optional"]
        assert "geometry" in optional
        assert "target_fps" in optional
        assert "memory_budget_mb" in optional
        assert "lod_levels" in optional

    def test_class_attributes(self, optimizer):
        """Test class attributes."""
        assert optimizer.RETURN_TYPES == ("IMAGE", "GEOMETRY", "OPTIMIZATION_REPORT")
        assert optimizer.RETURN_NAMES == ("optimized_texture", "optimized_geometry", "performance_report")
        assert optimizer.FUNCTION == "optimize_for_ar"
        assert optimizer.CATEGORY == "🔧 ComfyReality/Optimization"
        assert isinstance(optimizer.DESCRIPTION, str)

    def test_optimize_for_ar_basic(self, optimizer, sample_image):
        """Test basic AR optimization."""
        result = optimizer.optimize_for_ar(
            sample_image, target_platform="universal", optimization_level="balanced", max_texture_size=1024, compression_format="auto"
        )

        assert isinstance(result, tuple)
        assert len(result) == 3

        optimized_image, optimized_geometry, report = result
        assert isinstance(optimized_image, torch.Tensor)
        assert optimized_geometry is None  # No geometry input
        assert isinstance(report, dict)

    @pytest.mark.parametrize("platform", ["ios", "android", "universal"])
    def test_all_platforms(self, optimizer, sample_image, platform):
        """Test all target platforms."""
        result = optimizer.optimize_for_ar(
            sample_image, target_platform=platform, optimization_level="balanced", max_texture_size=1024, compression_format="auto"
        )

        assert isinstance(result, tuple)
        assert len(result) == 3

        optimized_image, _, report = result
        assert isinstance(optimized_image, torch.Tensor)
        assert report["platform"] == platform

    @pytest.mark.parametrize("level", ["aggressive", "balanced", "conservative"])
    def test_all_optimization_levels(self, optimizer, sample_image, level):
        """Test all optimization levels."""
        result = optimizer.optimize_for_ar(
            sample_image, target_platform="universal", optimization_level=level, max_texture_size=1024, compression_format="auto"
        )

        assert isinstance(result, tuple)
        assert len(result) == 3

        optimized_image, _, report = result
        assert isinstance(optimized_image, torch.Tensor)
        assert report["optimization_level"] == level

    @pytest.mark.parametrize("size", [256, 512, 1024, 2048])
    def test_all_texture_sizes(self, optimizer, sample_image, size):
        """Test all texture sizes."""
        result = optimizer.optimize_for_ar(
            sample_image, target_platform="universal", optimization_level="balanced", max_texture_size=size, compression_format="auto"
        )

        assert isinstance(result, tuple)
        assert len(result) == 3

        optimized_image, _, report = result
        assert isinstance(optimized_image, torch.Tensor)
        assert isinstance(report, dict)

    @pytest.mark.parametrize("format_type", ["auto", "astc", "etc2", "pvrtc", "dxt"])
    def test_all_compression_formats(self, optimizer, sample_image, format_type):
        """Test all compression formats."""
        result = optimizer.optimize_for_ar(
            sample_image, target_platform="universal", optimization_level="balanced", max_texture_size=1024, compression_format=format_type
        )

        assert isinstance(result, tuple)
        assert len(result) == 3

        optimized_image, _, report = result
        assert isinstance(optimized_image, torch.Tensor)
        assert isinstance(report, dict)

    def test_optimize_with_all_optional_params(self, optimizer, sample_image):
        """Test optimization with all optional parameters."""
        result = optimizer.optimize_for_ar(
            sample_image,
            target_platform="universal",
            optimization_level="balanced",
            max_texture_size=1024,
            compression_format="auto",
            geometry=None,
            target_fps=60,
            memory_budget_mb=100,
            lod_levels=3,
            quality_threshold=0.8,
        )

        assert isinstance(result, tuple)
        assert len(result) == 3

        optimized_image, optimized_geometry, report = result
        assert isinstance(optimized_image, torch.Tensor)
        assert optimized_geometry is None
        assert isinstance(report, dict)
        assert "estimated_fps" in report
        assert "estimated_memory_mb" in report

    def test_different_image_formats(self, optimizer):
        """Test optimization with different image formats."""
        # Test different tensor formats
        formats = [
            torch.rand(1, 3, 256, 256),  # BCHW
            torch.rand(3, 256, 256),  # CHW
        ]

        for i, image_format in enumerate(formats):
            result = optimizer.optimize_for_ar(
                image_format, target_platform="universal", optimization_level="balanced", max_texture_size=512, compression_format="auto"
            )

            assert isinstance(result, tuple)
            assert len(result) == 3

    def test_extreme_parameters(self, optimizer, sample_image):
        """Test with extreme parameter values."""
        # Test minimum texture size with aggressive optimization
        result = optimizer.optimize_for_ar(
            sample_image,
            target_platform="universal",
            optimization_level="aggressive",
            max_texture_size=256,
            compression_format="auto",
            target_fps=30,
            memory_budget_mb=10,
            lod_levels=1,
            quality_threshold=0.1,
        )

        assert isinstance(result, tuple)
        assert len(result) == 3

        # Test maximum texture size with conservative optimization
        result = optimizer.optimize_for_ar(
            sample_image,
            target_platform="universal",
            optimization_level="conservative",
            max_texture_size=2048,
            compression_format="auto",
            target_fps=120,
            memory_budget_mb=500,
            lod_levels=5,
            quality_threshold=0.95,
        )

        assert isinstance(result, tuple)
        assert len(result) == 3

    def test_report_structure(self, optimizer, sample_image):
        """Test optimization report structure."""
        result = optimizer.optimize_for_ar(
            sample_image, target_platform="ios", optimization_level="balanced", max_texture_size=1024, compression_format="astc"
        )

        _, _, report = result

        # Check required report fields
        assert "platform" in report
        assert "optimization_level" in report
        assert "texture_compression_ratio" in report
        assert "geometry_reduction" in report
        assert "estimated_memory_mb" in report
        assert "estimated_fps" in report

        # Check data types
        assert isinstance(report["platform"], str)
        assert isinstance(report["optimization_level"], str)
        assert isinstance(report["texture_compression_ratio"], (int, float))
        assert isinstance(report["geometry_reduction"], (int, float))
        assert isinstance(report["estimated_memory_mb"], (int, float))
        assert isinstance(report["estimated_fps"], (int, float))

    def test_invalid_inputs(self, optimizer):
        """Test handling of invalid inputs."""
        # Test with invalid image
        with pytest.raises(AROptimizationError):
            optimizer.optimize_for_ar(
                "not an image", target_platform="universal", optimization_level="balanced", max_texture_size=1024, compression_format="auto"
            )

        # Test with invalid platform (should handle gracefully or raise error)
        with pytest.raises(AROptimizationError):
            optimizer.optimize_for_ar(
                torch.rand(1, 3, 256, 256),
                target_platform="invalid_platform",
                optimization_level="balanced",
                max_texture_size=1024,
                compression_format="auto",
            )
