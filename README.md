# Busy Bar MCP Server

**NOTE: This project is still a work in progress**

A Python [MCP](https://modelcontextprotocol.io/) server written with [FastMCP](https://fastmcp.endpoints.com/) that wraps the **[busybar_python_sdk](https://github.com/nuxnik/busybar-python-sdk)** to communicate with a physical [Busy Bar](https://busy.app/) device over HTTP. The Busy Bar is a digital time-management display — this MCP server currently provides 13 tools for account retrieval, system information, and time operations, exposing its functionality through the standard Model Context Protocol so other tools and AI assistants can interact with it programmatically.

> **Status:** 28 MCP tools are fully implemented across account retrieval, system information, time operations, and device state queries, with a complete test suite documented in this README. The project is ready to use — see the [What's Next](#whats-next) section below for planned work.

## Prerequisites

- **Python ≥ 3.12** — the project pins Python 3.12+ (see `.python-version`)
- **[uv](https://github.com/astral-sh/uv)** — dependency manager and virtual environment resolver

## Installation

Clone the repository and install dependencies:

```sh
uv sync
```

This creates a virtual environment and installs all packages declared in `pyproject.toml` (including `busybar_python_sdk`).

## Configuration

Copy the example `.env.example` file (if present) to create your own `.env` at the project root with the following variables.

| Variable | Description | Example |
|---|---|---|
| `BUSYBAR_API_TOKEN` | API auth token for authenticating with the Busy Bar device | `my-super-secret-token` |
| `BUSYBAR_BASE_URL` | IP address or hostname of the Busy Bar device (no protocol prefix) | `10.0.4.20` |

```env
BUSYBAR_API_TOKEN=my-super-secret-token
BUSYBAR_BASE_URL=10.0.4.20
```

It is also possible to declare the variables before starting the server:
```env
export BUSYBAR_API_TOKEN=my-super-secret-token && export BUSYBAR_BASE_URL=10.0.4.20 
```

## Usage

Start the MCP server for development:

```sh
mcp dev server.py          # built-in MCP development server
```

Or run it standalone:

```sh
uv run server.py           # running the MCP server directly via uv
```

Once started, clients can connect to the server using their MCP transport.

## MCP Tools

### Account tools

| Tool | Description |
|---|---|
| `get_account_info` | Retrieve linked account information (email, account ID) from the Busy Bar device |
| `get_account_status` | Check MQTT connection state for the linked account |
| `get_account_backend` | Inspect MQTT backend configuration (server URL, certificate settings) |

### System tools

| Tool | Description |
|---|---|
| `get_api_version` | Query the API version supported by the device |
| `get_transport` | Get the current network transport type (USB or Wi-Fi) |
| `get_device_status` | Comprehensive health check: device, firmware, system, and power state |
| `get_device_info` | Retrieve hardware identifiers and manufacturing details |
| `get_firmware_info` | Get firmware version and build metadata |
| `get_system_status` | Runtime system metrics (uptime, API SemVer, auto-update settings) |
| `get_power_status` | Battery charge level, voltage, current, and charging state |

### Time tools

| Tool | Description |
|---|---|
| `get_time` | Retrieve the device's real-time clock timestamp in ISO 8601 format |
| `get_timezone` | Get the currently configured timezone (name, offset, abbreviation) |
| `get_tzlist` | List all supported timezones available for configuration |

### Device Status & Configuration

| Tool | Description |
|---|---|
| `get_ble_status` | Retrieve BLE module status (powered state, MAC address) |
| `get_busy_snapshot` | Get the current BUSY timer state including profile and timing details |
| `get_http_access` | Inspect HTTP API key management mode and validity |
| `get_device_name` | Get the human-readable device name |
| `get_display_brightness` | Retrieve the current display brightness level |
| `get_audio_volume` | Retrieve the current audio volume level |
| `get_smart_home_pairing_status` | Query Matter fabric count and latest commissioning outcome |
| `get_smart_home_switch_state` | Read smart home relay/output state and startup behavior |
| `list_storage_files` | List files and directories on device storage (accepts optional path argument) |
| `get_storage_status` | Get storage capacity details (used, free, total bytes) |
| `get_firmware_update_status` | Check currently installed firmware and pending update state |
| `get_update_changelog` | Retrieve release notes for a specific firmware version (accepts required version argument) |
| `get_autoupdate_settings` | Get automatic update configuration (enabled, window start/end) |
| `get_wifi_status` | Get Wi-Fi connection details (SSID, signal strength, channel, security) |
| `get_wifi_networks` | Retrieve scanned available Wi-Fi networks in range |

## Architecture

The project follows a thin-client layering:

1. **server.py** — single-file MCP server that declares tools/resources via FastMCP
2. **busybar_python_sdk** — Python SDK (Git dependency) that encapsulates all Busy Bar API logic
3. **HTTP → Busy Bar device** — the SDK communicates with the device over HTTP using the OpenAPI schema defined in `openapi.yaml`

```
┌─────────────┐     MCP/stdio      ┌──────────────────┐     SDK calls     ┌──────────────┐
│  MCP Client │ ◄────────────────► │ server.py        │                  │ Busy Bar     │
│  (AI tool)  │   FastMCP tools    │ (FastMCP binding)│                  │ Device       │
└─────────────┘                    └──────────────────┘ ◄────────────────► └──────────────┘
                                      │                              HTTP (OpenAPI)
                                busybar_python_sdk
                                 (internal lib)
```

## Testing

A working test suite is included with the project. The convenience runner at `run_tests.py` invokes pytest against the `tests/` directory with sensible defaults and no-header output.

### Run basic tests

```sh
python run_tests.py
```

### Run with coverage output

```sh
COVERAGE=1 python run_tests.py
```

Coverage is reported via `pytest-cov` (`--cov=server --cov-report=term-missing`).

### Test Coverage Summary

- **28 MCP tools** tested — one parametrized happy-path test per tool across account, system info, time, BLE, busy timer, settings, smart home, storage, update, and wifi categories.
- **Error-path tests** verify behaviour when the Busy Bar device is missing or unreachable (mocked HTTP failures).
- **Missing environment variable tests** confirm that absent `BUSYBAR_BASE_URL` / `BUSYBAR_API_TOKEN` are handled gracefully.
- **conftest fixtures**:
  - `mock_api_client` — patches `server._make_api` to return a mock client with all stubbed API methods, so no real HTTP requests are made.
  - `clear_env_vars` — temporarily removes `BUSYBAR_BASE_URL` and `BUSYBAR_API_TOKEN` from `os.environ` (restoring originals afterward).

## What's Next

- Extend with write/mutation tools (display messages, notifications)
- Implement MCP resources for live device data streams
- Configure linting and formatting toolchain


---

*Project status: 28 MCP tools implemented across account, system info, time, device state, and configuration endpoints.*
