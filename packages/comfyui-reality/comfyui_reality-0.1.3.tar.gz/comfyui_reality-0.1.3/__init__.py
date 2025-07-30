"""ComfyReality - Root ComfyUI Node Registration.

This is the root-level __init__.py file required by ComfyUI's custom node discovery system.
It exports NODE_CLASS_MAPPINGS and NODE_DISPLAY_NAME_MAPPINGS for ComfyUI to discover
and register all ComfyReality AR nodes.
"""

from src.comfy_reality.nodes import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

# ComfyUI requires these exact variable names at the root level
__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]

# Optional web components directory for ComfyUI frontend extensions
WEB_DIRECTORY = "./web"
