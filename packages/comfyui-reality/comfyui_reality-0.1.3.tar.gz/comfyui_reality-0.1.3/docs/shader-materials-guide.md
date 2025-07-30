# Shader & Materials Guide for USDZ

## Overview

This guide covers creating physically-based rendering (PBR) materials for USDZ files using UsdPreviewSurface shaders. Learn how to create realistic materials, work with textures, and optimize shaders for AR performance on mobile devices.

## UsdPreviewSurface Fundamentals

### Core Material Model

UsdPreviewSurface is the standard shader for USD/USDZ materials. It implements a Disney-inspired PBR model that balances realism with performance for real-time rendering.

**Key Properties:**
- **Diffuse Color**: Base albedo color
- **Metallic**: Controls metallic vs dielectric response  
- **Roughness**: Surface roughness (0=mirror, 1=completely rough)
- **Clearcoat**: Additional clear layer on top
- **Emissive Color**: Self-illumination
- **Normal**: Surface normal perturbation
- **Opacity**: Transparency control
- **Displacement**: Height-based geometry displacement

### Basic Material Creation

```python
from pxr import Usd, UsdShade, Sdf, UsdGeom

def create_basic_pbr_material(stage, material_path="/Materials/BasicPBR"):
    """Create a basic PBR material with UsdPreviewSurface"""
    
    # Create material prim
    material_prim = stage.DefinePrim(material_path, "Material")
    material = UsdShade.Material(material_prim)
    
    # Create the surface shader
    shader_prim = stage.DefinePrim(f"{material_path}/PBRShader", "Shader")
    shader = UsdShade.Shader(shader_prim)
    shader.CreateIdAttr("UsdPreviewSurface")
    
    # Set basic material properties
    shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set((0.8, 0.2, 0.1))
    shader.CreateInput("metallic", Sdf.ValueTypeNames.Float).Set(0.0)
    shader.CreateInput("roughness", Sdf.ValueTypeNames.Float).Set(0.5)
    shader.CreateInput("ior", Sdf.ValueTypeNames.Float).Set(1.5)
    
    # Connect shader to material surface
    surface_output = material.CreateSurfaceOutput()
    shader_surface_output = shader.CreateOutput("surface", Sdf.ValueTypeNames.Token)
    surface_output.ConnectToSource(shader_surface_output)
    
    return material

# Usage
stage = Usd.Stage.CreateNew("material_example.usd")
material = create_basic_pbr_material(stage)
stage.Save()
```

## Texture-Based Materials

### Diffuse (Albedo) Textures

```python
def create_textured_material(stage, material_path, texture_path):
    """Create material with diffuse texture"""
    
    # Material setup
    material_prim = stage.DefinePrim(material_path, "Material")
    material = UsdShade.Material(material_prim)
    
    # PBR Shader
    shader_prim = stage.DefinePrim(f"{material_path}/PBRShader", "Shader")
    shader = UsdShade.Shader(shader_prim)
    shader.CreateIdAttr("UsdPreviewSurface")
    
    # Texture reader for diffuse
    texture_prim = stage.DefinePrim(f"{material_path}/DiffuseTexture", "Shader")
    texture_shader = UsdShade.Shader(texture_prim)
    texture_shader.CreateIdAttr("UsdUVTexture")
    
    # Set texture file
    texture_file_input = texture_shader.CreateInput("file", Sdf.ValueTypeNames.Asset)
    texture_file_input.Set(texture_path)
    
    # Set texture wrapping mode
    texture_shader.CreateInput("wrapS", Sdf.ValueTypeNames.Token).Set("repeat")
    texture_shader.CreateInput("wrapT", Sdf.ValueTypeNames.Token).Set("repeat")
    
    # Connect texture to shader
    texture_output = texture_shader.CreateOutput("rgb", Sdf.ValueTypeNames.Float3)
    diffuse_input = shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f)
    diffuse_input.ConnectToSource(texture_output)
    
    # Set other material properties
    shader.CreateInput("metallic", Sdf.ValueTypeNames.Float).Set(0.0)
    shader.CreateInput("roughness", Sdf.ValueTypeNames.Float).Set(0.7)
    
    # Connect to material
    surface_output = material.CreateSurfaceOutput()
    shader_output = shader.CreateOutput("surface", Sdf.ValueTypeNames.Token)
    surface_output.ConnectToSource(shader_output)
    
    return material
```

### Normal Maps

