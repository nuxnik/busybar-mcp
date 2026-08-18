import os

from busybar_python_sdk import Configuration
from busybar_python_sdk.api_client import ApiClient

def _make_api(cls):
    """Create and return an API instance configured with env credentials."""
    base_url = os.environ.get("BUSYBAR_BASE_URL")
    api_token = os.environ.get("BUSYBAR_API_TOKEN")

    if not base_url:
        raise ValueError("Missing required environment variable: BUSYBAR_BASE_URL")
    if not api_token:
        raise ValueError("Missing required environment variable: BUSYBAR_API_TOKEN")

    config = Configuration(
        host=base_url,
        api_key={"ApiKeyAuth": api_token},
    )
    return cls(api_client=ApiClient(configuration=config))

def _serialize(obj):
    """Recursively serialize a busybar_python_sdk model to a JSON-serializable dict."""
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    if hasattr(obj, "to_dict"):
        return obj.to_dict()
    if hasattr(obj, "_to_dict"):
        return obj._to_dict()
    if isinstance(obj, list):
        return [_serialize(item) for item in obj]
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
