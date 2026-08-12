from busybar_python_sdk import BLEApi
from mcp.types import CallToolResult

from ._server import server
from .utils import _make_api, _serialize, _wrap_tool_error

@server.tool(name="get_ble_status")
def get_ble_status():
    """Retrieve BLE module status from the Busy Bar device.

    This tool queries GET /api/ble/status via `BLEApi.get_ble_status()` to return
    the current Bluetooth Low Energy module state.

    Returns a BleStatusResponse object containing:
        - status (str): Current BLE status string (e.g., "powered_on", "powered_off")
        - address (str | null): BLE MAC address if available

    Use case:
        Verify the BLE module is powered on and has a valid address before attempting
        Bluetooth operations like smart home pairing or device discovery.
    """
    try:
        api = _make_api(BLEApi)
        result = api.api_ble_status_get()
        return CallToolResult(content=[{"type": "text", "text": str(result.model_dump())}])
    except Exception as e:
        return _wrap_tool_error(f"Failed to get BLE status: {e}")