```python
def add_normal_map(stage, material_path, normal_map_path):
    """Add normal map to existing material"""
    
    material = UsdShade.Material.Get(stage, material_path)
    shader_path = f"{material_path}/PBRShader"
    shader = UsdShade.Shader.Get(stage, shader_path)
    
    # Create normal map texture reader
    normal_texture_prim = stage.DefinePrim(f"{material_path}/NormalTexture", "Shader")
    normal_texture = UsdShade.Shader(normal_texture_prim)
    normal_texture.CreateIdAttr("UsdUVTexture")
    
    # Set normal map file
    normal_file_input = normal_texture.CreateInput("file", Sdf.ValueTypeNames.Asset)
    normal_file_input.Set(normal_map_path)
    
    # Important: Set scale and bias for normal maps
    # Normal maps are typically in [0,1] range but need to be [-1,1]
    normal_texture.CreateInput("scale", Sdf.ValueTypeNames.Float4).Set((2.0, 2.0, 2.0, 1.0))
    normal_texture.CreateInput("bias", Sdf.ValueTypeNames.Float4).Set((-1.0, -1.0, -1.0, 0.0))
    
    # Connect to shader normal input
    normal_output = normal_texture.CreateOutput("rgb", Sdf.ValueTypeNames.Float3)
    normal_input = shader.CreateInput("normal", Sdf.ValueTypeNames.Normal3f)
    normal_input.ConnectToSource(normal_output)
    
    return material

# Advanced normal map with strength control
def create_normal_map_with_strength(stage, material_path, normal_map_path, strength=1.0):
    """Create normal map with adjustable strength"""
    
    # Normal texture
    normal_texture_prim = stage.DefinePrim(f"{material_path}/NormalTexture", "Shader")
    normal_texture = UsdShade.Shader(normal_texture_prim)
    normal_texture.CreateIdAttr("UsdUVTexture")
    normal_texture.CreateInput("file", Sdf.ValueTypeNames.Asset).Set(normal_map_path)
    
    # Transform normal values: (0,1) -> (-1,1) with strength
    # Use UsdTransform2d for this
    transform_prim = stage.DefinePrim(f"{material_path}/NormalTransform", "Shader")
    transform = UsdShade.Shader(transform_prim)
    transform.CreateIdAttr("UsdTransform2d")
    
    # Scale and bias
    scale_factor = 2.0 * strength
    bias_factor = -1.0 * strength
    
    transform.CreateInput("scale", Sdf.ValueTypeNames.Float2).Set((scale_factor, scale_factor))
    transform.CreateInput("translation", Sdf.ValueTypeNames.Float2).Set((bias_factor, bias_factor))
    
    # Connect chain: texture -> transform -> shader
    texture_output = normal_texture.CreateOutput("rgb", Sdf.ValueTypeNames.Float3)
    transform_input = transform.CreateInput("in", Sdf.ValueTypeNames.Float3)
    transform_input.ConnectToSource(texture_output)
    
    # Get shader and connect
    shader = UsdShade.Shader.Get(stage, f"{material_path}/PBRShader")
    transform_output = transform.CreateOutput("result", Sdf.ValueTypeNames.Float3)
    normal_input = shader.CreateInput("normal", Sdf.ValueTypeNames.Normal3f)
    normal_input.ConnectToSource(transform_output)
```

### Metallic-Roughness Workflow

