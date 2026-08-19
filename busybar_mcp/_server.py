"""Backward-compatible server import for existing tool modules."""

from .server import server

MCPServer = type(server)
