#!/usr/bin/env python3
"""
Simple UV Orientation Test for ComfyReality
===========================================

This script tests the UV orientation fix by creating a USDZ file
from the test texture and verifying it can be opened for manual inspection.

Usage:
    uv run python test_uv_orientation.py

Expected Result:
    - Generates USDZ file in output/ar_stickers/
    - Opens USDZ file automatically for inspection
    - Test texture should display with correct orientation:
      * Top-Left: Green (TL)
      * Top-Right: Blue (TR)
      * Bottom-Left: Yellow (BL)
      * Bottom-Right: Magenta (BR)
      * "TOP" text with upward arrow at top
      * "BOTTOM" text at bottom
"""

import subprocess
import sys
from pathlib import Path

import numpy as np
import torch
from PIL import Image

# Add the source directory to path
sys.path.append("src")

from comfy_reality.nodes.usdz_exporter import USDZExporter


def main():
    print("🧪 ComfyReality UV Orientation Test")
    print("=" * 50)

    # Load the test texture
    texture_path = Path("tests/fixtures/test_texture.png")
    if not texture_path.exists():
        print(f"❌ Test texture not found: {texture_path}")
        print("   Please ensure the test texture exists.")
        return False

    print(f"📐 Loading test texture: {texture_path}")

    # Load and convert image to tensor format
    image = Image.open(texture_path)
    image_np = np.array(image)

    # Remove alpha channel if present
    if image_np.shape[-1] == 4:
        image_np = image_np[:, :, :3]

    # Normalize and convert to BCHW tensor format
    image_np = image_np.astype(np.float32) / 255.0
    image_np = np.transpose(image_np, (2, 0, 1))  # HWC -> CHW
    image_tensor = torch.from_numpy(image_np).unsqueeze(0)  # Add batch dimension

    print(f"📊 Tensor shape: {image_tensor.shape} (BCHW format)")

    # Create and run USDZExporter
    exporter = USDZExporter()

    print("🚀 Exporting USDZ with UV orientation fix...")
    try:
        result = exporter.export_usdz(
            image=image_tensor,
            filename="uv_orientation_test",
            mask=None,
            scale=1.0,
            material_type="unlit",
            optimization_level="quality",
            coordinate_system="y_up",
            physics_enabled=False,
        )

        # Check result
        if isinstance(result, tuple) and len(result) > 0:
            output_file = Path(result[0])
            if output_file.exists():
                print(f"✅ USDZ file created: {output_file}")
                print(f"📏 File size: {output_file.stat().st_size:,} bytes")

                # Open the file for manual inspection
                print("\n🔍 Opening USDZ file for manual inspection...")
                try:
                    subprocess.run(["open", str(output_file)], check=True)
                    print("📱 USDZ file should now be open in the default viewer.")
                except subprocess.CalledProcessError:
                    print("⚠️  Could not open file automatically. Please open manually:")
                    print(f"   {output_file}")

                print("\n📋 Manual Verification Checklist:")
                print("   ✓ Top-Left corner: Green (TL)")
                print("   ✓ Top-Right corner: Blue (TR)")
                print("   ✓ Bottom-Left corner: Yellow (BL)")
                print("   ✓ Bottom-Right corner: Magenta (BR)")
                print("   ✓ 'TOP' text with upward arrow at top")
                print("   ✓ 'BOTTOM' text at bottom")
                print("   ✓ Overall texture appears right-side up")

                return True
            else:
                print(f"❌ Output file not found: {output_file}")
                return False
        else:
            print(f"❌ Export failed: {result}")
            return False

    except Exception as e:
        print(f"❌ Error during export: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
