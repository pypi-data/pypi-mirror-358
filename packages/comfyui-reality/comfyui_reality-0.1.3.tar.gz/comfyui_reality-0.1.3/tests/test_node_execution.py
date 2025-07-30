#!/usr/bin/env python3
"""Test script to verify ComfyUI nodes work with sample inputs."""

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


def create_sample_mask_tensor(height=512, width=512):
    """Create a sample mask tensor for testing."""
    # Create a circular mask
    center_x, center_y = width // 2, height // 2
    radius = min(width, height) // 3

    mask = np.zeros((height, width), dtype=np.float32)
    for i in range(height):
        for j in range(width):
            dist = np.sqrt((i - center_y) ** 2 + (j - center_x) ** 2)
            if dist < radius:
                mask[i, j] = 1.0

    # Convert to torch tensor with batch dimension [1, H, W]
    return torch.from_numpy(mask).unsqueeze(0)


def test_usdz_exporter():
    """Test USDZExporter with sample inputs."""
    print("🧪 Testing USDZExporter")
    try:
        from src.comfy_reality.nodes.usdz_exporter import USDZExporter

        node = USDZExporter()
        image_tensor = create_sample_image_tensor()

        # Test basic export
        result = node.export_usdz(
            image=image_tensor,
            filename="test_export",
            scale=1.0,
            material_type="standard",
            optimization_level="balanced",
            coordinate_system="y_up",
            physics_enabled=False,
        )

        print(f"  ✅ Basic export: {type(result)} returned")

        # Test with mask
        mask_tensor = create_sample_mask_tensor()
        result_with_mask = node.export_usdz(
            image=image_tensor,
            mask=mask_tensor,
            filename="test_export_masked",
            scale=0.5,
            material_type="unlit",
            optimization_level="mobile",
            coordinate_system="z_up",
            physics_enabled=True,
        )

        print(f"  ✅ Export with mask: {type(result_with_mask)} returned")

    except Exception as e:
        print(f"  ❌ Error: {e}")
        traceback.print_exc()


def test_ar_optimizer():
    """Test AROptimizer with sample inputs."""
    print("🧪 Testing AROptimizer")
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
            reduce_polygon_count=True,
            optimize_materials=True,
            generate_lod=False,
        )

        print(f"  ✅ Optimization: {type(result)} returned")

    except Exception as e:
        print(f"  ❌ Error: {e}")
        traceback.print_exc()


def test_spatial_positioner():
    """Test SpatialPositioner with sample inputs."""
    print("🧪 Testing SpatialPositioner")
    try:
        from src.comfy_reality.nodes.spatial_positioner import SpatialPositioner

        node = SpatialPositioner()

        result = node.create_spatial_transform(
            position_x=0.0,
            position_y=0.0,
            position_z=0.0,
            rotation_x=0.0,
            rotation_y=0.0,
            rotation_z=0.0,
            scale_x=1.0,
            scale_y=1.0,
            scale_z=1.0,
            anchor_point="center",
            coordinate_system="world",
            auto_ground_snap=False,
            collision_bounds="box",
            relative_to_parent=False,
        )

        print(f"  ✅ Spatial transform: {type(result)} returned")

    except Exception as e:
        print(f"  ❌ Error: {e}")
        traceback.print_exc()


def test_material_composer():
    """Test MaterialComposer with sample inputs."""
    print("🧪 Testing MaterialComposer")
    try:
        from src.comfy_reality.nodes.material_composer import MaterialComposer

        node = MaterialComposer()
        albedo_tensor = create_sample_image_tensor(256, 256, 3)

        result = node.compose_material(
            albedo=albedo_tensor,
            material_type="standard",
            metallic_factor=0.0,
            roughness_factor=0.5,
            emission_factor=0.0,
            alpha_factor=1.0,
            ior=1.5,
            transmission_factor=0.0,
            uv_scale_u=1.0,
            uv_scale_v=1.0,
            double_sided=False,
            optimize_for_ar=True,
        )

        print(f"  ✅ Material composition: {type(result)} returned")

    except Exception as e:
        print(f"  ❌ Error: {e}")
        traceback.print_exc()


def test_reality_composer():
    """Test RealityComposer with sample inputs."""
    print("🧪 Testing RealityComposer")
    try:
        from src.comfy_reality.nodes.reality_composer import RealityComposer

        node = RealityComposer()
        image_tensor = create_sample_image_tensor()

        # Create sample material data
        material_data = {
            "material_type": "standard",
            "properties": {"metallic_factor": 0.0, "roughness_factor": 0.5, "alpha_factor": 1.0},
            "textures": {},
            "preview": None,
        }

        # Create sample transform data
        transform_data = {
            "matrix": torch.eye(4).numpy().tolist(),
            "position": [0.0, 0.0, 0.0],
            "rotation": [0.0, 0.0, 0.0],
            "scale": [1.0, 1.0, 1.0],
            "anchor_point": "center",
            "bounding_box": {"min": [-0.5, -0.5, -0.5], "max": [0.5, 0.5, 0.5], "center": [0.0, 0.0, 0.0], "size": [1.0, 1.0, 1.0]},
        }

        result = node.compose_reality(
            image=image_tensor,
            material_data=material_data,
            spatial_transform=transform_data,
            scene_scale=1.0,
            lighting_preset="studio",
            environment_map="default",
            shadow_quality="medium",
            render_quality="balanced",
            enable_physics=False,
            physics_preset="default",
        )

        print(f"  ✅ Reality composition: {type(result)} returned")

    except Exception as e:
        print(f"  ❌ Error: {e}")
        traceback.print_exc()


def main():
    """Main test function."""
    print("🧪 Testing ComfyUI Node Execution with Sample Inputs")
    print("=" * 55)

    # Test key nodes that are most likely to be used
    test_usdz_exporter()
    print()
    test_ar_optimizer()
    print()
    test_spatial_positioner()
    print()
    test_material_composer()
    print()
    test_reality_composer()

    print("\n✅ Execution tests completed!")


if __name__ == "__main__":
    main()
