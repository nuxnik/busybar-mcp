"""Tests for package version alignment with the busybar-python-sdk dependency."""

import re
import tomllib
from pathlib import Path

PYPROJECT = Path(__file__).resolve().parent.parent / "pyproject.toml"
VERSION_RE = re.compile(r"\d+\.\d+\.\d+")
NAME_RE = re.compile(r"^[A-Za-z0-9_.\-]+")


def _load_project() -> dict:
    with PYPROJECT.open("rb") as fh:
        return tomllib.load(fh)["project"]


def _sdk_version_token(project: dict) -> str:
    """Return the first X.Y.Z token in the busybar-python-sdk dependency specifier.

    Mirrors the derivation in scripts/sync_metadata.py so the test and the publish
    automation agree by construction.
    """
    for dep in project.get("dependencies", []):
        match = NAME_RE.match(dep.strip())
        if match and match.group(0) == "busybar-python-sdk":
            token = VERSION_RE.search(dep)
            assert token is not None, f"no X.Y.Z token in {dep!r}"
            return token.group(0)
    raise AssertionError("busybar-python-sdk is not declared in [project] dependencies")


def test_package_version_matches_sdk_token():
    project = _load_project()
    assert project["version"] == _sdk_version_token(project)
