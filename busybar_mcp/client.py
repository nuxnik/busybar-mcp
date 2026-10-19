"""Busy Bar SDK client construction and shared API access."""

import json
from typing import TypeVar

from busybar_python_sdk import Configuration
from busybar_python_sdk.api_client import ApiClient

from .config import Settings

T = TypeVar("T")


def _normalize_base_url(base_url: str) -> str:
    """Ensure a scheme-prefixed URL; prepend ``http://`` to scheme-less hosts."""
    if base_url.startswith(("http://", "https://")):
        return base_url
    return f"http://{base_url}"


class BusyBarClient:
    """Create SDK API clients using one validated application configuration."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.base_url = _normalize_base_url(settings.base_url)
        self._api_client = ApiClient(
            configuration=Configuration(
                host=self.base_url,
                access_token=settings.api_token,
            )
        )

    def api(self, api_class: type[T]) -> T:
        """Return an SDK API namespace backed by this client's connection."""
        return api_class(api_client=self._api_client)

    def get_raw(self, path: str) -> dict:
        """GET a device endpoint via the SDK transport; return the JSON body as a dict.

        Uses the shared ``ApiClient`` so authorization and base URL behave
        identically to generated SDK calls. Raises ``ValueError`` for non-2xx
        responses or a non-JSON body.
        """
        response = self._api_client.call_api("GET", f"{self.base_url}{path}")
        status = response.status
        if not (200 <= (status or 0) < 300):
            raise ValueError(f"Request GET {path} failed with status {status}")
        body = response.read()
        if isinstance(body, bytes):
            body = body.decode("utf-8")
        try:
            return json.loads(body)
        except json.JSONDecodeError as e:
            raise ValueError(f"Could not parse JSON response from GET {path}") from e
