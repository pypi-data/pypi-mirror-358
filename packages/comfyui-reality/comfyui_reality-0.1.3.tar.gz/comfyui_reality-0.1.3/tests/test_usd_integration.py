"""Test USD integration for professional USDZ creation."""

import tempfile
from pathlib import Path

import numpy as np
import pytest
import torch

from comfy_reality.nodes.material_composer import MaterialComposer
from comfy_reality.nodes.usdz_exporter import USDZExporter

try:
    from pxr import Usd, UsdGeom, UsdShade

    USD_AVAILABLE = True
except ImportError:
    USD_AVAILABLE = False


class TestUSDIntegration:
    """Test USD library integration."""

    def test_usd_availability_detection(self):
        """Test that USD availability is correctly detected."""
        from comfy_reality.nodes.material_composer import USD_AVAILABLE as composer_usd
        from comfy_reality.nodes.usdz_exporter import USD_AVAILABLE as exporter_usd

        # Both should have the same availability status
        assert exporter_usd == composer_usd

    @pytest.mark.skipif(not USD_AVAILABLE, reason="USD library not available")
    def test_professional_usdz_creation(self):
        """Test professional USDZ file creation with real USD APIs."""
        exporter = USDZExporter()

        # Create test image
        image = torch.rand(1, 3, 512, 512)  # BCHW format
        mask = torch.ones(512, 512) * 0.8  # Semi-transparent mask

        with tempfile.TemporaryDirectory() as temp_dir:
            # Override output directory for test
            original_export = exporter.export_usdz

            def test_export_usdz(*args, **kwargs):
                # Temporarily change output path
                result = original_export(*args, **kwargs)
                return result

            exporter.export_usdz = test_export_usdz

            # Test USDZ export
            result = exporter.export_usdz(
                image=image,
                filename="test_professional",
                mask=mask,
                scale=1.5,
                material_type="metallic",
                optimization_level="quality",
                coordinate_system="y_up",
                physics_enabled=True,
            )

            # Should return path, not error
            assert isinstance(result, tuple)
            assert len(result) == 1
            assert not result[0].startswith("ERROR")

    def test_fallback_when_usd_unavailable(self):
        """Test fallback behavior when USD is not available."""
        exporter = USDZExporter()

        # Temporarily disable USD
        original_usd_available = exporter.__class__.__dict__.get("USD_AVAILABLE", True)

        # Mock USD as unavailable
        import comfy_reality.nodes.usdz_exporter as exporter_module

        original_available = exporter_module.USD_AVAILABLE
        exporter_module.USD_AVAILABLE = False

        try:
            # Create test image
            image = torch.rand(1, 3, 256, 256)

            result = exporter.export_usdz(
                image=image,
                filename="test_fallback",
            )

            # Should still work with fallback
            assert isinstance(result, tuple)
            assert len(result) == 1

        finally:
            # Restore original USD availability
            exporter_module.USD_AVAILABLE = original_available

    @pytest.mark.skipif(not USD_AVAILABLE, reason="USD library not available")
    def test_usd_stage_creation(self):
        """Test USD stage creation and basic scene setup."""
        exporter = USDZExporter()

        # Test stage metadata setting
        with tempfile.TemporaryDirectory() as temp_dir:
            usd_file = Path(temp_dir) / "test_stage.usd"
            stage = Usd.Stage.CreateNew(str(usd_file))

            # Test coordinate system setup
            exporter._set_stage_metadata(stage, "y_up")

            # Verify up axis is set
            up_axis = UsdGeom.GetStageUpAxis(stage)
            assert up_axis == UsdGeom.Tokens.y

            # Test Z-up system
            exporter._set_stage_metadata(stage, "z_up")
            up_axis = UsdGeom.GetStageUpAxis(stage)
            assert up_axis == UsdGeom.Tokens.z

    @pytest.mark.skipif(not USD_AVAILABLE, reason="USD library not available")
    def test_mesh_geometry_creation(self):
        """Test USD mesh geometry creation."""
        exporter = USDZExporter()

        with tempfile.TemporaryDirectory() as temp_dir:
            usd_file = Path(temp_dir) / "test_mesh.usd"
            stage = Usd.Stage.CreateNew(str(usd_file))

            # Create mesh geometry
            mesh = exporter._create_mesh_geometry(stage, "/TestMesh", 2.0, "y_up")

            assert mesh is not None

            # Verify geometry attributes
            points = mesh.GetPointsAttr().Get()
            assert len(points) == 4  # Quad has 4 vertices

            face_counts = mesh.GetFaceVertexCountsAttr().Get()
            assert len(face_counts) == 2  # Two triangles
            assert all(count == 3 for count in face_counts)  # Each triangle has 3 vertices

            # Check UV coordinates
            primvars_api = UsdGeom.PrimvarsAPI(mesh)
            uv_primvar = primvars_api.GetPrimvar("st")
            assert uv_primvar.IsDefined()
            uv_coords = uv_primvar.Get()
            assert len(uv_coords) == 4

    @pytest.mark.skipif(not USD_AVAILABLE, reason="USD library not available")
    def test_material_creation(self):
        """Test USD material creation with PBR properties."""
        exporter = USDZExporter()

        with tempfile.TemporaryDirectory() as temp_dir:
            usd_file = Path(temp_dir) / "test_material.usd"
            stage = Usd.Stage.CreateNew(str(usd_file))

            # Create material
            material = exporter._create_usd_material(stage, "/TestMaterial", "metallic", "test_texture.png")

            assert material is not None

            # Verify material has surface output
            surface_output = material.GetSurfaceOutput()
            assert surface_output.HasConnectedSource()

    def test_material_composer_usd_integration(self):
        """Test material composer USD definition creation."""
        composer = MaterialComposer()

        # Create test material
        albedo = torch.rand(3, 256, 256)  # CHW format

        result = composer.compose_material(
            albedo=albedo,
            material_name="test_usd_material",
            material_type="metallic",
            roughness_factor=0.2,
            metallic_factor=0.8,
            emission_strength=0.0,
            normal_strength=1.5,
        )

        material, preview, properties = result

        # Check if USD definition was created
        if USD_AVAILABLE:
            assert "usd_definition" in material
            usd_def = material["usd_definition"]

            # Verify USD shader definition
            assert usd_def["shader_type"] == "UsdPreviewSurface"
            assert "inputs" in usd_def
            assert "outputs" in usd_def

            # Check material inputs
            inputs = usd_def["inputs"]
            assert "diffuseColor" in inputs
            assert "roughness" in inputs
            assert "metallic" in inputs

            # Verify property mapping
            assert inputs["roughness"]["value"] == 0.2
            assert inputs["metallic"]["value"] == 0.8

    def test_texture_saving(self):
        """Test texture saving with proper alpha channel handling."""
        exporter = USDZExporter()

        # Create test image and mask
        image_np = np.random.randint(0, 255, (256, 256, 3), dtype=np.uint8)
        mask_np = np.random.randint(0, 255, (256, 256), dtype=np.uint8)

        with tempfile.TemporaryDirectory() as temp_dir:
            texture_path = Path(temp_dir) / "test_texture.png"

            # Save texture
            exporter._save_texture(image_np, mask_np, str(texture_path))

            # Verify file was created
            assert texture_path.exists()

            # Load and verify it's RGBA
            from PIL import Image

            loaded_image = Image.open(texture_path)
            assert loaded_image.mode == "RGBA"
            assert loaded_image.size == (256, 256)

    def test_physics_properties(self):
        """Test physics properties addition to mesh."""
        if not USD_AVAILABLE:
            pytest.skip("USD library not available")

        exporter = USDZExporter()

        with tempfile.TemporaryDirectory() as temp_dir:
            usd_file = Path(temp_dir) / "test_physics.usd"
            stage = Usd.Stage.CreateNew(str(usd_file))

            # Create mesh
            mesh = exporter._create_mesh_geometry(stage, "/PhysicsMesh", 1.0, "y_up")

            # Add physics properties
            exporter._add_physics_properties(mesh)

            # Verify physics attributes were added
            prim = mesh.GetPrim()
            collision_attr = prim.GetAttribute("physics:collisionEnabled")
            assert collision_attr.IsValid()
            assert collision_attr.Get() is True

    def test_coordinate_system_handling(self):
        """Test different coordinate system handling."""
        if not USD_AVAILABLE:
            pytest.skip("USD library not available")

        exporter = USDZExporter()

        with tempfile.TemporaryDirectory() as temp_dir:
            # Test Y-up system
            usd_file_y = Path(temp_dir) / "test_y_up.usd"
            stage_y = Usd.Stage.CreateNew(str(usd_file_y))
            mesh_y = exporter._create_mesh_geometry(stage_y, "/MeshY", 1.0, "y_up")

            points_y = mesh_y.GetPointsAttr().Get()
            # In Y-up, quad should lie in XZ plane (Y=0)
            assert all(point[1] == 0.0 for point in points_y)

            # Test Z-up system
            usd_file_z = Path(temp_dir) / "test_z_up.usd"
            stage_z = Usd.Stage.CreateNew(str(usd_file_z))
            mesh_z = exporter._create_mesh_geometry(stage_z, "/MeshZ", 1.0, "z_up")

            points_z = mesh_z.GetPointsAttr().Get()
            # In Z-up, quad should lie in XY plane (Z=0)
            assert all(point[2] == 0.0 for point in points_z)

    def test_material_types_usd_mapping(self):
        """Test different material types map correctly to USD properties."""
        composer = MaterialComposer()

        material_types = ["standard", "unlit", "metallic", "emission"]

        for mat_type in material_types:
            albedo = torch.rand(3, 128, 128)

            result = composer.compose_material(
                albedo=albedo,
                material_name=f"test_{mat_type}",
                material_type=mat_type,
                emission_strength=2.0 if mat_type == "emission" else 0.0,
            )

            material, _, _ = result

            if USD_AVAILABLE:
                assert "usd_definition" in material
                usd_def = material["usd_definition"]

                if mat_type == "unlit":
                    # Unlit should use emission instead of diffuse
                    assert "emissiveColor" in usd_def["inputs"]
                elif mat_type == "emission":
                    # Emission should have emissive color
                    assert "emissiveColor" in usd_def["inputs"]
                    emissive = usd_def["inputs"]["emissiveColor"]
                    assert emissive["value"] == (2.0, 2.0, 2.0)
