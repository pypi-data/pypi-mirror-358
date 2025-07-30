#!/usr/bin/env python3
"""Run UV orientation validation tests for ComfyReality."""

import argparse
import subprocess
import sys
from pathlib import Path


def run_pytest_tests(test_pattern: str = None, verbose: bool = False, markers: str = None) -> int:
    """Run pytest tests with optional filtering."""
    cmd = ["uv", "run", "pytest"]

    # Add test path
    if test_pattern:
        cmd.append(f"tests/{test_pattern}")
    else:
        cmd.extend(["tests/test_usdz_exporter.py", "tests/test_usdz_exporter_enhanced.py"])

    # Add verbosity
    if verbose:
        cmd.append("-v")
    else:
        cmd.append("-q")

    # Add marker filtering
    if markers:
        cmd.extend(["-m", markers])

    # Add coverage if available
    cmd.extend(["--cov=src/comfy_reality", "--cov-report=term-missing"])

    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=Path(__file__).parent.parent)
    return result.returncode


def run_validation_generator(output_dir: Path = None, quiet: bool = False) -> int:
    """Run the validation file generator."""
    cmd = ["python", "scripts/generate_validation_usdz.py"]

    if output_dir:
        cmd.extend(["--output-dir", str(output_dir)])

    if quiet:
        cmd.append("--quiet")

    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=Path(__file__).parent.parent)
    return result.returncode


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run ComfyReality UV orientation validation tests")
    parser.add_argument("--test-only", "-t", action="store_true", help="Run only pytest tests")
    parser.add_argument("--generate-only", "-g", action="store_true", help="Run only validation file generation")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--output-dir", "-o", type=Path, help="Output directory for validation files")
    parser.add_argument("--markers", "-m", help="Pytest marker expression (e.g., 'not slow')")
    parser.add_argument("--pattern", "-p", help="Test file pattern to run")

    args = parser.parse_args()

    print("🧪 ComfyReality UV Orientation Test Runner")
    print("=" * 45)

    exit_code = 0

    # Run pytest tests
    if not args.generate_only:
        print("\n📋 Running pytest tests...")
        pytest_result = run_pytest_tests(test_pattern=args.pattern, verbose=args.verbose, markers=args.markers)
        if pytest_result != 0:
            print("❌ Pytest tests failed")
            exit_code = pytest_result
        else:
            print("✅ Pytest tests passed")

    # Run validation file generation
    if not args.test_only:
        print("\n🎨 Generating validation files...")
        gen_result = run_validation_generator(output_dir=args.output_dir, quiet=not args.verbose)
        if gen_result != 0:
            print("❌ Validation file generation failed")
            exit_code = gen_result
        else:
            print("✅ Validation files generated successfully")

    if exit_code == 0:
        print("\n🎉 All UV orientation validation tests completed successfully!")
        print("\n📱 Next steps:")
        print("1. Check generated USDZ files in output/uv_validation/")
        print("2. Open files in iOS AR Quick Look for manual validation")
        print("3. Verify corner markers are correctly positioned")
    else:
        print(f"\n❌ Tests completed with errors (exit code: {exit_code})")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
