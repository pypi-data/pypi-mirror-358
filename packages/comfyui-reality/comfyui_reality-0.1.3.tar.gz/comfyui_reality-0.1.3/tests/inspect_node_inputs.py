#!/usr/bin/env python3
"""Inspect actual INPUT_TYPES and function signatures of nodes."""

import inspect
import sys

# Add current directory to path
sys.path.append(".")


def inspect_node(node_class, node_name):
    """Inspect a node's actual structure."""
    print(f"\n🔍 {node_name} ({node_class.__name__})")
    print("=" * 40)

    # Get INPUT_TYPES
    if hasattr(node_class, "INPUT_TYPES"):
        try:
            input_types = node_class.INPUT_TYPES()
            print("INPUT_TYPES:")
            if "required" in input_types:
                print("  Required:")
                for param, details in input_types["required"].items():
                    print(f"    {param}: {details}")
            if "optional" in input_types:
                print("  Optional:")
                for param, details in input_types["optional"].items():
                    print(f"    {param}: {details}")
        except Exception as e:
            print(f"  Error getting INPUT_TYPES: {e}")

    # Get FUNCTION and inspect the method
    if hasattr(node_class, "FUNCTION"):
        function_name = node_class.FUNCTION
        print(f"\nFUNCTION: {function_name}")

        if hasattr(node_class, function_name):
            method = getattr(node_class, function_name)
            sig = inspect.signature(method)
            print(f"Method signature: {sig}")
            print("Parameters:")
            for param_name, param in sig.parameters.items():
                if param_name != "self":
                    print(f"  {param_name}: {param.annotation if param.annotation != param.empty else 'Any'}")
        else:
            print(f"  ❌ Method {function_name} not found!")

    # Get RETURN_TYPES
    if hasattr(node_class, "RETURN_TYPES"):
        print(f"\nRETURN_TYPES: {node_class.RETURN_TYPES}")

    # Get CATEGORY
    if hasattr(node_class, "CATEGORY"):
        print(f"CATEGORY: {node_class.CATEGORY}")


def main():
    """Main inspection function."""
    try:
        import __init__ as comfy_reality_init

        mappings = comfy_reality_init.NODE_CLASS_MAPPINGS

        # Focus on the nodes that had issues
        problem_nodes = ["AROptimizer", "SpatialPositioner", "MaterialComposer", "RealityComposer"]

        for node_name in problem_nodes:
            if node_name in mappings:
                inspect_node(mappings[node_name], node_name)

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
