"""MCP tool registration boundary.

The concrete tool modules remain organized by Busy Bar API namespace. This
package provides one explicit registration point for the server.
"""

from .. import account, ble, busy, input, settings, smarthome, storage, system, time, updater, wifi

__all__ = [
    "account",
    "ble",
    "busy",
    "input",
    "settings",
    "smarthome",
    "storage",
    "system",
    "time",
    "updater",
    "wifi",
]