```python
def create_metallic_roughness_material(stage, material_path, 
                                     diffuse_map=None, normal_map=None,
                                     metallic_map=None, roughness_map=None,
                                     ao_map=None):
    """Create complete PBR material with metallic-roughness workflow"""
    
    # Base material and shader
    material_prim = stage.DefinePrim(material_path, "Material")
    material = UsdShade.Material(material_prim)
    
    shader_prim = stage.DefinePrim(f"{material_path}/PBRShader", "Shader")
    shader = UsdShade.Shader(shader_prim)
    shader.CreateIdAttr("UsdPreviewSurface")
    
    # Diffuse texture
    if diffuse_map:
        diffuse_tex = create_texture_reader(stage, f"{material_path}/DiffuseTexture", diffuse_map)
        diffuse_output = diffuse_tex.CreateOutput("rgb", Sdf.ValueTypeNames.Float3)
        shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).ConnectToSource(diffuse_output)
        
        # Also use alpha channel for opacity if available
        alpha_output = diffuse_tex.CreateOutput("a", Sdf.ValueTypeNames.Float)
        shader.CreateInput("opacity", Sdf.ValueTypeNames.Float).ConnectToSource(alpha_output)
    
    # Normal map
    if normal_map:
        normal_tex = create_texture_reader(stage, f"{material_path}/NormalTexture", normal_map)
        # Transform to correct range
        normal_tex.CreateInput("scale", Sdf.ValueTypeNames.Float4).Set((2.0, 2.0, 2.0, 1.0))
        normal_tex.CreateInput("bias", Sdf.ValueTypeNames.Float4).Set((-1.0, -1.0, -1.0, 0.0))
        
        normal_output = normal_tex.CreateOutput("rgb", Sdf.ValueTypeNames.Float3)
        shader.CreateInput("normal", Sdf.ValueTypeNames.Normal3f).ConnectToSource(normal_output)
    
    # Metallic map (typically uses blue channel)
    if metallic_map:
        metallic_tex = create_texture_reader(stage, f"{material_path}/MetallicTexture", metallic_map)
        metallic_output = metallic_tex.CreateOutput("b", Sdf.ValueTypeNames.Float)  # Blue channel
        shader.CreateInput("metallic", Sdf.ValueTypeNames.Float).ConnectToSource(metallic_output)
    else:
        shader.CreateInput("metallic", Sdf.ValueTypeNames.Float).Set(0.0)
    
    # Roughness map (typically uses green channel)
    if roughness_map:
        roughness_tex = create_texture_reader(stage, f"{material_path}/RoughnessTexture", roughness_map)
        roughness_output = roughness_tex.CreateOutput("g", Sdf.ValueTypeNames.Float)  # Green channel
        shader.CreateInput("roughness", Sdf.ValueTypeNames.Float).ConnectToSource(roughness_output)
    else:
        shader.CreateInput("roughness", Sdf.ValueTypeNames.Float).Set(0.5)
    
    # Ambient occlusion (multiply with diffuse color)
    if ao_map:
        ao_tex = create_texture_reader(stage, f"{material_path}/AOTexture", ao_map)
        
        # Create multiply node to combine AO with diffuse
        multiply_prim = stage.DefinePrim(f"{material_path}/AOMultiply", "Shader")
        multiply_shader = UsdShade.Shader(multiply_prim)
        multiply_shader.CreateIdAttr("UsdMultiply")
        
        # Connect AO and diffuse to multiply
        ao_output = ao_tex.CreateOutput("rgb", Sdf.ValueTypeNames.Float3)
        diffuse_output = diffuse_tex.CreateOutput("rgb", Sdf.ValueTypeNames.Float3)
        
        multiply_input1 = multiply_shader.CreateInput("in1", Sdf.ValueTypeNames.Float3)
        multiply_input2 = multiply_shader.CreateInput("in2", Sdf.ValueTypeNames.Float3)
        
        multiply_input1.ConnectToSource(diffuse_output)
        multiply_input2.ConnectToSource(ao_output)
        
        # Connect result to shader
        multiply_output = multiply_shader.CreateOutput("result", Sdf.ValueTypeNames.Float3)
        shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).ConnectToSource(multiply_output)
    
    # Set default values
    shader.CreateInput("ior", Sdf.ValueTypeNames.Float).Set(1.5)
    shader.CreateInput("useSpecularWorkflow", Sdf.ValueTypeNames.Int).Set(0)  # Use metallic workflow
    
    # Connect to material
    surface_output = material.CreateSurfaceOutput()
    shader_output = shader.CreateOutput("surface", Sdf.ValueTypeNames.Token)
    surface_output.ConnectToSource(shader_output)
    
    return material

def create_texture_reader(stage, texture_path, file_path):
    """Helper function to create texture reader shader"""
    
    texture_prim = stage.DefinePrim(texture_path, "Shader")
    texture_shader = UsdShade.Shader(texture_prim)
    texture_shader.CreateIdAttr("UsdUVTexture")
    
    # Set file path
    texture_shader.CreateInput("file", Sdf.ValueTypeNames.Asset).Set(file_path)
    
    # Set wrapping (clamp for AR to avoid tiling artifacts)
    texture_shader.CreateInput("wrapS", Sdf.ValueTypeNames.Token).Set("clamp")
    texture_shader.CreateInput("wrapT", Sdf.ValueTypeNames.Token).Set("clamp")
    
    return texture_shader
```

## Advanced Material Types

### Glass and Transparent Materials

