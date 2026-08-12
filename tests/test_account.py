from unittest.mock import MagicMock, patch

import pytest

from mcp.types import CallToolResult

import busybar_mcp.account as account_module


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

ACCOUNT_TOOLS = [
    ("get_account_info", "get_account_info"),
    ("get_account_status", "get_account_status"),
    ("get_account_backend", "get_account_backend"),
]


def _mock_model():
    """Return a mock SDK model with a model_dump method that returns a dict."""
    m = MagicMock()
    m.model_dump.return_value = {"_mock": True}
    return m


def _mock_client_with_exception(exc_class=ConnectionError):
    """Return a MagicMock client whose every stubbed method raises `exc_class`."""
    client = MagicMock()
    side_effects = [exc_class("simulated connection failure")] * 3
    for attr in ["get_account_info", "get_account_status", "get_account_backend"]:
        setattr(client, attr, MagicMock(side_effect=side_effects))
    return client


def _mock_client_for_happy_path():
    """Return a fully stubbed mock client matching ACCOUNT_TOOLS."""
    client = MagicMock()
    for attr in ["get_account_info", "get_account_status", "get_account_backend"]:
        setattr(client, attr, MagicMock(return_value=_mock_model()))
    return client


# ---------------------------------------------------------------------------
# Happy-path tests
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("tool_func_name,api_method_attr", ACCOUNT_TOOLS)
def test_tool_happy_path(tool_func_name, api_method_attr):
    """Every MCP tool returns a CallToolResult with is_error=False when the SDK method succeeds."""
    with patch.object(account_module, "_make_api") as mock_make_api:
        mock_client = _mock_client_for_happy_path()
        mock_make_api.return_value = mock_client

        fn = getattr(account_module, tool_func_name)
        result = fn()

        assert isinstance(result, CallToolResult)
        assert result.is_error is False


# ---------------------------------------------------------------------------
# Error-path tests
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("tool_func_name,api_method_attr", ACCOUNT_TOOLS)
def test_tool_error_path(tool_func_name, api_method_attr):
    """Every MCP tool returns a CallToolResult with is_error=True and 'Error:' prefix text when the SDK raises."""
    with patch.object(account_module, "_make_api") as mock_make_api:
        mock_client = _mock_client_with_exception(ConnectionError)
        mock_make_api.return_value = mock_client

        fn = getattr(account_module, tool_func_name)
        result = fn()

        assert isinstance(result, CallToolResult)
        assert result.is_error is True
        content_item = result.content[0]
        if hasattr(content_item, "text"):
            text = content_item.text
        else:
            text = content_item["text"]
        assert text.startswith("Error:")
