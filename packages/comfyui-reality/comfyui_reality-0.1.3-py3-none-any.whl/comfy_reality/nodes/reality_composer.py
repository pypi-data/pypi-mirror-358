"""Reality Composer Node for ComfyUI Reality."""

from typing import Any

import numpy as np


class RealityComposer:
    """Compose multi-object AR scenes with lighting and environment.

    This node combines multiple 3D objects, materials, and spatial transforms
    into cohesive AR scenes with proper lighting, shadows, and environmental setup.
    """

    @classmethod
    def INPUT_TYPES(cls) -> dict[str, Any]:
        """Define the input parameters for the node."""
        return {
            "required": {
                "scene_name": (
                    "STRING",
                    {"default": "ar_scene", "multiline": False},
                ),
                "environment_type": (
                    ["indoor", "outdoor", "studio", "custom"],
                    {"default": "indoor"},
                ),
                "lighting_setup": (
                    ["auto", "three_point", "ambient", "directional", "custom"],
                    {"default": "auto"},
                ),
            },
            "optional": {
                "object_1": ("GEOMETRY",),
                "material_1": ("MATERIAL",),
                "transform_1": ("SPATIAL_TRANSFORM",),
                "object_2": ("GEOMETRY",),
                "material_2": ("MATERIAL",),
                "transform_2": ("SPATIAL_TRANSFORM",),
                "object_3": ("GEOMETRY",),
                "material_3": ("MATERIAL",),
                "transform_3": ("SPATIAL_TRANSFORM",),
                "environment_map": ("IMAGE",),
                "ground_plane": ("BOOLEAN", {"default": True}),
                "shadows_enabled": ("BOOLEAN", {"default": True}),
                "ambient_intensity": (
                    "FLOAT",
                    {"default": 0.3, "min": 0.0, "max": 2.0, "step": 0.1},
                ),
                "directional_intensity": (
                    "FLOAT",
                    {"default": 1.0, "min": 0.0, "max": 5.0, "step": 0.1},
                ),
                "shadow_softness": (
                    "FLOAT",
                    {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.1},
                ),
                "ar_anchor_type": (
                    ["plane", "image", "face", "world"],
                    {"default": "plane"},
                ),
                "interaction_enabled": ("BOOLEAN", {"default": True}),
                "physics_simulation": ("BOOLEAN", {"default": False}),
            },
        }

    RETURN_TYPES = ("AR_SCENE", "SCENE_GRAPH", "LIGHTING_SETUP", "SCENE_BOUNDS")
    RETURN_NAMES = ("scene", "scene_graph", "lighting", "bounds")
    FUNCTION = "compose_scene"
    CATEGORY = "🏗️ ComfyReality/Scene"
    DESCRIPTION = "Compose multi-object AR scenes with lighting"

    def compose_scene(
        self,
        scene_name: str,
        environment_type: str,
        lighting_setup: str,
        object_1=None,
        material_1=None,
        transform_1=None,
        object_2=None,
        material_2=None,
        transform_2=None,
        object_3=None,
        material_3=None,
        transform_3=None,
        environment_map=None,
        ground_plane: bool = True,
        shadows_enabled: bool = True,
        ambient_intensity: float = 0.3,
        directional_intensity: float = 1.0,
        shadow_softness: float = 0.5,
        ar_anchor_type: str = "plane",
        interaction_enabled: bool = True,
        physics_simulation: bool = False,
    ):
        """Compose AR scene from multiple objects and lighting setup."""

        # Collect scene objects
        scene_objects = []
        for i in range(1, 4):
            obj = locals().get(f"object_{i}")
            mat = locals().get(f"material_{i}")
            transform = locals().get(f"transform_{i}")

            if obj is not None:
                scene_objects.append(
                    {
                        "id": f"object_{i}",
                        "geometry": obj,
                        "material": mat,
                        "transform": transform,
                    }
                )

        # Build scene graph
        scene_graph = {
            "name": scene_name,
            "objects": scene_objects,
            "object_count": len(scene_objects),
            "hierarchy": self._build_hierarchy(scene_objects),
        }

        # Setup lighting
        lighting = self._setup_lighting(
            lighting_setup,
            ambient_intensity,
            directional_intensity,
            shadow_softness,
            shadows_enabled,
            environment_type,
            environment_map,
        )

        # Calculate scene bounds
        bounds = self._calculate_scene_bounds(scene_objects)

        # Build complete AR scene
        ar_scene = {
            "name": scene_name,
            "type": "ar_scene",
            "environment": environment_type,
            "anchor_type": ar_anchor_type,
            "objects": scene_objects,
            "lighting": lighting,
            "settings": {
                "ground_plane": ground_plane,
                "shadows_enabled": shadows_enabled,
                "interaction_enabled": interaction_enabled,
                "physics_simulation": physics_simulation,
            },
            "bounds": bounds,
            "metadata": {
                "created_by": "ComfyReality",
                "version": "1.0",
                "mobile_optimized": True,
            },
        }

        return (ar_scene, scene_graph, lighting, bounds)

    def _build_hierarchy(self, objects):
        """Build scene hierarchy tree."""
        # Placeholder: build parent-child relationships
        hierarchy = {
            "root": {
                "children": [obj["id"] for obj in objects],
                "transform": np.eye(4).tolist(),
            }
        }
        return hierarchy

    def _setup_lighting(self, setup_type, ambient, directional, softness, shadows, env_type, env_map):
        """Configure scene lighting."""
        lighting = {
            "type": setup_type,
            "ambient": {
                "intensity": ambient,
                "color": [1.0, 1.0, 1.0],
            },
            "directional": {
                "intensity": directional,
                "color": [1.0, 1.0, 1.0],
                "direction": [-0.5, -1.0, -0.5],  # Default sun direction
            },
            "shadows": {
                "enabled": shadows,
                "softness": softness,
                "resolution": 1024,
            },
            "environment": {
                "type": env_type,
                "map": env_map,
            },
        }

        # Apply lighting presets based on setup type
        if setup_type == "three_point":
            lighting["key_light"] = {"intensity": directional, "angle": 45}
            lighting["fill_light"] = {"intensity": directional * 0.5, "angle": -45}
            lighting["rim_light"] = {"intensity": directional * 0.3, "angle": 135}

        return lighting

    def _calculate_scene_bounds(self, objects):
        """Calculate combined scene bounding box."""
        if not objects:
            return {"min": [0, 0, 0], "max": [0, 0, 0], "center": [0, 0, 0]}

        # Placeholder bounds calculation
        bounds = {
            "min": [-5.0, -5.0, -5.0],
            "max": [5.0, 5.0, 5.0],
            "center": [0.0, 0.0, 0.0],
            "radius": 7.07,  # sqrt(5^2 + 5^2 + 5^2)
        }
        return bounds
