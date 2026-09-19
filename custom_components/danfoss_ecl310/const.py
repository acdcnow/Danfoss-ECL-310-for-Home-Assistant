"""Constants for the Danfoss ECL 310 integration.

Every entity this integration exposes is described declaratively here, so
adding a register does not mean touching the entity code.

Sensor configuration keys
-------------------------
``key``
    Unique per config entry. Also the key the coordinator stores the value
    under, and the suffix of the entity's unique id.
``name``
    Displayed name. The prefix (``Mode:``, ``Temp:``, ``Limit:``, ...) groups
    the entities alphabetically.
``addr``
    Modbus register address, as documented by Danfoss (not the 4xxxx/3xxxx
    reference notation).
``type``
    ``"input"`` for input registers (FC04), ``"holding"`` for holding
    registers (FC03).
``signed``
    ``True`` to decode the register as a two's-complement int16. Temperatures
    may be negative; counters, serial numbers and status codes may not.
    Defaults to ``False``.
``scale``
    Multiplier applied to the raw register (``0.01`` turns ``2350`` into
    ``23.50``). Defaults to ``1``.
``unit`` / ``device_class`` / ``icon`` / ``precision``
    Passed straight to the entity.
``entity_category``
    ``EntityCategory.DIAGNOSTIC`` or ``EntityCategory.CONFIG``.
``trans_key``
    Translation key used to map a 0/1/2 status code onto a localized string.
    The value is exposed as ``str(int)`` so it matches the numbered
    ``entity.<platform>.<trans_key>.state`` translations.
``enabled_default``
    ``False`` to register the entity as disabled. Defaults to ``True``.
``value_fn``
    Optional callable applied to the raw value, overriding ``scale``.
    Used for values that are not a plain scalar, such as the packed
    firmware revision.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Final

from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.const import EntityCategory, UnitOfTemperature

DOMAIN: Final = "danfoss_ecl310"

MANUFACTURER: Final = "Danfoss"
MODEL: Final = "ECL 310"

DEFAULT_PORT: Final = 502

#: The ECL 310 answers on a fixed Modbus station address. Danfoss documents
#: 254 for application 247.1 (V01), and it is not user configurable, so it is
#: a constant here rather than a config flow option.
DEFAULT_UNIT_ID: Final = 254

# Polling intervals, in seconds.
DEFAULT_INTERVAL_STATUS: Final = 30
DEFAULT_INTERVAL_TEMPERATURE: Final = 60
DEFAULT_INTERVAL_SETTINGS: Final = 600

#: Ceiling for a single block read, below the protocol limit of 125 registers.
MAX_BLOCK_LENGTH: Final = 100


# --- Entity grouping ------------------------------------------------------------
# The entities are spread over several devices: one for the controller itself and
# a child device per group. Home Assistant 2026.9 child devices are exactly this -
# a lightweight logical part of a parent device - so the groups nest under the
# controller in the interface rather than showing up as unrelated devices.
GROUP_CONTROLS: Final = "controls"
GROUP_SENSORS: Final = "sensors"
GROUP_PUMPS: Final = "pumps"
GROUP_CONFIGURATION: Final = "configuration"
GROUP_DIAGNOSTICS: Final = "diagnostics"

#: Display names of the child devices, in the order they are created.
GROUP_NAMES: Final[dict[str, str]] = {
    GROUP_CONTROLS: "Controls",
    GROUP_SENSORS: "Sensors",
    GROUP_PUMPS: "Pumps",
    GROUP_CONFIGURATION: "Configuration",
    GROUP_DIAGNOSTICS: "Diagnostics",
}

GROUPS: Final[tuple[str, ...]] = tuple(GROUP_NAMES)

#: The pumps are read alongside the rest of the status registers but get a device
#: of their own, so they are called out by key.
PUMP_KEYS: Final[frozenset[str]] = frozenset(
    {
        "pump_1",
        "pump_2",
        "pump_3",
        "manual_pump_1",
        "manual_pump_2",
        "manual_pump_3",
    }
)


def device_group_for_sensor(config: Mapping[str, Any]) -> str:
    """Return which device a read-only entity belongs on.

    Pumps have a device of their own. Diagnostic entities - the limits, the
    setpoint read-backs and the system information - are kept together so they
    can be tucked away. Everything else is a live reading and goes with the
    sensors.
    """
    if config["key"] in PUMP_KEYS:
        return GROUP_PUMPS
    if config.get("entity_category") is EntityCategory.DIAGNOSTIC:
        return GROUP_DIAGNOSTICS
    return GROUP_SENSORS


# --- Status and operating modes -------------------------------------------------
SENSORS_STATUS: Final[list[dict[str, Any]]] = [
    {"key": "mode_heating", "name": "Mode: Heating", "addr": 4200, "type": "input", "trans_key": "operating_mode", "icon": "mdi:radiator"},
    {"key": "mode_dhw", "name": "Mode: DHW", "addr": 4201, "type": "input", "trans_key": "operating_mode", "icon": "mdi:water-boiler"},

    {"key": "pump_1", "name": "Mode: Pump P1", "addr": 4005, "type": "input", "trans_key": "simple_on_off", "icon": "mdi:pump"},
    {"key": "pump_2", "name": "Mode: Pump P2", "addr": 4006, "type": "input", "trans_key": "simple_on_off", "icon": "mdi:pump"},
    {"key": "pump_3", "name": "Mode: Pump P3", "addr": 4007, "type": "input", "trans_key": "simple_on_off", "icon": "mdi:pump"},

    {"key": "valve_m1_opening", "name": "Mode: Valve M1 Opening", "addr": 3999, "type": "input", "trans_key": "simple_on_off", "icon": "mdi:valve-open"},
    {"key": "valve_m1_closing", "name": "Mode: Valve M1 Closing", "addr": 4000, "type": "input", "trans_key": "simple_on_off", "icon": "mdi:valve-closed"},
    {"key": "valve_m2_opening", "name": "Mode: Valve M2 Opening", "addr": 4001, "type": "input", "trans_key": "simple_on_off", "icon": "mdi:valve-open"},
    {"key": "valve_m2_closing", "name": "Mode: Valve M2 Closing", "addr": 4002, "type": "input", "trans_key": "simple_on_off", "icon": "mdi:valve-closed"},
    {"key": "valve_m3_opening", "name": "Mode: Valve M3 Opening", "addr": 4003, "type": "input", "trans_key": "simple_on_off", "icon": "mdi:valve-open"},
    {"key": "valve_m3_closing", "name": "Mode: Valve M3 Closing", "addr": 4004, "type": "input", "trans_key": "simple_on_off", "icon": "mdi:valve-closed"},

    {"key": "manual_valve_m1", "name": "Mode: Manual Valve M1", "addr": 4059, "type": "input", "trans_key": "valve_manual_mode", "icon": "mdi:cog"},
    {"key": "manual_valve_m2", "name": "Mode: Manual Valve M2", "addr": 4060, "type": "input", "trans_key": "valve_manual_mode", "icon": "mdi:cog"},
    {"key": "manual_valve_m3", "name": "Mode: Manual Valve M3", "addr": 4061, "type": "input", "trans_key": "valve_manual_mode", "icon": "mdi:cog"},

    {"key": "manual_pump_1", "name": "Mode: Manual Pump P1", "addr": 4065, "type": "input", "trans_key": "pump_mode", "icon": "mdi:cog"},
    {"key": "manual_pump_2", "name": "Mode: Manual Pump P2", "addr": 4066, "type": "input", "trans_key": "pump_mode", "icon": "mdi:cog"},
    {"key": "manual_pump_3", "name": "Mode: Manual Pump P3", "addr": 4067, "type": "input", "trans_key": "pump_mode", "icon": "mdi:cog"},
]


# --- Temperatures and limits ----------------------------------------------------
# Temperatures are signed: outdoor and flow readings go below zero.
SENSORS_TEMPERATURE: Final[list[dict[str, Any]]] = [
    {"key": "temp_s1_outdoor", "name": "Temp: Outdoor (S1)", "addr": 10200, "type": "input", "signed": True, "scale": 0.01, "unit": UnitOfTemperature.CELSIUS, "device_class": SensorDeviceClass.TEMPERATURE, "precision": 1},
    {"key": "temp_s2_room", "name": "Temp: Room (S2)", "addr": 10201, "type": "input", "signed": True, "scale": 0.01, "unit": UnitOfTemperature.CELSIUS, "device_class": SensorDeviceClass.TEMPERATURE, "precision": 1},
    {"key": "temp_s3_flow", "name": "Temp: Flow (S3)", "addr": 10202, "type": "input", "signed": True, "scale": 0.01, "unit": UnitOfTemperature.CELSIUS, "device_class": SensorDeviceClass.TEMPERATURE, "precision": 1},
    {"key": "temp_s4_dhw", "name": "Temp: DHW (S4)", "addr": 10203, "type": "input", "signed": True, "scale": 0.01, "unit": UnitOfTemperature.CELSIUS, "device_class": SensorDeviceClass.TEMPERATURE, "precision": 1},
    {"key": "temp_s5", "name": "Temp: S5", "addr": 10204, "type": "input", "signed": True, "scale": 0.01, "unit": UnitOfTemperature.CELSIUS, "device_class": SensorDeviceClass.TEMPERATURE, "precision": 1},
    {"key": "temp_s6", "name": "Temp: S6", "addr": 10205, "type": "input", "signed": True, "scale": 0.01, "unit": UnitOfTemperature.CELSIUS, "device_class": SensorDeviceClass.TEMPERATURE, "precision": 1},

    {"key": "flow_target_calc", "name": "Temp: Flow Target (Calc)", "addr": 11253, "type": "input", "signed": True, "scale": 0.1, "unit": UnitOfTemperature.CELSIUS, "device_class": SensorDeviceClass.TEMPERATURE, "icon": "mdi:thermostat-auto", "precision": 1},

    {"key": "return_limit_day", "name": "Limit: Return (Day)", "addr": 11181, "type": "input", "signed": True, "scale": 0.1, "unit": UnitOfTemperature.CELSIUS, "device_class": SensorDeviceClass.TEMPERATURE, "icon": "mdi:arrow-left-bold-outline", "precision": 1},
    {"key": "return_limit_night", "name": "Limit: Return (Night)", "addr": 11182, "type": "input", "signed": True, "scale": 0.1, "unit": UnitOfTemperature.CELSIUS, "device_class": SensorDeviceClass.TEMPERATURE, "icon": "mdi:arrow-left-bold-outline", "precision": 1},
    {"key": "summer_cutout", "name": "Limit: Summer Cutout", "addr": 11189, "type": "input", "signed": True, "scale": 0.1, "unit": UnitOfTemperature.CELSIUS, "device_class": SensorDeviceClass.TEMPERATURE, "icon": "mdi:weather-sunny-off", "precision": 1},
]


# --- Settings, limits and system information ------------------------------------
SENSORS_SETTINGS: Final[list[dict[str, Any]]] = [
    {"key": "limit_outdoor_min", "name": "Limit: Min Outdoor", "addr": 10499, "type": "input", "signed": True, "scale": 0.01, "unit": UnitOfTemperature.CELSIUS, "device_class": SensorDeviceClass.TEMPERATURE, "entity_category": EntityCategory.DIAGNOSTIC, "precision": 1},
    {"key": "limit_outdoor_max", "name": "Limit: Max Outdoor", "addr": 10504, "type": "input", "signed": True, "scale": 0.01, "unit": UnitOfTemperature.CELSIUS, "device_class": SensorDeviceClass.TEMPERATURE, "entity_category": EntityCategory.DIAGNOSTIC, "precision": 1},
    {"key": "limit_frost", "name": "Limit: Frost Protection", "addr": 12092, "type": "input", "signed": True, "unit": UnitOfTemperature.CELSIUS, "device_class": SensorDeviceClass.TEMPERATURE, "entity_category": EntityCategory.DIAGNOSTIC},
    {"key": "limit_flow_min", "name": "Limit: Flow Min", "addr": 11176, "type": "input", "signed": True, "unit": UnitOfTemperature.CELSIUS, "device_class": SensorDeviceClass.TEMPERATURE, "entity_category": EntityCategory.DIAGNOSTIC},
    {"key": "limit_flow_max", "name": "Limit: Flow Max", "addr": 11177, "type": "input", "signed": True, "unit": UnitOfTemperature.CELSIUS, "device_class": SensorDeviceClass.TEMPERATURE, "entity_category": EntityCategory.DIAGNOSTIC},

    # Read-back of the setpoints the number entities write.
    {"key": "target_flow_status", "name": "Set: Flow Target (Read)", "addr": 11179, "type": "input", "signed": True, "scale": 0.1, "unit": UnitOfTemperature.CELSIUS, "device_class": SensorDeviceClass.TEMPERATURE, "entity_category": EntityCategory.DIAGNOSTIC, "precision": 1},
    {"key": "target_setback_status", "name": "Set: Setback Target (Read)", "addr": 11180, "type": "input", "signed": True, "scale": 0.1, "unit": UnitOfTemperature.CELSIUS, "device_class": SensorDeviceClass.TEMPERATURE, "entity_category": EntityCategory.DIAGNOSTIC, "precision": 1},
    {"key": "target_dhw", "name": "Set: DHW Normal (Read)", "addr": 12189, "type": "input", "signed": True, "scale": 0.1, "unit": UnitOfTemperature.CELSIUS, "device_class": SensorDeviceClass.TEMPERATURE, "entity_category": EntityCategory.DIAGNOSTIC, "precision": 1},
    {"key": "target_dhw_setback", "name": "Set: DHW Setback (Read)", "addr": 12190, "type": "input", "signed": True, "scale": 0.1, "unit": UnitOfTemperature.CELSIUS, "device_class": SensorDeviceClass.TEMPERATURE, "entity_category": EntityCategory.DIAGNOSTIC, "precision": 1},

    # System information. Unsigned: these are identity values, not temperatures,
    # so a serial number above 32767 must not be decoded as negative.
    {"key": "system_serial_number", "name": "System: Serial Number", "addr": 36, "type": "holding", "icon": "mdi:barcode", "entity_category": EntityCategory.DIAGNOSTIC},
    {"key": "system_app_key", "name": "System: Application Key", "addr": 2060, "type": "holding", "icon": "mdi:key-variant", "entity_category": EntityCategory.DIAGNOSTIC},
    {"key": "system_firmware", "name": "System: Firmware", "addr": 34, "type": "holding", "icon": "mdi:chip", "entity_category": EntityCategory.DIAGNOSTIC, "value_fn": lambda raw: f"{raw >> 8}.{raw & 0xFF:02d}"},
    {"key": "system_hardware", "name": "System: Hardware Revision", "addr": 33, "type": "holding", "icon": "mdi:chip", "entity_category": EntityCategory.DIAGNOSTIC},
    {"key": "system_modbus_addr", "name": "System: Modbus Address", "addr": 37, "type": "holding", "icon": "mdi:network", "entity_category": EntityCategory.DIAGNOSTIC},
]


# --- Writable setpoints and heat curve (number entities) ------------------------
# ``scale`` converts between the value shown in Home Assistant and the raw
# register value. ``min``/``max`` are in Home Assistant units.
NUMBER_ENTITIES: Final[list[dict[str, Any]]] = [
    # Registers 11179/11180 hold the *flow* temperature setpoints when
    # application 247.1 is loaded, which is why the range goes up to 90 °C.
    # Verify against your controller before relying on the extremes.
    {"name": "Set: Target Comfort", "key": "conf_target_comfort", "address": 11179, "min": 10, "max": 90, "step": 0.5, "icon": "mdi:thermometer-check", "scale": 0.1, "unit": UnitOfTemperature.CELSIUS},
    {"name": "Set: Target Setback", "key": "conf_target_setback", "address": 11180, "min": 10, "max": 90, "step": 0.5, "icon": "mdi:thermometer-low", "scale": 0.1, "unit": UnitOfTemperature.CELSIUS},
    # The slope is dimensionless: it must not be labelled with a unit.
    {"name": "Curve: Slope", "key": "heat_curve_slope", "address": 11174, "min": 0.1, "max": 2.5, "step": 0.1, "icon": "mdi:chart-line", "scale": 0.1, "unit": None},

    # Heat curve coordinates. Scale 1 because these are whole degrees.
    {"name": "Curve: -30°C", "key": "heat_curve_m30", "address": 11399, "min": 0, "max": 90, "step": 1, "icon": "mdi:chart-bell-curve", "scale": 1, "unit": UnitOfTemperature.CELSIUS},
    {"name": "Curve: -15°C", "key": "heat_curve_m15", "address": 11400, "min": 0, "max": 90, "step": 1, "icon": "mdi:chart-bell-curve", "scale": 1, "unit": UnitOfTemperature.CELSIUS},
    {"name": "Curve: -5°C", "key": "heat_curve_m05", "address": 11401, "min": 0, "max": 90, "step": 1, "icon": "mdi:chart-bell-curve", "scale": 1, "unit": UnitOfTemperature.CELSIUS},
    {"name": "Curve: 0°C", "key": "heat_curve_00", "address": 11402, "min": 0, "max": 90, "step": 1, "icon": "mdi:chart-bell-curve", "scale": 1, "unit": UnitOfTemperature.CELSIUS},
    {"name": "Curve: +5°C", "key": "heat_curve_p05", "address": 11403, "min": 0, "max": 90, "step": 1, "icon": "mdi:chart-bell-curve", "scale": 1, "unit": UnitOfTemperature.CELSIUS},
    {"name": "Curve: +15°C", "key": "heat_curve_p15", "address": 11404, "min": 0, "max": 90, "step": 1, "icon": "mdi:chart-bell-curve", "scale": 1, "unit": UnitOfTemperature.CELSIUS},
]


# --- Polling interval controls --------------------------------------------------
# ``coordinator`` names the coordinator attribute on the runtime data.
# ``key`` is deliberately left at its original value, even though the naming is
# inconsistent: it is part of the entity's unique id, and changing it would
# orphan the interval entities of existing installs.
INTERVAL_ENTITIES: Final[list[dict[str, Any]]] = [
    {"key": "interval_fast", "name": "Interval: Status", "coordinator": "status", "default": DEFAULT_INTERVAL_STATUS, "icon": "mdi:timer-refresh", "category": EntityCategory.CONFIG, "min": 15, "max": 600, "step": 5},
    {"key": "interval_temp", "name": "Interval: Temperature", "coordinator": "temperature", "default": DEFAULT_INTERVAL_TEMPERATURE, "icon": "mdi:timer-refresh", "category": EntityCategory.CONFIG, "min": 15, "max": 600, "step": 5},
    # Settings change rarely, so the ceiling is an hour rather than 10 minutes.
    {"key": "interval_settings", "name": "Interval: Settings", "coordinator": "settings", "default": DEFAULT_INTERVAL_SETTINGS, "icon": "mdi:timer-refresh", "category": EntityCategory.CONFIG, "min": 60, "max": 3600, "step": 30},
]


#: Sensor groups paired with their coordinator and default interval.
SENSOR_GROUPS: Final[tuple[tuple[str, list[dict[str, Any]], int], ...]] = (
    ("status", SENSORS_STATUS, DEFAULT_INTERVAL_STATUS),
    ("temperature", SENSORS_TEMPERATURE, DEFAULT_INTERVAL_TEMPERATURE),
    ("settings", SENSORS_SETTINGS, DEFAULT_INTERVAL_SETTINGS),
)
