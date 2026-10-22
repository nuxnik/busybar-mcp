from unittest.mock import MagicMock, patch

import pytest

from mcp.types import CallToolResult

import busybar_mcp.wifi as wifi_module


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# (tool function name, generated WiFiApi method the tool invokes in SDK 27.5.1).
# Both tools are generated SDK calls again (SDK 27.5.1 re-added
# `WiFiApi.get_wifi_networks`; the retired `BusyBarClient.get_raw` workaround
# is gone), so both are driven through the shared `_make_api(WiFiApi)`.
WIFI_TOOLS = [
    ("get_wifi_status", "api_wifi_status_get"),
    ("get_wifi_networks", "get_wifi_networks"),
]


def _mock_model(body):
    m = MagicMock()
    m.model_dump.return_value = body
    return m


# NetworkResponse-shaped model body for `WiFiApi.get_wifi_networks()`.
_NETWORKS_RESPONSE = {
    "count": 1,
    "networks": [
        {
            "ssid": "TestNetwork",
            "bssid": "AA:BB:CC:DD:EE:FF",
            "rssi": -58,
            "channel": 6,
            "security": "WPA3",
            "band": "2.4GHz",
        },
    ],
}

# StatusResponse-shaped model body for `WiFiApi.api_wifi_status_get()`.
_STATUS_RESPONSE = {
    "state": "connected",
    "ssid": "TestNetwork",
    "bssid": "AA:BB:CC:DD:EE:FF",
    "channel": 6,
    "rssi": -58,
    "security": "WPA3",
    "ip_config": {"method": "dhcp"},
}

_RESPONSE_BY_METHOD = {
    "api_wifi_status_get": _STATUS_RESPONSE,
    "get_wifi_networks": _NETWORKS_RESPONSE,
}


def _mock_client_for_happy_path(api_method_attr):
    client = MagicMock()
    setattr(client, api_method_attr, MagicMock(return_value=_mock_model(_RESPONSE_BY_METHOD[api_method_attr])))
    return client


def _mock_client_with_exception(api_method_attr, exc_class=ConnectionError):
    client = MagicMock()
    setattr(client, api_method_attr, MagicMock(side_effect=exc_class("simulated connection failure")))
    return client


# ---------------------------------------------------------------------------
# Happy-path tests
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("tool_func_name,api_method_attr", WIFI_TOOLS)
def test_tool_happy_path(tool_func_name, api_method_attr):
    with patch.object(wifi_module, "_make_api") as mock_make_api:
        mock_client = _mock_client_for_happy_path(api_method_attr)
        mock_make_api.return_value = mock_client

        fn = getattr(wifi_module, tool_func_name)
        result = fn()

        assert isinstance(result, CallToolResult)
        assert result.is_error is False
        # Non-vacuous: the tool called the exact 27.5.1 generated method.
        getattr(mock_client, api_method_attr).assert_called_once()


# ---------------------------------------------------------------------------
# Error-path tests
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("tool_func_name,api_method_attr", WIFI_TOOLS)
def test_tool_error_path(tool_func_name, api_method_attr):
    with patch.object(wifi_module, "_make_api") as mock_make_api:
        mock_client = _mock_client_with_exception(api_method_attr, ConnectionError)
        mock_make_api.return_value = mock_client

        fn = getattr(wifi_module, tool_func_name)
        result = fn()

        assert isinstance(result, CallToolResult)
        assert result.is_error is True
        content_item = result.content[0]
        if hasattr(content_item, "text"):
            text = content_item.text
        else:
            text = content_item["text"]
        assert text.startswith("Error:")
        # Non-vacuous: the failure was raised from the 27.5.1 generated method.
        getattr(mock_client, api_method_attr).assert_called_once()
