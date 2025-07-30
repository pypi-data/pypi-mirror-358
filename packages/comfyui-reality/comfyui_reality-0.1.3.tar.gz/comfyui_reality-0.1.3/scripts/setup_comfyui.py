#!/usr/bin/env python3
"""Setup script for ComfyUI integration."""

import shutil
import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    """Run a command and return the result."""
    print(f"Running: {' '.join(cmd)}")
    return subprocess.run(cmd, check=check)


def setup_comfyui():
    """Complete ComfyUI setup for development."""
    project_root = Path(__file__).parent.parent
    comfyui_path = project_root / "comfyui"

    print("🚀 Setting up ComfyUI for ComfyReality development...")

    # 1. Check if comfy-cli is installed
    try:
        run_command(["comfy", "--version"])
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ comfy-cli not found. Installing...")
        run_command([sys.executable, "-m", "pip", "install", "comfy-cli"])

    # 2. Install ComfyUI if not exists
    if not comfyui_path.exists():
        print(f"📦 Installing ComfyUI to {comfyui_path}...")
        run_command(["comfy", f"--workspace={comfyui_path}", "install"])
    else:
        print("✅ ComfyUI already installed")

    # 3. Create custom_nodes directory
    custom_nodes_path = comfyui_path / "custom_nodes" / "comfy-reality"
    custom_nodes_path.mkdir(parents=True, exist_ok=True)

    # 4. Copy ComfyReality nodes
    src_path = project_root / "src" / "comfy_reality"
    print(f"📋 Copying nodes from {src_path} to {custom_nodes_path}...")

    # Copy all Python files
    for item in src_path.rglob("*.py"):
        relative_path = item.relative_to(src_path)
        dest_path = custom_nodes_path / relative_path
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(item, dest_path)

    # Create __init__.py if not exists
    init_file = custom_nodes_path / "__init__.py"
    if not init_file.exists():
        shutil.copy2(src_path / "__init__.py", init_file)

    print("✅ ComfyReality nodes installed")

    # 5. Create directories
    for dir_name in ["models", "input", "output", "temp"]:
        dir_path = comfyui_path / dir_name
        dir_path.mkdir(exist_ok=True)
        print(f"📁 Created {dir_name}/ directory")

    # 6. Check GPU availability
    try:
        import torch

        if torch.cuda.is_available():
            print(f"✅ CUDA available: {torch.cuda.get_device_name(0)}")
        elif torch.backends.mps.is_available():
            print("✅ MPS (Apple Silicon) available")
        else:
            print("⚠️  No GPU detected, will use CPU mode")
    except ImportError:
        print("⚠️  PyTorch not installed, GPU detection skipped")

    print("\n✨ Setup complete! You can now:")
    print("  1. Start ComfyUI: uv run poe comfy-start")
    print("  2. Or demo mode: uv run poe demo")
    print("  3. Access at: http://127.0.0.1:8188")


if __name__ == "__main__":
    setup_comfyui()
