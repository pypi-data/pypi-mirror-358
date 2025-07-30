"""ComfyReality - Professional AR/USDZ Content Creation for ComfyUI.

A modern Python package providing AR-ready USDZ export capabilities for ComfyUI.

Key Features:
- 📦 Professional USDZ export for iOS ARKit
- 🚀 GPU-accelerated processing pipeline
- 📱 Mobile-optimized AR content

Usage:
    Install via UV (recommended):
        uv add comfy-reality

    Or via pip:
        pip install comfy-reality

    The ComfyUI nodes will be automatically available after installation.

Repository: https://github.com/gerred/stickerkit
Documentation: https://github.com/gerred/stickerkit#readme
"""

from .nodes import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

__version__ = "0.1.3"
__author__ = "Gerred Dillon"
__email__ = "hello@gerred.org"

__all__ = [
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS",
    "__version__",
]

# ComfyUI Discovery - Export for ComfyUI custom nodes system
WEB_DIRECTORY = "./web"  # Optional web components directory
