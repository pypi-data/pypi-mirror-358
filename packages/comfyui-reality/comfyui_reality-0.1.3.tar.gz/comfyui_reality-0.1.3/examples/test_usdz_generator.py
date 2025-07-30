#!/usr/bin/env python3
"""Generate a test USDZ file for Reality Composer testing."""

from pathlib import Path

import trimesh
from PIL import Image

# Try to import USD bindings
try:
    from pxr import Gf, Sdf, Usd, UsdGeom, UsdShade, UsdUtils

    USD_AVAILABLE = True
except ImportError:
    print("Warning: USD bindings not available. Will create basic geometry only.")
    USD_AVAILABLE = False


def create_test_texture(size=1024):
    """Create a colorful test texture."""
    # Create gradient texture with ComfyReality branding
    img = Image.new("RGBA", (size, size), (255, 255, 255, 255))
    pixels = img.load()

    # Create a gradient pattern
    for y in range(size):
        for x in range(size):
            # Gradient from purple to blue
            r = int(128 + 127 * (1 - x / size))
            g = int(100 + 100 * (y / size))
            b = int(200 + 55 * (x / size))

            # Add some pattern
            if (x // 64 + y // 64) % 2 == 0:
                r = min(255, r + 30)
                g = min(255, g + 30)
                b = min(255, b + 30)

            pixels[x, y] = (r, g, b, 255)

    # Add text (simple rectangle pattern for "CR")
    # C pattern
    for y in range(min(300, size), min(700, size)):
        for x in range(min(200, size), min(250, size)):
            pixels[x, y] = (255, 255, 255, 255)
    for x in range(min(200, size), min(350, size)):
        for y in range(min(300, size), min(350, size)):
            pixels[x, y] = (255, 255, 255, 255)
    for x in range(min(200, size), min(350, size)):
        for y in range(min(650, size), min(700, size)):
            pixels[x, y] = (255, 255, 255, 255)

    # R pattern (only if size is large enough)
    if size >= 600:
        for y in range(300, min(700, size)):
            for x in range(450, min(500, size)):
                pixels[x, y] = (255, 255, 255, 255)
        for x in range(450, min(600, size)):
            for y in range(300, min(350, size)):
                pixels[x, y] = (255, 255, 255, 255)
        for x in range(450, min(600, size)):
            for y in range(475, min(525, size)):
                pixels[x, y] = (255, 255, 255, 255)
        for x in range(550, min(600, size)):
            for y in range(300, min(525, size)):
                pixels[x, y] = (255, 255, 255, 255)
        # R leg
        for y in range(500, min(700, size)):
            dx = int((y - 500) * 0.5)
            for x in range(500 + dx, min(550 + dx, size)):
                pixels[x, y] = (255, 255, 255, 255)

    return img


def create_test_usdz_simple():
    """Create a simple test USDZ without USD bindings."""
    print("Creating simple test geometry...")

    # Create a simple cube mesh
    mesh = trimesh.creation.box(extents=[1.0, 1.0, 0.1])

    # Create and apply texture
    texture = create_test_texture(512)

    # Create UV coordinates for the box
    # This is a simplified UV mapping
    mesh.visual = trimesh.visual.TextureVisuals(
        material=trimesh.visual.material.PBRMaterial(
            baseColorTexture=texture, baseColorFactor=[1.0, 1.0, 1.0, 1.0], metallicFactor=0.0, roughnessFactor=0.8
        )
    )

    # Export as GLB (can be converted to USDZ later)
    output_path = Path("examples/test_outputs/comfy_reality_test.glb")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    mesh.export(str(output_path))

    print(f"Created test GLB file: {output_path}")
    print("\nTo convert to USDZ on macOS:")
    print(f"xcrun usdz_converter {output_path} {output_path.with_suffix('.usdz')}")

    return output_path


def create_test_usdz_full():
    """Create a full test USDZ with USD bindings."""
    print("Creating full USDZ with USD bindings...")

    output_dir = Path("examples/test_outputs")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create USDA file first (not USDZ directly)
    usda_path = output_dir / "comfy_reality_test.usda"
    output_path = output_dir / "comfy_reality_test.usdz"

    # Create USD stage
    stage = Usd.Stage.CreateNew(str(usda_path))

    # Set up the scene
    UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.y)
    UsdGeom.SetStageMetersPerUnit(stage, 1.0)

    # Create root xform
    root = UsdGeom.Xform.Define(stage, "/Root")

    # Create a card (plane) for the sticker
    card_path = "/Root/ARSticker"
    card = UsdGeom.Mesh.Define(stage, card_path)

    # Set card geometry (a simple quad)
    card.CreatePointsAttr([(-0.5, 0, -0.5), (0.5, 0, -0.5), (0.5, 0, 0.5), (-0.5, 0, 0.5)])
    card.CreateFaceVertexCountsAttr([4])
    card.CreateFaceVertexIndicesAttr([0, 1, 2, 3])
    card.CreateExtentAttr([(-0.5, 0, -0.5), (0.5, 0, 0.5)])

    # Create UV coordinates
    primvarsAPI = UsdGeom.PrimvarsAPI(card)
    texCoords = primvarsAPI.CreatePrimvar("st", Sdf.ValueTypeNames.TexCoord2fArray, UsdGeom.Tokens.vertex)
    texCoords.Set([(0, 1), (1, 1), (1, 0), (0, 0)])

    # Create material
    material_path = "/Root/Materials/StickerMaterial"
    material = UsdShade.Material.Define(stage, material_path)

    # Create shader
    shader_path = f"{material_path}/PBRShader"
    shader = UsdShade.Shader.Define(stage, shader_path)
    shader.CreateIdAttr("UsdPreviewSurface")

    # Set shader parameters
    shader.CreateInput("baseColor", Sdf.ValueTypeNames.Color3f).Set((1.0, 1.0, 1.0))
    shader.CreateInput("metallic", Sdf.ValueTypeNames.Float).Set(0.0)
    shader.CreateInput("roughness", Sdf.ValueTypeNames.Float).Set(0.8)
    shader.CreateInput("opacity", Sdf.ValueTypeNames.Float).Set(1.0)

    # Create texture
    texture = create_test_texture(1024)
    texture_path = output_path.parent / "test_texture.png"
    texture.save(texture_path)

    # Create texture shader
    texture_shader_path = f"{material_path}/Texture"
    texture_shader = UsdShade.Shader.Define(stage, texture_shader_path)
    texture_shader.CreateIdAttr("UsdUVTexture")
    # Use relative path for texture
    texture_shader.CreateInput("file", Sdf.ValueTypeNames.Asset).Set(texture_path.name)
    texture_shader.CreateOutput("rgb", Sdf.ValueTypeNames.Float3)

    # Connect texture to base color
    shader.CreateInput("baseColor", Sdf.ValueTypeNames.Color3f).ConnectToSource(texture_shader.ConnectableAPI(), "rgb")

    # Create material output
    material.CreateSurfaceOutput().ConnectToSource(shader.ConnectableAPI(), "surface")

    # Bind material to mesh
    UsdShade.MaterialBindingAPI(card).Bind(material)

    # Set default transform
    xform_api = UsdGeom.XformCommonAPI(card)
    xform_api.SetTranslate((0, 0, 0))
    xform_api.SetRotate((0, 0, 0))
    xform_api.SetScale((0.2, 0.2, 0.2))

    # Add AR metadata
    card.GetPrim().SetMetadata(
        "customData", {"arAnchorType": "horizontal", "arScale": 0.2, "createdBy": "ComfyReality", "isAROptimized": True}
    )

    # Save the stage
    stage.Save()

    # Package as USDZ (includes textures)
    UsdUtils.CreateNewUsdzPackage(str(usda_path), str(output_path))

    print(f"Created test USDZ file: {output_path}")
    print("\nYou can now:")
    print("1. Open in Reality Composer on macOS")
    print("2. View on iOS device with AR Quick Look")
    print("3. AirDrop to iPhone/iPad to test")

    # Clean up temporary files
    texture_path.unlink()
    usda_path.unlink()

    return output_path


def main():
    """Generate test USDZ file."""
    print("🎨 ComfyReality Test USDZ Generator")
    print("=" * 40)

    if USD_AVAILABLE:
        try:
            output = create_test_usdz_full()
            print("\n✅ Success! Full USDZ created with USD bindings")
        except Exception as e:
            print(f"\n⚠️  USD creation failed: {e}")
            print("Falling back to simple geometry...")
            output = create_test_usdz_simple()
    else:
        output = create_test_usdz_simple()

    print("\n📱 Next steps:")
    print("1. Transfer the file to your Mac/iOS device")
    print("2. Open in Reality Composer to edit")
    print("3. Test in AR Quick Look on iOS")
    print("\n🔧 To generate from ComfyUI workflow:")
    print("   uv run comfy-runtime run examples/ar_sticker_workflow.json")


if __name__ == "__main__":
    main()
