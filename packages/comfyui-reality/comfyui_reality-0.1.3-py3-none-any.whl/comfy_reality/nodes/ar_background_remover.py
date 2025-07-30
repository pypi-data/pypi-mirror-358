"""Advanced background removal for AR content."""

from typing import Any

import cv2
import numpy as np
import torch

from ..exceptions import ARProcessingError
from .base import BaseARNode


class ARBackgroundRemover(BaseARNode):
    """Remove backgrounds from images for AR sticker creation."""

    @classmethod
    def INPUT_TYPES(cls) -> dict[str, Any]:
        """Define input types for the node."""
        return {
            "required": {
                "image": ("IMAGE",),
                "method": (["threshold", "chroma_key", "grabcut", "edge_detection", "ai_model"], {"default": "threshold"}),
                "threshold_value": ("INT", {"default": 240, "min": 0, "max": 255, "step": 1}),
                "chroma_color": (["white", "green", "blue", "black", "custom"], {"default": "white"}),
                "edge_sensitivity": ("FLOAT", {"default": 0.1, "min": 0.01, "max": 1.0, "step": 0.01}),
                "feather": ("INT", {"default": 2, "min": 0, "max": 20, "step": 1}),
                "cleanup": ("BOOLEAN", {"default": True}),
            },
            "optional": {
                "ai_model": ("REMBG_MODEL",),  # Support external AI models
                "mask_hint": ("MASK",),  # User-provided mask hint
                "custom_color": ("COLOR",),
            },
        }

    RETURN_TYPES = ("IMAGE", "MASK", "IMAGE")
    RETURN_NAMES = ("image", "mask", "preview")
    FUNCTION = "remove_background"
    CATEGORY = "🎨 ComfyReality/Processing"

    def remove_background(
        self,
        image: torch.Tensor,
        method: str,
        threshold_value: int,
        chroma_color: str,
        edge_sensitivity: float,
        feather: int,
        cleanup: bool,
        ai_model: Any | None = None,
        mask_hint: torch.Tensor | None = None,
        custom_color: tuple[int, int, int] | None = None,
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """Remove background from image."""

        try:
            self.logger.info(f"Removing background using method: {method}")

            # Convert to numpy for processing
            img_np = self.tensor_to_numpy(image)

            # Apply selected method
            if method == "ai_model" and ai_model is not None:
                mask = self._use_ai_model(img_np, ai_model)
            elif method == "threshold":
                mask = self._threshold_removal(img_np, threshold_value)
            elif method == "chroma_key":
                mask = self._chroma_key_removal(img_np, chroma_color, custom_color)
            elif method == "grabcut":
                mask = self._grabcut_removal(img_np, mask_hint)
            elif method == "edge_detection":
                mask = self._edge_detection_removal(img_np, edge_sensitivity)
            else:
                # Fallback to threshold
                mask = self._threshold_removal(img_np, threshold_value)

            # Apply cleanup if requested
            if cleanup:
                mask = self._cleanup_mask(mask, feather)

            # Apply feathering
            if feather > 0:
                mask = self._feather_mask(mask, feather)

            # Convert mask to tensor
            mask_tensor = torch.from_numpy(mask).unsqueeze(0).unsqueeze(0)

            # Apply mask to image
            image_masked = self._apply_mask(image, mask_tensor)

            # Create preview with checkerboard background
            preview = self._create_preview(image_masked, mask_tensor)

            return (image_masked, mask_tensor, preview)

        except Exception as e:
            raise ARProcessingError(f"Background removal failed: {e!s}") from e

    def _threshold_removal(self, image: np.ndarray, threshold: int) -> np.ndarray:
        """Remove background based on brightness threshold."""
        # Convert to grayscale
        gray = cv2.cvtColor((image[0] * 255).astype(np.uint8), cv2.COLOR_RGB2GRAY)

        # Create mask based on threshold
        _, mask = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY_INV)

        return mask.astype(np.float32) / 255.0

    def _chroma_key_removal(self, image: np.ndarray, color: str, custom: tuple[int, int, int] | None) -> np.ndarray:
        """Remove background based on color."""
        img = (image[0] * 255).astype(np.uint8)

        # Define color ranges for different chroma keys
        color_ranges = {
            "white": ([200, 200, 200], [255, 255, 255]),
            "green": ([0, 100, 0], [100, 255, 100]),
            "blue": ([0, 0, 100], [100, 100, 255]),
            "black": ([0, 0, 0], [50, 50, 50]),
        }

        if color == "custom" and custom is not None:
            # Use custom color with tolerance
            tolerance = 30
            lower = np.array([max(0, c - tolerance) for c in custom])
            upper = np.array([min(255, c + tolerance) for c in custom])
        else:
            lower, upper = color_ranges.get(color, color_ranges["white"])
            lower = np.array(lower)
            upper = np.array(upper)

        # Create mask
        mask = cv2.inRange(img, lower, upper)
        mask = cv2.bitwise_not(mask)  # Invert to keep non-background

        return mask.astype(np.float32) / 255.0

    def _grabcut_removal(self, image: np.ndarray, mask_hint: torch.Tensor | None) -> np.ndarray:
        """Use GrabCut algorithm for foreground extraction."""
        img = (image[0] * 255).astype(np.uint8)
        height, width = img.shape[:2]

        # Initialize mask
        if mask_hint is not None:
            # Use provided mask as hint
            mask = (mask_hint.squeeze().numpy() * 255).astype(np.uint8)
            mask = cv2.resize(mask, (width, height))
            # Convert to GrabCut format (0=bg, 1=fg, 2=probably bg, 3=probably fg)
            mask_gc = np.where(mask > 128, cv2.GC_PR_FGD, cv2.GC_PR_BGD).astype(np.uint8)
        else:
            # Use rectangle in center as initial guess
            mask_gc = np.zeros((height, width), np.uint8)
            rect = (int(width * 0.1), int(height * 0.1), int(width * 0.8), int(height * 0.8))
            cv2.grabCut(img, mask_gc, rect, None, None, 5, cv2.GC_INIT_WITH_RECT)

        # Apply GrabCut
        bgd_model = np.zeros((1, 65), np.float64)
        fgd_model = np.zeros((1, 65), np.float64)
        cv2.grabCut(img, mask_gc, None, bgd_model, fgd_model, 5, cv2.GC_INIT_WITH_MASK)

        # Extract foreground mask
        mask = np.where((mask_gc == cv2.GC_FGD) | (mask_gc == cv2.GC_PR_FGD), 1, 0)

        return mask.astype(np.float32)

    def _edge_detection_removal(self, image: np.ndarray, sensitivity: float) -> np.ndarray:
        """Remove background using edge detection."""
        img = (image[0] * 255).astype(np.uint8)
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        # Detect edges using Canny
        threshold1 = int(100 * sensitivity)
        threshold2 = int(200 * sensitivity)
        edges = cv2.Canny(blurred, threshold1, threshold2)

        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Create mask from largest contour
        mask = np.zeros_like(gray)
        if contours:
            # Find largest contour (assumed to be main object)
            largest_contour = max(contours, key=cv2.contourArea)
            cv2.drawContours(mask, [largest_contour], -1, 255, -1)

        return mask.astype(np.float32) / 255.0

    def _use_ai_model(self, image: np.ndarray, model: Any) -> np.ndarray:
        """Use external AI model for background removal."""
        # This would integrate with REMBG or similar models
        # For now, return a placeholder
        return model.process(image) if hasattr(model, "process") else np.ones_like(image[0, :, :, 0])

    def _cleanup_mask(self, mask: np.ndarray, iterations: int = 2) -> np.ndarray:
        """Clean up mask using morphological operations."""
        mask_uint8 = (mask * 255).astype(np.uint8)

        # Remove small holes
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        mask_uint8 = cv2.morphologyEx(mask_uint8, cv2.MORPH_CLOSE, kernel, iterations=iterations)

        # Remove small isolated regions
        mask_uint8 = cv2.morphologyEx(mask_uint8, cv2.MORPH_OPEN, kernel, iterations=iterations)

        # Find contours and keep only significant ones
        contours, _ = cv2.findContours(mask_uint8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            # Calculate area threshold (keep regions larger than 1% of image)
            total_area = mask.shape[0] * mask.shape[1]
            area_threshold = total_area * 0.01

            # Filter contours by area
            significant_contours = [c for c in contours if cv2.contourArea(c) > area_threshold]

            # Redraw mask with only significant contours
            mask_uint8 = np.zeros_like(mask_uint8)
            cv2.drawContours(mask_uint8, significant_contours, -1, 255, -1)

        return mask_uint8.astype(np.float32) / 255.0

    def _feather_mask(self, mask: np.ndarray, radius: int) -> np.ndarray:
        """Apply feathering to mask edges."""
        # Apply Gaussian blur for feathering
        mask_blurred = cv2.GaussianBlur(mask, (radius * 2 + 1, radius * 2 + 1), radius)

        # Adjust levels to maintain overall opacity
        mask_blurred = np.clip(mask_blurred * 1.2, 0, 1)

        return mask_blurred

    def _apply_mask(self, image: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
        """Apply mask to image with alpha channel."""
        # Ensure mask is expanded to match image dimensions
        if mask.dim() == 4:  # [B, 1, H, W]
            mask = mask.squeeze(1)  # [B, H, W]

        # Create RGBA image
        b, h, w, c = image.shape
        if c == 3:
            # Add alpha channel
            alpha = mask.unsqueeze(-1)  # [B, H, W, 1]
            image_rgba = torch.cat([image, alpha], dim=-1)
        else:
            # Replace existing alpha
            image_rgba = image.clone()
            image_rgba[..., 3:4] = mask.unsqueeze(-1)

        return image_rgba

    def _create_preview(self, image: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
        """Create preview with checkerboard background."""
        # Create checkerboard pattern
        b, h, w, c = image.shape
        checker_size = 32

        checkerboard = np.zeros((h, w, 3), dtype=np.float32)
        for y in range(0, h, checker_size):
            for x in range(0, w, checker_size):
                if ((x // checker_size) + (y // checker_size)) % 2 == 0:
                    checkerboard[y : y + checker_size, x : x + checker_size] = 0.9
                else:
                    checkerboard[y : y + checker_size, x : x + checker_size] = 0.7

        checkerboard = torch.from_numpy(checkerboard).unsqueeze(0).to(image.device)

        # Composite image over checkerboard
        if c == 4:
            alpha = image[..., 3:4]
            rgb = image[..., :3]
        else:
            alpha = mask.unsqueeze(-1) if mask.dim() == 3 else mask.unsqueeze(-1).unsqueeze(-1)
            rgb = image

        preview = rgb * alpha + checkerboard * (1 - alpha)

        return preview


# Register the node
NODE_CLASS_MAPPINGS = {"ARBackgroundRemover": ARBackgroundRemover}

NODE_DISPLAY_NAME_MAPPINGS = {"ARBackgroundRemover": "🎭 AR Background Remover"}
