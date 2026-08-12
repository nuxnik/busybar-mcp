from unittest.mock import MagicMock, patch

import pytest

from mcp.types import CallToolResult

import busybar_mcp.storage as storage_module


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

STORAGE_STATUS_TOOLS = [
    ("get_storage_status", "get_storage_status"),
]

STORAGE_LIST_PATHS = ["/", "/photos"]


def _mock_model():
    m = MagicMock()
    m.model_dump.return_value = {"_mock": True}
    return m


def _mock_client_with_exception(exc_class=ConnectionError):
    client = MagicMock()
    side_effects = [exc_class("simulated connection failure")] * 2
    for attr in ["list_storage_files", "get_storage_status"]:
        setattr(client, attr, MagicMock(side_effect=side_effects))
    return client


def _mock_client_for_happy_path():
    client = MagicMock()
    for attr in ["list_storage_files", "get_storage_status"]:
        setattr(client, attr, MagicMock(return_value=_mock_model()))
    return client


# ---------------------------------------------------------------------------
# list_storage_files happy-path (parameterized over path)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("path", STORAGE_LIST_PATHS)
def test_list_storage_files_happy_path(path):
    with patch.object(storage_module, "_make_api") as mock_make_api:
        mock_client = _mock_client_for_happy_path()
        mock_make_api.return_value = mock_client

        result = storage_module.list_storage_files(path=path)

        assert isinstance(result, CallToolResult)
        assert result.is_error is False


# ---------------------------------------------------------------------------
# get_storage_status happy-path + error-path
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("tool_func_name,api_method_attr", STORAGE_STATUS_TOOLS)
def test_get_storage_status_happy_path(tool_func_name, api_method_attr):
    with patch.object(storage_module, "_make_api") as mock_make_api:
        mock_client = _mock_client_for_happy_path()
        mock_make_api.return_value = mock_client

        fn = getattr(storage_module, tool_func_name)
        result = fn()

        assert isinstance(result, CallToolResult)
        assert result.is_error is False


@pytest.mark.parametrize("tool_func_name,api_method_attr", STORAGE_STATUS_TOOLS)
def test_get_storage_status_error_path(tool_func_name, api_method_attr):
    with patch.object(storage_module, "_make_api") as mock_make_api:
        mock_client = _mock_client_with_exception(ConnectionError)
        mock_make_api.return_value = mock_client

        fn = getattr(storage_module, tool_func_name)
        result = fn()

        assert isinstance(result, CallToolResult)
        assert result.is_error is True
        content_item = result.content[0]
        if hasattr(content_item, "text"):
            text = content_item.text
        else:
            text = content_item["text"]
        assert text.startswith("Error:")
