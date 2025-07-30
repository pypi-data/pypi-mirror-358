#!/usr/bin/env python3
"""Test script to verify ComfyUI node structure and discoverability."""

import sys
import traceback
from typing import Any

# Add current directory to path
sys.path.append(".")


def test_node_structure(node_class: type, node_name: str) -> dict[str, Any]:
    """Test a node's ComfyUI structure requirements."""
    results = {
        "name": node_name,
        "class_name": node_class.__name__,
        "has_input_types": False,
        "has_return_types": False,
        "has_function": False,
        "has_category": False,
        "has_execute_method": False,
        "function_matches_method": False,
        "input_types_structure": None,
        "return_types_structure": None,
        "function_name": None,
        "category": None,
        "errors": [],
        "warnings": [],
    }

    try:
        # Check INPUT_TYPES classmethod
        if hasattr(node_class, "INPUT_TYPES") and callable(node_class.INPUT_TYPES):
            results["has_input_types"] = True
            try:
                input_types = node_class.INPUT_TYPES()
                results["input_types_structure"] = type(input_types).__name__
                if not isinstance(input_types, dict):
                    results["warnings"].append(f"INPUT_TYPES() returns {type(input_types)} instead of dict")
                elif "required" not in input_types:
                    results["warnings"].append("INPUT_TYPES() missing 'required' key")
            except Exception as e:
                results["errors"].append(f"INPUT_TYPES() call failed: {e}")
        else:
            results["errors"].append("Missing INPUT_TYPES classmethod")

        # Check RETURN_TYPES
        if hasattr(node_class, "RETURN_TYPES"):
            results["has_return_types"] = True
            return_types = node_class.RETURN_TYPES
            results["return_types_structure"] = (
                f"{type(return_types).__name__} with {len(return_types) if hasattr(return_types, '__len__') else '?'} items"
            )
            if not isinstance(return_types, (tuple, list)):
                results["warnings"].append(f"RETURN_TYPES is {type(return_types)} instead of tuple/list")
        else:
            results["errors"].append("Missing RETURN_TYPES attribute")

        # Check FUNCTION
        if hasattr(node_class, "FUNCTION"):
            results["has_function"] = True
            function_name = node_class.FUNCTION
            results["function_name"] = function_name
            if not isinstance(function_name, str):
                results["warnings"].append(f"FUNCTION is {type(function_name)} instead of str")
            else:
                # Check if corresponding method exists
                if hasattr(node_class, function_name):
                    results["has_execute_method"] = True
                    results["function_matches_method"] = True
                else:
                    results["errors"].append(f"Method '{function_name}' not found (specified in FUNCTION)")
        else:
            results["errors"].append("Missing FUNCTION attribute")

        # Check CATEGORY
        if hasattr(node_class, "CATEGORY"):
            results["has_category"] = True
            category = node_class.CATEGORY
            results["category"] = category
            if not isinstance(category, str):
                results["warnings"].append(f"CATEGORY is {type(category)} instead of str")
        else:
            results["errors"].append("Missing CATEGORY attribute")

        # Additional checks
        if hasattr(node_class, "OUTPUT_NODE"):
            results["is_output_node"] = node_class.OUTPUT_NODE

        if hasattr(node_class, "DESCRIPTION"):
            results["has_description"] = True

    except Exception as e:
        results["errors"].append(f"General inspection failed: {e}")

    return results


