from unittest.mock import MagicMock

import pytest

from busybar_mcp.utils import _serialize


# ---------------------------------------------------------------------------
# Serialization tests for `_serialize()`
# ---------------------------------------------------------------------------


def _make_mock_model_dump():
    """Mock object with model_dump attribute."""
    obj = MagicMock()
    obj.model_dump.return_value = {"name": "test", "value": 123}
    return obj


def _make_mock_to_dict():
    """Mock object with to_dict attribute (not model_dump, so first-match logic works)."""
    class ToDictObj:
        def to_dict(self):
            return {"name": "test", "value": 456}
    return ToDictObj()


def _make_mock_underscore_to_dict():
    """Mock object with _to_dict attribute (not model_dump, so first-match logic works)."""
    class UnderscoreObj:
        def _to_dict(self):
            return {"name": "test", "value": 789}
    return UnderscoreObj()


class TestSerializeModelDump:
    def test_model_dump_returns_dict(self):
        """Input with model_dump method is serialized via model_dump."""
        mock_obj = _make_mock_model_dump()
        result = _serialize(mock_obj)
        assert isinstance(result, dict)
        assert result == {"name": "test", "value": 123}

    def test_nested_objects_with_model_dump(self):
        """model_dump output is returned as-is (one level of serialization)."""
        nested = _make_mock_model_dump()
        wrapper = MagicMock()
        # model_dump returns a dict; values inside the dict are not re-serialized by _serialize
        wrapper.model_dump.return_value = {"nested": {"from": "model_dump"}}
        result = _serialize(wrapper)
        assert isinstance(result, dict)
        assert result == {"nested": {"from": "model_dump"}}


class TestSerializeToDict:
    def test_to_dict_returns_dict(self):
        """Input with to_dict method is serialized via to_dict."""
        mock_obj = _make_mock_to_dict()
        result = _serialize(mock_obj)
        assert isinstance(result, dict)
        assert result == {"name": "test", "value": 456}


class TestSerializeUnderscoreToDict:
    def test_underscore_to_dict_returns_dict(self):
        """Input with _to_dict method is serialized via _to_dict."""
        mock_obj = _make_mock_underscore_to_dict()
        result = _serialize(mock_obj)
        assert isinstance(result, dict)
        assert result == {"name": "test", "value": 789}


class TestSerializeList:
    def test_list_of_models_serializes_each_element(self):
        """Input is a list — each element is individually serialized."""
        mock1 = _make_mock_model_dump()
        mock2 = MagicMock()
        mock2.model_dump.return_value = {"other": "value"}
        result = _serialize([mock1, mock2])
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0] == {"name": "test", "value": 123}
        assert result[1] == {"other": "value"}

    def test_empty_list(self):
        """Empty list input returns empty list."""
        result = _serialize([])
        assert result == []


class TestSerializeScalarPassthrough:
    @pytest.mark.parametrize("input_val", [42, "hello", 3.14, True, None, {"key": "val"}])
    def test_scalar_passthrough(self, input_val):
        """Input is a non-model scalar passes through unchanged."""
        result = _serialize(input_val)
        assert result == input_val

    def test_none_input(self):
        """None passes through as None."""
        result = _serialize(None)
        assert result is None


class TestSerializeEdgeCases:
    def test_priority_model_dump_over_to_dict(self):
        """If an object has both model_dump and to_dict, model_dump wins (first match)."""
        mock_obj = MagicMock()
        mock_obj.model_dump.return_value = {"from": "model_dump"}
        mock_obj.to_dict.return_value = {"from": "to_dict"}
        result = _serialize(mock_obj)
        assert result == {"from": "model_dump"}

    def test_empty_model_result(self):
        """An object whose model_dump returns empty dict is handled correctly."""
        mock_obj = MagicMock()
        mock_obj.model_dump.return_value = {}
        result = _serialize(mock_obj)
        assert isinstance(result, dict)
        assert result == {}
