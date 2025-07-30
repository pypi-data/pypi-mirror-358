"""Test BaseARNode functionality."""

import numpy as np
import pytest
import torch

from comfy_reality.exceptions import ARValidationError
from comfy_reality.nodes.base import BaseARNode


class TestNode(BaseARNode):
    """Test node for BaseARNode functionality."""

    RETURN_TYPES = ("IMAGE", "STRING")

    def test_method(self, image: torch.Tensor, text: str) -> tuple:
        """Test method for validation."""
        self.validate_image_tensor(image)
        self.validate_string_parameter(text, "text", max_length=100)
        return (image, text)


class TestBaseARNode:
    """Test suite for BaseARNode."""

    def test_image_tensor_validation_valid(self):
        """Test valid image tensor validation."""
        node = TestNode()
        # Valid 3D tensor (H, W, C)
        tensor = torch.rand(512, 512, 3)
        node.validate_image_tensor(tensor)  # Should not raise

    def test_image_tensor_validation_invalid_dimensions(self):
        """Test image tensor validation with invalid dimensions."""
        node = TestNode()
        # Invalid 2D tensor
        tensor = torch.rand(512, 512)
        with pytest.raises(ARValidationError, match="must have 3-4 dimensions"):
            node.validate_image_tensor(tensor)

    def test_image_tensor_validation_invalid_channels(self):
        """Test image tensor validation with invalid channels."""
        node = TestNode()
        # Invalid channel count
        tensor = torch.rand(512, 512, 2)  # 2 channels
        with pytest.raises(ARValidationError, match="must have"):
            node.validate_image_tensor(tensor, channels=(3, 4))

    def test_image_tensor_validation_invalid_range(self):
        """Test image tensor validation with invalid value range."""
        node = TestNode()
        # Values outside [0, 1] range
        tensor = torch.rand(512, 512, 3) * 2.0  # [0, 2]
        with pytest.raises(ARValidationError, match="values must be in range"):
            node.validate_image_tensor(tensor, value_range=(0.0, 1.0))

    def test_mask_tensor_validation_valid(self):
        """Test valid mask tensor validation."""
        node = TestNode()
        # Valid mask
        mask = torch.rand(512, 512)
        node.validate_mask_tensor(mask)  # Should not raise

    def test_mask_tensor_validation_none(self):
        """Test mask tensor validation with None."""
        node = TestNode()
        node.validate_mask_tensor(None)  # Should not raise

    def test_mask_tensor_validation_invalid_range(self):
        """Test mask tensor validation with invalid range."""
        node = TestNode()
        # Mask with values outside [0, 1]
        mask = torch.rand(512, 512) + 1.0  # [1, 2]
        with pytest.raises(ARValidationError, match="values must be in range"):
            node.validate_mask_tensor(mask)

    def test_numeric_parameter_validation_valid(self):
        """Test valid numeric parameter validation."""
        node = TestNode()
        node.validate_numeric_parameter(5.0, "scale", min_val=1.0, max_val=10.0)

    def test_numeric_parameter_validation_invalid_type(self):
        """Test numeric parameter validation with invalid type."""
        node = TestNode()
        with pytest.raises(ARValidationError, match="must be numeric"):
            node.validate_numeric_parameter("5.0", "scale")

    def test_numeric_parameter_validation_out_of_range(self):
        """Test numeric parameter validation out of range."""
        node = TestNode()
        with pytest.raises(ARValidationError, match="must be <="):
            node.validate_numeric_parameter(15.0, "scale", max_val=10.0)

    def test_string_parameter_validation_valid(self):
        """Test valid string parameter validation."""
        node = TestNode()
        node.validate_string_parameter("mobile", "level", valid_values=["mobile", "desktop"])

    def test_string_parameter_validation_invalid_value(self):
        """Test string parameter validation with invalid value."""
        node = TestNode()
        with pytest.raises(ARValidationError, match="must be one of"):
            node.validate_string_parameter("tablet", "level", valid_values=["mobile", "desktop"])

    def test_string_parameter_validation_empty(self):
        """Test string parameter validation with empty string."""
        node = TestNode()
        with pytest.raises(ARValidationError, match="cannot be empty"):
            node.validate_string_parameter("", "filename", allow_empty=False)

    def test_tensor_to_numpy_conversion(self):
        """Test tensor to numpy conversion."""
        node = TestNode()
        # 4D tensor (batch, channels, height, width) - BCHW format
        tensor = torch.rand(1, 3, 512, 512)
        numpy_array = node.tensor_to_numpy(tensor)

        assert isinstance(numpy_array, np.ndarray)
        assert numpy_array.shape == (512, 512, 3)  # Batch dim removed, converted to HWC
        assert numpy_array.flags["C_CONTIGUOUS"]

    def test_tensor_to_numpy_none(self):
        """Test tensor to numpy conversion with None."""
        node = TestNode()
        result = node.tensor_to_numpy(None)
        assert result is None

    def test_numpy_to_tensor_conversion(self):
        """Test numpy to tensor conversion."""
        node = TestNode()
        numpy_array = np.random.rand(512, 512, 3).astype(np.float32)
        tensor = node.numpy_to_tensor(numpy_array, add_batch_dim=True)

        assert isinstance(tensor, torch.Tensor)
        assert tensor.shape == (1, 512, 512, 3)  # Batch dim added (HWC format maintained)
        assert tensor.dtype == torch.float32

    def test_safe_filename(self):
        """Test safe filename generation."""
        node = TestNode()

        # Test with invalid characters
        unsafe_name = "my<file>name|with?invalid*chars"
        safe_name = node.safe_filename(unsafe_name)
        assert "<" not in safe_name
        assert ">" not in safe_name
        assert "|" not in safe_name
        assert safe_name == "my_file_name_with_invalid_chars"

    def test_safe_filename_empty(self):
        """Test safe filename with empty input."""
        node = TestNode()
        safe_name = node.safe_filename("")
        assert safe_name == "ar_output"

    def test_safe_filename_too_long(self):
        """Test safe filename with long input."""
        node = TestNode()
        long_name = "a" * 150
        safe_name = node.safe_filename(long_name, max_length=100)
        assert len(safe_name) <= 100

    def test_return_types_validation_valid(self):
        """Test valid return types validation."""
        node = TestNode()
        result = (torch.rand(512, 512, 3), "test")
        node.validate_return_types(result, ("IMAGE", "STRING"))  # Should not raise

    def test_return_types_validation_invalid_length(self):
        """Test return types validation with wrong length."""
        node = TestNode()
        result = (torch.rand(512, 512, 3),)  # Missing second element
        with pytest.raises(ARValidationError, match="must have 2 elements"):
            node.validate_return_types(result, ("IMAGE", "STRING"))

    def test_logging_methods(self):
        """Test logging methods don't crash."""
        node = TestNode()
        # These should not raise exceptions
        node.log_processing_info("Test operation", param1="value1", param2=42)
        node.log_result_info("Test operation", success=True, result="output")
        node.log_result_info("Test operation", success=False, error="test error")
