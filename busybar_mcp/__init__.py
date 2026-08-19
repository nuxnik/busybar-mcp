"""Busy Bar MCP package."""

from .server import server


def main() -> None:
    """Load environment configuration and run the MCP server over stdio."""
    from dotenv import load_dotenv

    load_dotenv()
    from .server import run

    run()


__all__ = ["main", "server"]
