#!/usr/bin/env python3
"""Convenience test runner for the Busy Bar MCP test suite.

Invoke from the project root to run all tests in tests/:

    python run_tests.py          # basic run, --no-header
    COVERAGE=1 python run_tests.py  # enable coverage terminal output
"""

import os
import sys

import pytest


def main():
    """Run pytest with sensible defaults for the Busy Bar MCP project."""
    args = [
        "tests/",
        "--no-header",
        "-x",
    ]

    if os.environ.get("COVERAGE") == "1":
        # Coverage target: the busybar_mcp package (root module is busybar_mcp/__init__.py)
        args.extend([
            "-v",
            "--cov=busybar_mcp",
            "--cov-report=term-missing",
        ])

    exit_code = pytest.main(args)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
