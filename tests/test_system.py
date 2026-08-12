from unittest.mock import MagicMock, patch

import pytest

from mcp.types import CallToolResult

import busybar_mcp.system as system_module


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

SYSTEM_TOOLS = [
    ("get_api_version", "get_version"),
    ("get_transport", "get_transport"),
    ("get_device_status", "get_status"),
    ("get_device_info", "get_status_device"),
    ("get_firmware_info", "get_status_firmware"),
    ("get_system_status", "get_status_system"),
    ("get_power_status", "get_status_power"),
]


def _mock_model():
    m = MagicMock()
    m.model_dump.return_value = {"_mock": True}
    return m


def _mock_client_with_exception(exc_class=ConnectionError):
    client = MagicMock()
    side_effects = [exc_class("simulated connection failure")] * 7
    for i, attr in enumerate([
        "get_version", "get_transport", "get_status",
        "get_status_device", "get_status_firmware",
        "get_status_system", "get_status_power",
    ]):
        setattr(client, attr, MagicMock(side_effect=side_effects))
    return client


def _mock_client_for_happy_path():
    client = MagicMock()
    for attr in [
        "get_version", "get_transport", "get_status",
        "get_status_device", "get_status_firmware",
        "get_status_system", "get_status_power",
    ]:
        setattr(client, attr, MagicMock(return_value=_mock_model()))
    return client


# ---------------------------------------------------------------------------
# Happy-path tests
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("tool_func_name,api_method_attr", SYSTEM_TOOLS)
def test_tool_happy_path(tool_func_name, api_method_attr):
    with patch.object(system_module, "_make_api") as mock_make_api:
        mock_client = _mock_client_for_happy_path()
        mock_make_api.return_value = mock_client

        fn = getattr(system_module, tool_func_name)
        result = fn()

        assert isinstance(result, CallToolResult)
        assert result.is_error is False


# ---------------------------------------------------------------------------
# Error-path tests
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("tool_func_name,api_method_attr", SYSTEM_TOOLS)
def test_tool_error_path(tool_func_name, api_method_attr):
    with patch.object(system_module, "_make_api") as mock_make_api:
        mock_client = _mock_client_with_exception(ConnectionError)
        mock_make_api.return_value = mock_client

        fn = getattr(system_module, tool_func_name)
        result = fn()

        assert isinstance(result, CallToolResult)
        assert result.is_error is True
        content_item = result.content[0]
        if hasattr(content_item, "text"):
            text = content_item.text
        else:
            text = content_item["text"]
        assert text.startswith("Error:")
