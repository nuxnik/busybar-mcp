"""SDK-surface guard (design D5).

Closes the gap where 99 passing tests coexisted with 7 broken tools: the per-tool
tests mock the SDK with ``MagicMock`` (which fabricates any attribute), so a renamed
or removed generated method went uncaught until it hit the device as an
``AttributeError``.

This guard imports the REAL installed ``busybar_python_sdk`` API classes and asserts
that every generated method a ``busybar_mcp`` tool module actually invokes exists on
the corresponding class. A future SDK regeneration that renames/removes a method the
tools call fails this suite immediately, naming the tool module and the missing
method — instead of surfacing at device runtime.
"""

import pytest
from busybar_python_sdk import (
    AccountApi,
    BLEApi,
    BusyApi,
    InputApi,
    SettingsApi,
    SmartHomeApi,
    StorageApi,
    SystemApi,
    TimeApi,
    UpdaterApi,
    WiFiApi,
)


# Per-tool-module (SDK API class, generated method name) pairs. This table is the
# test-level statement of the tool -> SDK contract, and it mirrors exactly the
# methods each module in busybar_mcp/ calls.
TOOL_SDK_CONTRACT = [
    # busybar_mcp/ble.py
    (BLEApi, "api_ble_status_get"),
    (BLEApi, "api_ble_enable_post"),
    (BLEApi, "api_ble_disable_post"),
    (BLEApi, "api_ble_pairing_delete"),
    # busybar_mcp/settings.py
    (SettingsApi, "get_http_access"),
    (SettingsApi, "api_name_get"),
    (SettingsApi, "get_display_brightness"),
    (SettingsApi, "get_audio_volume"),
    # busybar_mcp/smarthome.py
    (SmartHomeApi, "get_smart_home_commissioning_status"),
    (SmartHomeApi, "api_smart_home_switch_get"),
    # busybar_mcp/wifi.py
    (WiFiApi, "api_wifi_status_get"),
    (WiFiApi, "get_wifi_networks"),
    # busybar_mcp/updater.py
    (UpdaterApi, "get_firmware_update_status"),
    (UpdaterApi, "get_update_changelog"),
    (UpdaterApi, "get_autoupdate_settings"),
    # busybar_mcp/busy.py
    (BusyApi, "get_busy_snapshot_without_preload_content"),
    # busybar_mcp/system.py
    (SystemApi, "get_version"),
    (SystemApi, "get_transport"),
    (SystemApi, "get_status"),
    (SystemApi, "get_status_device"),
    (SystemApi, "get_status_firmware"),
    (SystemApi, "get_status_system"),
    (SystemApi, "get_status_power"),
    # busybar_mcp/input.py
    (InputApi, "set_input_key"),
    # busybar_mcp/account.py
    (AccountApi, "get_account_info"),
    (AccountApi, "get_account_status"),
    (AccountApi, "get_account_backend"),
    # busybar_mcp/time.py
    (TimeApi, "get_time"),
    (TimeApi, "get_time_timezone"),
    (TimeApi, "get_time_tzlist"),
    # busybar_mcp/storage.py
    (StorageApi, "list_storage_files"),
    (StorageApi, "get_storage_status"),
]


def _ids():
    for api_cls, method in TOOL_SDK_CONTRACT:
        yield f"{api_cls.__name__}.{method}"


@pytest.mark.parametrize("api_class,method_name", TOOL_SDK_CONTRACT, ids=_ids())
def test_sdk_method_exists(api_class, method_name):
    """The generated SDK method a tool invokes must exist on the installed class."""
    assert hasattr(api_class, method_name), (
        f"SDK method '{api_class.__name__}.{method_name}' is invoked by a tool "
        f"module in busybar_mcp/ but does not exist on the installed "
        f"busybar_python_sdk — the tool would raise AttributeError at runtime."
    )


def test_contract_covers_a_specific_module_and_method():
    """Guard against the table silently losing a required entry.

    The failure message is required to name BOTH the tool module and the missing
    method (spec: SDK-surface-guard). Pin a known real pair plus a deliberate
    negative to lock the naming behavior down.
    """
    # Positive: the 27.5.1 rename the suite previously let slip.
    assert hasattr(BLEApi, "api_ble_status_get")
    # Negative: the withdrawn 27.5.0-era name must NOT be what we assert against.
    assert hasattr(BLEApi, "api_ble_status_get") and not hasattr(BLEApi, "busybar_ble_status_get")
