from busybar_python_sdk import SmartHomeApi
from mcp.types import CallToolResult

from ._server import server
from .utils import _make_api, _serialize, _wrap_tool_error

@server.tool(name="get_smart_home_pairing_status")
def get_smart_home_pairing_status():
    """Retrieve smart home commissioning (pairing) status from the Busy Bar device.

    This tool queries GET /api/smart_home/pairing via `SmartHomeApi.get_smart_home_commissioning_status()`
    to learn how many Matter fabric entries exist and the latest pairing outcome.

    Returns a SmartHomePairingInfo object containing:
        - fabric_count (int): Number of commissioned Matter fabrics
        - latest_pairing_status (str | null): Status of the most recent pairing attempt
            (e.g., "success", "failure", or null if no attempt yet)

    Use case:
        Verify smart home device commissioning state before troubleshooting connectivity,
        confirming pairings, or starting a new setup flow.
    """
    try:
        api = _make_api(SmartHomeApi)
        result = api.get_smart_home_commissioning_status()
        return CallToolResult(content=[{"type": "text", "text": str(result.model_dump())}])
    except Exception as e:
        return _wrap_tool_error(f"Failed to get smart home pairing status: {e}")


@server.tool(name="get_smart_home_switch_state")
def get_smart_home_switch_state():
    """Retrieve smart home switch (output) state from the Busy Bar device.

    This tool queries GET /api/smart_home/switch via `SmartHomeApi.get_smart_home_switch_state()`
    to read the current relay/driver output configuration.

    Returns a SmartHomeSwitchState object containing:
        - state (str): Current switch/output state (e.g., "on", "off")
        - startup (str | null): Startup behavior — what the switch does on power-on
            (e.g., "restore", "on", "off", "unknown")

    Use case:
        Check whether a smart home relay is currently active or inspect its configured
        startup behavior to avoid unexpected device activation after power events.
    """
    try:
        api = _make_api(SmartHomeApi)
        result = api.api_smart_home_switch_get()
        return CallToolResult(content=[{"type": "text", "text": str(result.model_dump())}])
    except Exception as e:
        return _wrap_tool_error(f"Failed to get smart home switch state: {e}")
