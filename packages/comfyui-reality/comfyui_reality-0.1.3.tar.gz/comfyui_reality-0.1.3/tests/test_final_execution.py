#!/usr/bin/env python3
"""Final test script with corrected tensor format."""

import sys
import traceback

import numpy as np
import torch

# Add current directory to path
sys.path.append(".")


def create_sample_image_tensor(height=512, width=512, channels=3):
    """Create a sample image tensor in ComfyUI format [B, H, W, C]."""
    # Create a simple gradient image
    image = np.zeros((1, height, width, channels), dtype=np.float32)
    for i in range(height):
        for j in range(width):
            image[0, i, j, 0] = i / height  # Red gradient
            image[0, i, j, 1] = j / width  # Green gradient
            if channels > 2:
                image[0, i, j, 2] = 0.5  # Blue constant

    return torch.from_numpy(image)


def inspect_tensor_shape(tensor, name):
    """Debug tensor shape."""
    print(f"  Debug: {name} shape: {tensor.shape}")
    if len(tensor.shape) == 4:
        print(f"    Batch: {tensor.shape[0]}, Height: {tensor.shape[1]}, Width: {tensor.shape[2]}, Channels: {tensor.shape[3]}")


def test_final_ar_optimizer():
    """Test AROptimizer with correct tensor format."""
    print("🧪 Testing AROptimizer (final)")
    try:
        from src.comfy_reality.nodes.ar_optimizer import AROptimizer

        node = AROptimizer()
        image_tensor = create_sample_image_tensor()
        inspect_tensor_shape(image_tensor, "image_tensor")

        result = node.optimize_for_ar(
            image=image_tensor, target_platform="ios", optimization_level="balanced", max_texture_size=1024, compression_format="auto"
        )

        print(f"  ✅ Optimization: {type(result)} returned")
        if isinstance(result, tuple):
            print(f"     Result components: {len(result)}")
            for i, component in enumerate(result):
                print(f"       [{i}]: {type(component)}")

    except Exception as e:
        print(f"  ❌ Error: {e}")
        traceback.print_exc()


def test_usdz_export_end_to_end():
    """Test complete USDZ export workflow."""
    print("🧪 Testing End-to-End USDZ Export")
    try:
        from src.comfy_reality.nodes.material_composer import MaterialComposer
        from src.comfy_reality.nodes.spatial_positioner import SpatialPositioner
        from src.comfy_reality.nodes.usdz_exporter import USDZExporter

        # Create sample image
        image_tensor = create_sample_image_tensor(256, 256, 3)

        # Create material
        material_node = MaterialComposer()
        material_result = material_node.compose_material(albedo=image_tensor, material_name="test_material", material_type="standard")
        print(f"  ✅ Material created: {type(material_result)}")

        # Create spatial transform
        spatial_node = SpatialPositioner()
        spatial_result = spatial_node.create_spatial_transform(position_x=0.0, position_y=0.0, position_z=0.0, scale=1.0)
        print(f"  ✅ Spatial transform created: {type(spatial_result)}")

        # Export USDZ
        export_node = USDZExporter()
        usdz_result = export_node.export_usdz(image=image_tensor, filename="test_end_to_end", material_type="standard", scale=1.0)
        print(f"  ✅ USDZ exported: {type(usdz_result)}")

    except Exception as e:
        print(f"  ❌ Error: {e}")
        traceback.print_exc()


def test_all_nodes_instantiation():
    """Test that all nodes can be instantiated without errors."""
    print("🧪 Testing All Node Instantiation")
    try:
        import __init__ as comfy_reality_init

        mappings = comfy_reality_init.NODE_CLASS_MAPPINGS

        success_count = 0
        total_count = len(mappings)

        for node_name, node_class in mappings.items():
            try:
                node_instance = node_class()
                print(f"  ✅ {node_name}: instantiated successfully")
                success_count += 1
            except Exception as e:
                print(f"  ❌ {node_name}: failed to instantiate - {e}")

        print(f"\nInstantiation Results: {success_count}/{total_count} nodes successful")

    except Exception as e:
        print(f"  ❌ Error: {e}")
        traceback.print_exc()


def main():
    """Main test function."""
    print("🧪 Final ComfyUI Node Testing")
    print("=" * 40)

    test_final_ar_optimizer()
    print()
    test_usdz_export_end_to_end()
    print()
    test_all_nodes_instantiation()

    print("\n✅ All tests completed!")


if __name__ == "__main__":
    main()
