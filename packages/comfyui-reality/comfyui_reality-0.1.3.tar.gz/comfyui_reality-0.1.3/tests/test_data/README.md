# Test Data Directory

This directory contains test data files used by the ComfyReality test suite.

## Contents

- Test textures with UV orientation markers
- Sample USDZ files for validation
- Reference images for comparison testing

## UV Orientation Test Textures

Test textures in this directory use the following corner marker convention:

- **Top-Left (TL)**: Green or White
- **Top-Right (TR)**: Red  
- **Bottom-Left (BL)**: Blue
- **Bottom-Right (BR)**: Yellow

This allows for automated and visual validation of UV coordinate orientation in exported USDZ files.

## Usage

Test textures are automatically loaded by the test fixtures in `conftest.py`. The main test texture is located at `comfyui/input/test_texture.png`.