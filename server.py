import os

from dotenv import load_dotenv

load_dotenv()

from mcp.server.mcpserver import MCPServer
from mcp.types import CallToolResult

from busybar_python_sdk import (
    AccountApi,
    Configuration,
    SystemApi,
    TimeApi,
)
from busybar_python_sdk.api_client import ApiClient

server = MCPServer("Busy Bar MCP")


def _make_api(cls):
    """Create and return an API instance configured with env credentials.

    Reads BUSYBAR_BASE_URL and BUSYBAR_API_TOKEN from the environment and passes
    them to the busybar_python_sdk Configuration for correct authentication.
    """
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


def _wrap_tool_error(message):
    """Wrap an error message into a CallToolResult with is_error=True."""
    return CallToolResult(content=[{"type": "text", "text": f"Error: {message}"}], is_error=True)


# ---------------------------------------------------------------------------
# Account endpoints
# ---------------------------------------------------------------------------


@server.tool(name="get_account_info")
def get_account_info():
    """Retrieve linked account information from the Busy Bar device.

    This tool queries GET /api/account/info via `AccountApi.get_account_info()` to get
    details about the account currently linked to the Busy Bar unit.

    Returns an AccountInfo object containing:
        - linked (bool): Whether the device is linked to a busy bar account
        - id (str): The unique account identifier (UUID)
        - email (str): The email address associated with the account
        - user_id (str): The user identifier (UUID)

    Use case:
        Verify an account is properly linked and inspect the associated email before
        performing account-specific operations like displaying messages or notifications.
    """
    try:
        api = _make_api(AccountApi)
        result = api.get_account_info()
        return CallToolResult(content=[{"type": "text", "text": str(result.model_dump())}])
    except Exception as e:
        return _wrap_tool_error(f"Failed to get account info: {e}")


@server.tool(name="get_account_status")
def get_account_status():
    """Retrieve MQTT connection status for the linked account from the Busy Bar device.

    This tool queries GET /api/account/status via `AccountApi.get_account_status()` to
    learn whether the device's MQTT client is actively connected to the busy bar server.

    Returns an AccountStatus object containing:
        - status (str): Connection state, one of "connected", "disconnected", or "error"

    Use case:
        Check MQTT connectivity before pushing data that requires cloud sync; if the
        account is not connected, queue operations locally until reconnection.
    """
    try:
        api = _make_api(AccountApi)
        result = api.get_account_status()
        return CallToolResult(content=[{"type": "text", "text": str(result.model_dump())}])
    except Exception as e:
        return _wrap_tool_error(f"Failed to get account status: {e}")


@server.tool(name="get_account_backend")
def get_account_backend():
    """Retrieve MQTT backend configuration for the linked account from the Busy Bar device.

    This tool queries GET /api/account/backend via `AccountApi.get_account_backend()` to
    inspect how the device is configured to reach the busy bar server over MQTT.

    Returns an AccountBackend object containing:
        - server_url (str): MQTT server URL to connect to (e.g., "default", "mqtts://mqtt.example.com:8883")
        - client_cert_type (str): Client certificate type, one of "default", "custom", or "none"
        - ignore_server_cert (bool): Whether to ignore the server certificate during TLS handshake

    Use case:
        Inspect backend configuration during MQTT troubleshooting; confirm the server URL
        and certificate settings match expectations.
    """
    try:
        api = _make_api(AccountApi)
        result = api.get_account_backend()
        return CallToolResult(content=[{"type": "text", "text": str(result.model_dump())}])
    except Exception as e:
        return _wrap_tool_error(f"Failed to get account backend: {e}")


# ---------------------------------------------------------------------------
# System / version endpoints
# ---------------------------------------------------------------------------


@server.tool(name="get_api_version")
def get_api_version():
    """Retrieve the API version information supported by the Busy Bar device.

    This tool queries /api/version on the device to learn which set of API
    operations are available.  Returns the full version response including
    api_semver and any other metadata the device exposes.

    Returns a VersionInfo object containing:
        - api_semver (str): API SemVer string (e.g., "0.0.0")

    Use case:
        Call this first when building integrations to verify API compatibility
        with the connected Busy Bar unit before issuing further commands.
    """
    try:
        api = _make_api(SystemApi)
        result = api.get_version()
        return CallToolResult(content=[{"type": "text", "text": str(result.model_dump())}])
    except Exception as e:
        return _wrap_tool_error(f"Failed to get API version: {e}")


@server.tool(name="get_transport")
def get_transport():
    """Retrieve the current network transport type used by the Busy Bar device.

    This tool queries /api/transport on the device.  The returned information
    describes how the MCP server is communicating with the Busy Bar hardware —
    typically "usb" (USB ethernet) or "wifi" (Wi-Fi).

    Use case:
        Diagnose connectivity path issues; shows whether the device is reachable
        via USB network interface or a Wi-Fi connection.
    """
    try:
        api = _make_api(SystemApi)
        result = api.get_transport()
        return CallToolResult(content=[{"type": "text", "text": str(result.model_dump())}])
    except Exception as e:
        return _wrap_tool_error(f"Failed to get transport info: {e}")


