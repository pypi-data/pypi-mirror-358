# USDZ Technical Format Guide

## Overview

USDZ (Universal Scene Description Zip) is Apple's AR-focused 3D file format built on Pixar's USD (Universal Scene Description). This guide covers the technical specifications and implementation details for creating production-ready USDZ files for AR experiences.

## Technical Specifications

### Core Architecture

**USDZ Package Structure:**
- Uncompressed ZIP archive (no encryption)
- 64-byte alignment for all files (performance optimization)
- Default Layer must be first USD file in package
- Memory-mapped access for zero-copy performance

**File Size Limits:**
- iOS Quick Look: ~25MB practical limit
- Texture Resolution: 2048×2048px maximum recommended
- Geometry: <50K vertices for mobile performance

### Supported File Types

**Required:**
- `.usd`, `.usda`, `.usdc` - Scene description files
- `.png`, `.jpg`, `.jpeg` - Textures (prefer PNG for transparency)

**Optional:**
- `.m4a`, `.mp3`, `.wav` - Audio files
- `.exr` - High dynamic range textures
- `.avif` - Modern image format (iOS 16+)

### Geometry Requirements

**Coordinate System:**
```python
# Y-up right-handed coordinate system (ARKit standard)
points = [
    (-scale, 0, -scale * aspect_ratio),  # Bottom-left
    (scale, 0, -scale * aspect_ratio),   # Bottom-right  
    (scale, 0, scale * aspect_ratio),    # Top-right
    (-scale, 0, scale * aspect_ratio),   # Top-left
]
```

**Mesh Optimization:**
- Triangulated geometry preferred
- UV coordinates required for textures
- Normals must be properly oriented
- Close manifold geometry for best results

## USD Python Implementation

### Essential Imports

```python
from pxr import Usd, UsdGeom, Sdf, UsdShade, Gf
import tempfile
import os
```

### Basic USDZ Creation

```python
def create_basic_usdz(output_path, texture_path, scale=0.1):
    """Create minimal USDZ with textured quad"""
    
    # Create USD stage
    stage = Usd.Stage.CreateNew(output_path)
    
    # Set time range
    stage.SetStartTimeCode(1)
    stage.SetEndTimeCode(1)
    
    # Root prim with AR metadata
    root_prim = stage.DefinePrimitive("/Root", "Xform")
    stage.SetDefaultPrim(root_prim)
    
    # AR Quick Look metadata
    root_prim.SetMetadata("customData", {
        "arQuickLookCompatible": True,
        "realWorldScale": scale
    })
    
    # Mesh geometry
    mesh_prim = stage.DefinePrim("/Root/Mesh", "Mesh")
    mesh = UsdGeom.Mesh(mesh_prim)
    
    # Quad vertices (Y-up)
    points = [
        (-scale, 0, -scale), (scale, 0, -scale),
        (scale, 0, scale), (-scale, 0, scale)
    ]
    mesh.CreatePointsAttr(points)
    mesh.CreateFaceVertexCountsAttr([4])
    mesh.CreateFaceVertexIndicesAttr([0, 1, 2, 3])
    
    # UV coordinates
    texCoords = [(0, 0), (1, 0), (1, 1), (0, 1)]
    texCoordsPrimvar = UsdGeom.PrimvarsAPI(mesh_prim).CreatePrimvar(
        "st", Sdf.ValueTypeNames.TexCoord2fArray, UsdGeom.Tokens.vertex
    )
    texCoordsPrimvar.Set(texCoords)
    
    # Save stage
    stage.GetRootLayer().Save()
    return True
```

### Material System

```python
def create_pbr_material(stage, material_path, texture_path):
    """Create PBR material with texture"""
    
    # Material prim
    material_prim = stage.DefinePrim(material_path, "Material")
    material = UsdShade.Material(material_prim)
    
    # Surface shader
    shader_prim = stage.DefinePrim(f"{material_path}/Shader", "Shader")
    shader = UsdShade.Shader(shader_prim)
    shader.CreateIdAttr("UsdPreviewSurface")
    
    # Texture reader
    tex_reader_prim = stage.DefinePrim(f"{material_path}/TextureReader", "Shader")
    tex_reader = UsdShade.Shader(tex_reader_prim)
    tex_reader.CreateIdAttr("UsdUVTexture")
    
    # Set texture file
    tex_file_input = tex_reader.CreateInput("file", Sdf.ValueTypeNames.Asset)
    tex_file_input.Set(texture_path)
    
    # Connect texture to diffuse
    tex_output = tex_reader.CreateOutput("rgb", Sdf.ValueTypeNames.Float3)
    diffuse_input = shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f)
    diffuse_input.ConnectToSource(tex_output)
    
    # Material properties
    shader.CreateInput("roughness", Sdf.ValueTypeNames.Float).Set(0.5)
    shader.CreateInput("metallic", Sdf.ValueTypeNames.Float).Set(0.0)
    
    # Connect shader to material
    surface_output = material.CreateSurfaceOutput()
    shader_output = shader.CreateOutput("surface", Sdf.ValueTypeNames.Token)
    surface_output.ConnectToSource(shader_output)
    
    return material
```

## AR Optimization Guidelines

### Performance Targets

**Mobile GPU Limits:**
- Vertex Count: <10K for complex scenes, <50K maximum  
- Texture Memory: <50MB total
- Draw Calls: <20 per frame
- Material Count: <10 unique materials

### Memory-Efficient Textures

