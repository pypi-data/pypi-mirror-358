# Python Libraries & Tools Guide for USDZ Development

## Overview

This guide covers the essential Python libraries, tools, and workflows for creating USDZ files and AR content. From basic installations to advanced 3D processing pipelines, learn how to set up a complete Python environment for USDZ development.

## Core USD Libraries

### USD Python (pxr)

**Official Pixar USD Python bindings - the gold standard for USDZ creation.**

#### Installation Options

**Option 1: Conda (Recommended)**
```bash
# Install from conda-forge (most reliable)
conda install -c conda-forge usd-core

# Or full USD with imaging features
conda install -c conda-forge usd

# Verify installation
python -c "from pxr import Usd; print('USD version:', Usd.GetVersion())"
```

**Option 2: PyPI**
```bash
# Install core USD library
pip install usd-core

# Note: Limited features compared to conda version
# Does not include imaging, plugins, or some tools
```

**Option 3: Build from Source (Advanced)**
```bash
# Clone OpenUSD repository
git clone https://github.com/PixarAnimationStudios/OpenUSD.git
cd OpenUSD

# Install dependencies
pip install pyside6 openimageio boost

# Build with Python support
python build_scripts/build_usd.py --build-shared --build-monolithic --python /usr/local/usd
```

#### Basic Usage

```python
from pxr import Usd, UsdGeom, Sdf, UsdShade, Gf

# Create new USD stage
stage = Usd.Stage.CreateNew("example.usd")

# Define root prim
root = stage.DefinePrim("/World", "Xform")
stage.SetDefaultPrim(root)

# Create mesh
mesh_prim = stage.DefinePrim("/World/Cube", "Mesh")
mesh = UsdGeom.Mesh(mesh_prim)

# Define cube geometry
points = [
    (-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1),  # Bottom face
    (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1)       # Top face
]
mesh.CreatePointsAttr(points)

# Define faces (quads)
faceVertexCounts = [4, 4, 4, 4, 4, 4]  # 6 faces, 4 vertices each
faceVertexIndices = [
    0, 1, 2, 3,  # Bottom
    4, 7, 6, 5,  # Top
    0, 4, 5, 1,  # Front
    2, 6, 7, 3,  # Back
    0, 3, 7, 4,  # Left
    1, 5, 6, 2   # Right
]
mesh.CreateFaceVertexCountsAttr(faceVertexCounts)
mesh.CreateFaceVertexIndicesAttr(faceVertexIndices)

# Save stage
stage.Save()
```

#### Advanced USD Operations

```python
# Material creation
def create_pbr_material(stage, material_path, diffuse_texture=None):
    """Create PBR material with optional texture"""
    
    # Create material prim
    material_prim = stage.DefinePrim(material_path, "Material")
    material = UsdShade.Material(material_prim)
    
    # Create PBR shader
    pbr_shader = UsdShade.Shader.Define(stage, f"{material_path}/PBRShader")
    pbr_shader.CreateIdAttr("UsdPreviewSurface")
    
    # Set material properties
    pbr_shader.CreateInput("roughness", Sdf.ValueTypeNames.Float).Set(0.5)
    pbr_shader.CreateInput("metallic", Sdf.ValueTypeNames.Float).Set(0.0)
    
    if diffuse_texture:
        # Create texture reader
        texture_reader = UsdShade.Shader.Define(stage, f"{material_path}/DiffuseTexture")
        texture_reader.CreateIdAttr("UsdUVTexture")
        texture_reader.CreateInput("file", Sdf.ValueTypeNames.Asset).Set(diffuse_texture)
        
        # Connect texture to diffuse color
        texture_output = texture_reader.CreateOutput("rgb", Sdf.ValueTypeNames.Float3)
        diffuse_input = pbr_shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f)
        diffuse_input.ConnectToSource(texture_output)
    
    # Connect shader to material surface
    material.CreateSurfaceOutput().ConnectToSource(
        pbr_shader.CreateOutput("surface", Sdf.ValueTypeNames.Token)
    )
    
    return material

# Animation support
def add_rotation_animation(prim, duration=4.0):
    """Add rotation animation to a prim"""
    
    # Create transform attribute with time samples
    xform = UsdGeom.Xformable(prim)
    transform_attr = xform.CreateXformOpOrderAttr()
    
    # Create rotation operation
    rotate_op = xform.AddRotateXYZOp()
    
    # Set keyframes
    rotate_op.Set(Gf.Vec3f(0, 0, 0), 1.0)      # Start frame
    rotate_op.Set(Gf.Vec3f(0, 360, 0), 24.0 * duration)  # End frame (24 fps)
    
    return rotate_op

# Layer composition
def create_layered_scene():
    """Create scene with multiple layers"""
    
    # Root layer
    root_layer = Sdf.Layer.CreateNew("root.usd")
    stage = Usd.Stage.Open(root_layer)
    
    # Create sublayers
    geometry_layer = Sdf.Layer.CreateNew("geometry.usd")
    material_layer = Sdf.Layer.CreateNew("materials.usd")
    
    # Add sublayers to root
    root_layer.subLayerPaths.append("geometry.usd")
    root_layer.subLayerPaths.append("materials.usd")
    
    return stage, [geometry_layer, material_layer]
```

