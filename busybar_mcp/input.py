from typing import Literal

from busybar_python_sdk import InputApi
from mcp.types import CallToolResult

from ._server import server
from .utils import _make_api, _wrap_tool_error


@server.tool(name="send_input_key")
def send_input_key(key: Literal["up", "down", "ok", "back", "start", "busy", "custom", "off", "apps", "settings"]):
    """Send a single key-press input event to the Busy Bar device.

    Issues POST /api/input via `InputApi.set_input_key(key)` to simulate a
    physical button press on the device.

    Args:
        key: The key to send. One of: up, down, ok, back, start, busy, custom,
             off, apps, settings.

    Use case:
        Remotely trigger a key action on the device, e.g. start/stop a BUSY
        timer or navigate system menus.
    """
    try:
        api = _make_api(InputApi)
        result = api.set_input_key(key)
        return CallToolResult(content=[{"type": "text", "text": str(result.model_dump())}])
    except Exception as e:
        return _wrap_tool_error(f"Failed to send input key '{key}': {e}")
