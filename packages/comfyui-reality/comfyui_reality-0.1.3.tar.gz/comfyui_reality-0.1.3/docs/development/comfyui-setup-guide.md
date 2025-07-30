# ComfyUI Setup Guide for ComfyReality Development

## Quick Start

The easiest way to get started is using the automated setup:

```bash
# Install all dependencies, ComfyUI, and ComfyReality nodes
uv run poe setup

# Start ComfyUI with browser
uv run poe demo
```

## Detailed Setup

### 1. Install Development Dependencies

```bash
# Create virtual environment and install deps
uv sync --extra dev
```

This installs `comfy-cli` along with other development tools.

### 2. Install ComfyUI Locally

```bash
# Install ComfyUI in ./comfyui directory
uv run poe comfy-install

# Or manually with comfy-cli
uv run comfy --workspace=./comfyui install
```

### 3. Install ComfyReality Nodes

```bash
# Copy nodes to ComfyUI custom_nodes directory
uv run poe install-nodes
```

This copies the ComfyReality nodes from `src/comfy_reality/` to `./comfyui/custom_nodes/comfy-reality/`.

### 4. Start ComfyUI

Multiple options for starting ComfyUI:

```bash
# Start with browser auto-open
uv run poe comfy-start

# Start in background (no browser)
uv run poe comfy-start-bg

# Start with developer settings (listens on all interfaces)
uv run poe comfy-dev

# GPU-optimized mode
uv run poe comfy-gpu

# Low VRAM mode
uv run poe comfy-lowvram
```

### 5. Access ComfyUI

- Default URL: http://127.0.0.1:8188
- To open browser manually: `uv run poe comfy-open`

## Managing ComfyUI

### Check Status
```bash
# Show ComfyUI environment info
uv run poe comfy-status

# Check if server is running
uv run poe serve
```

### Stop ComfyUI
```bash
# Stop background ComfyUI process
uv run poe comfy-stop
```

### Install Additional Nodes
```bash
# Install from ComfyUI Manager
uv run comfy --workspace=./comfyui node install <NODE_NAME>

# List installed nodes
uv run comfy --workspace=./comfyui node show
```

### Download Models
```bash
# Download model to ComfyUI
uv run comfy --workspace=./comfyui model download --url <URL> --path <PATH>

# Example: Download SDXL base model
uv run comfy --workspace=./comfyui model download \
  --url "https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors" \
  --path checkpoints
```

## Running Workflows

### With ComfyUI UI
1. Start ComfyUI: `uv run poe comfy-start`
2. Load workflow in browser
3. Queue prompt

### With CLI Runtime
```bash
# Execute workflow with progress UI
uv run comfy-runtime run examples/simple_workflow.json

# Execute without UI
uv run comfy-runtime run workflow.json --no-ui -o results.json

# Validate workflow first
uv run comfy-runtime validate workflow.json
```

## Troubleshooting

### Port Already in Use
```bash
# Kill existing ComfyUI
uv run poe comfy-stop

# Or use different port
uv run comfy --workspace=./comfyui launch -- --port 8189
```

### GPU Not Detected
```bash
# Force CPU mode
uv run comfy --workspace=./comfyui launch -- --cpu

# Check CUDA installation
nvidia-smi
```

### Low VRAM Issues
```bash
# Use low VRAM mode
uv run poe comfy-lowvram

# Or extreme low VRAM
uv run comfy --workspace=./comfyui launch -- --novram
```

### Nodes Not Loading
```bash
# Reinstall nodes
uv run poe install-nodes

# Check ComfyUI logs
tail -f ./comfyui/comfyui.log
```

## Development Workflow

1. **Edit nodes** in `src/comfy_reality/nodes/`
2. **Copy to ComfyUI**: `uv run poe install-nodes`
3. **Restart ComfyUI**: `uv run poe comfy-stop && uv run poe comfy-start`
4. **Test in browser** at http://127.0.0.1:8188

## Directory Structure

After setup, your project will have:

```
comfyui-reality/
├── src/comfy_reality/       # Source code
├── comfyui/                 # Local ComfyUI installation
│   ├── custom_nodes/
│   │   └── comfy-reality/   # Your nodes
│   ├── models/              # Model files
│   ├── input/               # Input images
│   └── output/              # Generated outputs
├── examples/                # Example workflows
└── tests/                   # Test suite
```

The `comfyui/` directory is gitignored to keep the repository clean.