from unittest.mock import MagicMock, patch

import pytest

from mcp.types import CallToolResult

import busybar_mcp.updater as updater_module


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

UPDATER_STATUS_TOOLS = [
    ("get_firmware_update_status", "get_firmware_update_status"),
    ("get_autoupdate_settings", "get_autoupdate_settings"),
]

CHANGELOG_VERSIONS = ["1.0.0", "2.0.0"]


def _mock_model():
    m = MagicMock()
    m.model_dump.return_value = {"_mock": True}
    return m


def _mock_client_with_exception(exc_class=ConnectionError):
    client = MagicMock()
    side_effects = [exc_class("simulated connection failure")] * 3
    for attr in ["get_firmware_update_status", "get_update_changelog", "get_autoupdate_settings"]:
        setattr(client, attr, MagicMock(side_effect=side_effects))
    return client


def _mock_client_for_happy_path():
    client = MagicMock()
    for attr in ["get_firmware_update_status", "get_update_changelog", "get_autoupdate_settings"]:
        setattr(client, attr, MagicMock(return_value=_mock_model()))
    return client


# ---------------------------------------------------------------------------
# Firmware update status + auto-update settings happy-path + error-path
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("tool_func_name,api_method_attr", UPDATER_STATUS_TOOLS)
def test_updater_happy_path(tool_func_name, api_method_attr):
    with patch.object(updater_module, "_make_api") as mock_make_api:
        mock_client = _mock_client_for_happy_path()
        mock_make_api.return_value = mock_client

        fn = getattr(updater_module, tool_func_name)
        result = fn()

        assert isinstance(result, CallToolResult)
        assert result.is_error is False


@pytest.mark.parametrize("tool_func_name,api_method_attr", UPDATER_STATUS_TOOLS)
def test_updater_error_path(tool_func_name, api_method_attr):
    with patch.object(updater_module, "_make_api") as mock_make_api:
        mock_client = _mock_client_with_exception(ConnectionError)
        mock_make_api.return_value = mock_client

        fn = getattr(updater_module, tool_func_name)
        result = fn()

        assert isinstance(result, CallToolResult)
        assert result.is_error is True
        content_item = result.content[0]
        if hasattr(content_item, "text"):
            text = content_item.text
        else:
            text = content_item["text"]
        assert text.startswith("Error:")


# ---------------------------------------------------------------------------
# get_update_changelog (parameterized over version)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("version", CHANGELOG_VERSIONS)
def test_get_update_changelog_happy_path(version):
    with patch.object(updater_module, "_make_api") as mock_make_api:
        mock_client = _mock_client_for_happy_path()
        mock_make_api.return_value = mock_client

        result = updater_module.get_update_changelog(version=version)

        assert isinstance(result, CallToolResult)
        assert result.is_error is False


@pytest.mark.parametrize("version", CHANGELOG_VERSIONS)
def test_get_update_changelog_error_path(version):
    with patch.object(updater_module, "_make_api") as mock_make_api:
        mock_client = _mock_client_with_exception(ConnectionError)
        mock_make_api.return_value = mock_client

        result = updater_module.get_update_changelog(version=version)

        assert isinstance(result, CallToolResult)
        assert result.is_error is True
        content_item = result.content[0]
        if hasattr(content_item, "text"):
            text = content_item.text
        else:
            text = content_item["text"]
        assert text.startswith("Error:")