```python
def create_glass_material(stage, material_path="/Materials/Glass", 
                         ior=1.5, roughness=0.0, color=(1.0, 1.0, 1.0)):
    """Create realistic glass material"""
    
    material_prim = stage.DefinePrim(material_path, "Material")
    material = UsdShade.Material(material_prim)
    
    shader_prim = stage.DefinePrim(f"{material_path}/GlassShader", "Shader")
    shader = UsdShade.Shader(shader_prim)
    shader.CreateIdAttr("UsdPreviewSurface")
    
    # Glass properties
    shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set(color)
    shader.CreateInput("metallic", Sdf.ValueTypeNames.Float).Set(0.0)
    shader.CreateInput("roughness", Sdf.ValueTypeNames.Float).Set(roughness)
    shader.CreateInput("clearcoat", Sdf.ValueTypeNames.Float).Set(1.0)
    shader.CreateInput("clearcoatRoughness", Sdf.ValueTypeNames.Float).Set(0.0)
    shader.CreateInput("ior", Sdf.ValueTypeNames.Float).Set(ior)
    shader.CreateInput("opacity", Sdf.ValueTypeNames.Float).Set(0.1)  # Very transparent
    shader.CreateInput("opacityThreshold", Sdf.ValueTypeNames.Float).Set(0.0)  # Enable transparency
    
    # Connect to material
    surface_output = material.CreateSurfaceOutput()
    shader_output = shader.CreateOutput("surface", Sdf.ValueTypeNames.Token)
    surface_output.ConnectToSource(shader_output)
    
    return material

# Frosted glass variation
def create_frosted_glass_material(stage, material_path, frost_amount=0.3):
    """Create frosted glass with controlled roughness"""
    
    return create_glass_material(
        stage, material_path, 
        ior=1.5, 
        roughness=frost_amount,
        color=(0.95, 0.95, 1.0)  # Slight blue tint
    )
```

### Emissive Materials

```python
def create_emissive_material(stage, material_path, emissive_color=(1.0, 1.0, 1.0), 
                           emissive_strength=1.0, base_color=(0.1, 0.1, 0.1)):
    """Create self-illuminating emissive material"""
    
    material_prim = stage.DefinePrim(material_path, "Material")
    material = UsdShade.Material(material_prim)
    
    shader_prim = stage.DefinePrim(f"{material_path}/EmissiveShader", "Shader")
    shader = UsdShade.Shader(shader_prim)
    shader.CreateIdAttr("UsdPreviewSurface")
    
    # Base material (should be dark for emissive effect)
    shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set(base_color)
    shader.CreateInput("metallic", Sdf.ValueTypeNames.Float).Set(0.0)
    shader.CreateInput("roughness", Sdf.ValueTypeNames.Float).Set(1.0)
    
    # Emissive properties
    emissive_final = [c * emissive_strength for c in emissive_color]
    shader.CreateInput("emissiveColor", Sdf.ValueTypeNames.Color3f).Set(emissive_final)
    
    # Connect to material
    surface_output = material.CreateSurfaceOutput()
    shader_output = shader.CreateOutput("surface", Sdf.ValueTypeNames.Token)
    surface_output.ConnectToSource(shader_output)
    
    return material

def create_neon_sign_material(stage, material_path, glow_color=(0.0, 1.0, 1.0)):
    """Create neon sign style material"""
    
    return create_emissive_material(
        stage, material_path,
        emissive_color=glow_color,
        emissive_strength=5.0,
        base_color=(0.02, 0.02, 0.02)
    )
```

### Fabric and Organic Materials

