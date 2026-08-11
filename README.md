# Busy Bar MCP Server

A Python [MCP](https://modelcontextprotocol.io/) server written with [FastMCP](https://fastmcp.endpoints.com/) that wraps the **busybar_python_sdk** to communicate with a physical [Busy Bar](https://busybar.co.uk/) device over HTTP. The Busy Bar is a digital queue-management display — this MCP server currently provides 13 tools for account retrieval, system information, and time operations, exposing its functionality through the standard Model Context Protocol so other tools and AI assistants can interact with it programmatically.

> **Status:** 13 MCP tools are fully implemented across account retrieval, system information, and time categories. The project is ready to use — see the [What's Next](#whats-next) section below for planned work.

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

Copy the example `.env.example` file (if present) or create your own `.env` at the project root with the following variables:

| Variable | Description | Example |
|---|---|---|
| `BUSYBAR_API_TOKEN` | API auth token for authenticating with the Busy Bar device | `my-super-secret-token` |
| `BUSYBAR_BASE_URL` | IP address or hostname of the Busy Bar device (no protocol prefix) | `10.0.4.20` |

```env
BUSYBAR_API_TOKEN=my-super-secret-token
BUSYBAR_BASE_URL=10.0.4.20
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

Once started, clients can connect to the server over stdio using their MCP transport.

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

## What's Next

- Extend with write/mutation tools (display messages, notifications)
- Implement MCP resources for live device data streams
- Configure linting and formatting toolchain
- Add test coverage

---

*Project status: 13 MCP tools implemented across account, system info, and time endpoints.*
