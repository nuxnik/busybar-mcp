from unittest.mock import MagicMock, patch

from mcp.types import CallToolResult

import busybar_mcp.input as input_module


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _mock_model():
    m = MagicMock()
    m.model_dump.return_value = {"result": "OK"}
    return m


def _mock_client_for_happy_path():
    client = MagicMock()
    client.set_input_key = MagicMock(return_value=_mock_model())
    return client


def _mock_client_with_exception():
    client = MagicMock()
    client.set_input_key = MagicMock(side_effect=ConnectionError("simulated connection failure"))
    return client


# ---------------------------------------------------------------------------
# Happy-path tests
# ---------------------------------------------------------------------------

def test_send_input_key_happy_path():
    with patch.object(input_module, "_make_api") as mock_make_api:
        mock_client = _mock_client_for_happy_path()
        mock_make_api.return_value = mock_client

        result = input_module.send_input_key(key="ok")

        assert isinstance(result, CallToolResult)
        assert result.is_error is False
        mock_client.set_input_key.assert_called_once_with("ok")


# ---------------------------------------------------------------------------
# Error-path tests
# ---------------------------------------------------------------------------

def test_send_input_key_error_path():
    with patch.object(input_module, "_make_api") as mock_make_api:
        mock_client = _mock_client_with_exception()
        mock_make_api.return_value = mock_client

        result = input_module.send_input_key(key="ok")

        assert isinstance(result, CallToolResult)
        assert result.is_error is True
        content_item = result.content[0]
        if hasattr(content_item, "text"):
            text = content_item.text
        else:
            text = content_item["text"]
        assert text.startswith("Error:")
