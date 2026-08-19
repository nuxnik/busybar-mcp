"""MCP server construction and tool registration."""

from dotenv import load_dotenv
from mcp.server.mcpserver import MCPServer


server = MCPServer("Busy Bar MCP")


def register_tools() -> None:
    """Import all tool modules through one explicit registration boundary."""
    from . import tools

    # The imported package intentionally performs decorator registration.
    _ = tools


def run() -> None:
    """Load .env without overriding exported variables, then run over stdio."""
    load_dotenv(override=False)
    register_tools()
    server.run(transport="stdio")
