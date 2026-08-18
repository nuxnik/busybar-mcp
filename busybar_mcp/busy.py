import json

from busybar_python_sdk import BusyApi
from mcp.types import CallToolResult

from ._server import server
from .utils import _flatten, _make_api, _wrap_tool_error

@server.tool(name="get_busy_snapshot")
def get_busy_snapshot():
    """Retrieve the current BUSY timer snapshot from the Busy Bar device.

    This tool queries the BUSY bar to return the current BUSY timer state including active profile and timing details.

    Returns a flat JSON object (single-level keys, nested structure joined with `.`):
        - type (str): One of "SIMPLE", "INTERVAL", "INFINITE", or "NOT_STARTED"
        - Simple type keys: card_id (uuid), is_paused (bool), time_left_ms (int)
        - Interval type keys: current_interval (int), current_interval_time_total_ms (int),
          current_interval_time_left_ms (int), interval_settings.* (nested keys from interval settings)
        - snapshot_timestamp_ms (int): Timestamp of the snapshot in milliseconds since epoch

    Use case:
        Check what BUSY timer profile is currently active and how much time remains
        before scheduling display messages or other operations around the timer.
    """
    try:
        api = _make_api(BusyApi)
        rest_response = api.get_busy_snapshot_without_preload_content()
        payload = json.loads(rest_response.read().decode("utf-8"))
        flat = _flatten(payload)
        return CallToolResult(content=[{"type": "text", "text": json.dumps(flat, ensure_ascii=False)}])
    except Exception as e:
        return _wrap_tool_error(f"Failed to get busy snapshot: {e}")

