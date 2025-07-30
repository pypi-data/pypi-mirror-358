"""Flux-based AR content generator node."""

from typing import Any

import numpy as np
import torch
from PIL import Image

from ..exceptions import ARProcessingError
from .base import BaseARNode


class FluxARGenerator(BaseARNode):
    """Generate AR-ready images using Flux models with automatic background removal."""

    @classmethod
    def INPUT_TYPES(cls) -> dict[str, Any]:
        """Define input types for the node."""
        return {
            "required": {
                "model": ("MODEL",),
                "clip": ("CLIP",),
                "vae": ("VAE",),
                "positive": (
                    "STRING",
                    {"multiline": True, "default": "cute cartoon sticker, flat design, vibrant colors, centered, white background"},
                ),
                "negative": ("STRING", {"multiline": True, "default": "realistic, photographic, 3d render, complex, shadows, gradients"}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xFFFFFFFFFFFFFFFF}),
                "steps": (
                    "INT",
                    {
                        "default": 4,  # Flux Schnell optimized for 4 steps
                        "min": 1,
                        "max": 100,
                    },
                ),
                "cfg": (
                    "FLOAT",
                    {
                        "default": 1.0,  # Flux requires CFG 1.0
                        "min": 0.0,
                        "max": 20.0,
                        "step": 0.1,
                    },
                ),
                "width": ("INT", {"default": 1024, "min": 64, "max": 2048, "step": 8}),
                "height": ("INT", {"default": 1024, "min": 64, "max": 2048, "step": 8}),
                "ar_style": (["sticker", "object", "character", "logo", "icon"], {"default": "sticker"}),
                "background_removal": ("BOOLEAN", {"default": True}),
            },
            "optional": {
                "latent": ("LATENT",),
                "background_remover": ("REMBG_MODEL",),  # Support external bg removal models
            },
        }

    RETURN_TYPES = ("IMAGE", "MASK", "AR_METADATA")
    RETURN_NAMES = ("image", "mask", "ar_metadata")
    FUNCTION = "generate_ar_content"
    CATEGORY = "🎨 ComfyReality/Generation"

    def generate_ar_content(
        self,
        model: Any,
        clip: Any,
        vae: Any,
        positive: str,
        negative: str,
        seed: int,
        steps: int,
        cfg: float,
        width: int,
        height: int,
        ar_style: str,
        background_removal: bool,
        latent: Any | None = None,
        background_remover: Any | None = None,
    ) -> tuple[torch.Tensor, torch.Tensor, dict]:
        """Generate AR-ready content using Flux."""

        try:
            # Enhance prompt based on AR style
            enhanced_positive = self._enhance_prompt_for_ar(positive, ar_style)
            enhanced_negative = self._enhance_negative_for_ar(negative, ar_style)

            self.logger.info(f"Generating AR content with Flux: style={ar_style}, size={width}x{height}, steps={steps}")

            # Import ComfyUI modules dynamically
            import comfy.sample as sample

            # Encode prompts
            positive_cond = self._encode_prompt(clip, enhanced_positive)
            negative_cond = self._encode_prompt(clip, enhanced_negative)

            # Create or use provided latent
            if latent is None:
                latent = self._create_empty_latent(width, height)

            # Sample with Flux
            # Note: Flux works best with CFG 1.0
            if cfg != 1.0:
                self.logger.warning(f"Flux models work best with CFG 1.0, but got {cfg}. Consider setting CFG to 1.0 for optimal results.")

            # Generate latent
            latent_image = sample.sample(
                model=model,
                seed=seed,
                steps=steps,
                cfg=cfg,
                sampler_name="euler",  # Flux works well with euler
                scheduler="simple",
                positive=positive_cond,
                negative=negative_cond,
                latent_image=latent["samples"] if isinstance(latent, dict) else latent,
                denoise=1.0,
            )

            # Decode to image
            image = vae.decode(latent_image)

            # Process for AR
            if background_removal:
                image, mask = self._remove_background(image, background_remover)
            else:
                # Create full opacity mask
                mask = torch.ones((image.shape[0], 1, image.shape[2], image.shape[3]), device=image.device)

            # Apply AR-specific optimizations
            image = self._optimize_for_ar(image, ar_style)

            # Create AR metadata
            ar_metadata = {
                "style": ar_style,
                "original_size": [width, height],
                "has_transparency": background_removal,
                "generator": "flux",
                "seed": seed,
                "prompt_style": ar_style,
                "recommended_scale": self._get_recommended_scale(ar_style),
                "recommended_material": self._get_recommended_material(ar_style),
            }

            return (image, mask, ar_metadata)

        except Exception as e:
            raise ARProcessingError(f"Failed to generate AR content: {e!s}") from e

    def _enhance_prompt_for_ar(self, prompt: str, style: str) -> str:
        """Enhance prompt for AR generation."""
        style_enhancements = {
            "sticker": "sticker style, flat design, bold outlines, simple shapes, centered composition, white background",
            "object": "single object, product photography style, clean background, studio lighting, centered",
            "character": "character design, full body, T-pose or A-pose, neutral expression, clean background",
            "logo": "logo design, vector style, minimal, scalable, centered, high contrast",
            "icon": "icon design, flat, minimalist, geometric shapes, centered, solid colors",
        }

        enhancement = style_enhancements.get(style, "")
        return f"{prompt}, {enhancement}" if enhancement else prompt

    def _enhance_negative_for_ar(self, negative: str, style: str) -> str:
        """Enhance negative prompt for AR."""
        ar_negatives = "complex background, multiple objects, busy scene, clutter, text, watermark"
        return f"{negative}, {ar_negatives}"

    def _encode_prompt(self, clip: Any, text: str) -> Any:
        """Encode text prompt using CLIP."""
        # This would use ComfyUI's CLIP encoding
        # Simplified for example
        tokens = clip.tokenize(text)
        return clip.encode_from_tokens(tokens)

    def _create_empty_latent(self, width: int, height: int) -> dict:
        """Create empty latent at specified size."""
        import comfy.utils

        # Calculate latent size (typically 1/8 of image size for SD models)
        latent_width = width // 8
        latent_height = height // 8

        return {"samples": comfy.utils.create_empty_latent(latent_width, latent_height, 1)}

    def _remove_background(self, image: torch.Tensor, remover: Any | None = None) -> tuple[torch.Tensor, torch.Tensor]:
        """Remove background from image."""
        if remover is not None:
            # Use provided background remover model
            return remover.remove_background(image)

        # Simple white background removal as fallback
        # Convert to numpy
        img_np = self.tensor_to_numpy(image)

        # Create mask based on white threshold
        # This is a simple implementation - real implementation would use
        # proper segmentation models
        white_threshold = 240
        mask = np.all(img_np[..., :3] > white_threshold / 255.0, axis=-1)

        # Invert mask (we want to keep non-white pixels)
        mask = ~mask

        # Apply some cleanup
        from scipy import ndimage

        mask = ndimage.binary_erosion(mask, iterations=2)
        mask = ndimage.binary_dilation(mask, iterations=2)

        # Convert mask to tensor
        mask_tensor = torch.from_numpy(mask.astype(np.float32))
        mask_tensor = mask_tensor.unsqueeze(0).unsqueeze(0)

        # Apply mask to image
        image_masked = image.clone()
        mask_expanded = mask_tensor.unsqueeze(-1).expand_as(image)
        image_masked = image_masked * mask_expanded

        return image_masked, mask_tensor

    def _optimize_for_ar(self, image: torch.Tensor, style: str) -> torch.Tensor:
        """Apply AR-specific optimizations to image."""
        # Convert to PIL for processing
        img_np = self.tensor_to_numpy(image)
        pil_image = Image.fromarray((img_np[0] * 255).astype(np.uint8))

        # Apply style-specific optimizations
        if style == "sticker":
            # Increase contrast for stickers
            from PIL import ImageEnhance

            enhancer = ImageEnhance.Contrast(pil_image)
            pil_image = enhancer.enhance(1.2)

            # Increase color saturation
            enhancer = ImageEnhance.Color(pil_image)
            pil_image = enhancer.enhance(1.3)

        elif style in ["logo", "icon"]:
            # Ensure high contrast for logos/icons
            from PIL import ImageOps

            pil_image = ImageOps.autocontrast(pil_image, cutoff=2)

        # Convert back to tensor
        img_array = np.array(pil_image).astype(np.float32) / 255.0
        img_tensor = torch.from_numpy(img_array).unsqueeze(0)

        return img_tensor

    def _get_recommended_scale(self, style: str) -> float:
        """Get recommended AR scale for style."""
        scales = {"sticker": 0.15, "object": 0.3, "character": 0.5, "logo": 0.2, "icon": 0.1}
        return scales.get(style, 0.2)

    def _get_recommended_material(self, style: str) -> str:
        """Get recommended material type for style."""
        materials = {"sticker": "unlit", "object": "standard", "character": "standard", "logo": "unlit", "icon": "unlit"}
        return materials.get(style, "unlit")


# Register the node
NODE_CLASS_MAPPINGS = {"FluxARGenerator": FluxARGenerator}

NODE_DISPLAY_NAME_MAPPINGS = {"FluxARGenerator": "🎨 Flux AR Generator"}
