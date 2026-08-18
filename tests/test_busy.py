from unittest.mock import MagicMock, patch

import pytest

from mcp.types import CallToolResult

import busybar_mcp.busy as busy_module


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

BUSY_TOOLS = [
    "get_busy_snapshot",
]


def _mock_client_with_exception(exc_class=ConnectionError):
    client = MagicMock()
    side_effects = [exc_class("simulated connection failure")] * 1
    for attr in ["get_busy_snapshot_without_preload_content"]:
        setattr(client, attr, MagicMock(side_effect=side_effects))
    return client


def _mock_client_for_happy_path():
    import json
    client = MagicMock()
    resp = MagicMock()
    resp.read.return_value = json.dumps({"snapshot": {"type": "NOT_STARTED"}, "snapshot_timestamp_ms": 1}).encode("utf-8")
    for attr in ["get_busy_snapshot_without_preload_content"]:
        setattr(client, attr, MagicMock(return_value=resp))
    return client


# ---------------------------------------------------------------------------
# Happy-path tests
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("tool_func_name", BUSY_TOOLS)
def test_tool_happy_path(tool_func_name):
    with patch.object(busy_module, "_make_api") as mock_make_api:
        mock_client = _mock_client_for_happy_path()
        mock_make_api.return_value = mock_client

        fn = getattr(busy_module, tool_func_name)
        result = fn()

        assert isinstance(result, CallToolResult)
        assert result.is_error is False


# ---------------------------------------------------------------------------
# Error-path tests
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("tool_func_name", BUSY_TOOLS)
def test_tool_error_path(tool_func_name):
    with patch.object(busy_module, "_make_api") as mock_make_api:
        mock_client = _mock_client_with_exception(ConnectionError)
        mock_make_api.return_value = mock_client

        fn = getattr(busy_module, tool_func_name)
        result = fn()

        assert isinstance(result, CallToolResult)
        assert result.is_error is True
        content_item = result.content[0]
        if hasattr(content_item, "text"):
            text = content_item.text
        else:
            text = content_item["text"]
        assert text.startswith("Error:")
