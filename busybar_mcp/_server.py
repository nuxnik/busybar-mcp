"""Backward-compatible server import for existing tool modules."""

from mcp.server.mcpserver import MCPServer

from .server import server

__all__ = ["MCPServer", "server"]