```python
def create_fabric_material(stage, material_path, fabric_color=(0.6, 0.4, 0.2)):
    """Create realistic fabric material"""
    
    material_prim = stage.DefinePrim(material_path, "Material")
    material = UsdShade.Material(material_prim)
    
    shader_prim = stage.DefinePrim(f"{material_path}/FabricShader", "Shader")
    shader = UsdShade.Shader(shader_prim)
    shader.CreateIdAttr("UsdPreviewSurface")
    
    # Fabric characteristics
    shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set(fabric_color)
    shader.CreateInput("metallic", Sdf.ValueTypeNames.Float).Set(0.0)
    shader.CreateInput("roughness", Sdf.ValueTypeNames.Float).Set(0.9)  # Very rough
    shader.CreateInput("ior", Sdf.ValueTypeNames.Float).Set(1.3)  # Lower than glass
    
    # Subsurface scattering approximation using clearcoat
    shader.CreateInput("clearcoat", Sdf.ValueTypeNames.Float).Set(0.1)
    shader.CreateInput("clearcoatRoughness", Sdf.ValueTypeNames.Float).Set(0.8)
    
    # Connect to material
    surface_output = material.CreateSurfaceOutput()
    shader_output = shader.CreateOutput("surface", Sdf.ValueTypeNames.Token)
    surface_output.ConnectToSource(shader_output)
    
    return material

def create_skin_material(stage, material_path, skin_tone=(0.9, 0.7, 0.6)):
    """Create basic skin material with subsurface approximation"""
    
    material_prim = stage.DefinePrim(material_path, "Material")
    material = UsdShade.Material(material_prim)
    
    shader_prim = stage.DefinePrim(f"{material_path}/SkinShader", "Shader")
    shader = UsdShade.Shader(shader_prim)
    shader.CreateIdAttr("UsdPreviewSurface")
    
    # Skin properties
    shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set(skin_tone)
    shader.CreateInput("metallic", Sdf.ValueTypeNames.Float).Set(0.0)
    shader.CreateInput("roughness", Sdf.ValueTypeNames.Float).Set(0.4)
    shader.CreateInput("ior", Sdf.ValueTypeNames.Float).Set(1.4)
    
    # Simulate subsurface scattering with clearcoat
    shader.CreateInput("clearcoat", Sdf.ValueTypeNames.Float).Set(0.3)
    shader.CreateInput("clearcoatRoughness", Sdf.ValueTypeNames.Float).Set(0.6)
    
    # Slight self-illumination for realistic skin
    subsurface_color = [c * 0.1 for c in skin_tone]  # 10% of base color
    shader.CreateInput("emissiveColor", Sdf.ValueTypeNames.Color3f).Set(subsurface_color)
    
    # Connect to material
    surface_output = material.CreateSurfaceOutput()
    shader_output = shader.CreateOutput("surface", Sdf.ValueTypeNames.Token)
    surface_output.ConnectToSource(shader_output)
    
    return material
```

## AR-Optimized Materials

### Mobile Performance Guidelines

```python
class ARMaterialOptimizer:
    """Utility class for optimizing materials for AR performance"""
    
    @staticmethod
    def optimize_material_for_ar(stage, material_path):
        """Optimize existing material for AR performance"""
        
        material = UsdShade.Material.Get(stage, material_path)
        if not material:
            return False
        
        # Get shader
        surface_output = material.GetSurfaceOutput()
        if not surface_output.HasConnectedSource():
            return False
        
        source_info = surface_output.GetConnectedSource()[0]
        shader = UsdShade.Shader(source_info.GetPrim())
        
        # AR optimization rules
        ARMaterialOptimizer._limit_texture_complexity(shader)
        ARMaterialOptimizer._optimize_for_mobile_gpu(shader)
        ARMaterialOptimizer._ensure_ar_compatibility(shader)
        
        return True
    
    @staticmethod
    def _limit_texture_complexity(shader):
        """Limit texture complexity for mobile performance"""
        
        # Disable expensive features for AR
        if shader.GetInput("displacement"):
            # Remove displacement - not supported in many AR viewers
            shader.GetInput("displacement").SetConnectedSources([])
        
        # Ensure reasonable roughness values (avoid extreme values)
        roughness_input = shader.GetInput("roughness")
        if roughness_input and not roughness_input.HasConnectedSource():
            current_value = roughness_input.Get()
            if current_value is not None:
                # Clamp to reasonable range
                clamped_value = max(0.1, min(0.9, current_value))
                roughness_input.Set(clamped_value)
    
    @staticmethod
    def _optimize_for_mobile_gpu(shader):
        """Optimize shader for mobile GPU performance"""
        
        # Disable clearcoat for basic AR (performance impact)
        clearcoat_input = shader.GetInput("clearcoat")
        if clearcoat_input:
            clearcoat_input.Set(0.0)
        
        # Limit metallic extremes
        metallic_input = shader.GetInput("metallic")
        if metallic_input and not metallic_input.HasConnectedSource():
            current_value = metallic_input.Get()
            if current_value is not None and current_value > 0.8:
                metallic_input.Set(0.8)  # Limit high metallic values
    
    @staticmethod
    def _ensure_ar_compatibility(shader):
        """Ensure AR viewer compatibility"""
        
        # Set opacity threshold for AR transparency
        opacity_input = shader.GetInput("opacity")
        if opacity_input:
            threshold_input = shader.GetInput("opacityThreshold")
            if not threshold_input:
                threshold_input = shader.CreateInput("opacityThreshold", Sdf.ValueTypeNames.Float)
            threshold_input.Set(0.01)  # Enable transparency in AR
        
        # Ensure IOR is in reasonable range
        ior_input = shader.GetInput("ior")
        if ior_input and not ior_input.HasConnectedSource():
            current_value = ior_input.Get()
            if current_value is None or current_value < 1.0:
                ior_input.Set(1.5)  # Default glass IOR

# AR-specific material presets
def create_ar_sticker_material(stage, material_path, texture_path):
    """Create optimized material specifically for AR stickers"""
    
    material_prim = stage.DefinePrim(material_path, "Material")
    material = UsdShade.Material(material_prim)
    
    shader_prim = stage.DefinePrim(f"{material_path}/ARStickerShader", "Shader")
    shader = UsdShade.Shader(shader_prim)
    shader.CreateIdAttr("UsdPreviewSurface")
    
    # Texture
    if texture_path:
        texture_shader = create_texture_reader(stage, f"{material_path}/Texture", texture_path)
        
        # RGB for diffuse
        rgb_output = texture_shader.CreateOutput("rgb", Sdf.ValueTypeNames.Float3)
        shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).ConnectToSource(rgb_output)
        
        # Alpha for transparency (crucial for stickers)
        alpha_output = texture_shader.CreateOutput("a", Sdf.ValueTypeNames.Float)
        shader.CreateInput("opacity", Sdf.ValueTypeNames.Float).ConnectToSource(alpha_output)
    
    # AR-optimized settings
    shader.CreateInput("metallic", Sdf.ValueTypeNames.Float).Set(0.0)  # Non-metallic for stickers
    shader.CreateInput("roughness", Sdf.ValueTypeNames.Float).Set(0.8)  # Slightly rough for realism
    shader.CreateInput("ior", Sdf.ValueTypeNames.Float).Set(1.5)
    shader.CreateInput("opacityThreshold", Sdf.ValueTypeNames.Float).Set(0.01)  # Enable transparency
    shader.CreateInput("useSpecularWorkflow", Sdf.ValueTypeNames.Int).Set(0)  # Use metallic workflow
    
    # Connect to material
    surface_output = material.CreateSurfaceOutput()
    shader_output = shader.CreateOutput("surface", Sdf.ValueTypeNames.Token)
    surface_output.ConnectToSource(shader_output)
    
    return material
```