## 3D Processing Libraries

### Trimesh

**Excellent for mesh processing, geometry operations, and format conversion.**

```bash
pip install trimesh[easy]
```

#### Basic Usage

```python
import trimesh
import numpy as np

# Load mesh from file
mesh = trimesh.load('model.obj')

# Basic operations
print(f"Vertices: {len(mesh.vertices)}")
print(f"Faces: {len(mesh.faces)}")
print(f"Volume: {mesh.volume}")
print(f"Surface area: {mesh.area}")

# Mesh processing
mesh_simplified = mesh.simplify_quadric_decimation(face_count=1000)
mesh_smooth = mesh.smoothed()

# Boolean operations
box = trimesh.creation.box([2, 2, 2])
result = mesh.difference(box)

# Export to various formats
mesh.export('output.obj')
mesh.export('output.ply')
mesh.export('output.stl')
```

#### Advanced Trimesh Features

```python
# Voxel processing
voxels = mesh.voxelized(pitch=0.1)
voxel_mesh = voxels.as_boxes()

# UV unwrapping (requires additional dependencies)
import trimesh.visual

# Apply texture coordinates
mesh.visual = trimesh.visual.TextureVisuals(
    uv=uv_coordinates,
    material=trimesh.visual.material.PBRMaterial()
)

# Mesh repair
mesh.fill_holes()
mesh.fix_normals()
mesh.remove_duplicate_faces()

# Scene composition
scene = trimesh.Scene()
scene.add_geometry(mesh)
scene.add_geometry(box, transform=trimesh.transformations.translation_matrix([5, 0, 0]))

# Export scene
scene.export('scene.obj')
```

### Open3D

**Powerful library for 3D data processing, point clouds, and mesh operations.**

```bash
pip install open3d
```

#### Basic Usage

```python
import open3d as o3d
import numpy as np

# Load mesh
mesh = o3d.io.read_triangle_mesh("model.obj")

# Mesh processing
mesh.compute_vertex_normals()
mesh.paint_uniform_color([1, 0.706, 0])

# Mesh simplification
mesh_simplified = mesh.simplify_quadric_decimation(target_number_of_triangles=5000)

# Mesh subdivision
mesh_subdivided = mesh.subdivide_midpoint(number_of_iterations=2)

# Point cloud operations
pcd = mesh.sample_points_uniformly(number_of_points=10000)

# Visualize
o3d.visualization.draw_geometries([mesh])
```

#### Advanced Open3D Features

