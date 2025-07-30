#!/bin/bash
# Complete setup: install deps, ComfyUI, and nodes

echo "Installing development dependencies..."
uv sync --extra dev

echo "Installing ComfyUI..."
comfy --workspace=./comfyui install

echo "Installing ComfyReality nodes in ComfyUI..."
mkdir -p ./comfyui/custom_nodes/comfy-reality
cp -r src/comfy_reality/* ./comfyui/custom_nodes/comfy-reality/
echo "Nodes installed! Restart ComfyUI to load them."