import json
from unittest.mock import MagicMock, patch

import pytest

from mcp.types import CallToolResult

import busybar_mcp.busy as busy_module
from busybar_mcp.utils import _flatten


# ---------------------------------------------------------------------------
# _flatten unit tests (task 3.1)
# ---------------------------------------------------------------------------

class TestFlatten:
    def test_nested_dict_produces_dot_separated_keys(self):
        result = _flatten({"snapshot": {"started": True, "remaining_ms": 42000}})
        assert result == {"snapshot.started": True, "snapshot.remaining_ms": 42000}

    def test_top_level_scalars_unchanged(self):
        result = _flatten({"type": "NOT_STARTED", "snapshot_timestamp_ms": 1700000000000})
        assert result == {"type": "NOT_STARTED", "snapshot_timestamp_ms": 1700000000000}

    def test_empty_dict_returns_empty_dict(self):
        assert _flatten({}) == {}

    def test_list_leaf_preserved(self):
        result = _flatten({"snapshot": {"intervals": [1, 2, 3]}})
        assert result == {"snapshot.intervals": [1, 2, 3]}

    def test_scalar_leaf_unchanged(self):
        result = _flatten({"a": 1, "b": "x", "c": None, "d": True})
        assert result == {"a": 1, "b": "x", "c": None, "d": True}

    def test_deeply_nested_dict(self):
        result = _flatten({"a": {"b": {"c": 1}}})
        assert result == {"a.b.c": 1}


# ---------------------------------------------------------------------------
# end-to-end tests for get_busy_snapshot (tasks 3.2, 3.3)
# ---------------------------------------------------------------------------

def _mock_rest_response(body):
    resp = MagicMock()
    resp.read.return_value = json.dumps(body).encode("utf-8")
    return resp


def _mock_client_not_started():
    client = MagicMock()
    client.get_busy_snapshot_without_preload_content.return_value = _mock_rest_response({
        "snapshot": {"type": "NOT_STARTED"},
        "snapshot_timestamp_ms": 1700000000000,
    })
    return client


def _mock_client_simple():
    client = MagicMock()
    client.get_busy_snapshot_without_preload_content.return_value = _mock_rest_response({
        "snapshot": {
            "type": "SIMPLE",
            "card_id": "00000000-0000-0000-0000-000000000000",
            "is_paused": False,
            "time_left_ms": 42000,
        },
        "snapshot_timestamp_ms": 1700000000000,
    })
    return client


def _mock_client_interval():
    client = MagicMock()
    client.get_busy_snapshot_without_preload_content.return_value = _mock_rest_response({
        "snapshot": {
            "type": "INTERVAL",
            "card_id": "00000000-0000-0000-0000-000000000000",
            "is_paused": False,
            "time_left_ms": 120000,
            "current_interval": 2,
            "current_interval_time_total_ms": 60000,
            "current_interval_time_left_ms": 42690,
            "interval_settings": {
                "intervals_count": 5,
                "interval_time_total_ms": 60000,
            },
        },
        "snapshot_timestamp_ms": 1700000000000,
    })
    return client


def _tool_text(result):
    assert isinstance(result, CallToolResult)
    assert result.is_error is False
    item = result.content[0]
    return item.text if hasattr(item, "text") else item["text"]


def test_get_busy_snapshot_not_started_returns_flat_json():
    with patch.object(busy_module, "_make_api") as mock_make_api:
        mock_make_api.return_value = _mock_client_not_started()
        result = busy_module.get_busy_snapshot()
        text = _tool_text(result)

        data = json.loads(text)
        assert data == {
            "snapshot.type": "NOT_STARTED",
            "snapshot_timestamp_ms": 1700000000000,
        }
        assert all(not isinstance(v, dict) for v in data.values())


def test_get_busy_snapshot_simple_returns_flat_json():
    with patch.object(busy_module, "_make_api") as mock_make_api:
        mock_make_api.return_value = _mock_client_simple()
        result = busy_module.get_busy_snapshot()
        text = _tool_text(result)

        data = json.loads(text)
        assert data == {
            "snapshot.type": "SIMPLE",
            "snapshot.card_id": "00000000-0000-0000-0000-000000000000",
            "snapshot.is_paused": False,
            "snapshot.time_left_ms": 42000,
            "snapshot_timestamp_ms": 1700000000000,
        }
        assert all(not isinstance(v, dict) for v in data.values())


def test_get_busy_snapshot_interval_returns_flat_json():
    with patch.object(busy_module, "_make_api") as mock_make_api:
        mock_make_api.return_value = _mock_client_interval()
        result = busy_module.get_busy_snapshot()
        text = _tool_text(result)

        data = json.loads(text)
        assert data["snapshot.type"] == "INTERVAL"
        assert data["snapshot.current_interval"] == 2
        assert data["snapshot.interval_settings.intervals_count"] == 5
        assert data["snapshot_timestamp_ms"] == 1700000000000
        # nested interval_settings is flattened, not an object
        assert all(not isinstance(v, dict) for v in data.values())


def test_get_busy_snapshot_json_literal_forms():
    with patch.object(busy_module, "_make_api") as mock_make_api:
        mock_make_api.return_value = _mock_client_simple()
        result = busy_module.get_busy_snapshot()
        text = _tool_text(result)

        # literal forms: true/false/null, not Python True/False/None
        assert "false" in text
        assert '"snapshot.type"' in text  # double-quoted key
        assert "True" not in text
        assert "False" not in text
        assert "None" not in text

        # and it parses back to the expected structure
        data = json.loads(text)
        assert data["snapshot.is_paused"] is False
