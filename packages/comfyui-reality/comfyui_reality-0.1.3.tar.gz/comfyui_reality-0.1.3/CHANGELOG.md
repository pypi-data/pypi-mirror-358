# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.3] - 2025-06-30

### Added
- PyPI version badge in README for package visibility

### Changed
- Updated installation instructions to use correct package name `comfyui-reality`

## [0.1.2] - 2025-06-30

### Added
- PyTorch and torchvision as core dependencies for proper ComfyUI node functionality
- ComfyUI cookiecutter template compliance for registry submission
- GitHub workflows for automated testing, building, and publishing
- Root-level `__init__.py` for proper ComfyUI node discovery
- `MANIFEST.in` for proper package distribution
- Registry metadata in `[tool.comfy]` section

### Changed
- Project name from `comfy-reality` to `comfyui-reality` for registry consistency
- Ruff line length increased from 88 to 140 characters (cookiecutter standard)
- Repository structure reorganized for ComfyUI compatibility
- Test files moved to proper `tests/` directory structure
- Build system updated with proper ComfyUI registry configuration

### Fixed
- Missing PyTorch dependency causing import errors
- ComfyUI node discovery and registration
- Duplicate dependencies in pyproject.toml
- Code formatting and linting issues
- Package installation and distribution

### Removed
- Redundant test files from repository root
- Build artifacts and temporary files
- Duplicate dependency entries

## [0.1.1] - 2025-06-30

### Fixed
- Initial dependency and configuration issues

## [0.1.0] - 2025-06-30

### Added
- Initial release of ComfyUI Reality nodes
- 10 AR/USDZ creation nodes for ComfyUI:
  - USDZExporter - Export AR-ready USDZ files
  - AROptimizer - Mobile AR performance optimization  
  - SpatialPositioner - 3D positioning and scale
  - MaterialComposer - PBR material workflow
  - RealityComposer - Multi-object scene composition
  - CrossPlatformExporter - Export to multiple AR formats
  - AnimationBuilder - Keyframe animation for AR objects
  - PhysicsIntegrator - Collision and physics properties
  - FluxARGenerator - FLUX-based AR content generation
  - ARBackgroundRemover - Background removal for AR stickers
- Professional USDZ export for iOS ARKit
- Mobile-optimized AR content creation pipeline
- Comprehensive test suite with 58% code coverage
- Modern Python packaging with uv support
