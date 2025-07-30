# ComfyReality Example Workflows

This directory contains example ComfyUI workflows that demonstrate how to create AR content using ComfyReality nodes.

## Available Workflows

### 1. Simple AR Sticker (`simple_workflow.json`)
Basic workflow that creates a flat AR sticker from a generated image.
- **Use case**: Simple 2D stickers for AR
- **Nodes used**: AROptimizer, MaterialComposer, SpatialPositioner, USDZExporter
- **Output**: USDZ file ready for Reality Composer

### 2. AR Sticker - Cute Robot (`ar_sticker_workflow.json`)
Creates a cute robot character as an AR sticker with optimized settings.
- **Use case**: Character stickers with proper materials
- **Features**: Unlit material, alpha cutout, iOS optimization
- **Output**: `cute_robot_sticker.usdz`

### 3. AR Scene - Interactive Mascot (`ar_scene_workflow.json`)
Advanced workflow creating an animated, physics-enabled AR mascot.
- **Use case**: Interactive AR characters
- **Features**: 
  - Floating animation
  - Physics simulation
  - Emissive materials
  - LOD generation
  - People occlusion
- **Output**: `cloud_mascot_interactive.usdz`

### 4. Flux AR Generator (`flux_ar_workflow.json`) 🆕
Complete Flux-based AR content generation with automatic background removal.
- **Use case**: AI-generated AR characters and objects
- **Features**:
  - Flux model integration
  - Automatic background removal
  - Edge detection refinement
  - Physics and animations
  - Multi-LOD generation
- **Output**: `flux_robot_mascot.usdz`

### 5. Flux Simple Sticker (`flux_simple_sticker.json`) 🆕
Minimal Flux workflow for quick AR sticker generation.
- **Use case**: Fast AR sticker creation with Flux Schnell
- **Features**:
  - 4-step generation (fast)
  - Automatic transparency
  - Mobile optimized
- **Output**: `sun_sticker.usdz`

## Quick Start

### 1. Using ComfyUI Web Interface

```bash
# Start ComfyUI
uv run poe comfy-start

# Navigate to http://127.0.0.1:8188
# Load workflow: Load -> Choose file -> Select a .json workflow
# Queue Prompt to execute
```

### 2. Using CLI Runtime

```bash
# Execute with progress tracking
uv run comfy-runtime run examples/ar_sticker_workflow.json

# Execute without UI
uv run comfy-runtime run examples/ar_sticker_workflow.json --no-ui -o results.json
```

### 3. Generate Test USDZ

```bash
# Generate a test USDZ file without running ComfyUI
python examples/test_usdz_generator.py
```

## Workflow Structure

All workflows follow this general pattern:

1. **Image Generation**
   - CheckpointLoaderSimple: Load model
   - CLIPTextEncode: Positive/negative prompts
   - KSampler: Generate image
   - VAEDecode: Decode to image

2. **AR Optimization**
   - AROptimizer: Optimize for mobile AR
   - MaterialComposer: Apply AR-ready materials
   - SpatialPositioner: Set 3D position/scale

3. **Optional Enhancements**
   - AnimationBuilder: Add animations
   - PhysicsIntegrator: Add physics
   - RealityComposer: Multi-object scenes

4. **Export**
   - USDZExporter: Export for iOS
   - CrossPlatformExporter: Universal export

## Customization Tips

### Prompts
Modify the positive prompt in node "2" for different characters:
```json
"text": "your custom prompt here, sticker style, simple design"
```

### Scale
Adjust the scale in SpatialPositioner (node "10"):
```json
"scale": 0.15  // Smaller values = smaller in AR
```

### Materials
Change material type in MaterialComposer (node "9"):
- `"unlit"`: No lighting effects (best for stickers)
- `"standard"`: PBR materials with lighting
- `"metallic"`: Metallic surfaces
- `"emission"`: Glowing effects

### Platform Optimization
In AROptimizer (node "8"):
- `"ios"`: Optimized for Apple devices
- `"android"`: Optimized for Android
- `"universal"`: Works everywhere

## Testing Your USDZ Files

### On macOS
1. Double-click the .usdz file to preview in Quick Look
2. Open in Reality Composer for editing
3. Check materials, scale, and animations

### On iOS
1. AirDrop the .usdz file to your device
2. Tap to view in AR
3. Place on surfaces and interact

### Reality Composer
1. Open Reality Composer
2. File -> Import -> Select your .usdz
3. Add behaviors and interactions
4. Export enhanced version

## Troubleshooting

### Image Not Transparent
- Ensure your prompt includes "white background" or "transparent background"
- Set `alpha_mode: "cutout"` in AROptimizer
- Adjust `alpha_cutoff` in MaterialComposer

### Too Large/Small in AR
- Adjust `scale` in SpatialPositioner
- Typical values: 0.1-0.3 for stickers, 0.5-1.0 for objects

### Materials Look Wrong
- Try different `material_type` settings
- Adjust `roughness` and `metallic` values
- Use `"unlit"` for sticker-like appearance

### Performance Issues
- Reduce `texture_size` in AROptimizer
- Lower `simplification_ratio` for fewer polygons
- Use `optimization_level: "performance"`

## Advanced Workflows

See `ar_scene_workflow.json` for examples of:
- Multiple objects in one scene
- Physics interactions
- Animations (floating, rotating)
- Advanced materials with emission
- People occlusion
- AR coaching overlay

## Model Requirements

### Standard Workflows
- Stable Diffusion XL checkpoint (`sd_xl_base_1.0.safetensors`)
- Or modify node "1" to use your preferred model

### Flux Workflows
- **Flux Dev** (full quality): `flux1-dev-fp8.safetensors`
- **Flux Schnell** (fast 4-step): `flux1-schnell-fp8.safetensors`
- **CLIP Models**: `t5xxl_fp8_e4m3fn.safetensors`, `clip_l.safetensors`
- **VAE**: `ae.safetensors`

Download models:
```bash
# Example for Flux Schnell
uv run comfy --workspace=./comfyui model download \
  --url "https://huggingface.co/black-forest-labs/FLUX.1-schnell/resolve/main/flux1-schnell.safetensors" \
  --path checkpoints

# Or use ComfyUI Manager to install models
```

## New Features

### FluxARGenerator Node
The `FluxARGenerator` node provides:
- Optimized prompts for AR content
- Built-in background removal
- Style presets (sticker, object, character, logo, icon)
- Automatic CFG=1.0 for Flux compatibility

### ARBackgroundRemover Node
Advanced background removal with multiple methods:
- **Threshold**: Simple white/black background removal
- **Chroma Key**: Remove specific colors
- **GrabCut**: AI-based foreground extraction
- **Edge Detection**: Contour-based removal
- **AI Model**: Integration with REMBG models

## Testing

Test the integration without ComfyUI:
```bash
python examples/test_flux_integration.py
```

This creates a test robot USDZ using the node pipeline.