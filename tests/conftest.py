import os
from unittest.mock import MagicMock, patch, Mock

import pytest


def _make_mock_model():
    """Return a mock SDK model object with a model_dump method."""
    model = Mock()
    model.model_dump.return_value = {"_mock": True}
    return model


@pytest.fixture
def mock_api_client():
    """Fixture that patches server._make_api to return a mock client with stubbed API methods.

    Each tool under test calls _make_api(<ApiClass>), then invokes an instance method
    on the returned object (e.g. api.get_account_info()). This fixture intercepts that chain
    so no real HTTP request is made.
    """
    with patch("server._make_api") as mock_make_api:
        mock_client = MagicMock()

        # Account API stubs
        mock_client.get_account_info.return_value = _make_mock_model()
        mock_client.get_account_status.return_value = _make_mock_model()
        mock_client.get_account_backend.return_value = _make_mock_model()

        # System API stubs
        mock_client.get_version.return_value = _make_mock_model()
        mock_client.get_transport.return_value = _make_mock_model()
        mock_client.get_status.return_value = _make_mock_model()
        mock_client.get_status_device.return_value = _make_mock_model()
        mock_client.get_status_firmware.return_value = _make_mock_model()
        mock_client.get_status_system.return_value = _make_mock_model()
        mock_client.get_status_power.return_value = _make_mock_model()

        # Time API stubs
        mock_client.get_time.return_value = _make_mock_model()
        mock_client.get_time_timezone.return_value = _make_mock_model()
        mock_client.get_time_tzlist.return_value = _make_mock_model()

        # BLE API stubs
        mock_client.api_ble_status_get.return_value = _make_mock_model()

        # Busy API stubs
        mock_client.get_busy_snapshot.return_value = _make_mock_model()

        # Settings API stubs
        mock_client.get_http_access.return_value = _make_mock_model()
        mock_client.api_name_get.return_value = _make_mock_model()
        mock_client.get_display_brightness.return_value = _make_mock_model()
        mock_client.get_audio_volume.return_value = _make_mock_model()

        # Smart Home API stubs
        mock_client.get_smart_home_commissioning_status.return_value = _make_mock_model()
        mock_client.api_smart_home_switch_get.return_value = _make_mock_model()

        # Storage API stubs
        mock_client.list_storage_files.return_value = _make_mock_model()
        mock_client.get_storage_status.return_value = _make_mock_model()

        # Updater API stubs
        mock_client.get_firmware_update_status.return_value = _make_mock_model()
        mock_client.get_update_changelog.return_value = _make_mock_model()
        mock_client.get_autoupdate_settings.return_value = _make_mock_model()

        # Wi-Fi API stubs
        mock_client.api_wifi_status_get.return_value = _make_mock_model()
        mock_client.get_wifi_networks.return_value = _make_mock_model()

        mock_make_api.return_value = mock_client
        yield mock_make_api, mock_client


@pytest.fixture
def clear_env_vars():
    """Temporarily unlink BUSYBAR_BASE_URL and BUSYBAR_API_TOKEN from os.environ.

    Restores original values (if any) after the test completes.
    """
    originals = {
        "BUSYBAR_BASE_URL": os.environ.pop("BUSYBAR_BASE_URL", None),
        "BUSYBAR_API_TOKEN": os.environ.pop("BUSYBAR_API_TOKEN", None),
    }
    yield
    # Restore
    for key, val in originals.items():
        if val is not None:
            os.environ[key] = val
