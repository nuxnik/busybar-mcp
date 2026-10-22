"""Client boundary tests: base URL scheme normalization and token wiring.

Lightweight: the SDK ``Configuration`` is mocked so no HTTP machinery runs.
"""

from unittest.mock import patch

from busybar_mcp import client as client_module
from busybar_mcp.config import Settings


def _settings(base_url):
    return Settings(base_url=base_url, api_token="secret-token")


def test_scheme_less_base_url_is_normalized_to_http():
    with patch.object(client_module, "Configuration") as mock_configuration, \
            patch.object(client_module, "ApiClient") as mock_api_client:
        settings = _settings("10.0.4.20")
        client = client_module.BusyBarClient(settings)

        assert client.base_url == "http://10.0.4.20"
        kwargs = mock_configuration.call_args.kwargs
        assert kwargs["host"] == "http://10.0.4.20"
        # The device token is wired through the generated `ApiKeyAuth` scheme
        # (SDK 27.5.x sends it as the `X-API-Token` header).
        assert kwargs["api_key"] == {"ApiKeyAuth": "secret-token"}
        mock_api_client.assert_called_once_with(configuration=mock_configuration.return_value)


def test_scheme_prefixed_base_url_is_left_as_is():
    with patch.object(client_module, "Configuration") as mock_configuration, \
            patch.object(client_module, "ApiClient") as mock_api_client:
        client = client_module.BusyBarClient(_settings("https://my-bar.example.com"))

        assert client.base_url == "https://my-bar.example.com"
        kwargs = mock_configuration.call_args.kwargs
        assert kwargs["host"] == "https://my-bar.example.com"


def test_api_token_is_wired_as_apikaut_api_key():
    """Regression guard: the token must reach the SDK as `api_key['ApiKeyAuth']`.

    On busybar_python_sdk 27.5.x, `Configuration(access_token=…)` produces NO
    header at all (silently dropped by `auth_settings()`), so pinning the
    `api_key` wiring is what actually transmits the device token as `X-API-Token`.
    """
    with patch.object(client_module, "Configuration") as mock_configuration, \
            patch.object(client_module, "ApiClient"):
        client_module.BusyBarClient(_settings("http://10.0.4.20"))

        kwargs = mock_configuration.call_args.kwargs
        assert kwargs["api_key"] == {"ApiKeyAuth": "secret-token"}
        assert "access_token" not in kwargs


def test_get_raw_raises_for_non_2xx_and_parses_json_body():
    client = client_module.BusyBarClient(_settings("10.0.4.20"))

    with patch.object(client._api_client, "call_api") as mock_call_api:
        # Non-2xx status surfaces as a ValueError.
        mock_call_api.return_value.status = 503
        mock_call_api.return_value.read.return_value = b"boom"
        try:
            client.get_raw("/api/ble/status")
        except ValueError:
            pass
        else:
            raise AssertionError("get_raw should raise for non-2xx responses")

        # 2xx JSON body is parsed and returned.
        mock_call_api.return_value.status = 200
        mock_call_api.return_value.read.return_value = b'{"count": 1}'
        assert client.get_raw("/api/wifi/networks") == {"count": 1}
        mock_call_api.assert_called()
