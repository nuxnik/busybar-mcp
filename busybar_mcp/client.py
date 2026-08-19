"""Busy Bar SDK client construction and shared API access."""

from typing import TypeVar

from busybar_python_sdk import Configuration
from busybar_python_sdk.api_client import ApiClient

from .config import Settings

T = TypeVar("T")


class BusyBarClient:
    """Create SDK API clients using one validated application configuration."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self._api_client = ApiClient(
            configuration=Configuration(
                host=settings.base_url,
                api_key={"ApiKeyAuth": settings.api_token},
            )
        )

    def api(self, api_class: type[T]) -> T:
        """Return an SDK API namespace backed by this client's connection."""
        return api_class(api_client=self._api_client)
