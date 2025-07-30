# UV Orientation Validation Test Suite

This document describes the comprehensive UV orientation validation test suite for ComfyReality's USDZExporter node.

## Overview

The test suite validates that texture UV coordinates are correctly oriented in exported USDZ files, ensuring that textures appear correctly in AR viewers without being flipped or rotated.

## Test Components

### 1. Enhanced Test Suite (`test_usdz_exporter_enhanced.py`)

**Purpose**: Comprehensive automated testing with UV orientation validation

**Key Features**:
- Converts the original `test_direct_usdz.py` into proper pytest format
- Automated UV orientation validation using corner markers
- Tests multiple material types and coordinate systems
- File size validation for iOS ARKit compliance
- Integration with existing test infrastructure

**Test Categories**:
- Direct export with real test texture
- Synthetic image validation with corner markers
- UV coordinate extraction and validation (when USD libraries available)
- Material type consistency testing
- Coordinate system validation
- File format and size compliance

### 2. Test Fixtures (`conftest.py`)

**Purpose**: Shared test infrastructure and data

**Provides**:
- Test texture loading from `comfyui/input/test_texture.png`
- Synthetic corner-marked image generation
- Temporary directory management
- Output cleanup utilities
- Sample tensor generation

### 3. Manual Validation Generator (`scripts/generate_validation_usdz.py`)

**Purpose**: Generate USDZ files for manual inspection

**Features**:
- Creates multiple test images with different patterns
- Generates USDZ files with various configurations
- Produces validation report with test results
- Provides manual validation instructions

**Generated Test Images**:
- Gradient with corner markers
- Checkerboard with colored corners
- Real test texture variations
- Different material types and sizes

### 4. Test Runner (`scripts/run_uv_tests.py`)

**Purpose**: Unified test execution interface

**Capabilities**:
- Run pytest tests with filtering options
- Generate validation files
- Combined test execution
- Detailed reporting

### 5. UV Validation Utilities (`src/comfy_reality/utils/uv_validation.py`)

**Purpose**: Programmatic UV orientation validation

**Features**:
- USDZ file structure validation
- Texture extraction from USDZ files
- Corner marker color analysis
- UV coordinate extraction (with USD libraries)
- Comprehensive validation reporting

## UV Orientation Testing Method

### Corner Marker System

The test suite uses a consistent corner marker system to validate UV orientation:

```
+---+-------+---+
| G |  TOP  | R |  <- Green (TL), Red (TR)
+---+-------+---+
|   |       |   |
| L |  MID  | R |
| E |       | I |
| F |       | G |
| T |       | H |
|   |       | T |
+---+-------+---+
| B | BOTTOM| Y |  <- Blue (BL), Yellow (BR)
+---+-------+---+
```

**Expected Orientation**:
- **Top-Left (TL)**: Green `(0, 255, 0)` or White `(255, 255, 255)`
- **Top-Right (TR)**: Red `(255, 0, 0)`
- **Bottom-Left (BL)**: Blue `(0, 0, 255)`
- **Bottom-Right (BR)**: Yellow `(255, 255, 0)`

### Validation Process

1. **Automated Testing**:
   - Extract texture from USDZ file
   - Analyze corner regions for expected colors
   - Validate with configurable color tolerance
   - Check UV coordinate values (when USD available)

2. **Manual Validation**:
   - Open USDZ files in iOS AR Quick Look
   - Visual inspection of corner marker positions
   - Verify gradients and patterns appear correctly

## Running the Tests

### Quick Start

```bash
# Run all UV validation tests
./scripts/run_uv_tests.py

# Run only automated tests
./scripts/run_uv_tests.py --test-only

# Generate validation files only
./scripts/run_uv_tests.py --generate-only

# Run with verbose output
./scripts/run_uv_tests.py --verbose
```

### Individual Components

```bash
# Run enhanced tests only
uv run pytest tests/test_usdz_exporter_enhanced.py -v

# Generate manual validation files
./scripts/generate_validation_usdz.py

# Run with specific pytest markers
uv run pytest tests/test_usdz_exporter_enhanced.py -m "not slow"
```

### CI/CD Integration

```bash
# Run tests suitable for CI (no manual validation)
uv run pytest tests/test_usdz_exporter_enhanced.py -m "not integration"

# Run with coverage
uv run pytest tests/test_usdz_exporter_enhanced.py --cov=src/comfy_reality
```

## Test Data Requirements

### Required Files

- `comfyui/input/test_texture.png`: Real test texture with corner markers (TL, TR, BL, BR)

### Optional Files

- Additional test textures in `tests/test_data/`
- Custom validation images for specific test cases

## Validation Criteria

### Automated Tests

- ✅ USDZ file structure is valid
- ✅ File size is within iOS ARKit limits (< 25MB)
- ✅ Texture is correctly embedded
- ✅ Corner markers are in correct positions
- ✅ UV coordinates match expected values (when USD available)

### Manual Validation

- ✅ Texture appears correctly oriented in AR viewer
- ✅ No unwanted flipping or rotation
- ✅ Corner markers visually match expected positions
- ✅ Gradients flow in correct directions

## Expected Results

### Test Image Characteristics

The test texture (`comfyui/input/test_texture.png`) contains:
- Corner markers: TL (green), TR (blue), BL (yellow), BR (purple)
- "TOP" text at the top
- "BOTTOM" text at the bottom
- Directional arrow pointing up
- Gradient from teal (top) to pink (bottom)

### Correct UV Orientation

When the USDZ file is correctly generated:
- The texture should appear exactly as in the source image
- "TOP" should be at the top of the AR object
- "BOTTOM" should be at the bottom of the AR object
- Corner markers should match the expected color positions
- The gradient should flow from teal (top) to pink (bottom)

## Troubleshooting

### Common Issues

1. **Test texture not found**:
   - Ensure `comfyui/input/test_texture.png` exists
   - Tests will skip if texture is unavailable

2. **UV coordinate extraction fails**:
   - Requires USD libraries (`pip install usd-core`)
   - Tests marked with `@pytest.mark.skipif` will skip if unavailable

3. **File size too large**:
   - Check optimization level settings
   - Ensure mobile optimization is working correctly

4. **Corner marker validation fails**:
   - Check color tolerance settings
   - Verify texture is being extracted correctly from USDZ

### Debug Mode

Enable debug output for detailed validation information:

```bash
# Verbose pytest output
uv run pytest tests/test_usdz_exporter_enhanced.py -v -s

# Detailed validation generation
./scripts/generate_validation_usdz.py --verbose
```

## Integration with Existing Tests

The enhanced test suite integrates with the existing `test_usdz_exporter.py`:

- Shared fixtures and utilities
- Consistent test patterns and naming
- Compatible with existing CI/CD pipelines
- Extends rather than replaces existing functionality

## Future Enhancements

Potential improvements to the test suite:

1. **Advanced UV Analysis**: More sophisticated UV coordinate validation
2. **Performance Testing**: Benchmark export times and optimization effectiveness
3. **Cross-Platform Testing**: Test on different AR platforms and viewers
4. **Automated Visual Comparison**: Image diff analysis for texture validation
5. **Stress Testing**: Large images, complex textures, edge cases