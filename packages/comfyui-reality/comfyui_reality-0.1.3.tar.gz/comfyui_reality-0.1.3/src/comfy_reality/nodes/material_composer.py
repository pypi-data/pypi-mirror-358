"""Material Composer Node for ComfyUI Reality."""

import importlib.util
from typing import Any

import torch

# Check if USD is available
USD_AVAILABLE = importlib.util.find_spec("pxr") is not None


class MaterialComposer:
    """Create PBR materials for AR assets.

    This node composes physically-based rendering materials from input textures
    with support for albedo, normal, roughness, metallic, and emission maps.
    """

    @classmethod
    def INPUT_TYPES(cls) -> dict[str, Any]:
        """Define the input parameters for the node."""
        return {
            "required": {
                "albedo": ("IMAGE",),
                "material_name": (
                    "STRING",
                    {"default": "ar_material", "multiline": False},
                ),
                "material_type": (
                    [
                        "standard",
                        "unlit",
                        "metallic",
                        "emission",
                        "glass",
                        "subsurface",
                    ],
                    {"default": "standard"},
                ),
            },
            "optional": {
                "normal_map": ("IMAGE",),
                "roughness_map": ("IMAGE",),
                "metallic_map": ("IMAGE",),
                "emission_map": ("IMAGE",),
                "opacity_map": ("IMAGE",),
                "occlusion_map": ("IMAGE",),
                "roughness_factor": (
                    "FLOAT",
                    {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01},
                ),
                "metallic_factor": (
                    "FLOAT",
                    {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.01},
                ),
                "emission_strength": (
                    "FLOAT",
                    {"default": 1.0, "min": 0.0, "max": 10.0, "step": 0.1},
                ),
                "opacity": (
                    "FLOAT",
                    {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01},
                ),
                "normal_strength": (
                    "FLOAT",
                    {"default": 1.0, "min": 0.0, "max": 2.0, "step": 0.1},
                ),
                "uv_tiling": (
                    "FLOAT",
                    {"default": 1.0, "min": 0.1, "max": 10.0, "step": 0.1},
                ),
                "double_sided": ("BOOLEAN", {"default": False}),
                "ar_optimized": ("BOOLEAN", {"default": True}),
            },
        }

    RETURN_TYPES = ("MATERIAL", "MATERIAL_PREVIEW", "MATERIAL_PROPERTIES")
    RETURN_NAMES = ("material", "preview_render", "properties")
    FUNCTION = "compose_material"
    CATEGORY = "🎨 ComfyReality/Materials"
    DESCRIPTION = "Create PBR materials for AR assets"

    def compose_material(
        self,
        albedo: torch.Tensor,
        material_name: str,
        material_type: str,
        normal_map=None,
        roughness_map=None,
        metallic_map=None,
        emission_map=None,
        opacity_map=None,
        occlusion_map=None,
        roughness_factor: float = 0.5,
        metallic_factor: float = 0.0,
        emission_strength: float = 1.0,
        opacity: float = 1.0,
        normal_strength: float = 1.0,
        uv_tiling: float = 1.0,
        double_sided: bool = False,
        ar_optimized: bool = True,
    ):
        """Compose PBR material from input textures and parameters."""
        # Input validation
        if not isinstance(albedo, torch.Tensor):
            raise ValueError("Albedo must be a torch.Tensor")

        if not material_name or not isinstance(material_name, str):
            raise ValueError("Material name must be a non-empty string")

        # Create properties dict that matches test expectations
        properties = {
            "material_type": material_type,
            "roughness_factor": roughness_factor,
            "metallic_factor": metallic_factor,
            "emission_strength": emission_strength,
            "opacity": opacity,
            "normal_strength": normal_strength,
            "uv_tiling": uv_tiling,
            "double_sided": double_sided,
            "ar_optimized": ar_optimized,
            "channels": 1,  # Will be updated below
            "memory_usage_mb": 4.0,  # Default value
            "mobile_compatible": True,
            "transparency": opacity < 1.0 or opacity_map is not None,
            "emission": emission_strength > 0.0 or emission_map is not None,
        }

        # Build material definition
        material = {
            "name": material_name,
            "type": material_type,
            "albedo": self._process_texture(albedo, "albedo"),
            "properties": properties,  # Add properties to material dict
        }

        # Process optional texture maps
        if normal_map is not None:
            material["normal_map"] = self._process_texture(normal_map, "normal")
        if roughness_map is not None:
            material["roughness_map"] = self._process_texture(roughness_map, "roughness")
        if metallic_map is not None:
            material["metallic_map"] = self._process_texture(metallic_map, "metallic")
        if emission_map is not None:
            material["emission_map"] = self._process_texture(emission_map, "emission")
        if opacity_map is not None:
            material["opacity_map"] = self._process_texture(opacity_map, "opacity")
        if occlusion_map is not None:
            material["occlusion_map"] = self._process_texture(occlusion_map, "occlusion")

        # Apply AR optimizations
        if ar_optimized:
            material = self._apply_ar_optimizations(material)

        # Update properties with calculated values
        properties["channels"] = self._get_channel_count(material)
        properties["memory_usage_mb"] = self._estimate_memory_usage(material)
        properties["mobile_compatible"] = self._check_mobile_compatibility(material)

        # Add USD shader definition if available
        if USD_AVAILABLE:
            material["usd_definition"] = self._create_usd_material_definition(material, properties)

        # Generate material preview
        preview = self._generate_preview(material)

        return (material, preview, properties)

    def _process_texture(self, texture: torch.Tensor, channel_type: str):
        """Process texture for specific material channel."""
        # Placeholder: process texture based on channel type
        processed = {
            "data": texture,
            "type": channel_type,
            "format": "RGB" if channel_type in ["albedo", "emission"] else "GRAYSCALE",
            "srgb": channel_type in ["albedo", "emission"],
        }
        return processed

    def _apply_ar_optimizations(self, material):
        """Apply AR-specific material optimizations."""
        # Placeholder: optimize material for AR rendering
        material["optimizations"] = {
            "texture_compression": True,
            "mip_mapping": True,
            "shader_complexity": "medium",
        }
        return material

    def _generate_preview(self, material):
        """Generate material preview render."""
        # Get albedo texture data
        albedo_data = material["albedo"]["data"]

        # Ensure preview has the correct shape (HWC with 3 channels for RGB)
        if albedo_data.dim() == 4:  # BCHW
            preview = albedo_data[0].permute(1, 2, 0)  # CHW -> HWC
        elif albedo_data.dim() == 3:  # CHW
            preview = albedo_data.permute(1, 2, 0)  # CHW -> HWC
        else:  # Already HWC
            preview = albedo_data

        # Ensure RGB channels
        if preview.shape[-1] != 3:
            if preview.shape[-1] == 1:
                preview = preview.repeat(1, 1, 3)  # Grayscale to RGB
            else:
                preview = preview[..., :3]  # Take first 3 channels

        return preview

    def _get_channel_count(self, material):
        """Count active material channels."""
        channels = ["albedo"]  # Always has albedo
        optional_channels = [
            "normal_map",
            "roughness_map",
            "metallic_map",
            "emission_map",
            "opacity_map",
            "occlusion_map",
        ]
        for channel in optional_channels:
            if channel in material:
                channels.append(channel)
        return len(channels)

    def _estimate_memory_usage(self, material):
        """Estimate material memory usage in MB."""
        # Placeholder calculation based on texture count and resolution
        base_size = 4.0  # MB for base albedo texture
        return base_size * self._get_channel_count(material)

    def _check_mobile_compatibility(self, material):
        """Check if material is mobile-compatible."""
        # Placeholder: check material complexity
        return self._get_channel_count(material) <= 4  # Limit channels for mobile

    def _create_usd_material_definition(self, material: dict, properties: dict) -> dict:
        """Create USD-specific material definition for professional USDZ export."""
        if not USD_AVAILABLE:
            return {}

        # Create USD material definition
        usd_definition = {
            "shader_type": "UsdPreviewSurface",
            "inputs": {},
            "outputs": {"surface": "token"},
        }

        # Map material properties to USD inputs
        material_type = material.get("type", "standard")

        # Base color from albedo
        usd_definition["inputs"]["diffuseColor"] = {
            "type": "color3f",
            "value": (1.0, 1.0, 1.0),
            "texture": "albedo" if "albedo" in material else None,
        }

        # Roughness
        roughness_value = properties.get("roughness_factor", 0.5)
        usd_definition["inputs"]["roughness"] = {
            "type": "float",
            "value": roughness_value,
            "texture": "roughness_map" if "roughness_map" in material else None,
        }

        # Metallic
        metallic_value = properties.get("metallic_factor", 0.0)
        usd_definition["inputs"]["metallic"] = {
            "type": "float",
            "value": metallic_value,
            "texture": "metallic_map" if "metallic_map" in material else None,
        }

        # Opacity
        opacity_value = properties.get("opacity", 1.0)
        usd_definition["inputs"]["opacity"] = {
            "type": "float",
            "value": opacity_value,
            "texture": "opacity_map" if "opacity_map" in material else None,
        }

        # Normal map
        if "normal_map" in material:
            usd_definition["inputs"]["normal"] = {
                "type": "normal3f",
                "texture": "normal_map",
                "strength": properties.get("normal_strength", 1.0),
            }

        # Emission for emission materials
        if material_type == "emission" or properties.get("emission_strength", 0) > 0:
            emission_strength = properties.get("emission_strength", 1.0)
            usd_definition["inputs"]["emissiveColor"] = {
                "type": "color3f",
                "value": (emission_strength, emission_strength, emission_strength),
                "texture": "emission_map" if "emission_map" in material else None,
            }

        # Occlusion map
        if "occlusion_map" in material:
            usd_definition["inputs"]["occlusion"] = {
                "type": "float",
                "texture": "occlusion_map",
            }

        # Material-specific adjustments
        if material_type == "unlit":
            # Unlit materials use emission instead of diffuse
            usd_definition["inputs"]["emissiveColor"] = usd_definition["inputs"]["diffuseColor"]
            usd_definition["inputs"]["diffuseColor"] = {
                "type": "color3f",
                "value": (0.0, 0.0, 0.0),
            }

        # ARKit-specific properties
        usd_definition["arkit_properties"] = {
            "double_sided": properties.get("double_sided", False),
            "transparency_mode": "blend" if properties.get("transparency", False) else "opaque",
            "mobile_optimized": properties.get("ar_optimized", True),
        }

        return usd_definition
