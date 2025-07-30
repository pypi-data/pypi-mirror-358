#!/usr/bin/env python3
"""Generate USDZ files for manual UV orientation validation.

This script creates a series of USDZ files with different configurations
to allow for manual inspection of UV orientation correctness.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

# Add the source directory to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

import numpy as np
import torch
from PIL import Image

from comfy_reality.nodes.usdz_exporter import USDZExporter


def create_uv_test_image(size: int = 512) -> torch.Tensor:
    """Create a test image with clear UV orientation markers."""
    image = torch.zeros(1, size, size, 3)

    # Add gradient background for depth perception
    for y in range(size):
        for x in range(size):
            image[0, y, x, 0] = x / (size - 1)  # Red gradient left to right
            image[0, y, x, 1] = y / (size - 1)  # Green gradient top to bottom
            image[0, y, x, 2] = 0.2  # Constant blue for contrast

    # Add corner markers
    corner_size = size // 8  # 1/8 of image size

    # Top-Left: Bright White
    image[0, :corner_size, :corner_size] = torch.tensor([1.0, 1.0, 1.0])

    # Top-Right: Bright Red
    image[0, :corner_size, -corner_size:] = torch.tensor([1.0, 0.0, 0.0])

    # Bottom-Left: Bright Blue
    image[0, -corner_size:, :corner_size] = torch.tensor([0.0, 0.0, 1.0])

    # Bottom-Right: Bright Yellow
    image[0, -corner_size:, -corner_size:] = torch.tensor([1.0, 1.0, 0.0])

    # Add center cross for reference
    center = size // 2
    cross_size = size // 20

    # Horizontal bar
    image[0, center - cross_size : center + cross_size, :] = torch.tensor([0.0, 0.0, 0.0])

    # Vertical bar
    image[0, :, center - cross_size : center + cross_size] = torch.tensor([0.0, 0.0, 0.0])

    return image


def load_test_texture() -> torch.Tensor:
    """Load the actual test texture if available."""
    texture_path = Path("tests/fixtures/test_texture.png")
    if not texture_path.exists():
        return None

    # Load image using PIL
    image = Image.open(texture_path)

    # Convert to tensor format expected by ComfyUI nodes
    image_np = np.array(image)
    if image_np.shape[-1] == 4:  # RGBA
        image_np = image_np[:, :, :3]  # Remove alpha

    # Normalize to 0-1 range
    image_np = image_np.astype(np.float32) / 255.0

    # Convert to ComfyUI format: [1, H, W, C]
    image_tensor = torch.from_numpy(image_np).unsqueeze(0)

    return image_tensor


def create_checkerboard_image(size: int = 512, squares: int = 8) -> torch.Tensor:
    """Create a checkerboard pattern for UV validation."""
    image = torch.zeros(1, size, size, 3)

    square_size = size // squares

    for y in range(size):
        for x in range(size):
            square_y = y // square_size
            square_x = x // square_size

            # Checkerboard pattern
            if (square_x + square_y) % 2 == 0:
                image[0, y, x] = torch.tensor([1.0, 1.0, 1.0])  # White
            else:
                image[0, y, x] = torch.tensor([0.0, 0.0, 0.0])  # Black

    # Add colored corners to show orientation
    corner_size = size // 16

    # Top-Left: Green
    image[0, :corner_size, :corner_size, 1] = 1.0
    image[0, :corner_size, :corner_size, 0] = 0.0
    image[0, :corner_size, :corner_size, 2] = 0.0

    # Top-Right: Red
    image[0, :corner_size, -corner_size:, 0] = 1.0
    image[0, :corner_size, -corner_size:, 1] = 0.0
    image[0, :corner_size, -corner_size:, 2] = 0.0

    # Bottom-Left: Blue
    image[0, -corner_size:, :corner_size, 2] = 1.0
    image[0, -corner_size:, :corner_size, 0] = 0.0
    image[0, -corner_size:, :corner_size, 1] = 0.0

    # Bottom-Right: Yellow
    image[0, -corner_size:, -corner_size:, 0] = 1.0
    image[0, -corner_size:, -corner_size:, 1] = 1.0
    image[0, -corner_size:, -corner_size:, 2] = 0.0

    return image


def generate_validation_files(output_dir: Path = None, verbose: bool = True) -> list[dict[str, Any]]:
    """Generate USDZ files for UV orientation validation."""
    if output_dir is None:
        output_dir = Path("output/uv_validation")

    output_dir.mkdir(parents=True, exist_ok=True)

    exporter = USDZExporter()
    results = []

    # Test configurations
    test_configs = [
        {
            "name": "synthetic_gradient",
            "image": create_uv_test_image(512),
            "material_type": "unlit",
            "description": "Synthetic gradient with corner markers",
        },
        {
            "name": "synthetic_standard",
            "image": create_uv_test_image(512),
            "material_type": "standard",
            "description": "Synthetic gradient with standard material",
        },
        {
            "name": "checkerboard_unlit",
            "image": create_checkerboard_image(512, 8),
            "material_type": "unlit",
            "description": "Checkerboard pattern with colored corners",
        },
        {
            "name": "checkerboard_metallic",
            "image": create_checkerboard_image(512, 8),
            "material_type": "metallic",
            "description": "Checkerboard pattern with metallic material",
        },
        {
            "name": "large_gradient",
            "image": create_uv_test_image(1024),
            "material_type": "unlit",
            "description": "Large gradient image (1024x1024)",
        },
    ]

    # Add real texture if available
    real_texture = load_test_texture()
    if real_texture is not None:
        test_configs.extend(
            [
                {
                    "name": "real_texture_unlit",
                    "image": real_texture,
                    "material_type": "unlit",
                    "description": "Real test texture with unlit material",
                },
                {
                    "name": "real_texture_standard",
                    "image": real_texture,
                    "material_type": "standard",
                    "description": "Real test texture with standard material",
                },
            ]
        )

    # Generate all test files
    for config in test_configs:
        if verbose:
            print(f"Generating {config['name']}...")

        try:
            result = exporter.export_usdz(
                image=config["image"],
                filename=config["name"],
                material_type=config["material_type"],
                optimization_level="quality",
                coordinate_system="y_up",
                physics_enabled=False,
            )

            # Find the actual output path
            result_path = Path(result[0]) if Path(result[0]).exists() else Path(f"output/ar_stickers/{config['name']}.usdz")

            if result_path.exists():
                file_size = result_path.stat().st_size
                results.append(
                    {
                        "name": config["name"],
                        "path": str(result_path),
                        "size_bytes": file_size,
                        "size_mb": file_size / (1024 * 1024),
                        "material_type": config["material_type"],
                        "description": config["description"],
                        "success": True,
                    }
                )

                if verbose:
                    print(f"  ✅ Generated: {result_path} ({file_size / 1024:.1f} KB)")
            else:
                results.append({"name": config["name"], "success": False, "error": "File not found after export"})
                if verbose:
                    print("  ❌ Failed: File not found")

        except Exception as e:
            results.append({"name": config["name"], "success": False, "error": str(e)})
            if verbose:
                print(f"  ❌ Failed: {e}")

    return results


def create_validation_report(results: list[dict[str, Any]], output_path: Path = None):
    """Create a validation report with test results."""
    if output_path is None:
        output_path = Path("output/uv_validation/validation_report.json")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Generate summary statistics
    total_tests = len(results)
    successful_tests = sum(1 for r in results if r.get("success", False))
    failed_tests = total_tests - successful_tests

    total_size_mb = sum(r.get("size_mb", 0) for r in results if r.get("success", False))

    report = {
        "timestamp": str(Path(__file__).stat().st_mtime),
        "summary": {
            "total_tests": total_tests,
            "successful": successful_tests,
            "failed": failed_tests,
            "success_rate": successful_tests / total_tests if total_tests > 0 else 0,
            "total_size_mb": total_size_mb,
        },
        "test_results": results,
        "validation_instructions": {
            "manual_validation": [
                "Open each USDZ file in iOS AR Quick Look or ARKit viewer",
                "Check that corner markers are correctly positioned:",
                "  - Top-Left should be WHITE (or GREEN for checkerboard)",
                "  - Top-Right should be RED",
                "  - Bottom-Left should be BLUE",
                "  - Bottom-Right should be YELLOW",
                "Verify that the gradient flows correctly (if applicable)",
                "Ensure the center cross is visible and centered",
            ],
            "expected_orientation": {
                "uv_origin": "Bottom-left corner should be UV (0,0)",
                "uv_max": "Top-right corner should be UV (1,1)",
                "texture_direction": "Texture should not be flipped or rotated",
            },
        },
    }

    with open(output_path, "w") as f:
        json.dump(report, f, indent=2)

    return report


def main():
    """Main entry point for the validation generator."""
    parser = argparse.ArgumentParser(description="Generate USDZ files for UV orientation validation")
    parser.add_argument("--output-dir", "-o", type=Path, help="Output directory for generated files")
    parser.add_argument("--quiet", "-q", action="store_true", help="Suppress verbose output")
    parser.add_argument("--report", "-r", type=Path, help="Path for validation report JSON file")

    args = parser.parse_args()

    print("🧪 ComfyReality UV Orientation Validation Generator")
    print("=" * 50)

    # Generate validation files
    results = generate_validation_files(output_dir=args.output_dir, verbose=not args.quiet)

    # Create validation report
    report = create_validation_report(results, args.report)

    # Print summary
    summary = report["summary"]
    print("\n📊 Generation Summary:")
    print(f"  Total tests: {summary['total_tests']}")
    print(f"  Successful: {summary['successful']}")
    print(f"  Failed: {summary['failed']}")
    print(f"  Success rate: {summary['success_rate']:.1%}")
    print(f"  Total size: {summary['total_size_mb']:.2f} MB")

    if summary["failed"] > 0:
        print("\n❌ Failed tests:")
        for result in results:
            if not result.get("success", False):
                print(f"  - {result['name']}: {result.get('error', 'Unknown error')}")

    # Print validation instructions
    print("\n📱 Manual Validation Instructions:")
    print("1. Open generated USDZ files in iOS AR Quick Look or compatible AR viewer")
    print("2. Verify corner marker positions:")
    print("   - Top-Left: WHITE/GREEN")
    print("   - Top-Right: RED")
    print("   - Bottom-Left: BLUE")
    print("   - Bottom-Right: YELLOW")
    print("3. Check that gradients and patterns appear correctly oriented")

    report_path = args.report or Path("output/uv_validation/validation_report.json")
    print(f"\n📋 Detailed report saved to: {report_path}")

    return 0 if summary["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
