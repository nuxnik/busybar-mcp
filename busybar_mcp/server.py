"""MCP server construction and tool registration."""

from mcp.server.mcpserver import MCPServer

from .client import BusyBarClient
from .config import Settings


server = MCPServer("Busy Bar MCP")


def register_tools() -> None:
    """Import all tool modules so their decorators register with the server."""
    from .tools import account, ble, busy, input, settings, smarthome, storage, system, time, updater, wifi

    # Keep explicit references so registration remains obvious and import-time side effects are intentional.
    _ = (account, ble, busy, input, settings, smarthome, storage, system, time, updater, wifi)


def create_client() -> BusyBarClient:
    """Build a device client from environment configuration."""
    return BusyBarClient(Settings.from_env())


def run() -> None:
    """Run the MCP server over stdio."""
    register_tools()
    server.run(transport="stdio")