def test_sample_execution(node_class: type, node_name: str) -> dict[str, Any]:
    """Test node with sample inputs to check for crashes."""
    results = {"can_instantiate": False, "instantiation_error": None, "sample_execution_attempted": False, "sample_execution_error": None}

    try:
        # Try to instantiate the node
        node_instance = node_class()
        results["can_instantiate"] = True

        # Try to get sample inputs based on INPUT_TYPES
        if hasattr(node_class, "INPUT_TYPES"):
            try:
                input_types = node_class.INPUT_TYPES()
                if isinstance(input_types, dict) and "required" in input_types:
                    required = input_types["required"]
                    sample_inputs = {}

                    # Generate sample inputs
                    for param_name, param_info in required.items():
                        if isinstance(param_info, tuple) and len(param_info) > 0:
                            param_type = param_info[0]
                            if isinstance(param_type, list):
                                # Choice parameter
                                sample_inputs[param_name] = param_type[0] if param_type else ""
                            elif param_type == "STRING":
                                sample_inputs[param_name] = "test"
                            elif param_type == "INT":
                                sample_inputs[param_name] = 1
                            elif param_type == "FLOAT":
                                sample_inputs[param_name] = 1.0
                            elif param_type == "BOOLEAN":
                                sample_inputs[param_name] = True
                            elif param_type == "IMAGE":
                                # Skip image inputs for basic test
                                continue
                            else:
                                # Unknown type, skip
                                continue

                    # Only attempt execution if we have basic parameters
                    if sample_inputs and hasattr(node_class, "FUNCTION"):
                        function_name = node_class.FUNCTION
                        if hasattr(node_instance, function_name):
                            execute_method = getattr(node_instance, function_name)
                            results["sample_execution_attempted"] = True
                            # Note: Not actually executing to avoid side effects

            except Exception as e:
                results["sample_execution_error"] = str(e)

    except Exception as e:
        results["instantiation_error"] = str(e)

    return results


def main():
    """Main test function."""
    print("🧪 Testing ComfyUI Node Structure and Discoverability")
    print("=" * 60)

    # Test node discovery
    try:
        import __init__ as comfy_reality_init

        if not hasattr(comfy_reality_init, "NODE_CLASS_MAPPINGS"):
            print("❌ CRITICAL: NODE_CLASS_MAPPINGS not found in __init__.py")
            return

        mappings = comfy_reality_init.NODE_CLASS_MAPPINGS
        print(f"✅ Found {len(mappings)} nodes in NODE_CLASS_MAPPINGS")

        display_mappings = getattr(comfy_reality_init, "NODE_DISPLAY_NAME_MAPPINGS", {})
        print(f"✅ Found {len(display_mappings)} display names")

    except Exception as e:
        print(f"❌ CRITICAL: Failed to import root __init__.py: {e}")
        traceback.print_exc()
        return

    print("\n📋 Testing Individual Nodes")
    print("-" * 40)

    all_results = []

    for node_name, node_class in mappings.items():
        print(f"\n🔍 Testing {node_name} ({node_class.__name__})")

        # Test structure
        structure_results = test_node_structure(node_class, node_name)

        # Test instantiation
        execution_results = test_sample_execution(node_class, node_name)

        # Combine results
        combined_results = {**structure_results, **execution_results}
        all_results.append(combined_results)

        # Print immediate results
        errors = structure_results["errors"]
        warnings = structure_results["warnings"]

        if not errors:
            print("  ✅ Structure: OK")
        else:
            print(f"  ❌ Structure: {len(errors)} errors")
            for error in errors:
                print(f"    • {error}")

        if warnings:
            print(f"  ⚠️  Warnings: {len(warnings)}")
            for warning in warnings:
                print(f"    • {warning}")

        if execution_results["can_instantiate"]:
            print("  ✅ Instantiation: OK")
        else:
            print(f"  ❌ Instantiation: {execution_results['instantiation_error']}")

    # Summary
    print("\n📊 Summary")
    print("-" * 20)

    total_nodes = len(all_results)
    nodes_with_errors = sum(1 for r in all_results if r["errors"])
    nodes_with_warnings = sum(1 for r in all_results if r["warnings"])
    nodes_can_instantiate = sum(1 for r in all_results if r["can_instantiate"])

    print(f"Total nodes: {total_nodes}")
    print(f"Nodes with errors: {nodes_with_errors}")
    print(f"Nodes with warnings: {nodes_with_warnings}")
    print(f"Nodes that can instantiate: {nodes_can_instantiate}")

    # Check required ComfyUI attributes
    required_attrs = ["has_input_types", "has_return_types", "has_function", "has_category"]
    for attr in required_attrs:
        count = sum(1 for r in all_results if r.get(attr, False))
        print(f"Nodes with {attr.replace('has_', '').replace('_', ' ').title()}: {count}/{total_nodes}")

    if nodes_with_errors == 0:
        print("\n🎉 All nodes passed structural tests!")
    else:
        print(f"\n⚠️  {nodes_with_errors} nodes need fixes")

        # List problematic nodes
        print("\nNodes needing fixes:")
        for result in all_results:
            if result["errors"]:
                print(f"  • {result['name']}: {len(result['errors'])} errors")

    return all_results


if __name__ == "__main__":
    results = main()