## Material Animation

### Time-Varying Properties

```python
def create_animated_material(stage, material_path, animation_duration=4.0):
    """Create material with animated properties"""
    
    material = create_basic_pbr_material(stage, material_path)
    shader = UsdShade.Shader.Get(stage, f"{material_path}/PBRShader")
    
    # Set up time code range
    stage.SetStartTimeCode(1.0)
    stage.SetEndTimeCode(24.0 * animation_duration)  # 24 fps
    
    # Animate roughness
    roughness_input = shader.GetInput("roughness")
    roughness_input.Set(0.0, 1.0)                    # Smooth at start
    roughness_input.Set(1.0, 24.0 * animation_duration)  # Rough at end
    
    # Animate color
    color_input = shader.GetInput("diffuseColor")
    color_input.Set((1.0, 0.0, 0.0), 1.0)           # Red at start
    color_input.Set((0.0, 0.0, 1.0), 24.0 * animation_duration)  # Blue at end
    
    return material

def create_pulsing_emissive_material(stage, material_path, pulse_frequency=2.0):
    """Create material with pulsing emissive animation"""
    
    import math
    
    material = create_emissive_material(stage, material_path)
    shader = UsdShade.Shader.Get(stage, f"{material_path}/EmissiveShader")
    
    # Set up animation
    duration = 4.0
    fps = 24
    total_frames = int(duration * fps)
    
    stage.SetStartTimeCode(1.0)
    stage.SetEndTimeCode(total_frames)
    
    # Animate emissive strength with sine wave
    emissive_input = shader.GetInput("emissiveColor")
    base_color = (0.0, 1.0, 1.0)  # Cyan
    
    for frame in range(1, total_frames + 1):
        time = (frame - 1) / fps
        intensity = 0.5 + 0.5 * math.sin(2 * math.pi * pulse_frequency * time)
        
        animated_color = [c * intensity * 3.0 for c in base_color]  # Scale up for visibility
        emissive_input.Set(animated_color, float(frame))
    
    return material
```

## Validation and Testing

### Material Validation

