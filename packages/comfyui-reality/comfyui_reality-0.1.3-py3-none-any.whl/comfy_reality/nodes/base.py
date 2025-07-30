"""Base class for all ComfyReality AR nodes."""

import logging

import numpy as np
import torch

from ..exceptions import ARFormatError, ARValidationError

logger = logging.getLogger(__name__)


class BaseARNode:
    """Base class providing common functionality for all AR nodes."""

    def __init__(self):
        """Initialize base AR node."""
        self.logger = logger.getChild(self.__class__.__name__)

    def validate_image_tensor(
        self,
        tensor: torch.Tensor,
        name: str = "image",
        min_dims: int = 3,
        max_dims: int = 4,
        channels: tuple[int, ...] | None = None,
        dtype: torch.dtype | None = None,
        value_range: tuple[float, float] = (0.0, 1.0),
    ) -> None:
        """Validate image tensor parameters.

        Args:
            tensor: Input tensor to validate
            name: Parameter name for error messages
            min_dims: Minimum number of dimensions
            max_dims: Maximum number of dimensions
            channels: Expected number of channels (if specified)
            dtype: Expected tensor dtype (if specified)
            value_range: Expected value range (min, max)

        Raises:
            ARValidationError: If validation fails
        """
        if not isinstance(tensor, torch.Tensor):
            raise ARValidationError(f"{name} must be a torch.Tensor, got {type(tensor)}", name)

        if tensor.dim() < min_dims or tensor.dim() > max_dims:
            raise ARValidationError(
                f"{name} must have {min_dims}-{max_dims} dimensions, got {tensor.dim()}",
                name,
            )

        if channels is not None:
            # Check channel dimension based on tensor format
            # Support both BCHW and BHWC formats
            if tensor.dim() == 4:
                # Check if it looks like BHWC (ComfyUI standard) or BCHW (PyTorch standard)
                if tensor.shape[3] in channels:  # BHWC format
                    actual_channels = tensor.shape[3]
                elif tensor.shape[1] in channels:  # BCHW format
                    actual_channels = tensor.shape[1]
                else:
                    # Try both to give a better error message
                    actual_channels = tensor.shape[3]  # Default to BHWC for error
            elif tensor.dim() == 3:  # HWC or CHW format
                if tensor.shape[2] in channels:  # HWC format
                    actual_channels = tensor.shape[2]
                elif tensor.shape[0] in channels:  # CHW format
                    actual_channels = tensor.shape[0]
                else:
                    actual_channels = tensor.shape[2]  # Default to HWC for error
            else:
                actual_channels = 1  # Single channel for 2D tensors

            if actual_channels not in channels:
                raise ARValidationError(
                    f"{name} must have {channels} channels, got {actual_channels}",
                    name,
                )

        if dtype is not None and tensor.dtype != dtype:
            raise ARValidationError(f"{name} must be {dtype}, got {tensor.dtype}", name)

        # Check value range
        min_val, max_val = value_range
        tensor_min = tensor.min().item()
        tensor_max = tensor.max().item()

        if tensor_min < min_val or tensor_max > max_val:
            raise ARValidationError(
                f"{name} values must be in range [{min_val}, {max_val}], got range [{tensor_min:.3f}, {tensor_max:.3f}]",
                name,
            )

    def validate_mask_tensor(
        self,
        tensor: torch.Tensor | None,
        name: str = "mask",
        image_shape: tuple[int, ...] | None = None,
    ) -> None:
        """Validate mask tensor parameters.

        Args:
            tensor: Mask tensor to validate (can be None)
            name: Parameter name for error messages
            image_shape: Expected shape to match image (excluding channel dim)

        Raises:
            ARValidationError: If validation fails
        """
        if tensor is None:
            return

        if not isinstance(tensor, torch.Tensor):
            raise ARValidationError(f"{name} must be a torch.Tensor or None, got {type(tensor)}", name)

        # Mask should be 2D or 3D (batch, height, width) or (height, width)
        if tensor.dim() not in [2, 3]:
            raise ARValidationError(f"{name} must have 2-3 dimensions, got {tensor.dim()}", name)

        # Check values are in [0, 1] range for masks
        if tensor.min() < 0.0 or tensor.max() > 1.0:
            raise ARValidationError(
                f"{name} values must be in range [0.0, 1.0], got range [{tensor.min():.3f}, {tensor.max():.3f}]",
                name,
            )

        # Check shape compatibility with image if provided
        if image_shape is not None:
            expected_shape = image_shape[:2]  # height, width
            actual_shape = tensor.shape[-2:]  # last 2 dims
            if actual_shape != expected_shape:
                raise ARValidationError(
                    f"{name} shape {actual_shape} doesn't match image shape {expected_shape}",
                    name,
                )

    def validate_numeric_parameter(
        self,
        value: float | int,
        name: str,
        min_val: float | int | None = None,
        max_val: float | int | None = None,
        valid_values: list[float | int] | None = None,
    ) -> None:
        """Validate numeric parameters.

        Args:
            value: Value to validate
            name: Parameter name for error messages
            min_val: Minimum allowed value
            max_val: Maximum allowed value
            valid_values: List of valid discrete values

        Raises:
            ARValidationError: If validation fails
        """
        if not isinstance(value, int | float):
            raise ARValidationError(f"{name} must be numeric, got {type(value)}", name)

        if min_val is not None and value < min_val:
            raise ARValidationError(f"{name} must be >= {min_val}, got {value}", name)

        if max_val is not None and value > max_val:
            raise ARValidationError(f"{name} must be <= {max_val}, got {value}", name)

        if valid_values is not None and value not in valid_values:
            raise ARValidationError(f"{name} must be one of {valid_values}, got {value}", name)

    def validate_string_parameter(
        self,
        value: str,
        name: str,
        valid_values: list[str] | None = None,
        allow_empty: bool = False,
        max_length: int | None = None,
    ) -> None:
        """Validate string parameters.

        Args:
            value: String value to validate
            name: Parameter name for error messages
            valid_values: List of valid values
            allow_empty: Whether empty strings are allowed
            max_length: Maximum string length

        Raises:
            ARValidationError: If validation fails
        """
        if not isinstance(value, str):
            raise ARValidationError(f"{name} must be a string, got {type(value)}", name)

        if not allow_empty and not value.strip():
            raise ARValidationError(f"{name} cannot be empty", name)

        if max_length is not None and len(value) > max_length:
            raise ARValidationError(f"{name} must be <= {max_length} characters, got {len(value)}", name)

        if valid_values is not None and value not in valid_values:
            raise ARValidationError(f"{name} must be one of {valid_values}, got '{value}'", name)

    def tensor_to_numpy(self, tensor: torch.Tensor | None) -> np.ndarray | None:
        """Convert PyTorch tensor to numpy array with validation.

        Args:
            tensor: Input tensor to convert (expects BCHW or CHW format)

        Returns:
            Numpy array in HWC format or None if input is None

        Raises:
            ARFormatError: If conversion fails
        """
        if tensor is None:
            return None

        try:
            # Remove batch dimension if present (BCHW -> CHW)
            if tensor.dim() == 4 and tensor.shape[0] == 1:
                tensor = tensor.squeeze(0)  # (1, C, H, W) -> (C, H, W)

            # Convert from CHW to HWC format for image processing
            if tensor.dim() == 3:  # CHW format
                tensor = tensor.permute(1, 2, 0)  # (C, H, W) -> (H, W, C)

            # Convert to numpy and ensure C-contiguous
            numpy_array = tensor.detach().cpu().numpy()
            if not numpy_array.flags["C_CONTIGUOUS"]:
                numpy_array = np.ascontiguousarray(numpy_array)

            return numpy_array

        except Exception as e:
            raise ARFormatError(f"Failed to convert tensor to numpy: {e}") from e

    def numpy_to_tensor(self, array: np.ndarray | None, add_batch_dim: bool = True) -> torch.Tensor | None:
        """Convert numpy array to PyTorch tensor.

        Args:
            array: Input numpy array
            add_batch_dim: Whether to add batch dimension for ComfyUI format

        Returns:
            PyTorch tensor or None if input is None

        Raises:
            ARFormatError: If conversion fails
        """
        if array is None:
            return None

        try:
            tensor = torch.from_numpy(array).float()

            # Add batch dimension if requested
            if add_batch_dim and tensor.dim() == 3:
                tensor = tensor.unsqueeze(0)

            return tensor

        except Exception as e:
            raise ARFormatError(f"Failed to convert numpy to tensor: {e}") from e

    def log_processing_info(self, operation: str, **kwargs) -> None:
        """Log processing information with consistent format.

        Args:
            operation: Description of the operation
            **kwargs: Additional key-value pairs to log
        """
        info_parts = [f"🔄 {operation}"]
        for key, value in kwargs.items():
            if isinstance(value, torch.Tensor | np.ndarray):
                info_parts.append(f"{key}={tuple(value.shape)}")
            else:
                info_parts.append(f"{key}={value}")

        self.logger.info(" | ".join(info_parts))

    def log_result_info(self, operation: str, success: bool = True, **kwargs) -> None:
        """Log operation results with consistent format.

        Args:
            operation: Description of the completed operation
            success: Whether operation succeeded
            **kwargs: Additional key-value pairs to log
        """
        icon = "✅" if success else "❌"
        status = "completed" if success else "failed"

        info_parts = [f"{icon} {operation} {status}"]
        for key, value in kwargs.items():
            info_parts.append(f"{key}={value}")

        self.logger.info(" | ".join(info_parts))

    def safe_filename(self, filename: str, max_length: int = 100) -> str:
        """Create a safe filename for file system operations.

        Args:
            filename: Input filename
            max_length: Maximum filename length

        Returns:
            Sanitized filename safe for file systems
        """
        if not filename.strip():
            return "ar_output"

        # Remove invalid characters
        invalid_chars = '<>:"/\\|?*'
        safe_name = filename
        for char in invalid_chars:
            safe_name = safe_name.replace(char, "_")

        # Remove leading/trailing spaces and dots
        safe_name = safe_name.strip(" .")

        # Limit length
        if len(safe_name) > max_length:
            safe_name = safe_name[:max_length]

        # Ensure not empty after sanitization
        if not safe_name:
            safe_name = "ar_output"

        return safe_name

    def validate_return_types(self, result: tuple, expected_types: tuple) -> None:
        """Validate that return values match expected RETURN_TYPES.

        Args:
            result: Tuple of return values
            expected_types: Expected RETURN_TYPES tuple

        Raises:
            ARValidationError: If return types don't match
        """
        if not isinstance(result, tuple):
            raise ARValidationError(f"Return value must be tuple, got {type(result)}", "return_value")

        if len(result) != len(expected_types):
            raise ARValidationError(
                f"Return tuple must have {len(expected_types)} elements, got {len(result)}",
                "return_value",
            )

        # Additional type checking could be added here based on expected_types
        self.logger.debug(f"Validated return types: {[type(r) for r in result]}")
