# ComfyReality Agent Guidelines

## Commands
- **Test**: `uv run pytest` (all tests), `uv run pytest tests/test_specific.py` (single test)
- **Lint/Format**: `uv run ruff check` (lint), `uv run ruff format` (format), `uv run mypy` (typecheck)
- **Coverage**: `uv run pytest --cov=comfy_reality --cov-report=html`
- **Build**: `uv build` (package), `uv sync --extra dev` (dev install)
- **Pre-commit**: `pre-commit run --all-files`

## Architecture
- **Package**: Python package for AR/USDZ content creation in ComfyUI
- **Core modules**: `src/comfy_reality/nodes/` (ComfyUI nodes), `src/comfy_reality/models/` (model loaders), `src/comfy_reality/utils/` (utilities)
- **Key nodes**: ARStickerGenerator (FLUX/SDXL), SAM2Segmenter (background removal), USDZExporter (AR export)
- **Tech stack**: PyTorch, diffusers, transformers, trimesh, OpenCV, Pillow
- **Target**: iOS ARKit USDZ files, mobile-optimized AR stickers

## Code Style
- **Line length**: 88 characters (Ruff)
- **Python**: 3.12+, type hints required, use `dict[str, Any]` not `Dict`
- **Imports**: Use absolute imports, group by stdlib/third-party/local
- **Error handling**: Raise specific exceptions, document in docstrings
- **Testing**: PyTest with coverage, mark slow tests with `@pytest.mark.slow`
- **Format**: Double quotes, 4-space indent, trailing commas
