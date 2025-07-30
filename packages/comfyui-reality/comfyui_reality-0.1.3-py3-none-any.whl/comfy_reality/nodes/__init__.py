"""ComfyUI Reality Nodes Package.

This package provides professional AR/USDZ content creation nodes for ComfyUI:
- USDZExporter: Export AR-ready USDZ files for iOS/ARKit
- AROptimizer: Mobile AR performance optimization
- SpatialPositioner: 3D positioning and scale for AR placement
- MaterialComposer: PBR material workflow for AR assets
- RealityComposer: Multi-object scene composition
- CrossPlatformExporter: Export to multiple AR formats
- AnimationBuilder: Simple keyframe animation for AR objects
- PhysicsIntegrator: Basic collision and physics properties
"""

from .animation_builder import AnimationBuilder
from .ar_background_remover import ARBackgroundRemover
from .ar_optimizer import AROptimizer
from .base import BaseARNode
from .cross_platform_exporter import CrossPlatformExporter
from .flux_ar_generator import FluxARGenerator
from .material_composer import MaterialComposer
from .physics_integrator import PhysicsIntegrator
from .reality_composer import RealityComposer
from .spatial_positioner import SpatialPositioner
from .usdz_exporter import USDZExporter

__all__ = [
    "ARBackgroundRemover",
    "AROptimizer",
    "AnimationBuilder",
    "BaseARNode",
    "CrossPlatformExporter",
    "FluxARGenerator",
    "MaterialComposer",
    "PhysicsIntegrator",
    "RealityComposer",
    "SpatialPositioner",
    "USDZExporter",
]

# ComfyUI node registration
NODE_CLASS_MAPPINGS = {
    "USDZExporter": USDZExporter,
    "AROptimizer": AROptimizer,
    "SpatialPositioner": SpatialPositioner,
    "MaterialComposer": MaterialComposer,
    "RealityComposer": RealityComposer,
    "CrossPlatformExporter": CrossPlatformExporter,
    "AnimationBuilder": AnimationBuilder,
    "PhysicsIntegrator": PhysicsIntegrator,
    "FluxARGenerator": FluxARGenerator,
    "ARBackgroundRemover": ARBackgroundRemover,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "USDZExporter": "📦 USDZ AR Exporter",
    "AROptimizer": "🔧 AR Optimizer",
    "SpatialPositioner": "📐 Spatial Positioner",
    "MaterialComposer": "🎨 Material Composer",
    "RealityComposer": "🏗️ Reality Composer",
    "CrossPlatformExporter": "🚀 Cross-Platform Exporter",
    "AnimationBuilder": "🎬 Animation Builder",
    "PhysicsIntegrator": "⚛️ Physics Integrator",
    "FluxARGenerator": "🎨 Flux AR Generator",
    "ARBackgroundRemover": "🎭 AR Background Remover",
}
