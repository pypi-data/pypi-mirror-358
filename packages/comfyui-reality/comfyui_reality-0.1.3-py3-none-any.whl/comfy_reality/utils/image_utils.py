"""Image processing utilities for ComfyReality."""

import numpy as np
import torch
from PIL import Image


def preprocess_image(image: torch.Tensor | np.ndarray | Image.Image) -> torch.Tensor:
    """Preprocess image for model input.

    Args:
        image: Input image in various formats

    Returns:
        Preprocessed image tensor
    """
    if isinstance(image, Image.Image):
        image = np.array(image)

    if isinstance(image, np.ndarray):
        image = torch.from_numpy(image).float()

    # Normalize to [0, 1] if needed
    if image.max() > 1.0:
        image = image / 255.0

    # Ensure correct dimensions
    if image.dim() == 3 and image.shape[2] == 3:
        image = image.permute(2, 0, 1)  # HWC to CHW

    if image.dim() == 3:
        image = image.unsqueeze(0)  # Add batch dimension

    return image


def postprocess_image(image: torch.Tensor) -> np.ndarray:
    """Postprocess image tensor to numpy array.

    Args:
        image: Image tensor

    Returns:
        Image as numpy array (HWC format, uint8)
    """
    if image.dim() == 4:
        image = image.squeeze(0)  # Remove batch dimension

    if image.dim() == 3 and image.shape[0] == 3:
        image = image.permute(1, 2, 0)  # CHW to HWC

    # Convert to numpy and scale to [0, 255]
    image_np = image.cpu().numpy()
    image_np = np.clip(image_np * 255, 0, 255).astype(np.uint8)

    return image_np


def resize_image(image: torch.Tensor, target_size: tuple[int, int]) -> torch.Tensor:
    """Resize image tensor.

    Args:
        image: Input image tensor
        target_size: (height, width) target size

    Returns:
        Resized image tensor
    """
    import torch.nn.functional as F

    if image.dim() == 3:
        image = image.unsqueeze(0)

    resized = F.interpolate(image, size=target_size, mode="bilinear", align_corners=False)

    result: torch.Tensor = resized.squeeze(0) if resized.shape[0] == 1 else resized
    return result


def create_alpha_channel(mask: torch.Tensor) -> torch.Tensor:
    """Create alpha channel from mask.

    Args:
        mask: Binary mask tensor

    Returns:
        Alpha channel tensor
    """
    if mask.dim() == 3:
        mask = mask.squeeze(-1)  # Remove channel dimension if present

    return mask.float()


def apply_mask(image: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
    """Apply mask to image.

    Args:
        image: Input image tensor
        mask: Mask tensor

    Returns:
        Masked image with alpha channel
    """
    if image.dim() == 4:
        image = image.squeeze(0)

    if mask.dim() == 4:
        mask = mask.squeeze(0)

    # Ensure mask is single channel
    if mask.dim() == 3:
        mask = mask.mean(dim=0, keepdim=True)
    elif mask.dim() == 2:
        mask = mask.unsqueeze(0)

    # Add alpha channel
    if image.shape[0] == 3:  # RGB
        alpha = mask
        rgba_image = torch.cat([image, alpha], dim=0)
    else:  # Already has alpha
        rgba_image = image.clone()
        rgba_image[3:4] = mask

    return rgba_image
