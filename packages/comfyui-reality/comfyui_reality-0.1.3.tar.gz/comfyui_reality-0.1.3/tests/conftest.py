"""Pytest configuration and shared fixtures for ComfyReality tests."""

import shutil
import tempfile
from collections.abc import Generator
from pathlib import Path

import numpy as np
import pytest
import torch
from PIL import Image

# Test data paths
TEST_DATA_DIR = Path(__file__).parent / "test_data"
TEST_TEXTURE_PATH = Path("comfyui/input/test_texture.png")


@pytest.fixture(scope="session")
def test_data_dir() -> Path:
    """Provide path to test data directory."""
    return TEST_DATA_DIR


@pytest.fixture(scope="session")
def test_texture_image() -> Image.Image | None:
    """Load the test texture with corner markers for UV validation."""
    if TEST_TEXTURE_PATH.exists():
        return Image.open(TEST_TEXTURE_PATH)
    return None


@pytest.fixture(scope="session")
def test_texture_tensor(test_texture_image) -> torch.Tensor | None:
    """Convert test texture to ComfyUI tensor format."""
    if test_texture_image is None:
        return None

    # Convert PIL Image to numpy array
    image_np = np.array(test_texture_image)
    if image_np.shape[-1] == 4:  # RGBA
        image_np = image_np[:, :, :3]  # Remove alpha for basic tests

    # Normalize to 0-1 range
    image_np = image_np.astype(np.float32) / 255.0

    # Convert to ComfyUI format: [1, C, H, W] (BCHW)
    image_tensor = torch.from_numpy(image_np).permute(2, 0, 1).unsqueeze(0)

    return image_tensor


@pytest.fixture
def temp_output_dir() -> Generator[Path, None, None]:
    """Create temporary directory for test outputs."""
    temp_dir = Path(tempfile.mkdtemp(prefix="comfyreality_test_"))
    try:
        yield temp_dir
    finally:
        if temp_dir.exists():
            shutil.rmtree(temp_dir)


@pytest.fixture
def sample_image_tensor() -> torch.Tensor:
    """Create a sample image tensor for basic tests in BCHW format."""
    return torch.rand(1, 3, 512, 512)


@pytest.fixture
def sample_mask_tensor() -> torch.Tensor:
    """Create a sample mask tensor."""
    return torch.rand(1, 512, 512)


@pytest.fixture
def corner_marked_image() -> torch.Tensor:
    """Create a synthetic image with corner markers for UV validation.

    Creates a 512x512 image with distinct colors in each corner in BCHW format:
    - Top-Left: Green
    - Top-Right: Blue
    - Bottom-Left: Yellow
    - Bottom-Right: Magenta
    """
    image = torch.zeros(1, 3, 512, 512)

    # Define corner regions (64x64 pixels each)
    corner_size = 64

    # Top-Left: Green (0, 1, 0)
    image[0, 1, :corner_size, :corner_size] = 1.0

    # Top-Right: Blue (0, 0, 1)
    image[0, 2, :corner_size, -corner_size:] = 1.0

    # Bottom-Left: Yellow (1, 1, 0)
    image[0, 0, -corner_size:, :corner_size] = 1.0
    image[0, 1, -corner_size:, :corner_size] = 1.0

    # Bottom-Right: Magenta (1, 0, 1)
    image[0, 0, -corner_size:, -corner_size:] = 1.0
    image[0, 2, -corner_size:, -corner_size:] = 1.0

    return image


@pytest.fixture
def output_cleanup():
    """Fixture to clean up test output files after tests."""
    output_paths = []

    def register_path(path: Path):
        """Register a path for cleanup."""
        output_paths.append(path)

    yield register_path

    # Cleanup after test
    for path in output_paths:
        if path.exists():
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                shutil.rmtree(path)
