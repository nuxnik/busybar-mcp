from busybar_python_sdk import AccountApi
from mcp.types import CallToolResult

from ._server import server
from .utils import _make_api, _serialize, _wrap_tool_error

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
