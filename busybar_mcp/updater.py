from busybar_python_sdk import UpdaterApi
from mcp.types import CallToolResult

from ._server import server
from .utils import _make_api, _serialize, _wrap_tool_error

@server.tool(name="get_firmware_update_status")
def get_firmware_update_status():
    """Retrieve firmware update state from the Busy Bar device.

    This tool queries GET /api/update/status via `UpdaterApi.get_firmware_update_status()`
    to learn about the current and pending firmware states.

    Returns an UpdateStatus object containing:
        - install (UpdateStatusInstall): The currently installed firmware info — version, etc.
        - check (UpdateStatusCheck): Status of the latest automatic or manual update check

    Use case:
        Verify which firmware is running and whether a new update has been detected but
        not yet installed — useful for maintenance and rollout planning.
    """
    try:
        api = _make_api(UpdaterApi)
        result = api.get_firmware_update_status()
        return CallToolResult(content=[{"type": "text", "text": str(result.model_dump())}])
    except Exception as e:
        return _wrap_tool_error(f"Failed to get firmware update status: {e}")


@server.tool(name="get_update_changelog")
def get_update_changelog(version: str):
    """Retrieve the changelog for a specific firmware version from the Busy Bar device.

    This tool queries GET /api/update/changelog via `UpdaterApi.get_update_changelog(version)`
    to obtain release notes and change details for the given firmware version.

    Args:
        version: The firmware version string to fetch the changelog for (e.g., "1.0.0").

    Returns a GetUpdateChangelog200Response object containing:
        - changelog (str): Human-readable release notes and change log text

    Use case:
        Review what changed in a specific firmware revision before deploying updates,
        or compare versions to understand new features and bug fixes.
    """
    try:
        api = _make_api(UpdaterApi)
        result = api.get_update_changelog(version=version)
        return CallToolResult(content=[{"type": "text", "text": str(result.model_dump())}])
    except Exception as e:
        return _wrap_tool_error(f"Failed to get changelog for version {version!r}: {e}")


@server.tool(name="get_autoupdate_settings")
def get_autoupdate_settings():
    """Retrieve automatic firmware update settings from the Busy Bar device.

    This tool queries GET /api/update/autoupdate via `UpdaterApi.get_autoupdate_settings()`
    to obtain the current autoupdate configuration.

    Returns an AutoupdateSettings object containing:
        - is_enabled (bool): Whether automatic updates are enabled
        - interval_start (str): Start of the update window (e.g., "02:00")
        - interval_end (str): End of the update window (e.g., "04:00")

    Use case:
        Confirm when or whether firmware updates happen automatically, to avoid unexpected
        reboots during active usage or schedule maintenance around the update window.
    """
    try:
        api = _make_api(UpdaterApi)
        result = api.get_autoupdate_settings()
        return CallToolResult(content=[{"type": "text", "text": str(result.model_dump())}])
    except Exception as e:
        return _wrap_tool_error(f"Failed to get autoupdate settings: {e}")
