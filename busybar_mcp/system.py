from busybar_python_sdk import SystemApi
from mcp.types import CallToolResult

from ._server import server
from .utils import _make_api, _serialize, _wrap_tool_error

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
