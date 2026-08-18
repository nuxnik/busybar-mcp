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

@server.tool(name="enable_ble")
def enable_ble():
    """Enable the BLE module and start advertising.

    Issues POST /api/ble/enable via `BLEApi.api_ble_enable_post()` to turn on
    Bluetooth Low Energy and begin broadcasting.

    Use case:
        Enable BLE before attempting Bluetooth pairing or device discovery.
    """
    try:
        api = _make_api(BLEApi)
        result = api.api_ble_enable_post()
        return CallToolResult(content=[{"type": "text", "text": str(result.model_dump())}])
    except Exception as e:
        return _wrap_tool_error(f"Failed to enable BLE: {e}")

@server.tool(name="disable_ble")
def disable_ble():
    """Disable the BLE module and stop advertising.

    Issues POST /api/ble/disable via `BLEApi.api_ble_disable_post()` to turn off
    Bluetooth Low Energy and cease broadcasting.

    Use case:
        Disable BLE to save power or stop advertising when pairing is complete.
    """
    try:
        api = _make_api(BLEApi)
        result = api.api_ble_disable_post()
        return CallToolResult(content=[{"type": "text", "text": str(result.model_dump())}])
    except Exception as e:
        return _wrap_tool_error(f"Failed to disable BLE: {e}")

@server.tool(name="remove_ble_pairing")
def remove_ble_pairing():
    """Remove the current BLE pairing so the device becomes discoverable again.

    Issues DELETE /api/ble/pairing via `BLEApi.api_ble_pairing_delete()` to
    clear the existing Bluetooth pairing bond.

    Use case:
        Remove a stale pairing before re-pairing with a different device.
    """
    try:
        api = _make_api(BLEApi)
        result = api.api_ble_pairing_delete()
        return CallToolResult(content=[{"type": "text", "text": str(result.model_dump())}])
    except Exception as e:
        return _wrap_tool_error(f"Failed to remove BLE pairing: {e}")
