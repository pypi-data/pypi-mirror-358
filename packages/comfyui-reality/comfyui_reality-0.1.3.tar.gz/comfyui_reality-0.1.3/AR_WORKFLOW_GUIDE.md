# ComfyReality AR Workflow Guide

This guide explains how to create AR content using ComfyReality nodes in ComfyUI, with examples that can be opened in Reality Composer.

## Overview

ComfyReality provides specialized nodes for creating AR-ready content:
- Convert 2D images to 3D AR stickers
- Apply AR-optimized materials
- Position objects in 3D space
- Add animations and physics
- Export to USDZ for iOS Reality Composer

## Basic AR Sticker Workflow

### Step 1: Generate or Load Image
Use standard ComfyUI nodes to create your base image:
```
CheckpointLoader → CLIPTextEncode → KSampler → VAEDecode → Image
```

**Tips for AR-friendly images:**
- Use clear, simple designs
- Include "sticker style" in prompts
- White or transparent backgrounds work best
- High contrast edges for clean cutouts

### Step 2: AR Optimization
Pass your image through the AR pipeline:

#### AROptimizer Node
Converts 2D images to AR-ready geometry:
```json
{
  "inputs": {
    "image": ["previous_node", 0],
    "optimization_level": "balanced",  // performance/balanced/quality
    "target_platform": "ios",          // ios/android/universal
    "texture_size": 1024,              // 512/1024/2048
    "alpha_mode": "cutout"             // opaque/blend/cutout
  }
}
```

#### MaterialComposer Node
Applies AR-appropriate materials:
```json
{
  "inputs": {
    "geometry": ["ar_optimizer", 0],
    "material_type": "unlit",          // unlit = no shadows (best for stickers)
    "double_sided": true,              // visible from both sides
    "alpha_cutoff": 0.5                // transparency threshold
  }
}
```

#### SpatialPositioner Node
Sets position and scale in AR space:
```json
{
  "inputs": {
    "ar_object": ["material_composer", 0],
    "scale": 0.15,                     // AR world scale (meters)
    "position_y": 0.0,                 // height above surface
    "anchor_type": "horizontal"        // horizontal/vertical/face
  }
}
```

### Step 3: Export
#### USDZExporter Node
Creates Reality Composer compatible files:
```json
{
  "inputs": {
    "ar_scene": ["spatial_positioner", 0],
    "filename": "my_ar_sticker",
    "optimize_for_ar": true,
    "include_preview": true
  }
}
```

## Advanced Features

### Adding Animation
Use AnimationBuilder for simple animations:
```json
{
  "inputs": {
    "ar_object": ["material_composer", 0],
    "animation_type": "float",         // float/rotate/bounce
    "float_amplitude": 0.05,           // movement range
    "rotation_speed": 10.0,            // degrees per second
    "loop": true
  }
}
```

### Adding Physics
Make objects interactive with PhysicsIntegrator:
```json
{
  "inputs": {
    "ar_object": ["animation_builder", 0],
    "physics_type": "dynamic",         // static/dynamic/kinematic
    "mass": 0.5,
    "restitution": 0.7,               // bounciness
    "enable_gravity": false            // floating objects
  }
}
```

### Multi-Object Scenes
Combine multiple objects with RealityComposer:
```json
{
  "inputs": {
    "ar_objects": [["object1", 0], ["object2", 0]],
    "enable_shadows": true,
    "enable_people_occlusion": true,   // objects behind people
    "ar_coaching": true                // placement hints
  }
}
```

## Platform-Specific Settings

### iOS (Reality Composer)
- Use `target_platform: "ios"`
- Enable `reality_composer: true` in CrossPlatformExporter
- Supports USDZ with animations and physics
- Recommended texture sizes: 1024x1024 or 2048x2048

### Android (ARCore)
- Use `target_platform: "android"`
- Exports to GLB format
- Limited physics support
- ETC2 texture compression

### Universal
- Works on both platforms
- May be larger file size
- Safe default choice

## Best Practices

### 1. Image Preparation
- **Resolution**: Start with 1024x1024 or higher
- **Style**: Simple, cartoon, sticker-like designs work best
- **Background**: Pure white or transparent
- **Content**: Center your subject with padding

### 2. Optimization Settings
- **Stickers**: Use "performance" mode, 512-1024 texture
- **Detailed Objects**: Use "quality" mode, 2048 texture
- **Interactive**: Enable physics with low polygon count

### 3. Scale Guidelines
- **Stickers**: 0.1 - 0.3 scale
- **Tabletop Objects**: 0.3 - 0.5 scale
- **Life-size**: 1.0 - 2.0 scale

### 4. Material Selection
- **Stickers**: Unlit material, no shadows
- **3D Objects**: Standard PBR materials
- **Glowing**: Use emission for magical effects

## Example Workflows

### Simple Sticker
See: `examples/ar_sticker_workflow.json`
- Basic 2D to AR conversion
- Unlit material for sticker look
- Optimized for quick loading

### Interactive Character
See: `examples/ar_scene_workflow.json`
- Animated floating motion
- Physics for tap interactions
- Emissive glow effects

### Multi-Object Scene
Combine multiple workflows:
1. Create individual objects
2. Use RealityComposer node to combine
3. Set relative positions
4. Export as single USDZ

## Testing Your Creations

### Quick Test
```bash
# Generate test USDZ without ComfyUI
python examples/test_usdz_generator.py
```

### In Reality Composer
1. Open Reality Composer on macOS
2. Create new project → Choose anchor
3. Import → Select your USDZ
4. Add behaviors:
   - Tap & Flip
   - Proximity triggers
   - Sound effects
   - Custom animations

### On iOS Device
1. AirDrop USDZ to iPhone/iPad
2. Tap to open in AR Quick Look
3. Place on surface
4. Test interactions

## Troubleshooting

### Common Issues

**Object too large/small**
- Adjust `scale` in SpatialPositioner
- Check your input image resolution

**No transparency**
- Set `alpha_mode: "cutout"` in AROptimizer
- Ensure white/transparent background
- Adjust `alpha_cutoff` threshold

**Black shadows on sticker**
- Use `material_type: "unlit"`
- Disable shadows in RealityComposer

**Crashes on device**
- Reduce texture_size to 512 or 1024
- Use "performance" optimization
- Check file size (<25MB recommended)

**Animation not playing**
- Enable `include_animations: true` in exporter
- Check `loop: true` in AnimationBuilder
- Verify Reality Composer compatibility

### Performance Tips
1. Keep textures under 2048x2048
2. Use LOD (Level of Detail) for complex objects
3. Limit animation complexity
4. Test on target devices early

## Next Steps

1. Start with simple stickers to understand the pipeline
2. Experiment with materials and animations
3. Combine multiple objects into scenes
4. Add interactivity in Reality Composer
5. Share your creations!

For more examples, check the `examples/` directory.