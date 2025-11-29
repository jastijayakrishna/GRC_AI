"""
Test runner for AI Auditor unit tests
"""
import pytest
import sys

if __name__ == "__main__":
    # Run all tests with verbose output
    exit_code = pytest.main([
        "tests/",
        "-v",
        "--tb=short",
        "--color=yes"
    ])

    sys.exit(exit_code)
