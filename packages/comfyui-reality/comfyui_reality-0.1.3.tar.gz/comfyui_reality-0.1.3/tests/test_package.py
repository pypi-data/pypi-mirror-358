"""Test package imports and basic functionality."""

import pytest


def test_package_import():
    """Test that the main package imports correctly."""
    from comfy_reality import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

    assert isinstance(NODE_CLASS_MAPPINGS, dict)
    assert isinstance(NODE_DISPLAY_NAME_MAPPINGS, dict)
    assert len(NODE_CLASS_MAPPINGS) > 0
    assert len(NODE_DISPLAY_NAME_MAPPINGS) > 0


def test_node_mappings():
    """Test that all expected nodes are available."""
    from comfy_reality import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

    expected_nodes = [
        "USDZExporter",
        "AROptimizer",
        "SpatialPositioner",
        "MaterialComposer",
        "RealityComposer",
        "CrossPlatformExporter",
        "AnimationBuilder",
        "PhysicsIntegrator",
    ]

    for node_name in expected_nodes:
        assert node_name in NODE_CLASS_MAPPINGS
        assert node_name in NODE_DISPLAY_NAME_MAPPINGS


def test_version():
    """Test that version is available."""
    from comfy_reality import __version__

    assert isinstance(__version__, str)
    assert len(__version__) > 0


@pytest.mark.slow
def test_node_instantiation():
    """Test that nodes can be instantiated."""
    from comfy_reality.nodes import AROptimizer, MaterialComposer, SpatialPositioner, USDZExporter

    # Should not raise exceptions
    USDZExporter()
    AROptimizer()
    SpatialPositioner()
    MaterialComposer()