```python
# Mesh reconstruction from point cloud
def reconstruct_mesh_from_points(points):
    """Reconstruct mesh from point cloud using Poisson reconstruction"""
    
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)
    
    # Estimate normals
    pcd.estimate_normals()
    pcd.orient_normals_consistent_tangent_plane(100)
    
    # Poisson reconstruction
    mesh, densities = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(
        pcd, depth=9
    )
    
    return mesh

# Texture mapping
def apply_texture_mapping(mesh, texture_path):
    """Apply texture to mesh"""
    
    # Load texture
    texture = o3d.io.read_image(texture_path)
    
    # Create texture coordinates (UV mapping)
    # This is a simplified example - real UV unwrapping is more complex
    uv_coordinates = np.random.rand(len(mesh.vertices), 2)
    
    # Apply texture
    mesh.textures = [texture]
    mesh.triangle_uvs = o3d.utility.Vector2dVector(uv_coordinates)
    
    return mesh

# Mesh analysis
def analyze_mesh_quality(mesh):
    """Analyze mesh quality metrics"""
    
    # Check if mesh is watertight
    is_watertight = mesh.is_watertight()
    
    # Check if mesh is orientable
    is_orientable = mesh.is_orientable()
    
    # Get edge manifold status
    edge_manifold = mesh.is_edge_manifold()
    
    # Get vertex manifold status
    vertex_manifold = mesh.is_vertex_manifold()
    
    return {
        'watertight': is_watertight,
        'orientable': is_orientable,
        'edge_manifold': edge_manifold,
        'vertex_manifold': vertex_manifold,
        'volume': mesh.get_volume(),
        'surface_area': mesh.get_surface_area()
    }
```

## Image Processing Libraries

### Pillow (PIL)

**Essential for texture processing and optimization.**

```bash
pip install Pillow
```

#### Texture Optimization

```python
from PIL import Image, ImageFilter, ImageEnhance
import os

def optimize_texture_for_ar(image_path, output_path, max_size=1024):
    """Optimize texture for AR performance"""
    
    with Image.open(image_path) as img:
        # Convert to RGBA for transparency support
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # Resize to power-of-2 dimensions
        width, height = img.size
        new_width = min(max_size, 1 << (width - 1).bit_length())
        new_height = min(max_size, 1 << (height - 1).bit_length())
        
        if (new_width, new_height) != (width, height):
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Enhance for AR
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.1)  # Slight contrast boost
        
        # Apply subtle sharpening
        img = img.filter(ImageFilter.UnsharpMask(radius=1, percent=10, threshold=3))
        
        # Save optimized
        img.save(output_path, 'PNG', optimize=True)
        
        return img

def create_normal_map(height_map_path, strength=1.0):
    """Create normal map from height map"""
    
    with Image.open(height_map_path) as height_img:
        # Convert to grayscale
        height_img = height_img.convert('L')
        
        width, height = height_img.size
        normal_map = Image.new('RGB', (width, height))
        
        # Calculate normals (simplified)
        for y in range(1, height - 1):
            for x in range(1, width - 1):
                # Sample neighboring pixels
                tl = height_img.getpixel((x-1, y-1))  # Top-left
                tm = height_img.getpixel((x, y-1))    # Top-middle
                tr = height_img.getpixel((x+1, y-1))  # Top-right
                ml = height_img.getpixel((x-1, y))    # Middle-left
                mr = height_img.getpixel((x+1, y))    # Middle-right
                bl = height_img.getpixel((x-1, y+1))  # Bottom-left
                bm = height_img.getpixel((x, y+1))    # Bottom-middle
                br = height_img.getpixel((x+1, y+1))  # Bottom-right
                
                # Calculate gradients
                dx = (tr + 2*mr + br) - (tl + 2*ml + bl)
                dy = (bl + 2*bm + br) - (tl + 2*tm + tr)
                
                # Convert to normal vector
                normal_x = int(128 + dx * strength)
                normal_y = int(128 + dy * strength)
                normal_z = 255
                
                # Clamp values
                normal_x = max(0, min(255, normal_x))
                normal_y = max(0, min(255, normal_y))
                
                normal_map.putpixel((x, y), (normal_x, normal_y, normal_z))
        
        return normal_map
```

