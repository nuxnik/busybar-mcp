from unittest.mock import MagicMock, patch

import pytest

from mcp.types import CallToolResult

import server


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

ALL_TOOLS = [
    ("get_account_info", "get_account_info"),
    ("get_account_status", "get_account_status"),
    ("get_account_backend", "get_account_backend"),
    ("get_api_version", "get_version"),
    ("get_transport", "get_transport"),
    ("get_device_status", "get_status"),
    ("get_device_info", "get_status_device"),
    ("get_firmware_info", "get_status_firmware"),
    ("get_system_status", "get_status_system"),
    ("get_power_status", "get_status_power"),
    ("get_time", "get_time"),
    ("get_timezone", "get_time_timezone"),
    ("get_tzlist", "get_time_tzlist"),
    ("get_ble_status", "api_ble_status_get"),
    ("get_busy_snapshot", "get_busy_snapshot"),
    ("get_http_access", "get_http_access"),
    ("get_device_name", "api_name_get"),
    ("get_display_brightness", "get_display_brightness"),
    ("get_audio_volume", "get_audio_volume"),
    ("get_smart_home_pairing_status", "get_smart_home_commissioning_status"),
    ("get_smart_home_switch_state", "api_smart_home_switch_get"),
    ("list_storage_files", "list_storage_files"),
    ("get_storage_status", "get_storage_status"),
    ("get_firmware_update_status", "get_firmware_update_status"),
    ("get_update_changelog", "get_update_changelog"),
    ("get_autoupdate_settings", "get_autoupdate_settings"),
    ("get_wifi_status", "api_wifi_status_get"),
    ("get_wifi_networks", "get_wifi_networks"),
]


def _mock_model():
    """Return a mock SDK model with a model_dump method that returns a dict."""
    m = MagicMock()
    m.model_dump.return_value = {"_mock": True}
    return m


def _mock_client_with_exception(exc_class=ConnectionError):
    """Return a MagicMock client whose every stubbed method raises `exc_class`."""
    client = MagicMock()
    side_effects = [
        exc_class("simulated connection failure"),
    ] * 29
    for attr in [
        "get_account_info", "get_account_status", "get_account_backend",
        "get_version", "get_transport", "get_status",
        "get_status_device", "get_status_firmware", "get_status_system",
        "get_status_power", "get_time", "get_time_timezone", "get_time_tzlist",
        "api_ble_status_get", "get_busy_snapshot", "get_http_access",
        "api_name_get", "get_display_brightness", "get_audio_volume",
        "get_smart_home_commissioning_status", "api_smart_home_switch_get",
        "list_storage_files", "get_storage_status", "get_firmware_update_status",
        "get_update_changelog", "get_autoupdate_settings", "api_wifi_status_get",
        "get_wifi_networks",
    ]:
        setattr(client, attr, MagicMock(side_effect=side_effects))
    return client


# Tools that require arguments (not the default no-arg pattern)
_TOOL_ARGS = {
    "list_storage_files": ("/",),
    "get_update_changelog": ("1.0.0",),
}


def _mock_client_for_happy_path():
    """Return a fully stubbed mock client matching ALL_TOOLS."""
    client = MagicMock()
    attrs_to_stub = [
        "get_account_info", "get_account_status", "get_account_backend",
        "get_version", "get_transport", "get_status",
        "get_status_device", "get_status_firmware", "get_status_system",
        "get_status_power", "get_time", "get_time_timezone", "get_time_tzlist",
        "api_ble_status_get", "get_busy_snapshot", "get_http_access",
        "api_name_get", "get_display_brightness", "get_audio_volume",
        "get_smart_home_commissioning_status", "api_smart_home_switch_get",
        "list_storage_files", "get_storage_status", "get_firmware_update_status",
        "get_update_changelog", "get_autoupdate_settings", "api_wifi_status_get",
        "get_wifi_networks",
    ]
    for attr in attrs_to_stub:
        setattr(client, attr, MagicMock(return_value=_mock_model()))
    return client


# ---------------------------------------------------------------------------
# Happy-path tests
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("tool_func_name,api_method_attr", ALL_TOOLS)
def test_tool_happy_path(tool_func_name, api_method_attr):
    """Every MCP tool returns a CallToolResult with is_error=False when the SDK method succeeds."""
    with patch("server._make_api") as mock_make_api:
        mock_client = _mock_client_for_happy_path()
        mock_make_api.return_value = mock_client

        # Use the ALL_TOOLS mapping to build the list of attributes for assertion checking.
        attrs = [
            "get_account_info", "get_account_status", "get_account_backend",
            "get_version", "get_transport", "get_status",
            "get_status_device", "get_status_firmware", "get_status_system",
            "get_status_power", "get_time", "get_time_timezone", "get_time_tzlist",
        ]

        fn = getattr(server, tool_func_name)
        args = _TOOL_ARGS.get(tool_func_name, ())
        result = fn(*args)

        assert isinstance(result, CallToolResult)
        assert result.is_error is False
        assert len(result.content) == 1
        content_item = result.content[0]
        # content items may be TextContent objects or plain dicts depending on MCP lib version
        if hasattr(content_item, "type"):
            text = content_item.text
        else:
            text = content_item["text"]


# ---------------------------------------------------------------------------
# Error-path tests for all tools (including parameterized ones)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("tool_func_name,api_method_attr", ALL_TOOLS)
def test_tool_error_path(tool_func_name, api_method_attr):
    """Every MCP tool returns a CallToolResult with is_error=True and 'Error:' prefix text when the SDK raises."""
    with patch("server._make_api") as mock_make_api:
        mock_client = _mock_client_with_exception(ConnectionError)
        mock_make_api.return_value = mock_client

        fn = getattr(server, tool_func_name)
        args = _TOOL_ARGS.get(tool_func_name, ())
        result = fn(*args)

        assert isinstance(result, CallToolResult)
        assert result.is_error is True
        content_item = result.content[0]
        if hasattr(content_item, "text"):
            text = content_item.text
        else:
            text = content_item["text"]
        assert text.startswith("Error:")


# ---------------------------------------------------------------------------
# Missing env var test
# ---------------------------------------------------------------------------

def test_missing_env_vars_raises_valueerror(clear_env_vars):
    """_make_api raises ValueError when BUSYBAR_BASE_URL or BUSYBAR_API_TOKEN are absent."""
    with pytest.raises(ValueError, match="Missing required environment variable"):
        server._make_api(server.AccountApi)