@server.tool(name="get_device_status")
def get_device_status():
    """Retrieve the current device status from the Busy Bar device.

    This tool queries GET /api/status via `SystemApi.get_status()` and returns a comprehensive
    overview of whether the device is online and healthy.  The response bundles four sub-objects:
    device, firmware, system, and power.

    Returns a Status object containing:
        - device (StatusDevice): Hardware identifiers — serial_number, usb_mac, wifi_mac,
          ble_mac, otp_valid, otp_model, otp_timestamp, firmware_security
        - firmware (StatusFirmware): Firmware details — version, target, branch, build_date,
          commit_hash, intercom_version, nwp_version, matter_version
        - system (StatusSystem): System metrics — api_semver, uptime, boot_time, auto_update_enabled
        - power (StatusPower): Power state — state (discharging/charging/charged), battery_charge
          (int %), battery_voltage (mV), battery_current (mA), usb_voltage (mV)

    Use case:
        A quick health-check to confirm the device is reachable and in a valid
        operational state before issuing other commands.
    """
    try:
        api = _make_api(SystemApi)
        result = api.get_status()
        return CallToolResult(content=[{"type": "text", "text": str(result.model_dump())}])
    except Exception as e:
        return _wrap_tool_error(f"Failed to get device status: {e}")


@server.tool(name="get_device_info")
def get_device_info():
    """Retrieve detailed hardware and identification info about the Busy Bar device.

    This tool queries GET /api/status/device via `SystemApi.get_status_device()` to obtain
    physical identifiers and manufacturing details of the unit.

    Returns a StatusDevice object containing:
        - serial_number (str): Device serial number
        - usb_mac (str): MAC address of the USB ethernet interface
        - wifi_mac (str): Wi-Fi MAC address
        - ble_mac (str): Bluetooth Low Energy MAC address
        - otp_valid (bool): Whether OTP data has been programmed and is valid
        - otp_model (str): Device model code (e.g., "BB.1")
        - otp_timestamp (int): Production timestamp as Unix epoch seconds
        - firmware_security (str): Firmware signature protection state — one of "secure",
          "insecure", "other", or "unknown"

    Use case:
        Inventory tracking, device identification in multi-device setups, or
        troubleshooting hardware-specific issues.
    """
    try:
        api = _make_api(SystemApi)
        result = api.get_status_device()
        return CallToolResult(content=[{"type": "text", "text": str(result.model_dump())}])
    except Exception as e:
        return _wrap_tool_error(f"Failed to get device info: {e}")


@server.tool(name="get_firmware_info")
def get_firmware_info():
    """Retrieve firmware version details from the Busy Bar device.

    This tool queries GET /api/status/firmware via `SystemApi.get_status_firmware()` to get
    information about the firmware currently installed on the unit.

    Returns a StatusFirmware object containing:
        - version (str): Firmware version string (e.g., "1.0.0")
        - target (int): Firmware target code
        - branch (str): Git branch name the firmware was built from
        - build_date (str): Build date (e.g., "2024-01-01")
        - commit_hash (str): Git commit hash, may include a "-dirty" suffix
        - intercom_version (str): Intercom handshake version string
        - nwp_version (str): Radio firmware / NWP version (e.g., "1711.2.14.5.2.0.7")
        - matter_version (str): Matter framework version (e.g., "1.0")

    Use case:
        Verify which firmware revision is running on a unit before deploying
        updates or diagnosing firmware-related bugs.
    """
    try:
        api = _make_api(SystemApi)
        result = api.get_status_firmware()
        return CallToolResult(content=[{"type": "text", "text": str(result.model_dump())}])
    except Exception as e:
        return _wrap_tool_error(f"Failed to get firmware info: {e}")


@server.tool(name="get_system_status")
def get_system_status():
    """Retrieve detailed system metrics from the Busy Bar device.

    This tool queries GET /api/status/system via `SystemApi.get_status_system()` to get
    runtime resource usage and health information.

    Returns a StatusSystem object containing:
        - api_semver (str): API SemVer string (e.g., "0.0.0")
        - uptime (str): System uptime as a human-readable duration (e.g., "00d 00h 04m 13s")
        - boot_time (int): System boot timestamp as Unix epoch seconds
        - auto_update_enabled (bool): Whether automatic firmware updates are enabled

    Use case:
        Monitor available system resources before performing heavy operations (e.g. large
        file uploads or firmware updates) to avoid exhausting the device.
    """
    try:
        api = _make_api(SystemApi)
        result = api.get_status_system()
        return CallToolResult(content=[{"type": "text", "text": str(result.model_dump())}])
    except Exception as e:
        return _wrap_tool_error(f"Failed to get system status: {e}")


@server.tool(name="get_power_status")
def get_power_status():
    """Retrieve power/battery status from the Busy Bar device.

    This tool queries GET /api/status/power via `SystemApi.get_status_power()` to check
    the current battery and charging state of the unit.

    Returns a StatusPower object containing:
        - state (str): Power state — one of "discharging", "charging", or "charged"
        - battery_charge (int): Battery charge level as a percentage (0–100)
        - battery_voltage (int): Battery voltage in millivolts (e.g., 4183 mV)
        - battery_current (int): Battery current in milliamperes; negative means discharging
        - usb_voltage (int): USB input voltage in millivolts (e.g., 4843 mV)

    Use case:
        Check battery health before operations that consume significant power;
        alert users when the device needs to be plugged in.
    """
    try:
        api = _make_api(SystemApi)
        result = api.get_status_power()
        return CallToolResult(content=[{"type": "text", "text": str(result.model_dump())}])
    except Exception as e:
        return _wrap_tool_error(f"Failed to get power status: {e}")


# ---------------------------------------------------------------------------
# Time endpoints
# ---------------------------------------------------------------------------


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


if __name__ == "__main__":
    server.run()