### OpenCV

**Computer vision library useful for advanced image processing.**

```bash
pip install opencv-python
```

#### Advanced Image Processing

```python
import cv2
import numpy as np

def remove_background_mask(image_path, mask_path):
    """Remove background using mask"""
    
    # Load image and mask
    image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
    
    # Ensure image has alpha channel
    if image.shape[2] == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)
    
    # Apply mask to alpha channel
    image[:, :, 3] = mask
    
    return image

def create_seamless_texture(image_path, output_path, tile_size=512):
    """Create seamless tiling texture"""
    
    image = cv2.imread(image_path)
    height, width = image.shape[:2]
    
    # Resize to tile size
    image = cv2.resize(image, (tile_size, tile_size))
    
    # Create seamless edges using Poisson editing
    # (Simplified approach - actual implementation would use cv2.seamlessClone)
    
    # Blend edges
    blend_width = tile_size // 10
    
    # Top-bottom blending
    for i in range(blend_width):
        alpha = i / blend_width
        image[i, :] = (1 - alpha) * image[-(blend_width-i), :] + alpha * image[i, :]
        image[-(i+1), :] = (1 - alpha) * image[blend_width-i-1, :] + alpha * image[-(i+1), :]
    
    # Left-right blending
    for i in range(blend_width):
        alpha = i / blend_width
        image[:, i] = (1 - alpha) * image[:, -(blend_width-i)] + alpha * image[:, i]
        image[:, -(i+1)] = (1 - alpha) * image[:, blend_width-i-1] + alpha * image[:, -(i+1)]
    
    cv2.imwrite(output_path, image)
    
    return image
```

## Specialized AR Libraries

### Background Removal (rembg)

**AI-powered background removal for sticker creation.**

```bash
pip install rembg[gpu]  # GPU acceleration
# or
pip install rembg       # CPU only
```

#### Usage

```python
from rembg import remove, new_session
from PIL import Image
import io

# Basic background removal
def remove_background_simple(input_path, output_path):
    """Simple background removal"""
    
    with open(input_path, 'rb') as input_file:
        input_data = input_file.read()
    
    output_data = remove(input_data)
    
    with open(output_path, 'wb') as output_file:
        output_file.write(output_data)

# Advanced background removal with specific models
def remove_background_advanced(input_path, output_path, model_name='u2net'):
    """Advanced background removal with model selection"""
    
    # Available models: u2net, u2netp, u2net_human_seg, silueta
    session = new_session(model_name)
    
    with open(input_path, 'rb') as input_file:
        input_data = input_file.read()
    
    output_data = remove(input_data, session=session)
    
    # Convert to PIL Image for further processing
    output_image = Image.open(io.BytesIO(output_data))
    
    # Post-process for better edges
    output_image = refine_alpha_edges(output_image)
    
    output_image.save(output_path, 'PNG')
    
    return output_image

def refine_alpha_edges(image):
    """Refine alpha channel edges for cleaner cutout"""
    
    if image.mode != 'RGBA':
        return image
    
    # Convert to numpy array
    img_array = np.array(image)
    alpha = img_array[:, :, 3]
    
    # Apply slight blur to alpha channel for smoother edges
    alpha_blurred = cv2.GaussianBlur(alpha, (3, 3), 0.5)
    
    # Apply threshold to clean up semi-transparent pixels
    alpha_clean = np.where(alpha_blurred > 128, 255, 0).astype(np.uint8)
    
    # Update image
    img_array[:, :, 3] = alpha_clean
    
    return Image.fromarray(img_array)
```

## Development Tools and Utilities

### Command Line Tools

```bash
# USD command line tools (available after installing USD)

# Convert models to USDZ
usdzip package.usdz file.usd texture.png

# View USD file contents
usdcat file.usd

# View USD file tree structure
usdedit file.usd

# Validate USD files
usdchecker file.usd

# Convert between USD formats
usdconvert input.usd output.usda

# Package validation for AR
usdchecker --arkit file.usdz
```

