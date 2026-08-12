from busybar_python_sdk import BusyApi
from mcp.types import CallToolResult

from ._server import server
from .utils import _make_api, _serialize, _wrap_tool_error

@server.tool(name="get_busy_snapshot")
def get_busy_snapshot():
    """Retrieve the current BUSY timer snapshot from the Busy Bar device.

    This tool queries GET /api/busy/snapshot via `BusyApi.get_busy_snapshot()` to
    return the current BUSY timer state including active profile and timing details.

    Returns a BusySnapshot object containing:
        - snapshot (BusySnapshotSnapshot): The busy snapshot data — varies by type:
            - BusySnapshotSimple: started (bool), remaining_ms (int)
            - BusySnapshotInterval: started, remaining_ms, interval_index, intervals_count
            - BusySnapshotInfinite: started (bool)
            - BusySnapshotNotStarted: fields not applicable
        - snapshot_timestamp_ms (int): Timestamp of the snapshot in milliseconds since epoch

    Use case:
        Check what BUSY timer profile is currently active and how much time remains
        before scheduling display messages or other operations around the timer.
    """
    try:
        api = _make_api(BusyApi)
        result = api.get_busy_snapshot()
        return CallToolResult(content=[{"type": "text", "text": str(result.model_dump())}])
    except Exception as e:
        return _wrap_tool_error(f"Failed to get busy snapshot: {e}")
