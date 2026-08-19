"""Shared helpers for MCP tool implementations."""

from busybar_python_sdk.api_client import ApiClient

from .client import BusyBarClient
from .config import Settings


def _make_api(cls):
    """Create an SDK API instance using the validated environment settings."""
    return BusyBarClient(Settings.from_env()).api(cls)


def _serialize(obj):
    """Recursively serialize a busybar_python_sdk model to a JSON-serializable value."""
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    if hasattr(obj, "to_dict"):
        return obj.to_dict()
    if hasattr(obj, "_to_dict"):
        return obj._to_dict()
    if isinstance(obj, list):
        return [_serialize(item) for item in obj]
    if isinstance(obj, dict):
        return {key: _serialize(value) for key, value in obj.items()}
    return obj


def _flatten(d, prefix=""):
    """Flatten a nested dict into a single-level dict using `.` as key separator."""
    out = {}
    for k, v in d.items():
        key = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            out.update(_flatten(v, key))
        else:
            out[key] = v
    return out


def _wrap_tool_error(message):
    """Wrap an error message into a CallToolResult with is_error=True."""
    from mcp.types import CallToolResult

    return CallToolResult(content=[{"type": "text", "text": f"Error: {message}"}], is_error=True)
