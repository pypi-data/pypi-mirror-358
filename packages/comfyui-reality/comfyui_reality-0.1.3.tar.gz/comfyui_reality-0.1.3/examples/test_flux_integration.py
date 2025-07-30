#!/usr/bin/env python3
"""Test the Flux AR integration by creating a simple USDZ."""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import numpy as np
import torch
from PIL import Image

from comfy_reality.nodes.ar_background_remover import ARBackgroundRemover
from comfy_reality.nodes.ar_optimizer import AROptimizer
from comfy_reality.nodes.material_composer import MaterialComposer
from comfy_reality.nodes.spatial_positioner import SpatialPositioner
from comfy_reality.nodes.usdz_exporter import USDZExporter


def create_test_image() -> torch.Tensor:
    """Create a test image tensor."""
    # Create a colorful test image
    size = 1024
    img = Image.new("RGBA", (size, size), (255, 255, 255, 255))
    pixels = img.load()

    # Create a simple robot face
    # Background gradient
    for y in range(size):
        for x in range(size):
            # Gradient from purple to blue
            r = int(180 + 75 * (1 - x / size))
            g = int(120 + 80 * (y / size))
            b = int(200 + 55 * (x / size))

            # Keep center area white for the robot
            center_x, center_y = size // 2, size // 2
            dist = ((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5
            if dist < size * 0.3:
                pixels[x, y] = (255, 255, 255, 255)
            else:
                pixels[x, y] = (r, g, b, 255)

    # Draw robot features
    # Eyes
    eye_y = int(size * 0.45)
    for eye_x in [int(size * 0.4), int(size * 0.6)]:
        for dy in range(-30, 30):
            for dx in range(-30, 30):
                if dx * dx + dy * dy < 900:  # Circle
                    x, y = eye_x + dx, eye_y + dy
                    if 0 <= x < size and 0 <= y < size:
                        pixels[x, y] = (100, 200, 255, 255)  # Blue eyes

    # Smile
    smile_y = int(size * 0.6)
    for x in range(int(size * 0.35), int(size * 0.65)):
        y = smile_y + int(20 * np.sin((x - size * 0.35) / (size * 0.3) * np.pi))
        for dy in range(-5, 5):
            if 0 <= y + dy < size:
                pixels[x, y + dy] = (255, 100, 150, 255)  # Pink smile

    # Convert to tensor
    img_array = np.array(img).astype(np.float32) / 255.0
    img_tensor = torch.from_numpy(img_array).unsqueeze(0)

    return img_tensor


def main():
    """Test the Flux AR workflow."""
    print("🤖 Testing Flux AR Integration")
    print("=" * 40)

    # Create test image
    print("Creating test robot image...")
    image = create_test_image()

    # Initialize nodes
    bg_remover = ARBackgroundRemover()
    optimizer = AROptimizer()
    material = MaterialComposer()
    positioner = SpatialPositioner()
    exporter = USDZExporter()

    try:
        # Step 1: Remove background
        print("\n1. Removing background...")
        image_clean, mask, preview = bg_remover.remove_background(
            image=image, method="chroma_key", threshold_value=240, chroma_color="white", edge_sensitivity=0.1, feather=2, cleanup=True
        )

        # Save preview
        preview_path = Path("examples/test_outputs/robot_preview.png")
        preview_path.parent.mkdir(parents=True, exist_ok=True)
        preview_img = Image.fromarray((preview[0].numpy() * 255).astype(np.uint8))
        preview_img.save(preview_path)
        print(f"   Saved preview: {preview_path}")

        # Step 2: Optimize for AR
        print("\n2. Optimizing for AR...")
        geometry, metadata = optimizer.optimize(
            image=image_clean,
            mask=mask,
            optimization_level="balanced",
            target_platform="universal",
            texture_size=1024,
            simplification_ratio=0.8,
            alpha_mode="blend",
        )

        # Step 3: Apply materials
        print("\n3. Applying materials...")
        ar_object = material.apply_material(
            geometry=geometry,
            material_type="standard",
            base_color=[1.0, 1.0, 1.0, 1.0],
            metallic=0.0,
            roughness=0.8,
            double_sided=True,
            emissive_color=[0.5, 0.7, 1.0],
            emissive_intensity=0.1,
        )

        # Step 4: Position in AR space
        print("\n4. Positioning in AR space...")
        ar_scene = positioner.position(
            ar_object=ar_object, position_x=0.0, position_y=0.0, position_z=0.0, scale=0.2, anchor_type="horizontal"
        )

        # Step 5: Export USDZ
        print("\n5. Exporting USDZ...")
        output_path = exporter.export(
            ar_scene=ar_scene,
            filename="test_robot_ar",
            metadata={"title": "Test Robot AR Sticker", "author": "ComfyReality Test", "description": "Test integration of Flux AR nodes"},
            optimize_for_ar=True,
        )

        print(f"\n✅ Success! USDZ created: {output_path}")
        print("\nYou can now:")
        print("1. Open in Reality Composer on macOS")
        print("2. View on iOS device with AR Quick Look")
        print("3. Test in ComfyUI with the flux_ar_workflow.json")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
