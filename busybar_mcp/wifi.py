from busybar_python_sdk import WiFiApi
from mcp.types import CallToolResult

from ._server import server
from .utils import _make_api, _serialize, _wrap_tool_error

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
