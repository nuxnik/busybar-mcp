from unittest.mock import MagicMock, patch

import pytest

from mcp.types import CallToolResult

import busybar_mcp.wifi as wifi_module


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

WIFI_TOOLS = [
    ("get_wifi_status", "api_wifi_status_get"),
    ("get_wifi_networks", "get_wifi_networks"),
]


def _mock_model():
    m = MagicMock()
    m.model_dump.return_value = {"_mock": True}
    return m


def _mock_client_with_exception(exc_class=ConnectionError):
    client = MagicMock()
    side_effects = [exc_class("simulated connection failure")] * 2
    for attr in ["api_wifi_status_get", "get_wifi_networks"]:
        setattr(client, attr, MagicMock(side_effect=side_effects))
    return client


def _mock_client_for_happy_path():
    client = MagicMock()
    for attr in ["api_wifi_status_get", "get_wifi_networks"]:
        setattr(client, attr, MagicMock(return_value=_mock_model()))
    return client


# ---------------------------------------------------------------------------
# Happy-path tests
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("tool_func_name,api_method_attr", WIFI_TOOLS)
def test_tool_happy_path(tool_func_name, api_method_attr):
    with patch.object(wifi_module, "_make_api") as mock_make_api:
        mock_client = _mock_client_for_happy_path()
        mock_make_api.return_value = mock_client

        fn = getattr(wifi_module, tool_func_name)
        result = fn()

        assert isinstance(result, CallToolResult)
        assert result.is_error is False


# ---------------------------------------------------------------------------
# Error-path tests
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("tool_func_name,api_method_attr", WIFI_TOOLS)
def test_tool_error_path(tool_func_name, api_method_attr):
    with patch.object(wifi_module, "_make_api") as mock_make_api:
        mock_client = _mock_client_with_exception(ConnectionError)
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
