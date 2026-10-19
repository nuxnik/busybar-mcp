from contextlib import contextmanager
from unittest.mock import MagicMock, patch

import pytest

from mcp.types import CallToolResult

import busybar_mcp.wifi as wifi_module


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

WIFI_TOOLS = [
    ("get_wifi_status", "busybar_wifi_status_get"),
    ("get_wifi_networks", "get_raw"),
]

# A NetworkResponse-shaped body: `get_wifi_networks` validates the dict
# returned by `BusyBarClient.get_raw` with the real `NetworkResponse` model.
NETWORKS_BODY = {
    "count": 1,
    "networks": [
        {"ssid": "TestNetwork", "security": "WPA3", "rssi": -58},
    ],
}


def _mock_model():
    m = MagicMock()
    m.model_dump.return_value = {"_mock": True}
    return m


@contextmanager
def _apply_happy_path():
    with patch.object(wifi_module, "_make_api") as mock_make_api, \
            patch.object(wifi_module, "_client") as mock_client:
        mock_make_api.return_value.busybar_wifi_status_get.return_value = _mock_model()
        mock_client.return_value.get_raw.return_value = NETWORKS_BODY
        yield mock_make_api, mock_client


@contextmanager
def _apply_error_path(exc_class=ConnectionError):
    with patch.object(wifi_module, "_make_api") as mock_make_api, \
            patch.object(wifi_module, "_client") as mock_client:
        exc = exc_class("simulated connection failure")
        mock_make_api.return_value.busybar_wifi_status_get.side_effect = exc
        mock_client.return_value.get_raw.side_effect = exc
        yield mock_make_api, mock_client


# ---------------------------------------------------------------------------
# Happy-path tests
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("tool_func_name,api_method_attr", WIFI_TOOLS)
def test_tool_happy_path(tool_func_name, api_method_attr):
    with _apply_happy_path():
        fn = getattr(wifi_module, tool_func_name)
        result = fn()

        assert isinstance(result, CallToolResult)
        assert result.is_error is False


# ---------------------------------------------------------------------------
# Error-path tests
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("tool_func_name,api_method_attr", WIFI_TOOLS)
def test_tool_error_path(tool_func_name, api_method_attr):
    with _apply_error_path(ConnectionError):
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
