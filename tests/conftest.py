import os

import pytest


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
