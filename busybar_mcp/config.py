"""Application configuration for Busy Bar MCP."""

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    """Runtime settings required to connect to a Busy Bar device."""

    base_url: str
    api_token: str

    @classmethod
    def from_env(cls) -> "Settings":
        """Load settings from the process environment."""
        base_url = os.environ.get("BUSYBAR_BASE_URL")
        api_token = os.environ.get("BUSYBAR_API_TOKEN")

        if not base_url:
            raise ValueError("Missing required environment variable: BUSYBAR_BASE_URL")
        if not api_token:
            raise ValueError("Missing required environment variable: BUSYBAR_API_TOKEN")

        return cls(base_url=base_url, api_token=api_token)
