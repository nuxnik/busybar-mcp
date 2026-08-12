from busybar_python_sdk import SettingsApi
from mcp.types import CallToolResult

from ._server import server
from .utils import _make_api, _serialize, _wrap_tool_error

@server.tool(name="get_http_access")
def get_http_access():
    """Retrieve HTTP access configuration from the Busy Bar device.

    This tool queries GET /api/access via `SettingsApi.get_http_access()` to obtain
    the current HTTP API key management mode and validity state.

    Returns an HttpAccessInfo object containing:
        - mode (str): HTTP access mode — one of "default", "custom_key", or "disabled"
        - key_valid (bool): Whether the configured key is currently valid

    Use case:
        Inspect HTTP access configuration before deploying tools that rely on the device's
        HTTP API (e.g., remote messaging) to confirm the key setup is correct.
    """
    try:
        api = _make_api(SettingsApi)
        result = api.get_http_access()
        return CallToolResult(content=[{"type": "text", "text": str(result.model_dump())}])
    except Exception as e:
        return _wrap_tool_error(f"Failed to get HTTP access settings: {e}")


@server.tool(name="get_device_name")
def get_device_name():
    """Retrieve the device name configured on the Busy Bar device.

    This tool queries GET /api/name via `SettingsApi.get_name()` to obtain
    the human-readable name currently set for this unit.

    Returns a NameInfo object containing:
        - name (str): The device name (e.g., "My Busy Bar")

    Use case:
        Confirm or audit the display name shown on the device, especially useful in
        multi-device setups where each unit needs an identifiable label.
    """
    try:
        api = _make_api(SettingsApi)
        result = api.api_name_get()
        return CallToolResult(content=[{"type": "text", "text": str(result.model_dump())}])
    except Exception as e:
        return _wrap_tool_error(f"Failed to get device name: {e}")


@server.tool(name="get_display_brightness")
def get_display_brightness():
    """Retrieve the display brightness setting from the Busy Bar device.

    This tool queries GET /api/display/brightness via `SettingsApi.get_display_brightness()`
    to obtain the current screen brightness level.

    Returns a DisplayBrightnessInfo object containing:
        - value (int): Brightness level as an integer percentage or stepped value

    Use case:
        Check brightness before adjusting display behavior, or audit settings during
        device configuration management.
    """
    try:
        api = _make_api(SettingsApi)
        result = api.get_display_brightness()
        return CallToolResult(content=[{"type": "text", "text": str(result.model_dump())}])
    except Exception as e:
        return _wrap_tool_error(f"Failed to get display brightness: {e}")


@server.tool(name="get_audio_volume")
def get_audio_volume():
    """Retrieve the audio volume setting from the Busy Bar device.

    This tool queries GET /api/audio/volume via `SettingsApi.get_audio_volume()`
    to obtain the current volume level configuration.

    Returns an AudioVolumeInfo object containing:
        - volume (int): Volume level as an integer value

    Use case:
        Check or audit volume settings before playing audio notifications or tones;
        useful for confirming device is configured at an audible level.
    """
    try:
        api = _make_api(SettingsApi)
        result = api.get_audio_volume()
        return CallToolResult(content=[{"type": "text", "text": str(result.model_dump())}])
    except Exception as e:
        return _wrap_tool_error(f"Failed to get audio volume: {e}")