```python
def validate_material_for_ar(stage, material_path):
    """Validate material for AR compatibility"""
    
    issues = []
    material = UsdShade.Material.Get(stage, material_path)
    
    if not material:
        return ["Material not found"]
    
    # Check for surface shader
    surface_output = material.GetSurfaceOutput()
    if not surface_output.HasConnectedSource():
        issues.append("No surface shader connected")
        return issues
    
    # Get shader
    source_info = surface_output.GetConnectedSource()[0]
    shader = UsdShade.Shader(source_info.GetPrim())
    
    # Check shader type
    shader_id = shader.GetIdAttr().Get()
    if shader_id != "UsdPreviewSurface":
        issues.append(f"Non-standard shader: {shader_id}. Use UsdPreviewSurface for best compatibility.")
    
    # Check texture resolutions
    texture_issues = _validate_textures(shader)
    issues.extend(texture_issues)
    
    # Check material properties
    property_issues = _validate_material_properties(shader)
    issues.extend(property_issues)
    
    return issues

def _validate_textures(shader):
    """Validate texture properties"""
    
    issues = []
    
    # Check all texture inputs
    texture_inputs = ["diffuseColor", "normal", "roughness", "metallic", "emissiveColor"]
    
    for input_name in texture_inputs:
        input_attr = shader.GetInput(input_name)
        if input_attr and input_attr.HasConnectedSource():
            source_info = input_attr.GetConnectedSource()[0]
            texture_shader = UsdShade.Shader(source_info.GetPrim())
            
            if texture_shader.GetIdAttr().Get() == "UsdUVTexture":
                file_input = texture_shader.GetInput("file")
                if file_input:
                    file_path = file_input.Get()
                    if file_path:
                        # Check if file exists and validate resolution
                        texture_issues = _check_texture_file(str(file_path))
                        issues.extend(texture_issues)
    
    return issues

def _check_texture_file(file_path):
    """Check individual texture file"""
    
    issues = []
    
    try:
        from PIL import Image
        import os
        
        if not os.path.exists(file_path):
            issues.append(f"Texture file not found: {file_path}")
            return issues
        
        with Image.open(file_path) as img:
            width, height = img.size
            
            # Check if power of 2
            if not (width & (width - 1) == 0) or not (height & (height - 1) == 0):
                issues.append(f"Texture {file_path} is not power-of-2: {width}x{height}")
            
            # Check maximum size for AR
            max_size = 2048
            if width > max_size or height > max_size:
                issues.append(f"Texture {file_path} too large for AR: {width}x{height} (max: {max_size})")
            
            # Check format
            if img.format not in ['PNG', 'JPEG', 'JPG']:
                issues.append(f"Texture {file_path} format {img.format} may not be supported")
    
    except Exception as e:
        issues.append(f"Error checking texture {file_path}: {str(e)}")
    
    return issues

def _validate_material_properties(shader):
    """Validate material property values"""
    
    issues = []
    
    # Check roughness range
    roughness_input = shader.GetInput("roughness")
    if roughness_input and not roughness_input.HasConnectedSource():
        roughness_value = roughness_input.Get()
        if roughness_value is not None:
            if roughness_value < 0.0 or roughness_value > 1.0:
                issues.append(f"Roughness value {roughness_value} outside valid range [0,1]")
    
    # Check metallic range
    metallic_input = shader.GetInput("metallic")
    if metallic_input and not metallic_input.HasConnectedSource():
        metallic_value = metallic_input.Get()
        if metallic_value is not None:
            if metallic_value < 0.0 or metallic_value > 1.0:
                issues.append(f"Metallic value {metallic_value} outside valid range [0,1]")
    
    # Check IOR value
    ior_input = shader.GetInput("ior")
    if ior_input and not ior_input.HasConnectedSource():
        ior_value = ior_input.Get()
        if ior_value is not None:
            if ior_value < 1.0:
                issues.append(f"IOR value {ior_value} is less than 1.0 (physically invalid)")
            elif ior_value > 3.0:
                issues.append(f"IOR value {ior_value} is very high (may cause rendering issues)")
    
    return issues
```

## Material Library and Presets

### Common Material Presets

