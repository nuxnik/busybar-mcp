# Busy Bar MCP Server

A Python [MCP](https://modelcontextprotocol.io/) server written with [FastMCP](https://fastmcp.endpoints.com/) that wraps the **[busybar_python_sdk](https://github.com/nuxnik/busybar-python-sdk)** to communicate with a physical [Busy Bar](https://busy.app/) device over HTTP. The Busy Bar is a digital time-management display — this MCP server provides 32 tools for account retrieval, system information, time operations, BLE control, and input events, exposing its functionality through the standard Model Context Protocol so other tools and AI assistants can interact with it programmatically.

> **Status:** 32 MCP tools are fully implemented across account retrieval, system information, time operations, device state queries, BLE control, and input events, with a complete test suite. The project is ready to use — see the [What's Next](#whats-next) section below for planned work.

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

The server supports configuration through either a `.env` file or environment variables. The same two variables are required in both cases:

| Variable | Description | Example |
|---|---|---|
| `BUSYBAR_API_TOKEN` | API auth token for authenticating with the Busy Bar device | `my-super-secret-token` |
| `BUSYBAR_BASE_URL` | IP address or hostname of the Busy Bar device (no protocol prefix) | `10.0.4.20` |

### Using `.env`

Create a `.env` file in the project root:

```env
BUSYBAR_API_TOKEN=my-super-secret-token
BUSYBAR_BASE_URL=10.0.4.20
```

The server loads `.env` when it starts.

### Using environment variables

You can also configure the server through variables already present in the process environment:

```sh
export BUSYBAR_API_TOKEN=my-super-secret-token
export BUSYBAR_BASE_URL=10.0.4.20
```

Then start the server normally.

### Configuration precedence

Environment variables take precedence over values in `.env`. The server loads `.env` with `override=False`, so an environment variable that has already been exported is never replaced by the value in `.env`.

For example, if `.env` contains:

```env
BUSYBAR_BASE_URL=10.0.4.20
```

but the shell contains:

```sh
export BUSYBAR_BASE_URL=10.0.4.30
```

then `10.0.4.30` is used.

## Usage

Set `BUSYBAR_API_TOKEN` and `BUSYBAR_BASE_URL` through either `.env` or the environment, then start the MCP server:

```sh
# One-shot run via uvx (no local install required)
BUSYBAR_API_TOKEN=… BUSYBAR_BASE_URL=10.0.4.20 uvx busybar-mcp

# Or install locally and run the console script
uv sync
BUSYBAR_API_TOKEN=… BUSYBAR_BASE_URL=10.0.4.20 busybar-mcp

# Development (built-in MCP dev server / inspector)
uv sync
BUSYBAR_API_TOKEN=… BUSYBAR_BASE_URL=10.0.4.20 mcp dev -- uvx busybar-mcp
```

`python -m busybar_mcp` is equivalent to the console script and starts the same stdio server.

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
| `enable_ble` | Enable the BLE module and start advertising |
| `disable_ble` | Disable the BLE module and stop advertising |
| `remove_ble_pairing` | Remove the current BLE pairing so the device becomes discoverable again |
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

### Input tools

| Tool | Description |
|---|---|
| `send_input_key` | Send a single key-press event to the device (up, down, ok, back, start, busy, custom, off, apps, settings) |

## Architecture

The project follows a thin-client layering with a clear separation between MCP presentation, configuration, and device access:

```text
┌───────────────────────────────┐      MCP/stdio       ┌──────────────────┐
│           MCP Client          │ ◄──────────────────► │   busybar_mcp    │
│         (AI tool)             │                      │                  │
└───────────────────────────────┘                      └────────┬─────────┘
                                                                │
                                      ┌─────────────────────────┼─────────────────────┐
                                      │                         │                     │
                                      ▼                         ▼                     ▼
                                  config.py                tools/              client.py
                                      │                         │                     │
                                      └─────────────────────────┼─────────────────────┘
                                                                │ SDK calls
                                                                ▼
                                                        busybar_python_sdk
                                                                │ HTTP
                                                                ▼
                                                          Busy Bar Device
```

### Package structure

```text
busybar_mcp/
├── __init__.py       # Package API and entry point
├── __main__.py       # python -m busybar_mcp entry point
├── server.py         # MCP server and tool registration
├── client.py         # Busy Bar SDK client boundary
├── config.py         # Runtime configuration from environment
├── _server.py        # Backwards-compatible server import
├── utils.py          # Shared serialization/error utilities
└── tools/             # MCP tool modules and registration
```

The key responsibilities are:

- `server.py` — creates the MCP server, registers the tool package, and starts the stdio transport.
- `config.py` — reads `BUSYBAR_BASE_URL` and `BUSYBAR_API_TOKEN` from the process environment and validates that they are present.
- `client.py` — provides the boundary between the MCP application and `busybar_python_sdk`.
- `tools/` — contains the MCP tool implementations and their registration.
- `utils.py` — contains shared serialization and tool-error helpers.
- `__init__.py` / `__main__.py` — provide the package and command-line entry points.

At startup, `server.py` loads `.env` using `load_dotenv(override=False)`. This means exported environment variables are preserved and take precedence over `.env` values.

The SDK communicates with the device over HTTP using the OpenAPI schema defined by `openapi.yaml`.

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

Coverage is reported via `pytest-cov` (`--cov=busybar_mcp --cov-report=term-missing`).

### Test Coverage Summary

- **32 MCP tools** tested — one parametrized happy-path test per tool across account, system info, time, BLE, busy timer, settings, smart home, storage, update, wifi, and input categories.
- **Configuration tests** verify required environment variables and configuration parsing.
- **Error-path tests** verify behaviour when the Busy Bar device is missing or unreachable (mocked HTTP failures).
- **Missing environment variable tests** confirm that absent `BUSYBAR_BASE_URL` / `BUSYBAR_API_TOKEN` are handled gracefully.
- **Serialization tests** verify `_serialize()` handles SDK models, dicts, lists, scalars, and edge cases correctly.

## What's Next

- Extend with additional write/mutation tools (display messages, notifications)
- Implement MCP resources for live device data streams
- Configure linting and formatting toolchain
