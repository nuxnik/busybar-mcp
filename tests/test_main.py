"""Smoke test for the package entry point.

Only verifies that ``busybar_mcp.main`` is importable and callable; it does
not start the server.
"""

import busybar_mcp


def test_main_is_importable():
    """busybar_mcp.main exists and is callable."""
    assert hasattr(busybar_mcp, "main")
    assert callable(busybar_mcp.main)
