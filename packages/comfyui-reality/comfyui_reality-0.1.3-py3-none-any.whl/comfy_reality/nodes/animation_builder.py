"""Animation Builder Node for ComfyUI Reality."""

from typing import Any


class AnimationBuilder:
    """Create keyframe animations for AR objects.

    This node builds simple keyframe animations including transforms, materials,
    and visibility changes with support for common easing functions and timing.
    """

    @classmethod
    def INPUT_TYPES(cls) -> dict[str, Any]:
        """Define the input parameters for the node."""
        return {
            "required": {
                "animation_name": (
                    "STRING",
                    {"default": "ar_animation", "multiline": False},
                ),
                "animation_type": (
                    [
                        "transform",
                        "material",
                        "visibility",
                        "scale_pulse",
                        "rotation",
                        "custom",
                    ],
                    {"default": "transform"},
                ),
                "duration": (
                    "FLOAT",
                    {"default": 2.0, "min": 0.1, "max": 60.0, "step": 0.1},
                ),
                "loop_mode": (
                    ["none", "loop", "ping_pong", "reverse"],
                    {"default": "loop"},
                ),
            },
            "optional": {
                "start_transform": ("SPATIAL_TRANSFORM",),
                "end_transform": ("SPATIAL_TRANSFORM",),
                "easing_function": (
                    [
                        "linear",
                        "ease_in",
                        "ease_out",
                        "ease_in_out",
                        "bounce",
                        "elastic",
                    ],
                    {"default": "ease_in_out"},
                ),
                "delay": (
                    "FLOAT",
                    {"default": 0.0, "min": 0.0, "max": 10.0, "step": 0.1},
                ),
                "keyframes": ("KEYFRAMES",),
                "auto_reverse": ("BOOLEAN", {"default": False}),
                "start_material": ("MATERIAL",),
                "end_material": ("MATERIAL",),
                "visibility_pattern": (
                    ["fade", "blink", "dissolve", "wipe"],
                    {"default": "fade"},
                ),
                "trigger_type": (
                    ["auto", "tap", "proximity", "time", "custom"],
                    {"default": "auto"},
                ),
                "repeat_count": (
                    "INT",
                    {"default": -1, "min": -1, "max": 100, "step": 1},  # -1 = infinite
                ),
            },
        }

    RETURN_TYPES = ("ANIMATION", "ANIMATION_TIMELINE", "ANIMATION_PROPERTIES")
    RETURN_NAMES = ("animation", "timeline", "properties")
    FUNCTION = "build_animation"
    CATEGORY = "🎬 ComfyReality/Animation"
    DESCRIPTION = "Create keyframe animations for AR objects"

    def build_animation(
        self,
        animation_name: str,
        animation_type: str,
        duration: float,
        loop_mode: str,
        start_transform=None,
        end_transform=None,
        easing_function: str = "ease_in_out",
        delay: float = 0.0,
        keyframes=None,
        auto_reverse: bool = False,
        start_material=None,
        end_material=None,
        visibility_pattern: str = "fade",
        trigger_type: str = "auto",
        repeat_count: int = -1,
    ):
        """Build keyframe animation for AR objects."""

        # Build animation based on type
        if animation_type == "transform":
            animation = self._build_transform_animation(start_transform, end_transform, duration, easing_function)
        elif animation_type == "material":
            animation = self._build_material_animation(start_material, end_material, duration, easing_function)
        elif animation_type == "visibility":
            animation = self._build_visibility_animation(visibility_pattern, duration, easing_function)
        elif animation_type == "scale_pulse":
            animation = self._build_scale_pulse_animation(duration, easing_function)
        elif animation_type == "rotation":
            animation = self._build_rotation_animation(duration, easing_function)
        else:
            animation = self._build_custom_animation(keyframes, duration, easing_function)

        # Apply animation settings
        animation.update(
            {
                "name": animation_name,
                "type": animation_type,
                "duration": duration,
                "delay": delay,
                "loop_mode": loop_mode,
                "auto_reverse": auto_reverse,
                "trigger_type": trigger_type,
                "repeat_count": repeat_count,
            }
        )

        # Build timeline
        timeline = self._build_timeline(animation, duration, loop_mode, repeat_count)

        # Compile animation properties
        properties = {
            "total_duration": self._calculate_total_duration(duration, repeat_count, auto_reverse, delay),
            "keyframe_count": len(animation.get("keyframes", [])),
            "interpolation_type": easing_function,
            "mobile_optimized": True,
            "smooth_playback": self._check_smooth_playback(animation),
        }

        return (animation, timeline, properties)

    def _build_transform_animation(self, start_transform, end_transform, duration, easing):
        """Build position/rotation/scale animation."""
        keyframes = []

        if start_transform and end_transform:
            # Start keyframe
            keyframes.append(
                {
                    "time": 0.0,
                    "transform": start_transform,
                    "easing": easing,
                }
            )

            # End keyframe
            keyframes.append(
                {
                    "time": duration,
                    "transform": end_transform,
                    "easing": easing,
                }
            )
        else:
            # Default transform animation (placeholder)
            keyframes = [
                {
                    "time": 0.0,
                    "position": [0, 0, 0],
                    "rotation": [0, 0, 0],
                    "scale": 1.0,
                },
                {
                    "time": duration,
                    "position": [0, 1, 0],
                    "rotation": [0, 360, 0],
                    "scale": 1.0,
                },
            ]

        return {"keyframes": keyframes, "interpolation": "transform"}

    def _build_material_animation(self, start_material, end_material, duration, easing):
        """Build material property animation."""
        keyframes = []

        if start_material and end_material:
            keyframes.append(
                {
                    "time": 0.0,
                    "material": start_material,
                    "easing": easing,
                }
            )

            keyframes.append(
                {
                    "time": duration,
                    "material": end_material,
                    "easing": easing,
                }
            )
        else:
            # Default material animation (opacity fade)
            keyframes = [
                {"time": 0.0, "opacity": 0.0},
                {"time": duration, "opacity": 1.0},
            ]

        return {"keyframes": keyframes, "interpolation": "material"}

    def _build_visibility_animation(self, pattern, duration, easing):
        """Build visibility animation with various patterns."""
        keyframes = []

        if pattern == "fade":
            keyframes = [
                {"time": 0.0, "opacity": 0.0},
                {"time": duration, "opacity": 1.0},
            ]
        elif pattern == "blink":
            keyframes = [
                {"time": 0.0, "opacity": 1.0},
                {"time": duration * 0.5, "opacity": 0.0},
                {"time": duration, "opacity": 1.0},
            ]
        elif pattern == "dissolve":
            keyframes = [
                {"time": 0.0, "dissolve": 0.0},
                {"time": duration, "dissolve": 1.0},
            ]
        elif pattern == "wipe":
            keyframes = [
                {"time": 0.0, "wipe_progress": 0.0},
                {"time": duration, "wipe_progress": 1.0},
            ]

        return {"keyframes": keyframes, "interpolation": "visibility"}

    def _build_scale_pulse_animation(self, duration, easing):
        """Build pulsing scale animation."""
        keyframes = [
            {"time": 0.0, "scale": 1.0},
            {"time": duration * 0.5, "scale": 1.2},
            {"time": duration, "scale": 1.0},
        ]
        return {"keyframes": keyframes, "interpolation": "transform"}

    def _build_rotation_animation(self, duration, easing):
        """Build continuous rotation animation."""
        keyframes = [
            {"time": 0.0, "rotation": [0, 0, 0]},
            {"time": duration, "rotation": [0, 360, 0]},
        ]
        return {"keyframes": keyframes, "interpolation": "transform"}

    def _build_custom_animation(self, keyframes, duration, easing):
        """Build custom animation from user keyframes."""
        if keyframes:
            return {"keyframes": keyframes, "interpolation": "custom"}
        else:
            # Default empty animation
            return {"keyframes": [], "interpolation": "none"}

    def _build_timeline(self, animation, duration, loop_mode, repeat_count):
        """Build animation timeline."""
        timeline = {
            "total_duration": self._calculate_total_duration(duration, repeat_count, False, 0),
            "segments": [],
            "loop_mode": loop_mode,
        }

        # Add animation segments based on loop mode
        current_time = 0.0
        iterations = repeat_count if repeat_count > 0 else 1

        for i in range(iterations):
            segment = {
                "start_time": current_time,
                "end_time": current_time + duration,
                "iteration": i + 1,
                "direction": "forward" if loop_mode != "reverse" else "reverse",
            }
            timeline["segments"].append(segment)
            current_time += duration

        return timeline

    def _calculate_total_duration(self, base_duration, repeat_count, auto_reverse, delay):
        """Calculate total animation duration."""
        if repeat_count == -1:  # Infinite loop
            return float("inf")

        total = delay + base_duration
        if repeat_count > 1:
            total += (repeat_count - 1) * base_duration
        if auto_reverse:
            total *= 2

        return total

    def _check_smooth_playback(self, animation):
        """Check if animation will play smoothly on mobile."""
        keyframe_count = len(animation.get("keyframes", []))
        # Simple heuristic: fewer keyframes = smoother playback
        return keyframe_count < 10
