"""Tests for application configuration."""

import pytest

from busybar_mcp.config import Settings


def test_settings_from_env(monkeypatch):
    monkeypatch.setenv("BUSYBAR_BASE_URL", "10.0.4.20")
    monkeypatch.setenv("BUSYBAR_API_TOKEN", "secret")

    assert Settings.from_env() == Settings(base_url="10.0.4.20", api_token="secret")


@pytest.mark.parametrize("missing", ["BUSYBAR_BASE_URL", "BUSYBAR_API_TOKEN"])
def test_settings_requires_credentials(monkeypatch, missing):
    monkeypatch.setenv("BUSYBAR_BASE_URL", "10.0.4.20")
    monkeypatch.setenv("BUSYBAR_API_TOKEN", "secret")
    monkeypatch.delenv(missing)

    with pytest.raises(ValueError, match=missing):
        Settings.from_env()
