import os

from dotenv import load_dotenv

load_dotenv()

from mcp.server.mcpserver import MCPServer
from mcp.types import CallToolResult

from busybar_python_sdk import (
    AccountApi,
    BLEApi,
    BusyApi,
    Configuration,
    SettingsApi,
    SmartHomeApi,
    StorageApi,
    SystemApi,
    TimeApi,
    UpdaterApi,
    WiFiApi,
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


# ---------------------------------------------------------------------------
# BLE endpoints
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Busy Timer endpoints
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Settings GET endpoints
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Smart Home endpoints
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Storage endpoints
# ---------------------------------------------------------------------------


@server.tool(name="list_storage_files")
def list_storage_files(path: str = "/"):
    """List files and directories stored on the Busy Bar device at a given path.

    This tool calls `StorageApi.list_storage_files(path)` to enumerate the directory
    contents on the device's internal storage for the specified path.

    Args:
        path: The directory path to list (e.g., "/", "/photos"). Defaults to "/".

    Returns a StorageList object containing:
        - A list of StorageListElement objects, each with:
            - type (str): File type — "file" or "dir"
            - name (str): Name of the file or directory

    Use case:
        Browse device storage to find files before uploading, downloading, or managing
        media assets for display on the Busy Bar unit.
    """
    try:
        api = _make_api(StorageApi)
        result = api.list_storage_files(path=path)
        return CallToolResult(content=[{"type": "text", "text": str(_serialize(result))}])
    except Exception as e:
        return _wrap_tool_error(f"Failed to list storage files at {path!r}: {e}")


@server.tool(name="get_storage_status")
def get_storage_status():
    """Retrieve storage capacity information from the Busy Bar device.

    This tool queries GET /api/storage/status via `StorageApi.get_storage_status()`
    to learn current flash storage usage and available space.

    Returns a StorageStatus object containing:
        - used_bytes (int): Bytes currently used on the device storage
        - free_bytes (int): Bytes available for writing
        - total_bytes (int): Total capacity of the storage

    Use case:
        Check available storage before uploading files or media to confirm there is
        sufficient space, and monitor storage consumption over time.
    """
    try:
        api = _make_api(StorageApi)
        result = api.get_storage_status()
        return CallToolResult(content=[{"type": "text", "text": str(result.model_dump())}])
    except Exception as e:
        return _wrap_tool_error(f"Failed to get storage status: {e}")


# ---------------------------------------------------------------------------
# Update endpoints
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Wi-Fi endpoints
# ---------------------------------------------------------------------------


@server.tool(name="get_wifi_status")
def get_wifi_status():
    """Retrieve Wi-Fi connection status from the Busy Bar device.

    This tool queries GET /api/wifi/status via `WiFiApi.api_wifi_status_get()` to obtain
    the current network connection details on the Wi-Fi interface.

    Returns a StatusResponse object containing:
        - state (str): Connection state — e.g., "connected", "disconnected"
        - ssid (str | null): SSID of the connected access point
        - bssid (str | null): MAC address of the connected access point
        - channel (int): Wi-Fi channel number (e.g., 1, 6, 36)
        - rssi (int): Received signal strength indicator in dBm (negative value)
        - security (str): Security type — e.g., "open", "wpa2", "wpa3"
        - ip_config (StatusResponseIpConfig): IP configuration including:
            - method (WifiIpType): How the IP was obtained ("dhcp" or "static")

    Use case:
        Diagnostics for network troubleshooting — verify SSID, signal strength, security
        type, and IP assignment before debugging connectivity issues.
    """
    try:
        api = _make_api(WiFiApi)
        result = api.api_wifi_status_get()
        return CallToolResult(content=[{"type": "text", "text": str(result.model_dump())}])
    except Exception as e:
        return _wrap_tool_error(f"Failed to get Wi-Fi status: {e}")


@server.tool(name="get_wifi_networks")
def get_wifi_networks():
    """Retrieve currently scanned Wi-Fi networks from the Busy Bar device.

    This tool queries GET /api/wifi/networks via `WiFiApi.get_wifi_networks()` to obtain
    the latest scan results of available wireless access points in range.

    Returns a NetworkResponse object containing:
        - count (int): Number of networks found in the scan
        - networks (list[Network]): Array of network entries, each with SSID, BSSID, RSSI,
          channel, security method, and frequency band information

    Use case:
        Browse available Wi-Fi networks before switching the Busy Bar to a different
        access point or confirming signal quality at a new location.
    """
    try:
        api = _make_api(WiFiApi)
        result = api.get_wifi_networks()
        return CallToolResult(content=[{"type": "text", "text": str(result.model_dump())}])
    except Exception as e:
        return _wrap_tool_error(f"Failed to get Wi-Fi networks: {e}")


if __name__ == "__main__":
    server.run()
