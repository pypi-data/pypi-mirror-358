"""Physics Integrator Node for ComfyUI Reality."""

from typing import Any


class PhysicsIntegrator:
    """Add physics properties and collision to AR objects.

    This node integrates basic physics simulation including collision detection,
    rigid body dynamics, and environmental physics for interactive AR experiences.
    """

    @classmethod
    def INPUT_TYPES(cls) -> dict[str, Any]:
        """Define the input parameters for the node."""
        return {
            "required": {
                "physics_type": (
                    ["static", "kinematic", "dynamic", "ghost"],
                    {"default": "dynamic"},
                ),
                "collision_shape": (
                    [
                        "auto",
                        "box",
                        "sphere",
                        "capsule",
                        "cylinder",
                        "mesh",
                        "convex_hull",
                    ],
                    {"default": "auto"},
                ),
                "mass": (
                    "FLOAT",
                    {"default": 1.0, "min": 0.0, "max": 1000.0, "step": 0.1},
                ),
            },
            "optional": {
                "geometry": ("GEOMETRY",),
                "material_physics": ("MATERIAL",),
                "friction": (
                    "FLOAT",
                    {"default": 0.5, "min": 0.0, "max": 2.0, "step": 0.01},
                ),
                "restitution": (
                    "FLOAT",
                    {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.01},
                ),
                "linear_damping": (
                    "FLOAT",
                    {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.01},
                ),
                "angular_damping": (
                    "FLOAT",
                    {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.01},
                ),
                "gravity_scale": (
                    "FLOAT",
                    {"default": 1.0, "min": -2.0, "max": 2.0, "step": 0.1},
                ),
                "collision_layers": (
                    "STRING",
                    {"default": "default", "multiline": False},
                ),
                "collision_mask": (
                    "STRING",
                    {"default": "all", "multiline": False},
                ),
                "trigger_events": ("BOOLEAN", {"default": False}),
                "continuous_collision": ("BOOLEAN", {"default": False}),
                "lock_rotation": ("BOOLEAN", {"default": False}),
                "freeze_position_x": ("BOOLEAN", {"default": False}),
                "freeze_position_y": ("BOOLEAN", {"default": False}),
                "freeze_position_z": ("BOOLEAN", {"default": False}),
            },
        }

    RETURN_TYPES = ("PHYSICS_BODY", "COLLISION_SHAPE", "PHYSICS_PROPERTIES")
    RETURN_NAMES = ("physics_body", "collision_shape", "properties")
    FUNCTION = "integrate_physics"
    CATEGORY = "⚛️ ComfyReality/Physics"
    DESCRIPTION = "Add physics properties and collision to AR objects"

    def integrate_physics(
        self,
        physics_type: str,
        collision_shape: str,
        mass: float,
        geometry=None,
        material_physics=None,
        friction: float = 0.5,
        restitution: float = 0.0,
        linear_damping: float = 0.0,
        angular_damping: float = 0.0,
        gravity_scale: float = 1.0,
        collision_layers: str = "default",
        collision_mask: str = "all",
        trigger_events: bool = False,
        continuous_collision: bool = False,
        lock_rotation: bool = False,
        freeze_position_x: bool = False,
        freeze_position_y: bool = False,
        freeze_position_z: bool = False,
    ):
        """Integrate physics properties into AR object."""

        # Build collision shape
        collision_shape_data = self._build_collision_shape(collision_shape, geometry, mass)

        # Build physics body
        physics_body = {
            "type": physics_type,
            "mass": mass if physics_type == "dynamic" else 0.0,
            "friction": friction,
            "restitution": restitution,
            "linear_damping": linear_damping,
            "angular_damping": angular_damping,
            "gravity_scale": gravity_scale,
            "collision_shape": collision_shape_data,
            "collision_layers": self._parse_collision_layers(collision_layers),
            "collision_mask": self._parse_collision_mask(collision_mask),
            "is_trigger": trigger_events,
            "continuous_collision_detection": continuous_collision,
            "constraints": {
                "lock_rotation": lock_rotation,
                "freeze_position": [
                    freeze_position_x,
                    freeze_position_y,
                    freeze_position_z,
                ],
            },
        }

        # Apply material physics properties
        if material_physics:
            physics_body = self._apply_material_physics(physics_body, material_physics)

        # Compile physics properties
        properties = {
            "simulation_ready": True,
            "mobile_optimized": self._check_mobile_optimization(physics_body),
            "collision_complexity": self._calculate_collision_complexity(collision_shape_data),
            "performance_cost": self._estimate_performance_cost(physics_body),
            "interaction_types": self._get_interaction_types(physics_body),
        }

        return (physics_body, collision_shape_data, properties)

    def _build_collision_shape(self, shape_type, geometry, mass):
        """Build collision shape from geometry or primitive."""
        if shape_type == "auto":
            # Auto-detect best collision shape
            if geometry is not None:
                shape_type = self._auto_detect_shape(geometry)
            else:
                shape_type = "box"  # Default fallback

        collision_shape = {
            "type": shape_type,
            "mass": mass,
        }

        if shape_type == "box":
            collision_shape["size"] = [1.0, 1.0, 1.0]  # Default box size
        elif shape_type == "sphere":
            collision_shape["radius"] = 0.5  # Default sphere radius
        elif shape_type == "capsule":
            collision_shape["radius"] = 0.5
            collision_shape["height"] = 2.0
        elif shape_type == "cylinder":
            collision_shape["radius"] = 0.5
            collision_shape["height"] = 1.0
        elif shape_type == "mesh":
            if geometry is not None:
                collision_shape["vertices"] = self._extract_vertices(geometry)
                collision_shape["triangles"] = self._extract_triangles(geometry)
            else:
                # Fallback to box if no geometry provided
                collision_shape["type"] = "box"
                collision_shape["size"] = [1.0, 1.0, 1.0]
        elif shape_type == "convex_hull":
            if geometry is not None:
                collision_shape["hull_vertices"] = self._compute_convex_hull(geometry)
            else:
                # Fallback to sphere if no geometry provided
                collision_shape["type"] = "sphere"
                collision_shape["radius"] = 0.5

        return collision_shape

    def _auto_detect_shape(self, geometry):
        """Auto-detect best collision shape for geometry."""
        # Placeholder: analyze geometry to determine best collision shape
        # This would analyze the geometry's dimensions and complexity
        return "convex_hull"  # Conservative choice for arbitrary geometry

    def _extract_vertices(self, geometry):
        """Extract vertices from geometry for mesh collision."""
        # Placeholder: extract vertex data from geometry
        return [[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]]  # Tetrahedron

    def _extract_triangles(self, geometry):
        """Extract triangle indices from geometry."""
        # Placeholder: extract triangle data from geometry
        return [[0, 1, 2], [0, 1, 3], [0, 2, 3], [1, 2, 3]]  # Tetrahedron faces

    def _compute_convex_hull(self, geometry):
        """Compute convex hull vertices from geometry."""
        # Placeholder: compute convex hull
        return [[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]]  # Simplified hull

    def _parse_collision_layers(self, layers_str):
        """Parse collision layers string into bit mask."""
        # Placeholder: parse layer names into bit flags
        layers = layers_str.split(",") if "," in layers_str else [layers_str]
        layer_map = {
            "default": 1,
            "environment": 2,
            "objects": 4,
            "ui": 8,
            "effects": 16,
        }

        mask = 0
        for layer in layers:
            layer = layer.strip()
            if layer in layer_map:
                mask |= layer_map[layer]

        return mask if mask > 0 else 1  # Default layer if none found

    def _parse_collision_mask(self, mask_str):
        """Parse collision mask string into bit mask."""
        if mask_str == "all":
            return 0xFFFFFFFF  # All layers
        elif mask_str == "none":
            return 0
        else:
            return self._parse_collision_layers(mask_str)

    def _apply_material_physics(self, physics_body, material):
        """Apply material-specific physics properties."""
        # Placeholder: extract physics properties from material
        if "physics_properties" in material:
            props = material["physics_properties"]
            physics_body["friction"] = props.get("friction", physics_body["friction"])
            physics_body["restitution"] = props.get("restitution", physics_body["restitution"])

        return physics_body

    def _check_mobile_optimization(self, physics_body):
        """Check if physics setup is mobile-optimized."""
        # Simple heuristic: convex shapes and reasonable constraints
        shape_type = physics_body["collision_shape"]["type"]
        mobile_friendly_shapes = ["box", "sphere", "capsule", "cylinder", "convex_hull"]

        return shape_type in mobile_friendly_shapes and not physics_body["continuous_collision_detection"] and physics_body["mass"] < 100.0

    def _calculate_collision_complexity(self, collision_shape):
        """Calculate collision detection complexity."""
        shape_type = collision_shape["type"]
        complexity_map = {
            "sphere": 1,
            "box": 2,
            "capsule": 3,
            "cylinder": 4,
            "convex_hull": 6,
            "mesh": 10,
        }
        return complexity_map.get(shape_type, 5)

    def _estimate_performance_cost(self, physics_body):
        """Estimate physics performance cost (1-10 scale)."""
        cost = 1

        # Body type cost
        if physics_body["type"] == "dynamic":
            cost += 3
        elif physics_body["type"] == "kinematic":
            cost += 1

        # Collision shape cost
        shape_complexity = self._calculate_collision_complexity(physics_body["collision_shape"])
        cost += shape_complexity // 2

        # Feature costs
        if physics_body["continuous_collision_detection"]:
            cost += 2
        if physics_body["is_trigger"]:
            cost += 1

        return min(cost, 10)  # Cap at 10

    def _get_interaction_types(self, physics_body):
        """Get list of possible interaction types."""
        interactions = []

        if physics_body["type"] == "dynamic":
            interactions.extend(["collision", "forces", "impulses"])

        if physics_body["is_trigger"]:
            interactions.append("trigger_events")

        if physics_body["mass"] > 0:
            interactions.append("gravity_affected")

        return interactions