### Python Packaging Utilities

```python
# Custom USDZ packaging utilities
import zipfile
import os
from pathlib import Path

class USDZPackager:
    """Utility class for creating USDZ packages"""
    
    def __init__(self):
        self.files = []
        self.default_layer = None
    
    def add_usd_file(self, file_path, is_default=False):
        """Add USD file to package"""
        if is_default:
            self.default_layer = file_path
            # Insert at beginning for default layer
            self.files.insert(0, file_path)
        else:
            self.files.append(file_path)
    
    def add_texture(self, texture_path):
        """Add texture file to package"""
        self.files.append(texture_path)
    
    def create_package(self, output_path):
        """Create USDZ package with proper alignment"""
        
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_STORED) as zf:
            current_offset = 0
            
            for file_path in self.files:
                file_size = os.path.getsize(file_path)
                filename = os.path.basename(file_path)
                
                # Calculate padding for 64-byte alignment
                padding = (64 - (current_offset % 64)) % 64
                
                # Add padding if needed
                if padding > 0:
                    zf.writestr(f"_padding_{current_offset}", b'\\0' * padding)
                    current_offset += padding
                
                # Add file
                zf.write(file_path, filename)
                current_offset += file_size
        
        return output_path
    
    def validate_package(self, package_path):
        """Validate USDZ package"""
        
        with zipfile.ZipFile(package_path, 'r') as zf:
            file_list = zf.namelist()
            
            # Check for USD file as first entry
            first_file = file_list[0]
            if not first_file.endswith(('.usd', '.usda', '.usdc')):
                return False, "First file must be USD format"
            
            # Check compression
            for info in zf.infolist():
                if info.compress_type != zipfile.ZIP_STORED:
                    return False, "USDZ files must be uncompressed"
            
            return True, "Valid USDZ package"

# Usage example
def create_ar_sticker_package():
    """Create complete AR sticker USDZ package"""
    
    packager = USDZPackager()
    
    # Add main USD file
    packager.add_usd_file("sticker.usd", is_default=True)
    
    # Add textures
    packager.add_texture("diffuse.png")
    packager.add_texture("normal.png")
    
    # Create package
    output_path = packager.create_package("ar_sticker.usdz")
    
    # Validate
    is_valid, message = packager.validate_package(output_path)
    print(f"Package validation: {message}")
    
    return output_path
```

## Installation Scripts and Environment Setup

### Complete Environment Setup

```bash
#!/bin/bash
# complete_usdz_setup.sh

echo "Setting up complete USDZ development environment..."

# Create conda environment
conda create -n usdz-dev python=3.11 -y
conda activate usdz-dev

# Install core USD
conda install -c conda-forge usd-core -y

# Install 3D processing libraries
pip install trimesh[easy] open3d

# Install image processing
pip install Pillow opencv-python

# Install AI tools
pip install rembg[gpu] segment-anything-2

# Install development tools
pip install jupyter notebook ipython

# Install optional tools
pip install meshlab pymeshlab

# Verify installation
python -c "
try:
    from pxr import Usd
    print('✅ USD installed successfully')
except ImportError:
    print('❌ USD installation failed')

try:
    import trimesh
    print('✅ Trimesh installed successfully')
except ImportError:
    print('❌ Trimesh installation failed')

try:
    import open3d
    print('✅ Open3D installed successfully')
except ImportError:
    print('❌ Open3D installation failed')

try:
    from rembg import remove
    print('✅ Rembg installed successfully')
except ImportError:
    print('❌ Rembg installation failed')
"

echo "Environment setup complete!"
echo "Activate with: conda activate usdz-dev"
```

### Requirements File

