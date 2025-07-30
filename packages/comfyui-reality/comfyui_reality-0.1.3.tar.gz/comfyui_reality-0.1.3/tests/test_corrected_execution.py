#!/usr/bin/env python3
"""Test script with corrected function signatures."""

import sys
import traceback

import numpy as np
import torch

# Add current directory to path
sys.path.append(".")


def create_sample_image_tensor(height=512, width=512, channels=3):
    """Create a sample image tensor for testing."""
    # Create a simple gradient image
    image = np.zeros((height, width, channels), dtype=np.float32)
    for i in range(height):
        for j in range(width):
            image[i, j, 0] = i / height  # Red gradient
            image[i, j, 1] = j / width  # Green gradient
            if channels > 2:
                image[i, j, 2] = 0.5  # Blue constant

    # Convert to torch tensor with batch dimension [1, H, W, C]
    return torch.from_numpy(image).unsqueeze(0)


def test_corrected_ar_optimizer():
    """Test AROptimizer with corrected parameters."""
    print("🧪 Testing AROptimizer (corrected)")
    try:
        from src.comfy_reality.nodes.ar_optimizer import AROptimizer

        node = AROptimizer()
        image_tensor = create_sample_image_tensor()

        result = node.optimize_for_ar(
            image=image_tensor,
            target_platform="ios",
            optimization_level="balanced",
            max_texture_size=1024,
            compression_format="auto",
            target_fps=60,
            memory_budget_mb=100,
            lod_levels=3,
            quality_threshold=0.8,
        )

        print(f"  ✅ Optimization: {type(result)} returned")
        print(f"     Result length: {len(result) if hasattr(result, '__len__') else 'N/A'}")

    except Exception as e:
        print(f"  ❌ Error: {e}")
        traceback.print_exc()


def test_corrected_spatial_positioner():
    """Test SpatialPositioner with corrected parameters."""
    print("🧪 Testing SpatialPositioner (corrected)")
    try:
        from src.comfy_reality.nodes.spatial_positioner import SpatialPositioner

        node = SpatialPositioner()

        result = node.create_spatial_transform(
            position_x=0.0,
            position_y=0.0,
            position_z=0.0,
            scale=1.0,
            rotation_x=0.0,
            rotation_y=0.0,
            rotation_z=0.0,
            anchor_point="center",
            coordinate_system="world",
            auto_ground_snap=False,
            collision_bounds="box",
            relative_positioning=False,
        )

        print(f"  ✅ Spatial transform: {type(result)} returned")
        print(f"     Result length: {len(result) if hasattr(result, '__len__') else 'N/A'}")

    except Exception as e:
        print(f"  ❌ Error: {e}")
        traceback.print_exc()


def test_corrected_material_composer():
    """Test MaterialComposer with corrected parameters."""
    print("🧪 Testing MaterialComposer (corrected)")
    try:
        from src.comfy_reality.nodes.material_composer import MaterialComposer

        node = MaterialComposer()
        albedo_tensor = create_sample_image_tensor(256, 256, 3)

        result = node.compose_material(
            albedo=albedo_tensor,
            material_name="test_material",
            material_type="standard",
            metallic_factor=0.0,
            roughness_factor=0.5,
            emission_strength=1.0,
            opacity=1.0,
            normal_strength=1.0,
            uv_tiling=1.0,
            double_sided=False,
            ar_optimized=True,
        )

        print(f"  ✅ Material composition: {type(result)} returned")
        print(f"     Result length: {len(result) if hasattr(result, '__len__') else 'N/A'}")

    except Exception as e:
        print(f"  ❌ Error: {e}")
        traceback.print_exc()


def test_corrected_reality_composer():
    """Test RealityComposer with corrected parameters."""
    print("🧪 Testing RealityComposer (corrected)")
    try:
        from src.comfy_reality.nodes.reality_composer import RealityComposer

        node = RealityComposer()

        result = node.compose_scene(
            scene_name="test_scene",
            environment_type="indoor",
            lighting_setup="auto",
            ground_plane=True,
            shadows_enabled=True,
            ambient_intensity=0.3,
            directional_intensity=1.0,
            shadow_softness=0.5,
            ar_anchor_type="plane",
            interaction_enabled=True,
            physics_simulation=False,
        )

        print(f"  ✅ Scene composition: {type(result)} returned")
        print(f"     Result length: {len(result) if hasattr(result, '__len__') else 'N/A'}")

    except Exception as e:
        print(f"  ❌ Error: {e}")
        traceback.print_exc()


def main():
    """Main test function."""
    print("🧪 Testing ComfyUI Nodes with Corrected Parameters")
    print("=" * 50)

    test_corrected_ar_optimizer()
    print()
    test_corrected_spatial_positioner()
    print()
    test_corrected_material_composer()
    print()
    test_corrected_reality_composer()

    print("\n✅ Corrected execution tests completed!")


if __name__ == "__main__":
    main()
