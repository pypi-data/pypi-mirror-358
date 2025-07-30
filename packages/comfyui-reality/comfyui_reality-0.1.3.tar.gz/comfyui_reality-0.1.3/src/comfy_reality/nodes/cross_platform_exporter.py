"""Cross Platform Exporter Node for ComfyUI Reality."""

from typing import Any


class CrossPlatformExporter:
    """Export AR scenes to multiple platform formats.

    This node exports AR scenes to various formats including USDZ (iOS),
    glTF/GLB (Android/WebXR), FBX (Unity), and OBJ (universal 3D).
    """

    @classmethod
    def INPUT_TYPES(cls) -> dict[str, Any]:
        """Define the input parameters for the node."""
        return {
            "required": {
                "scene": ("AR_SCENE",),
                "export_formats": (
                    ["usdz", "gltf", "glb", "fbx", "obj", "all"],
                    {"default": "all"},
                ),
                "filename": (
                    "STRING",
                    {"default": "ar_export", "multiline": False},
                ),
                "target_platforms": (
                    ["ios", "android", "web", "unity", "unreal", "all"],
                    {"default": "all"},
                ),
            },
            "optional": {
                "output_directory": (
                    "STRING",
                    {"default": "./output", "multiline": False},
                ),
                "compression_level": (
                    ["none", "low", "medium", "high", "maximum"],
                    {"default": "medium"},
                ),
                "texture_format": (
                    ["auto", "png", "jpg", "webp", "ktx2", "astc"],
                    {"default": "auto"},
                ),
                "geometry_precision": (
                    ["low", "medium", "high", "maximum"],
                    {"default": "medium"},
                ),
                "animation_support": ("BOOLEAN", {"default": True}),
                "physics_export": ("BOOLEAN", {"default": False}),
                "materials_embedded": ("BOOLEAN", {"default": True}),
                "draco_compression": ("BOOLEAN", {"default": True}),
                "include_metadata": ("BOOLEAN", {"default": True}),
                "mobile_optimization": ("BOOLEAN", {"default": True}),
            },
        }

    RETURN_TYPES = ("EXPORT_RESULTS", "FILE_PATHS", "EXPORT_REPORT")
    RETURN_NAMES = ("results", "file_paths", "report")
    FUNCTION = "export_cross_platform"
    CATEGORY = "🚀 ComfyReality/Export"
    DESCRIPTION = "Export AR scenes to multiple platform formats"

    def export_cross_platform(
        self,
        scene: dict,
        export_formats: str,
        filename: str,
        target_platforms: str,
        output_directory: str = "./output",
        compression_level: str = "medium",
        texture_format: str = "auto",
        geometry_precision: str = "medium",
        animation_support: bool = True,
        physics_export: bool = False,
        materials_embedded: bool = True,
        draco_compression: bool = True,
        include_metadata: bool = True,
        mobile_optimization: bool = True,
    ):
        """Export AR scene to multiple platform formats."""

        # Determine export formats
        formats_to_export = self._get_export_formats(export_formats, target_platforms)

        # Prepare export settings
        export_settings = {
            "compression_level": compression_level,
            "texture_format": texture_format,
            "geometry_precision": geometry_precision,
            "animation_support": animation_support,
            "physics_export": physics_export,
            "materials_embedded": materials_embedded,
            "draco_compression": draco_compression,
            "include_metadata": include_metadata,
            "mobile_optimization": mobile_optimization,
        }

        # Export to each format
        export_results = {}
        file_paths = {}

        for format_name in formats_to_export:
            result = self._export_format(scene, format_name, filename, output_directory, export_settings)
            export_results[format_name] = result
            file_paths[format_name] = result.get("file_path", "")

        # Generate export report
        report = self._generate_export_report(export_results, export_settings)

        return (export_results, file_paths, report)

    def _get_export_formats(self, export_formats: str, target_platforms: str):
        """Determine which formats to export based on settings."""
        if export_formats == "all":
            formats = ["usdz", "gltf", "glb", "fbx", "obj"]
        else:
            formats = [export_formats]

        # Filter by target platforms if specified
        if target_platforms != "all":
            platform_formats = {
                "ios": ["usdz"],
                "android": ["gltf", "glb"],
                "web": ["gltf", "glb"],
                "unity": ["fbx", "obj"],
                "unreal": ["fbx", "obj"],
            }

            if target_platforms in platform_formats:
                formats = [f for f in formats if f in platform_formats[target_platforms]]

        return formats

    def _export_format(
        self,
        scene: dict,
        format_name: str,
        filename: str,
        output_dir: str,
        settings: dict,
    ):
        """Export scene to specific format."""
        export_functions = {
            "usdz": self._export_usdz,
            "gltf": self._export_gltf,
            "glb": self._export_glb,
            "fbx": self._export_fbx,
            "obj": self._export_obj,
        }

        if format_name in export_functions:
            return export_functions[format_name](scene, filename, output_dir, settings)
        else:
            return {"success": False, "error": f"Unsupported format: {format_name}"}

    def _export_usdz(self, scene: dict, filename: str, output_dir: str, settings: dict):
        """Export to USDZ format for iOS ARKit."""
        file_path = f"{output_dir}/{filename}.usdz"

        # Placeholder USDZ export
        result = {
            "success": True,
            "format": "usdz",
            "file_path": file_path,
            "file_size_mb": 2.5,  # Placeholder
            "mobile_optimized": settings["mobile_optimization"],
            "ios_compatible": True,
            "features": {
                "animations": settings["animation_support"],
                "physics": settings["physics_export"],
                "materials": settings["materials_embedded"],
            },
        }

        return result

    def _export_gltf(self, scene: dict, filename: str, output_dir: str, settings: dict):
        """Export to glTF format for Android/WebXR."""
        file_path = f"{output_dir}/{filename}.gltf"

        # Placeholder glTF export
        result = {
            "success": True,
            "format": "gltf",
            "file_path": file_path,
            "file_size_mb": 1.8,  # Placeholder
            "draco_compressed": settings["draco_compression"],
            "web_compatible": True,
            "features": {
                "animations": settings["animation_support"],
                "physics": settings["physics_export"],
                "materials": settings["materials_embedded"],
            },
        }

        return result

    def _export_glb(self, scene: dict, filename: str, output_dir: str, settings: dict):
        """Export to GLB format (binary glTF)."""
        file_path = f"{output_dir}/{filename}.glb"

        # Placeholder GLB export
        result = {
            "success": True,
            "format": "glb",
            "file_path": file_path,
            "file_size_mb": 1.5,  # Placeholder (more compressed)
            "draco_compressed": settings["draco_compression"],
            "web_compatible": True,
            "binary_format": True,
            "features": {
                "animations": settings["animation_support"],
                "physics": settings["physics_export"],
                "materials": settings["materials_embedded"],
            },
        }

        return result

    def _export_fbx(self, scene: dict, filename: str, output_dir: str, settings: dict):
        """Export to FBX format for Unity/Unreal."""
        file_path = f"{output_dir}/{filename}.fbx"

        # Placeholder FBX export
        result = {
            "success": True,
            "format": "fbx",
            "file_path": file_path,
            "file_size_mb": 3.2,  # Placeholder
            "unity_compatible": True,
            "unreal_compatible": True,
            "features": {
                "animations": settings["animation_support"],
                "physics": settings["physics_export"],
                "materials": settings["materials_embedded"],
            },
        }

        return result

    def _export_obj(self, scene: dict, filename: str, output_dir: str, settings: dict):
        """Export to OBJ format (universal 3D)."""
        file_path = f"{output_dir}/{filename}.obj"

        # Placeholder OBJ export
        result = {
            "success": True,
            "format": "obj",
            "file_path": file_path,
            "file_size_mb": 0.8,  # Placeholder (geometry only)
            "universal_compatible": True,
            "material_file": f"{filename}.mtl",
            "features": {
                "animations": False,  # OBJ doesn't support animations
                "physics": False,
                "materials": True,  # Via MTL file
            },
        }

        return result

    def _generate_export_report(self, results: dict, settings: dict):
        """Generate comprehensive export report."""
        total_formats = len(results)
        successful_exports = sum(1 for r in results.values() if r.get("success", False))
        total_size_mb = sum(r.get("file_size_mb", 0) for r in results.values())

        report = {
            "summary": {
                "total_formats": total_formats,
                "successful_exports": successful_exports,
                "failed_exports": total_formats - successful_exports,
                "total_size_mb": round(total_size_mb, 2),
            },
            "formats": results,
            "settings": settings,
            "recommendations": self._generate_recommendations(results, settings),
        }

        return report

    def _generate_recommendations(self, results: dict, settings: dict):
        """Generate optimization recommendations."""
        recommendations = []

        # Size optimization recommendations
        total_size = sum(r.get("file_size_mb", 0) for r in results.values())
        if total_size > 10:
            recommendations.append("Consider higher compression for mobile deployment")

        # Format recommendations
        if "usdz" in results and "gltf" in results:
            recommendations.append("Use USDZ for iOS and glTF/GLB for Android/Web")

        # Performance recommendations
        if not settings["mobile_optimization"]:
            recommendations.append("Enable mobile optimization for better AR performance")

        return recommendations
