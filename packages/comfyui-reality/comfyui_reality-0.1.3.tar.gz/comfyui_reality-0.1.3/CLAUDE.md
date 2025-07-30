# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ComfyReality is a professional AR/USDZ content creation pipeline for ComfyUI. It provides custom nodes for converting 2D images into AR-ready content optimized for mobile devices, following iOS ARKit standards.

## Development Commands

### Setup
```bash
# Install dependencies (requires Python 3.12+)
uv sync --extra dev

# Install pre-commit hooks
pre-commit install
```

### Testing
```bash
# Run all tests with coverage
uv run pytest

# Run specific test categories
uv run pytest -m "not slow"  # Skip slow tests
uv run pytest -m gpu         # GPU tests only
uv run pytest -m integration # Integration tests

# Run a single test file
uv run pytest tests/test_ar_optimizer.py
```

### Code Quality
```bash
# Linting
uv run ruff check

# Formatting
uv run ruff format

# Type checking
uv run mypy src

# Run all pre-commit hooks
pre-commit run --all-files
```

### Building
```bash
# Build package
uv run python -m build

# Upload to PyPI
uv run twine upload dist/*
```

### Development Scripts
```bash
# Complete setup (install deps, ComfyUI, and nodes)
./scripts/setup.sh

# Or run individual commands:
# Install dependencies with dev extras
uv sync --extra dev

# Run all tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=comfy_reality --cov-report=html

# Run async runtime tests
uv run pytest tests/test_runtime/ -v

# Run all quality checks
uv run ruff check . && uv run mypy src/

# Format code
uv run ruff format .

# Build package
uv build

# Clean build artifacts
rm -rf dist/ build/ *.egg-info .coverage htmlcov/ .pytest_cache/ .mypy_cache/ .ruff_cache/
```

### ComfyUI Management
```bash
# Install ComfyUI locally
comfy --workspace=./comfyui install

# Start ComfyUI (opens browser)
comfy --workspace=./comfyui launch

# Start ComfyUI in background
comfy --workspace=./comfyui launch --background

# Start ComfyUI with dev settings
comfy --workspace=./comfyui launch -- --listen 0.0.0.0 --port 8188 --preview-method auto

# Start with GPU optimization
comfy --workspace=./comfyui launch -- --gpu-only --preview-method auto

# Start for low VRAM systems
comfy --workspace=./comfyui launch -- --lowvram --preview-method auto

# Stop ComfyUI
comfy --workspace=./comfyui stop

# Check ComfyUI status
comfy --workspace=./comfyui env

# Install ComfyReality nodes into ComfyUI
mkdir -p ./comfyui/custom_nodes/comfy-reality
cp -r src/comfy_reality/* ./comfyui/custom_nodes/comfy-reality/

# Open ComfyUI in browser
python -c "import webbrowser; webbrowser.open('http://127.0.0.1:8188')"
```

## Architecture Overview

### Async Runtime System
ComfyReality includes a modern async runtime for executing ComfyUI workflows with real-time progress tracking:

- **AsyncTaskManager**: Manages task lifecycle with event-driven updates
- **ComfyUIAsyncRuntime**: Executes workflows via ComfyUI API with WebSocket tracking
- **RichTaskPrinter**: Terminal UI for real-time task visualization
- **Pydantic Models**: Type-safe data models for all runtime components

#### Runtime Usage
```bash
# Check server status
uv run comfy-runtime status

# Execute workflow with UI
uv run comfy-runtime run workflow.json

# Execute without UI and save results
uv run comfy-runtime run workflow.json --no-ui -o results.json

# Validate workflow
uv run comfy-runtime validate workflow.json

# Generate example workflow
uv run comfy-runtime generate --example simple
```

### Node-Based Architecture
ComfyReality follows ComfyUI's node-based architecture with 8 specialized AR nodes that inherit from `BaseARNode`. Each node:
- Defines inputs via `INPUT_TYPES()` classmethod
- Specifies outputs via `RETURN_TYPES` tuple
- Implements processing via method specified in `FUNCTION`
- Uses custom data types (GEOMETRY, MATERIAL, AR_SCENE, etc.) for type-safe workflow

### Key Design Patterns

1. **Base Node Pattern**: All nodes inherit from `BaseARNode` (src/comfy_reality/nodes/base_node.py) which provides:
   - Validation methods for tensors and parameters
   - Logging infrastructure
   - Error handling
   - Type conversion utilities

2. **Data Flow**: Nodes progressively enhance data through the pipeline:
   ```
   Image → AROptimizer → MaterialComposer → SpatialPositioner → USDZExporter
   ```

3. **Exception Hierarchy**: Structured exceptions in src/comfy_reality/exceptions.py:
   - ARValidationError: Input validation failures
   - ARProcessingError: Processing failures
   - ARExportError: Export failures
   - ARGeometryError: 3D geometry issues

### Core Components

- **nodes/**: ComfyUI custom nodes (ar_optimizer.py, material_composer.py, etc.)
- **utils/**: Shared utilities for image processing and USDZ creation
- **models/**: Model loaders and handlers
- **exceptions.py**: Custom exception hierarchy

### Platform-Specific Considerations

- **iOS**: USDZ format with Y-up orientation, 64-byte alignment, <25MB files
- **Android**: glTF/GLB format with ETC2 compression
- **Web**: Optimized glTF for WebXR

### Development Guidelines

1. **Type Safety**: Always use type hints and validate inputs
2. **Error Handling**: Use appropriate exception types from exceptions.py
3. **Logging**: Use the logging infrastructure from BaseARNode
4. **Testing**: Write tests for new nodes in tests/ directory
5. **Mobile First**: Optimize for mobile performance (texture compression, polygon reduction)

### Adding New Nodes

1. Create new file in src/comfy_reality/nodes/
2. Inherit from BaseARNode
3. Define INPUT_TYPES, RETURN_TYPES, FUNCTION, CATEGORY
4. Implement processing method with proper validation
5. Add to NODE_CLASS_MAPPINGS in __init__.py
6. Write tests in tests/test_<node_name>.py

### Code Style

- Line length: 88 characters
- Use double quotes for strings
- Space indentation
- Follow Ruff configuration in pyproject.toml