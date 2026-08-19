"""Busy Bar MCP package."""

from .server import server


def main() -> None:
    """Run the MCP server over stdio."""
    from .server import run

    run()


__all__ = ["main", "server"]
