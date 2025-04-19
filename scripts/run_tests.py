#!/usr/bin/env python3
"""
Test Runner for Agentic Game Framework.

This script provides a simple way to run the test suite
from the command line.
"""

import argparse
import sys
import pytest


def main():
    """Parse command line arguments and run the tests."""
    parser = argparse.ArgumentParser(
        description="Run tests for the Agentic Game Framework."
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    parser.add_argument(
        "--test-path",
        default="tests",
        help="Path to test directory or file (default: tests)"
    )
    
    parser.add_argument(
        "--unit-only",
        action="store_true",
        help="Run only unit tests (skip integration tests)"
    )
    
    parser.add_argument(
        "--integration-only",
        action="store_true",
        help="Run only integration tests"
    )
    
    args = parser.parse_args()
    
    # Build pytest arguments
    pytest_args = [args.test_path]
    
    if args.verbose:
        pytest_args.append("-v")
    
    # Filter tests if requested
    if args.unit_only:
        pytest_args.extend(["-k", "not test_integration"])
    elif args.integration_only:
        pytest_args.extend(["-k", "test_integration"])
    
    print("Agentic Game Framework - Test Runner")
    print("====================================")
    print(f"Running tests from: {args.test_path}")
    if args.unit_only:
        print("Mode: Unit tests only")
    elif args.integration_only:
        print("Mode: Integration tests only")
    else:
        print("Mode: All tests")
    print()
    
    # Run the tests
    result = pytest.main(pytest_args)
    
    return result


if __name__ == "__main__":
    sys.exit(main())