```python
class MaterialLibrary:
    """Library of common material presets for AR applications"""
    
    @staticmethod
    def create_plastic(stage, material_path, color=(0.8, 0.2, 0.1)):
        """Create plastic material"""
        material = create_basic_pbr_material(stage, material_path)
        shader = UsdShade.Shader.Get(stage, f"{material_path}/PBRShader")
        
        shader.GetInput("diffuseColor").Set(color)
        shader.GetInput("metallic").Set(0.0)
        shader.GetInput("roughness").Set(0.3)
        shader.GetInput("ior").Set(1.45)
        
        return material
    
    @staticmethod
    def create_rubber(stage, material_path, color=(0.1, 0.1, 0.1)):
        """Create rubber material"""
        material = create_basic_pbr_material(stage, material_path)
        shader = UsdShade.Shader.Get(stage, f"{material_path}/PBRShader")
        
        shader.GetInput("diffuseColor").Set(color)
        shader.GetInput("metallic").Set(0.0)
        shader.GetInput("roughness").Set(0.9)
        shader.GetInput("ior").Set(1.4)
        
        return material
    
    @staticmethod
    def create_metal(stage, material_path, metal_type="aluminum"):
        """Create metal material with different types"""
        
        metal_properties = {
            "aluminum": {"color": (0.91, 0.92, 0.92), "roughness": 0.1},
            "gold": {"color": (1.0, 0.84, 0.0), "roughness": 0.05},
            "copper": {"color": (0.95, 0.64, 0.54), "roughness": 0.15},
            "iron": {"color": (0.56, 0.57, 0.58), "roughness": 0.2},
            "chrome": {"color": (0.55, 0.56, 0.59), "roughness": 0.02}
        }
        
        props = metal_properties.get(metal_type, metal_properties["aluminum"])
        
        material = create_basic_pbr_material(stage, material_path)
        shader = UsdShade.Shader.Get(stage, f"{material_path}/PBRShader")
        
        shader.GetInput("diffuseColor").Set(props["color"])
        shader.GetInput("metallic").Set(1.0)
        shader.GetInput("roughness").Set(props["roughness"])
        shader.GetInput("ior").Set(1.5)
        
        return material
    
    @staticmethod
    def create_wood(stage, material_path, wood_color=(0.6, 0.4, 0.2)):
        """Create wood material"""
        material = create_basic_pbr_material(stage, material_path)
        shader = UsdShade.Shader.Get(stage, f"{material_path}/PBRShader")
        
        shader.GetInput("diffuseColor").Set(wood_color)
        shader.GetInput("metallic").Set(0.0)
        shader.GetInput("roughness").Set(0.7)
        shader.GetInput("ior").Set(1.35)
        
        return material
    
    @staticmethod
    def create_ceramic(stage, material_path, color=(0.9, 0.9, 0.85)):
        """Create ceramic material"""
        material = create_basic_pbr_material(stage, material_path)
        shader = UsdShade.Shader.Get(stage, f"{material_path}/PBRShader")
        
        shader.GetInput("diffuseColor").Set(color)
        shader.GetInput("metallic").Set(0.0)
        shader.GetInput("roughness").Set(0.2)
        shader.GetInput("ior").Set(1.5)
        
        # Add slight clearcoat for ceramic shine
        shader.CreateInput("clearcoat", Sdf.ValueTypeNames.Float).Set(0.3)
        shader.CreateInput("clearcoatRoughness", Sdf.ValueTypeNames.Float).Set(0.1)
        
        return material
```

## Resources and Best Practices

### Performance Guidelines

1. **Texture Optimization:**
   - Use power-of-2 dimensions (512, 1024, 2048)
   - Limit maximum resolution to 2048×2048 for AR
   - Prefer PNG for textures with transparency
   - Use JPEG for opaque textures to save space

2. **Material Complexity:**
   - Limit to 5-10 unique materials per scene
   - Avoid complex shader networks on mobile
   - Use texture atlasing when possible
   - Minimize transparent materials (performance impact)

3. **AR-Specific Considerations:**
   - Test materials in actual AR environment
   - Consider lighting conditions in AR
   - Use appropriate roughness values (avoid extremes)
   - Ensure transparency works correctly

### Common Issues and Solutions

1. **Textures Not Displaying:**
   - Check file paths are relative to USD file
   - Verify texture format compatibility
   - Ensure UV coordinates are properly set

2. **Materials Too Dark/Bright:**
   - Adjust diffuse color values
   - Check emissive color settings
   - Verify normal map scaling

3. **Transparency Issues:**
   - Set opacityThreshold to enable transparency
   - Use RGBA textures for alpha channel
   - Test on actual AR devices

### Documentation References

- **UsdPreviewSurface Specification:** https://openusd.org/release/spec_usdpreviewsurface.html
- **USD Shading:** https://openusd.org/release/api/usd_shade_page_front.html
- **Material Best Practices:** https://openusd.org/release/tut_simple_shading.html

## Next Steps

1. **Mobile Optimization Guide** - Performance tuning for AR devices
2. **Advanced AR Features Guide** - Animations, physics, and interactions
3. **Distribution Guide** - Web deployment and sharing strategies
4. **Cross-Platform Compatibility** - Android ARCore and WebXR support
