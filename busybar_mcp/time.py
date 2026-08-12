from busybar_python_sdk import TimeApi
from mcp.types import CallToolResult

from ._server import server
from .utils import _make_api, _serialize, _wrap_tool_error

@server.tool(name="get_time")
def get_time():
    """Retrieve the current timestamp from the Busy Bar device's real-time clock.

    This tool queries /api/time on the device and returns the current date and time
    in ISO 8601 format with timezone information (e.g., '2025-10-02T14:30:45+04:00').

    Returns a TimestampInfo object containing:
        - timestamp: str  — the current UTC/RFC timestamp in ISO 8601 format

    Use case:
        Querying the device's clock as an authoritative time source for scheduling,
        logging, or coordinating events with BUSY timer profiles.
    """
    try:
        api = _make_api(TimeApi)
        result = api.get_time()
        return CallToolResult(content=[{"type": "text", "text": str(result.model_dump())}])
    except Exception as e:
        return _wrap_tool_error(f"Failed to get time: {e}")


@server.tool(name="get_timezone")
def get_timezone():
    """Retrieve the current timezone configured on the Busy Bar device.

    This tool queries /api/time/timezone on the device and returns the currently
    active timezone configuration including the display name, UTC offset, and
    abbreviation.

    Returns a TimezoneInfo object containing:
        - name:  str  — human-readable timezone name (e.g., 'America/New_York')
        - offset: str — UTC offset string (e.g., '-05:00', '+05:30')
        - abbr:   str — timezone abbreviation (e.g., 'EST', 'IST')

    Use case:
        Checking which timezone the device is configured to so you can display
        times correctly or decide whether an update is needed.
    """
    try:
        api = _make_api(TimeApi)
        result = api.get_time_timezone()
        return CallToolResult(content=[{"type": "text", "text": str(result.model_dump())}])
    except Exception as e:
        return _wrap_tool_error(f"Failed to get timezone: {e}")


@server.tool(name="get_tzlist")
def get_tzlist():
    """Retrieve the full list of supported timezones from the Busy Bar device.

    This tool queries /api/time/tzlist on the device and returns every timezone
    that can be used with the set_timezone functionality (/api/time/timezone POST).

    Returns a TimezoneListResponse object containing:
        - list:  list[TimezoneInfo]  — an array of available timezones, each with:
            - name:  str  — human-readable timezone name (e.g., 'America/New_York')
            - offset: str — UTC offset string (e.g., '-05:00', '+05:30')
            - abbr:   str — timezone abbreviation (e.g., 'EST', 'IST')

    Use case:
        Browsing the available timezones before choosing one to apply via set_timezone.
        Useful for building a UI dropdown or confirming that a specific named timezone is supported.
    """
    try:
        api = _make_api(TimeApi)
        result = api.get_time_tzlist()
        return CallToolResult(content=[{"type": "text", "text": str(result.model_dump())}])
    except Exception as e:
        return _wrap_tool_error(f"Failed to get timezone list: {e}")
