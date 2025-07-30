# ComfyReality 🎨✨

> **Professional AR/USDZ Content Creation Pipeline for ComfyUI**

[![PyPI version](https://img.shields.io/pypi/v/comfyui-reality.svg)](https://pypi.org/project/comfyui-reality/)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![UV](https://img.shields.io/badge/uv-package-green.svg)](https://docs.astral.sh/uv/)
[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![ComfyUI](https://img.shields.io/badge/ComfyUI-Ready-purple.svg)](https://www.comfy.org/)

**ComfyReality** transforms ComfyUI into a professional AR content creation studio. Generate stunning AR stickers, remove backgrounds with precision, and export production-ready USDZ files - all optimized for iOS ARKit and mobile devices.

## ✨ Features

- 🎨 **FLUX/SDXL AR Sticker Generation** - Create stunning stickers optimized for AR viewing
- ✂️ **Advanced SAM2 Segmentation** - Precise background removal with clean alpha channels  
- 📦 **Professional USDZ Export** - iOS ARKit-ready files with proper optimization
- 🚀 **GPU-Accelerated Pipeline** - Optimized for NVIDIA GPUs with CUDA support
- 📱 **Mobile-First Design** - AR content optimized for phones and tablets
- 🔧 **Modern Python Standards** - Built with UV, Ruff, and 2025 best practices

## 🚀 Quick Start

### Installation

**Using UV (Recommended):**
```bash
uv add comfyui-reality
```

**Using pip:**
```bash
pip install comfyui-reality
```

The ComfyUI nodes will be automatically available after installation - no manual setup required!

### Available Nodes

1. **🎨 AR Sticker Generator** - Generate AR-optimized stickers using FLUX/SDXL
2. **✂️ SAM2 Background Remover** - Advanced segmentation and background removal
3. **📦 USDZ AR Exporter** - Export production-ready AR files for iOS

## 🎛️ Node Documentation

### ARStickerGenerator

Generates high-quality stickers optimized for AR viewing using state-of-the-art diffusion models.

**Parameters:**
- `prompt`: Text description of desired sticker
- `sticker_style`: Style preset (cartoon, realistic, artistic, etc.)
- `background_style`: Background handling (clean_white, transparent, etc.)
- `width/height`: Output dimensions (recommended: 1024x1024)
- `guidance_scale`: Control prompt adherence (7.5 typical)
- `num_inference_steps`: Quality vs speed tradeoff (20-50)

### SAM2Segmenter

Advanced background removal using Meta's Segment Anything Model 2.

**Features:**
- Automatic subject detection
- Clean alpha channel generation
- Configurable edge smoothing
- Multiple output formats

### USDZExporter

Professional USDZ file creation for iOS ARKit compatibility.

**Specifications:**
- Y-up coordinate system
- 64-byte alignment
- <25MB file size optimization
- <25K vertex count limits
- 1024×1024 texture optimization

## 🛠️ Development

### Prerequisites

- Python 3.12+
- UV package manager
- NVIDIA GPU with CUDA (recommended)

### Development Setup

```bash
# Clone repository
git clone https://github.com/gerred/stickerkit.git
cd stickerkit/comfy-reality

# Install dependencies
uv sync --extra dev

# Install pre-commit hooks
pre-commit install

# Run tests
uv run pytest

# Lint code
uv run ruff check
uv run ruff format
```

### Project Structure

```
comfy-reality/
├── src/comfy_reality/     # Main package
│   ├── nodes/            # ComfyUI nodes
│   ├── models/           # Model loaders
│   └── utils/            # Shared utilities
├── tests/                # PyTest test suite
├── docs/                 # Documentation
├── examples/             # Example workflows
└── pyproject.toml        # Modern Python project config
```

## 📊 Performance

- **Sticker Generation**: ~10-30 seconds (depends on steps, GPU)
- **Background Removal**: ~2-5 seconds per image
- **USDZ Export**: ~1-3 seconds per file
- **Memory Usage**: ~6-12GB VRAM (varies by model)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [ComfyUI](https://github.com/comfyanonymous/ComfyUI) - The amazing node-based UI
- [Meta SAM2](https://github.com/facebookresearch/segment-anything-2) - Segmentation model
- [FLUX/SDXL](https://huggingface.co/black-forest-labs/FLUX.1-dev) - Diffusion models
- [USD](https://openusd.org/) - Universal Scene Description

## 🔗 Links

- [Repository](https://github.com/gerred/stickerkit)
- [Issues](https://github.com/gerred/stickerkit/issues)
- [Documentation](https://github.com/gerred/stickerkit#readme)
- [ComfyUI](https://www.comfy.org/)

---

**Made with ❤️ for the ComfyUI community**
