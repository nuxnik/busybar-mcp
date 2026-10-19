#!/usr/bin/env python3
"""Synchronize publish metadata for busybar-mcp.

This script is run by the CI pipeline on every push to main. It:

1. Derives the target project version from the ``busybar-python-sdk``
   dependency specifier in ``pyproject.toml`` (the first ``X.Y.Z`` token).
   If no such token exists the script exits non-zero with a descriptive
   error.
2. Ensures ``[project.urls]`` declares
   ``repository = "https://github.com/nuxnik/busybar-mcp"``.
3. Ensures the testpypi ``[[tool.uv.index]]`` block is present.
4. Sets ``project.version`` to the target version when it differs.

Edits are made as minimal, formatting-preserving text operations; the file
is re-parsed with ``tomllib`` after editing to guarantee validity. The
script prints exactly two machine-readable lines on stdout:

    TARGET_VERSION=<version>
    CHANGED=<true|false>

Exits 0 on success (whether or not a change was made) and 1 on error.

Stdlib only (Python 3.11+ required for ``tomllib``).
"""

from __future__ import annotations

import re
import sys
import tomllib
from pathlib import Path

REPOSITORY = "https://github.com/nuxnik/busybar-mcp"
VERSION_RE = re.compile(r"\d+\.\d+\.\d+")
SECTION_RE = re.compile(r"^\s*\[([^\]\s]+)\]")
VERSION_KEY_RE = re.compile(r'^\s*version\s*=')


def die(message: str) -> None:
    print(f"sync_metadata: error: {message}", file=sys.stderr)
    sys.exit(1)


def load_toml(path: Path) -> dict:
    try:
        with path.open("rb") as fh:
            return tomllib.load(fh)
    except tomllib.TOMLDecodeError as exc:
        die(f"cannot parse {path}: {exc}")


def derive_target_version(data: dict) -> str:
    dependencies = data.get("project", {}).get("dependencies", [])
    name_match = re.compile(r"^[A-Za-z0-9_.\-]+")
    for dep in dependencies:
        match0 = name_match.match(dep.strip())
        if match0 and match0.group(0) == "busybar-python-sdk":
            match = VERSION_RE.search(dep)
            if match:
                return match.group(0)
            die(
                f"busybar-python-sdk dependency {dep!r} contains no X.Y.Z "
                "version token; expected a form like 'busybar-python-sdk>=27.5.0'"
            )
    die(
        "busybar-python-sdk is not declared in "
        "[project] dependencies; cannot derive a target version"
    )


def section_of(line: str) -> str | None:
    match = SECTION_RE.match(line)
    return match.group(1).strip() if match else None


def find_line(lines: list[str], predicate, section: str | None = None) -> int:
    """Index of the first line matching ``predicate``, optionally only inside ``section``."""
    current = None
    for i, line in enumerate(lines):
        header = section_of(line)
        if header is not None:
            current = header
            continue
        if section is None or current == section:
            if predicate(line):
                return i
    return -1


def find_section_header(lines: list[str], section: str) -> int:
    for i, line in enumerate(lines):
        if section_of(line) == section:
            return i
    return -1


def bump_version(lines: list[str], target: str) -> bool:
    index = find_line(lines, VERSION_KEY_RE.match, section="project")
    if index == -1:
        die("no 'version' key found in the [project] table")
    original = lines[index]
    indent = re.match(r"^\s*", original).group(0)
    updated = f'{indent}version = "{target}"'
    if updated == original:
        return False
    lines[index] = updated
    return True


def ensure_repository_url(lines: list[str], data: dict) -> bool:
    urls = data.get("project", {}).get("urls", {})
    if urls.get("repository") == REPOSITORY:
        return False
    block = f'repository = "{REPOSITORY}"'
    if "project.urls" in {section_of(l) for l in lines}:
        header = find_section_header(lines, "project.urls")
        lines.insert(header + 1, block)
        return True
    # No [project.urls] table: insert it immediately after the last key of
    # [project] (i.e. before the next section header).
    start = find_section_header(lines, "project")
    if start == -1:
        die("no [project] table found")
    end = len(lines)
    for i in range(start + 1, len(lines)):
        if section_of(lines[i]) is not None:
            end = i
            break
    # Drop trailing blank lines of the [project] block for clean spacing.
    insert_at = end
    while insert_at > start + 1 and not lines[insert_at - 1].strip():
        insert_at -= 1
    lines[insert_at:insert_at] = ("", "[project.urls]", block)
    return True


def testpypi_index_present(data: dict) -> bool:
    index_tables = (
        data.get("tool", {}).get("uv", {}).get("index")
        if isinstance(data.get("tool", {}).get("uv", {}).get("index"), list)
        else []
    )
    for entry in index_tables:
        if entry.get("name") == "testpypi":
            if entry.get("url") != "https://test.pypi.org/simple/":
                die("[[tool.uv.index]] 'testpypi' has an unexpected url")
            if entry.get("publish-url") != "https://test.pypi.org/legacy/":
                die("[[tool.uv.index]] 'testpypi' has an unexpected publish-url")
            if entry.get("explicit") is not True:
                die("[[tool.uv.index]] 'testpypi' must declare explicit = true")
            return True
    return False


def ensure_testpypi_index(lines: list[str], data: dict) -> bool:
    if testpypi_index_present(data):
        return False
    block = [
        "",
        "[[tool.uv.index]]",
        'name = "testpypi"',
        'url = "https://test.pypi.org/simple/"',
        'publish-url = "https://test.pypi.org/legacy/"',
        "explicit = true",
    ]
    lines.extend(block)
    return True


def main() -> None:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("pyproject.toml")
    if not path.is_file():
        die(f"{path} not found")

    data = load_toml(path)
    target = derive_target_version(data)

    lines = [line.rstrip("\r\n") for line in path.read_text(encoding="utf-8").splitlines(keepends=True)]

    changed = False
    changed |= bump_version(lines, target)
    changed |= ensure_repository_url(lines, data)
    changed |= ensure_testpypi_index(lines, data)

    text = "\n".join(lines) + "\n"
    # Sanity-check the written TOML parses and carries the expected values.
    try:
        reparsed = tomllib.loads(text)
    except tomllib.TOMLDecodeError as exc:
        die(f"generated pyproject.toml is invalid: {exc}")
    if reparsed.get("project", {}).get("version") != target:
        die(f"validation failed: project.version is {reparsed.get('project', {}).get('version')!r}, expected {target!r}")
    if reparsed.get("project", {}).get("urls", {}).get("repository") != REPOSITORY:
        die("validation failed: [project.urls] repository is missing")
    if not testpypi_index_present(reparsed):
        die("validation failed: testpypi [[tool.uv.index]] is missing")

    if changed:
        path.write_text(text, encoding="utf-8")
        print(f"sync_metadata: updated {path} (version={target}, repository/testpypi ensured)")

    print(f"TARGET_VERSION={target}")
    print(f"CHANGED={'true' if changed else 'false'}")


if __name__ == "__main__":
    main()