```python
def optimize_texture_for_ar(image_path, max_size=1024):
    """Optimize texture for mobile AR performance"""
    from PIL import Image
    
    img = Image.open(image_path)
    
    # Convert to RGBA for transparency support
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    # Resize to power-of-2 dimensions
    width, height = img.size
    new_width = min(max_size, 2 ** (width - 1).bit_length())
    new_height = min(max_size, 2 ** (height - 1).bit_length())
    
    if (new_width, new_height) != (width, height):
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    return img
```

### Geometry Simplification

```python
def create_optimized_quad(scale, aspect_ratio, ar_behavior="billboard"):
    """Create AR-optimized quad geometry"""
    
    if ar_behavior == "billboard":
        # Billboard: Always faces camera (Y-up plane)
        points = [
            (-scale, 0, -scale * aspect_ratio),
            (scale, 0, -scale * aspect_ratio),
            (scale, 0, scale * aspect_ratio),
            (-scale, 0, scale * aspect_ratio)
        ]
        normals = [(0, 1, 0)] * 4  # Y-up normal
        
    else:  # "fixed"
        # Fixed: Maintains orientation (Z-up plane)
        points = [
            (-scale, -scale * aspect_ratio, 0),
            (scale, -scale * aspect_ratio, 0),
            (scale, scale * aspect_ratio, 0),
            (-scale, scale * aspect_ratio, 0)
        ]
        normals = [(0, 0, 1)] * 4  # Z-forward normal
    
    return points, normals
```

## AR Metadata and Behaviors

### Quick Look Metadata

```python
def add_ar_metadata(root_prim, scale, behavior="billboard"):
    """Add AR Quick Look compatible metadata"""
    
    metadata = {
        "arQuickLookCompatible": True,
        "realWorldScale": scale,
        "behavior": behavior,
        # iOS-specific behaviors
        "allowsInteraction": True,
        "initialViewingMode": "ar"
    }
    
    if behavior == "physics":
        metadata.update({
            "hasPhysics": True,
            "physicsBody": "dynamic"
        })
    
    root_prim.SetMetadata("customData", metadata)
```

### AR Behaviors

**Billboard Mode:**
- Object always faces camera
- Best for text, UI elements, stickers
- Minimal depth perception

**Fixed Mode:**
- Object maintains world orientation  
- Best for 3D models, sculptures
- Full 3D depth perception

**Physics Mode:**
- Object responds to gravity/collisions
- Requires collision mesh
- Interactive AR experiences

## Validation and Testing

### USDZ Validation

```python
def validate_usdz_package(usdz_path):
    """Validate USDZ package for AR compatibility"""
    import zipfile
    
    checks = {
        "is_zip": False,
        "uncompressed": True,
        "has_default_layer": False,
        "64_byte_aligned": True,
        "size_limit": True
    }
    
    try:
        with zipfile.ZipFile(usdz_path, 'r') as zf:
            checks["is_zip"] = True
            
            # Check compression
            for info in zf.infolist():
                if info.compress_type != zipfile.ZIP_STORED:
                    checks["uncompressed"] = False
                    
            # Check for USD file as first entry
            first_file = zf.infolist()[0]
            if first_file.filename.endswith(('.usd', '.usda', '.usdc')):
                checks["has_default_layer"] = True
            
            # Check file size
            if os.path.getsize(usdz_path) > 25 * 1024 * 1024:  # 25MB
                checks["size_limit"] = False
                
    except Exception as e:
        print(f"Validation error: {e}")
    
    return checks
```

### Command Line Tools

```bash
# Validate USDZ package
usdchecker --arkit myfile.usdz

# Package USD files into USDZ
usdzip mypackage.usdz mylayer.usd texture.png

# Extract USDZ package
unzip mypackage.usdz -d extracted/

# View USD content
usdview myfile.usd
usdcat myfile.usdz
```

## Common Issues and Solutions

### Texture Not Displaying

**Problem:** Texture appears black or missing
**Solutions:**
- Ensure UV coordinates named "st" not "UVMap"
- Check texture file path is package-relative
- Verify texture format is supported (PNG/JPG)
- Confirm texture resolution is power-of-2

### AR Quick Look Not Working

**Problem:** File doesn't open in AR mode
**Solutions:**  
- Add `arQuickLookCompatible: true` metadata
- Ensure uncompressed ZIP format
- Check 64-byte alignment of files
- Verify iOS compatibility (iOS 12+)

### Performance Issues

**Problem:** Slow loading or stuttering
**Solutions:**
- Reduce texture resolution
- Simplify geometry (fewer vertices)
- Use single material when possible
- Optimize UV layout for texture atlas

## Installation and Dependencies

### Python USD

```bash
# Install USD with conda (recommended)
conda install -c conda-forge usd-core

# Or with pip (limited features)
pip install usd-core

# Verify installation
python -c "from pxr import Usd; print('USD installed successfully')"
```

### Alternative Tools

```bash
# Apple Reality Composer (macOS only)
# Available from Mac App Store

# Blender USD add-on
# Built into Blender 3.0+

# USD Manager (GUI tool)
# Download from GitHub: dreamworksanimation/usdmanager
```

## Resources and Documentation

- **Official USD Documentation:** https://openusd.org/
- **USDZ Specification:** https://openusd.org/release/spec_usdz.html
- **Apple AR Quick Look:** https://developer.apple.com/augmented-reality/quick-look/
- **USD Python API:** https://openusd.org/dev/api/index.html
- **Reality Composer:** https://developer.apple.com/augmented-reality/reality-composer/

## Next Steps

1. **ARKit Integration Guide** - iOS-specific implementation details
2. **Material and Shader Guide** - Advanced PBR materials  
3. **Animation and Physics** - Dynamic USDZ content
4. **Distribution Strategies** - Web delivery and optimization