```txt
# requirements.txt - USDZ Development Dependencies

# Core USD (install via conda recommended)
# usd-core>=23.11

# 3D Processing
trimesh[easy]>=3.23.0
open3d>=0.17.0
pymeshlab>=2022.2.post4

# Image Processing
Pillow>=10.0.0
opencv-python>=4.8.0
scikit-image>=0.21.0

# AI/ML Tools
rembg[gpu]>=2.0.50
segment-anything>=1.0
torch>=2.0.0
torchvision>=0.15.0

# File Format Support
numpy>=1.24.0
scipy>=1.11.0

# Development Tools
jupyter>=1.0.0
notebook>=7.0.0
ipython>=8.0.0

# Optional Visualization
matplotlib>=3.7.0
plotly>=5.15.0
```

## Best Practices and Workflows

### Complete AR Sticker Pipeline

```python
class ARStickerPipeline:
    """Complete pipeline for creating AR stickers from images"""
    
    def __init__(self, output_dir="output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def process_image_to_usdz(self, image_path, output_name, scale=0.1):
        """Complete pipeline from image to USDZ"""
        
        # Step 1: Remove background
        print("🔧 Removing background...")
        cutout_path = self.output_dir / f"{output_name}_cutout.png"
        self.remove_background(image_path, cutout_path)
        
        # Step 2: Optimize for AR
        print("🎨 Optimizing for AR...")
        optimized_path = self.output_dir / f"{output_name}_optimized.png"
        self.optimize_for_ar(cutout_path, optimized_path)
        
        # Step 3: Create USD file
        print("🏗️ Creating USD file...")
        usd_path = self.output_dir / f"{output_name}.usd"
        self.create_usd_with_texture(usd_path, optimized_path, scale)
        
        # Step 4: Package as USDZ
        print("📦 Creating USDZ package...")
        usdz_path = self.output_dir / f"{output_name}.usdz"
        self.package_usdz(usd_path, optimized_path, usdz_path)
        
        # Step 5: Validate
        print("✅ Validating package...")
        is_valid = self.validate_usdz(usdz_path)
        
        if is_valid:
            print(f"🎯 AR sticker created successfully: {usdz_path}")
        else:
            print("❌ USDZ validation failed")
        
        return usdz_path
    
    def remove_background(self, input_path, output_path):
        """Remove background using rembg"""
        from rembg import remove
        
        with open(input_path, 'rb') as input_file:
            input_data = input_file.read()
        
        output_data = remove(input_data)
        
        with open(output_path, 'wb') as output_file:
            output_file.write(output_data)
    
    def optimize_for_ar(self, input_path, output_path, max_size=1024):
        """Optimize image for AR performance"""
        from PIL import Image
        
        with Image.open(input_path) as img:
            # Ensure RGBA
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            # Resize to power-of-2
            width, height = img.size
            new_width = min(max_size, 1 << (width - 1).bit_length())
            new_height = min(max_size, 1 << (height - 1).bit_length())
            
            if (new_width, new_height) != (width, height):
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            img.save(output_path, 'PNG', optimize=True)
    
    def create_usd_with_texture(self, usd_path, texture_path, scale):
        """Create USD file with textured quad"""
        from pxr import Usd, UsdGeom, UsdShade, Sdf
        
        # Create stage
        stage = Usd.Stage.CreateNew(str(usd_path))
        
        # Root prim
        root = stage.DefinePrim("/Root", "Xform")
        stage.SetDefaultPrim(root)
        
        # Add AR metadata
        root.SetMetadata("customData", {
            "arQuickLookCompatible": True,
            "realWorldScale": scale
        })
        
        # Create mesh
        mesh_prim = stage.DefinePrim("/Root/Sticker", "Mesh")
        mesh = UsdGeom.Mesh(mesh_prim)
        
        # Geometry (quad)
        points = [(-scale, 0, -scale), (scale, 0, -scale), 
                 (scale, 0, scale), (-scale, 0, scale)]
        mesh.CreatePointsAttr(points)
        mesh.CreateFaceVertexCountsAttr([4])
        mesh.CreateFaceVertexIndicesAttr([0, 1, 2, 3])
        
        # UV coordinates
        texCoords = [(0, 0), (1, 0), (1, 1), (0, 1)]
        texCoordsPrimvar = UsdGeom.PrimvarsAPI(mesh_prim).CreatePrimvar(
            "st", Sdf.ValueTypeNames.TexCoord2fArray, UsdGeom.Tokens.vertex
        )
        texCoordsPrimvar.Set(texCoords)
        
        # Material
        material = self.create_material_with_texture(stage, "/Root/Material", str(texture_path))
        UsdShade.MaterialBindingAPI(mesh_prim).Bind(material)
        
        stage.Save()
    
    def create_material_with_texture(self, stage, material_path, texture_path):
        """Create material with texture"""
        from pxr import UsdShade, Sdf
        
        # Material
        material_prim = stage.DefinePrim(material_path, "Material")
        material = UsdShade.Material(material_prim)
        
        # Shader
        shader_prim = stage.DefinePrim(f"{material_path}/Shader", "Shader")
        shader = UsdShade.Shader(shader_prim)
        shader.CreateIdAttr("UsdPreviewSurface")
        
        # Texture reader
        tex_reader_prim = stage.DefinePrim(f"{material_path}/TextureReader", "Shader")
        tex_reader = UsdShade.Shader(tex_reader_prim)
        tex_reader.CreateIdAttr("UsdUVTexture")
        tex_reader.CreateInput("file", Sdf.ValueTypeNames.Asset).Set(texture_path)
        
        # Connect texture to diffuse
        tex_output = tex_reader.CreateOutput("rgb", Sdf.ValueTypeNames.Float3)
        diffuse_input = shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f)
        diffuse_input.ConnectToSource(tex_output)
        
        # Alpha channel
        alpha_output = tex_reader.CreateOutput("a", Sdf.ValueTypeNames.Float)
        opacity_input = shader.CreateInput("opacity", Sdf.ValueTypeNames.Float)
        opacity_input.ConnectToSource(alpha_output)
        
        # Connect to material
        surface_output = material.CreateSurfaceOutput()
        shader_output = shader.CreateOutput("surface", Sdf.ValueTypeNames.Token)
        surface_output.ConnectToSource(shader_output)
        
        return material
    
    def package_usdz(self, usd_path, texture_path, output_path):
        """Package files into USDZ"""
        import zipfile
        
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_STORED) as zf:
            zf.write(usd_path, usd_path.name)
            zf.write(texture_path, texture_path.name)
    
    def validate_usdz(self, usdz_path):
        """Basic USDZ validation"""
        import zipfile
        
        try:
            with zipfile.ZipFile(usdz_path, 'r') as zf:
                # Check compression
                for info in zf.infolist():
                    if info.compress_type != zipfile.ZIP_STORED:
                        return False
                
                # Check for USD file
                files = zf.namelist()
                has_usd = any(f.endswith(('.usd', '.usda', '.usdc')) for f in files)
                
                return has_usd
                
        except Exception:
            return False

# Usage
pipeline = ARStickerPipeline()
result = pipeline.process_image_to_usdz("input_image.png", "my_sticker", scale=0.15)
```

## Resources and Documentation

### Official Documentation
- **OpenUSD Documentation:** https://openusd.org/release/index.html
- **USD Python API:** https://openusd.org/release/api/index.html
- **Trimesh Documentation:** https://trimsh.org/
- **Open3D Documentation:** http://www.open3d.org/docs/

### Installation Guides
- **USD Build Guide:** https://github.com/PixarAnimationStudios/OpenUSD/blob/dev/BUILDING.md
- **Conda USD Package:** https://anaconda.org/conda-forge/usd-core

### Community Resources
- **OpenUSD Forum:** https://forum.openusd.org/
- **USD GitHub Issues:** https://github.com/PixarAnimationStudios/OpenUSD/issues

## Next Steps

1. **Shader & Materials Guide** - Advanced PBR materials and custom shaders
2. **Mobile Optimization Guide** - Performance tuning for AR devices
3. **Distribution Guide** - Web deployment and sharing strategies
4. **Advanced AR Features** - Animations, physics, and interactions
