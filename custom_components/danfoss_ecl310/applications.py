"""Application profiles for the Danfoss ECL 310.

The ECL 310 runs one *application key* at a time (A247.1, P330.7, ...). Every
application has its own circuits, sensors and parameters, so which registers
exist - and what they mean - depends on the key that is loaded. A profile bundles
the declarative entity descriptions for one application; the config flow stores
which profile an entry uses and the platforms read the entities from it.

Register addresses follow the rule documented in the README: a Danfoss
parameter ID *n* is served at the zero-based register *n - 1*.

Adding an application means adding a profile here and listing it in
:data:`APPLICATIONS`. The entity keys of the A247.1 profile must never change:
they are part of the unique ids of existing installs.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Final

from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import (
    EntityCategory,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfTemperature,
    UnitOfVolume,
    UnitOfVolumeFlowRate,
)

from .const import (
    APPLICATION_A247_1,
    APPLICATION_P330_7,
    DEFAULT_INTERVAL_SETTINGS,
    DEFAULT_INTERVAL_STATUS,
    DEFAULT_INTERVAL_TEMPERATURE,
    GROUP_CIRCUIT_1,
    GROUP_CIRCUIT_2,
    GROUP_MASTER,
    GROUP_METERS,
    GROUP_SENSORS,
    NUMBER_ENTITIES,
    SENSORS_SETTINGS,
    SENSORS_STATUS,
    SENSORS_TEMPERATURE,
)

#: Valve travel is derived from the two per-valve status registers, so it is not
#: a register of its own. Entries are ``(name, opening key, closing key,
#: device group)``.
MOVEMENT_SENSORS: Final[tuple[tuple[str, str, str, str], ...]] = (
    ("M1 Movement", "valve_m1_opening", "valve_m1_closing", GROUP_SENSORS),
    ("M2 Movement", "valve_m2_opening", "valve_m2_closing", GROUP_SENSORS),
    ("M3 Movement", "valve_m3_opening", "valve_m3_closing", GROUP_SENSORS),
)


@dataclass(frozen=True, slots=True)
class Application:
    """The entities one ECL application exposes."""

    key: str
    #: Name shown in the config flow.
    name: str
    sensors_status: list[dict[str, Any]]
    sensors_temperature: list[dict[str, Any]]
    sensors_settings: list[dict[str, Any]]
    numbers: list[dict[str, Any]]
    movement_sensors: tuple[tuple[str, str, str, str], ...] = MOVEMENT_SENSORS
    #: Value of register 2060 / 2061 the controller reports for this
    #: application. ``None`` means "do not check", which keeps the behaviour of
    #: the original A247.1 setup untouched.
    expected_app_key: int | None = None
    expected_subtype: int | None = None

    @property
    def sensor_groups(self) -> tuple[tuple[str, list[dict[str, Any]], int], ...]:
        """Sensor lists paired with their coordinator name and default interval."""
        return (
            ("status", self.sensors_status, DEFAULT_INTERVAL_STATUS),
            ("temperature", self.sensors_temperature, DEFAULT_INTERVAL_TEMPERATURE),
            ("settings", self.sensors_settings, DEFAULT_INTERVAL_SETTINGS),
        )


# --- A247.1 ---------------------------------------------------------------------
# The original register map, unchanged. It lives in ``const.py``.
APPLICATION_A247_1_PROFILE: Final = Application(
    key=APPLICATION_A247_1,
    name="A247.1",
    sensors_status=SENSORS_STATUS,
    sensors_temperature=SENSORS_TEMPERATURE,
    sensors_settings=SENSORS_SETTINGS,
    numbers=NUMBER_ENTITIES,
)


# --- P330.7 ---------------------------------------------------------------------
# One master circuit (pump P1, valve M1, sensors S3/S5) feeding two heating
# circuits as sub-circuits. There is no domestic hot water circuit.
#
# Parameter blocks, as listed for subtype 7 in the Danfoss P330 operating guide
# (section 7.8): 11xxx = heating circuit 1, 12xxx = heating circuit 2,
# 15xxx = master circuit. 13xxx and 14xxx do not apply to subtype 7.
#
# Everything below was read back from a P330.7 controller. Parameters answered
# with their documented factory defaults, which confirms the "ID - 1" rule.
# Scaling observed on the device:
#   * whole degrees: limits, summer cut-out, frost protection, pump temperatures
#   * tenths: room setpoints and the return-limit influence factors
#   * hundredths: sensor readings, which are signed

_CELSIUS = UnitOfTemperature.CELSIUS


def _temperature(
    key: str,
    name: str,
    addr: int,
    *,
    scale: float = 0.01,
    precision: int | None = 1,
    **extra: Any,
) -> dict[str, Any]:
    """Describe a signed temperature input register."""
    config: dict[str, Any] = {
        "key": key,
        "name": name,
        "addr": addr,
        "type": "input",
        "signed": True,
        "scale": scale,
        "unit": _CELSIUS,
        "device_class": SensorDeviceClass.TEMPERATURE,
    }
    if precision is not None:
        config["precision"] = precision
    config.update(extra)
    return config


def _diagnostic(
    key: str, name: str, addr: int, *, scale: float = 1, **extra: Any
) -> dict[str, Any]:
    """Describe a temperature setting that is only read back."""
    return _temperature(
        key,
        name,
        addr,
        scale=scale,
        precision=None if scale == 1 else 1,
        entity_category=EntityCategory.DIAGNOSTIC,
        **extra,
    )


def _heating_circuit_settings(
    prefix: str, group: str, base: int
) -> list[dict[str, Any]]:
    """Read-back settings of one heating circuit (``base`` is 11000 or 12000).

    The entities live on the circuit's own device, so their names carry no
    circuit number.
    """
    return [
        _diagnostic(f"{prefix}_flow_min", "Limit: Flow Min", base + 176, device_group=group),
        _diagnostic(f"{prefix}_flow_max", "Limit: Flow Max", base + 177, device_group=group),
        {
            # Whole degrees, 0 = OFF (the controller serves "OFF" as the value
            # below the minimum, as it does for every other OFF parameter).
            "key": f"{prefix}_summer_cutout",
            "name": "Limit: Summer Cutout",
            "addr": base + 178,
            "type": "input",
            "scale": 1,
            "unit": _CELSIUS,
            "device_class": SensorDeviceClass.TEMPERATURE,
            "icon": "mdi:weather-sunny-off",
            "entity_category": EntityCategory.DIAGNOSTIC,
            "device_group": group,
        },
        _diagnostic(f"{prefix}_frost", "Limit: Frost Protection", base + 92, device_group=group),
        # Influence of the room temperature on the flow temperature (parameters
        # x182 / x183, section "Raumtemp." in the controller's own interface).
        _diagnostic(
            f"{prefix}_room_influence_max",
            "Limit: Room Influence Max",
            base + 181,
            scale=0.1,
            device_group=group,
        ),
        _diagnostic(
            f"{prefix}_room_influence_min",
            "Limit: Room Influence Min",
            base + 182,
            scale=0.1,
            device_group=group,
        ),
        # Influence of the return temperature limit (parameters x035 / x036,
        # section "Rücklauftemp.").
        _diagnostic(
            f"{prefix}_return_influence_max",
            "Limit: Return Influence Max",
            base + 34,
            scale=0.1,
            device_group=group,
        ),
        _diagnostic(
            f"{prefix}_return_influence_min",
            "Limit: Return Influence Min",
            base + 35,
            scale=0.1,
            device_group=group,
        ),
        _diagnostic(
            f"{prefix}_target_comfort_status",
            "Set: Comfort (Read)",
            base + 179,
            scale=0.1,
            device_group=group,
        ),
        _diagnostic(
            f"{prefix}_target_setback_status",
            "Set: Setback (Read)",
            base + 180,
            scale=0.1,
            device_group=group,
        ),
        _diagnostic(
            f"{prefix}_pump_frost_status",
            "Set: Pump Frost Protection (Read)",
            base + 76,
            device_group=group,
        ),
        _diagnostic(
            f"{prefix}_pump_start_status",
            "Set: Pump Start Temperature (Read)",
            base + 77,
            device_group=group,
        ),
    ]


def _meter_sensors(number: int, base: int) -> list[dict[str, Any]]:
    """M-Bus energy meter ``number``; its registers start at ``base``.

    Meter 1 is configured at parameter 6000 and meter 2 at 6050, so meter *n*
    sits ``50 * (n - 1)`` registers further on. Flow, volume, energy and power
    are 32-bit values in tenths (high word first), the temperatures are signed
    hundredths. Checked on a P330.7 against the "Gerätezähler" page of the
    Leanheat Monitor: energy, power, supply and return temperature, volume and
    flow of both meters match, and the energy equals what an existing Modbus
    configuration reads.
    """
    group = {"device_group": GROUP_METERS, "type": "input"}
    return [
        {
            **group,
            "key": f"meter_{number}_energy",
            "name": f"Meter {number}: Energy",
            "addr": base + 13,
            "count": 2,
            "scale": 0.1,
            "unit": UnitOfEnergy.KILO_WATT_HOUR,
            "device_class": SensorDeviceClass.ENERGY,
            "state_class": SensorStateClass.TOTAL_INCREASING,
            "precision": 1,
        },
        {
            **group,
            "key": f"meter_{number}_power",
            "name": f"Meter {number}: Power",
            "addr": base + 9,
            "count": 2,
            "scale": 0.1,
            "unit": UnitOfPower.KILO_WATT,
            "device_class": SensorDeviceClass.POWER,
            "state_class": SensorStateClass.MEASUREMENT,
            "precision": 1,
        },
        {
            **group,
            "key": f"meter_{number}_flow",
            "name": f"Meter {number}: Flow",
            "addr": base + 7,
            "count": 2,
            "scale": 0.1,
            "unit": UnitOfVolumeFlowRate.LITERS_PER_HOUR,
            "device_class": SensorDeviceClass.VOLUME_FLOW_RATE,
            "state_class": SensorStateClass.MEASUREMENT,
            "precision": 1,
        },
        {
            **group,
            "key": f"meter_{number}_volume",
            "name": f"Meter {number}: Volume",
            "addr": base + 11,
            "count": 2,
            "scale": 0.1,
            "unit": UnitOfVolume.CUBIC_METERS,
            "device_class": SensorDeviceClass.VOLUME,
            "state_class": SensorStateClass.TOTAL_INCREASING,
            "precision": 1,
        },
        _temperature(
            f"meter_{number}_supply",
            f"Meter {number}: Supply Temperature",
            base + 5,
            device_group=GROUP_METERS,
        ),
        _temperature(
            f"meter_{number}_return",
            f"Meter {number}: Return Temperature",
            base + 6,
            device_group=GROUP_METERS,
        ),
    ]


#: A247.1 status entities that are not taken over: its two mode registers are
#: heating circuits (not heating and DHW), and the manual registers of valves
#: M2 and M3 are laid out differently (see below).
_P330_7_UNUSED_STATUS_KEYS: Final[frozenset[str]] = frozenset(
    {
        "mode_heating",
        "mode_dhw",
        "manual_valve_m2",
        "manual_valve_m3",
    }
)

_P330_7_STATUS_BASE: Final[list[dict[str, Any]]] = [
    {"key": "mode_circuit_1", "name": "Mode: Operating Mode", "addr": 4200, "type": "input", "trans_key": "operating_mode", "icon": "mdi:radiator", "device_group": GROUP_CIRCUIT_1},
    {"key": "mode_circuit_2", "name": "Mode: Operating Mode", "addr": 4201, "type": "input", "trans_key": "operating_mode", "icon": "mdi:radiator", "device_group": GROUP_CIRCUIT_2},
    # P330.7 has pumps P1 (master), P2 (circuit 1) and P3 (circuit 2) and three
    # valves: M1 in the master circuit, M2 in circuit 1 and M3 in circuit 2
    # (application diagram, page 20 of the P330 operating guide; the Leanheat
    # Monitor's own diagram leaves M2 out).
    #
    # The controller's interface lists the manual outputs as M1 4060, M2 4062,
    # M3 4064 and P1/P2/P3 4066/4067/4068, i.e. registers 4059, 4061, 4063 and
    # 4065-4067. The pumps and M1 therefore match A247.1, but M2 and M3 do not
    # (A247.1: 4060 and 4061).
    #
    # Status registers 3999-4004 keep the A247.1 layout (M1 3999/4000, M2
    # 4001/4002, M3 4003/4004). Read once a second while the valves moved: 3999
    # pulsed while M1 opened and 4000 while it closed, and 4001 and 4003 pulsed
    # too. The controller reports movement as pulses of about a second, so a
    # poll every 30 s mostly sees 0.
    {"key": "manual_valve_m2", "name": "Mode: Manual Valve M2", "addr": 4061, "type": "input", "trans_key": "valve_manual_mode", "icon": "mdi:cog"},
    {"key": "manual_valve_m3", "name": "Mode: Manual Valve M3", "addr": 4063, "type": "input", "trans_key": "valve_manual_mode", "icon": "mdi:cog"},
    *(
        config
        for config in SENSORS_STATUS
        if config["key"] not in _P330_7_UNUSED_STATUS_KEYS
    ),
]

#: Device of every pump and valve entity: P1 / M1 belong to the master circuit,
#: P2 / M2 to heating circuit 1 and P3 / M3 to heating circuit 2.
_P330_7_OUTPUT_GROUPS: Final[dict[str, str]] = {
    f"{kind}{number}{suffix}": group
    for number, group in ((1, GROUP_MASTER), (2, GROUP_CIRCUIT_1), (3, GROUP_CIRCUIT_2))
    for kind, suffix in (
        ("pump_", ""),
        ("manual_pump_", ""),
    )
} | {
    f"{kind}m{number}{suffix}": group
    for number, group in ((1, GROUP_MASTER), (2, GROUP_CIRCUIT_1), (3, GROUP_CIRCUIT_2))
    for kind, suffix in (
        ("valve_", "_opening"),
        ("valve_", "_closing"),
        ("manual_valve_", ""),
    )
}

_P330_7_STATUS: Final[list[dict[str, Any]]] = [
    {**config, "device_group": _P330_7_OUTPUT_GROUPS[config["key"]]}
    if config["key"] in _P330_7_OUTPUT_GROUPS
    else config
    for config in _P330_7_STATUS_BASE
]

_P330_7_TEMPERATURE: Final[list[dict[str, Any]]] = [
    _temperature("temp_s1_outdoor", "Temp: Outdoor (S1)", 10200),
    _temperature("temp_s3_flow", "Temp: Flow (S3)", 10202, device_group=GROUP_MASTER),
    _temperature("temp_s5", "Temp: Return (S5)", 10204, device_group=GROUP_MASTER),
    # S4/S6 belong to heating circuit 1 and S9/S7 to heating circuit 2. S4 and S9
    # follow the flow targets of circuits 1 and 2 (about 2 K below them), and the
    # operating guide pairs them the same way (P2/M2/S4/S6 and P3/M3/S9/S7).
    _temperature("temp_s4", "Temp: Flow (S4)", 10203, device_group=GROUP_CIRCUIT_1),
    _temperature("temp_s9", "Temp: Flow (S9)", 10208, device_group=GROUP_CIRCUIT_2),
    # The return sensors are optional. An unconnected input reads 192.00 °C, so
    # they are off by default.
    _temperature("temp_s6", "Temp: Return (S6)", 10205, enabled_default=False, device_group=GROUP_CIRCUIT_1),
    _temperature("temp_s7", "Temp: Return (S7)", 10206, enabled_default=False, device_group=GROUP_CIRCUIT_2),
    # Room temperature of an ECA30 room unit with address A: parameter 10213,
    # "ECA30 room A, Raw sensor 13", in Danfoss's communication description of
    # the ECL Comfort 210 / 296 / 310. The controller's interface shows it as
    # "ECA A Temperatur" (22.52 °C while the register read 22.40 °C a little
    # earlier). It reads 192.00 °C without an ECA, so it is off by default.
    _temperature("temp_eca_a", "Temp: Room (ECA A)", 10212, enabled_default=False, icon="mdi:home-thermometer"),
    # Sensors S13 and S14 of an ECA 32 module (parameters 10219 and 10220 in the
    # same document, registers 10218 and 10219). The sensor numbering "S(n) at
    # 10199 + n" holds up to S12 only. Not connected on the test controller:
    # both registers read 192.00 there, as the Monitor shows "--". Off by
    # default.
    _temperature("temp_s13_room", "Temp: Room (S13)", 10218, enabled_default=False, device_group=GROUP_CIRCUIT_1),
    _temperature("temp_s14_room", "Temp: Room (S14)", 10219, enabled_default=False, device_group=GROUP_CIRCUIT_2),
    _temperature("temp_outdoor_acc", "Temp: Outdoor (Acc.)", 11099, precision=2, icon="mdi:thermometer"),
    # M-Bus energy meters 1 and 2 (meters 3-5 are not configured).
    *_meter_sensors(1, 6000),
    *_meter_sensors(2, 6050),
    # Not documented by Danfoss. The values sit a few kelvin below the flow
    # sensors, which fits the calculated flow setpoint that the "Sende T-Soll"
    # parameter (IDs 11500 / 12500, registers 11499 / 12499) transmits.
    _temperature("flow_target_circuit_1", "Temp: Flow Target", 11500, precision=2, icon="mdi:thermostat-auto", device_group=GROUP_CIRCUIT_1),
    _temperature("flow_target_circuit_2", "Temp: Flow Target", 12500, precision=2, icon="mdi:thermostat-auto", device_group=GROUP_CIRCUIT_2),
]

_HEAT_CURVE_POINTS: Final[tuple[tuple[str, str, int], ...]] = (
    # Spelled out because Home Assistant drops the sign when it builds the
    # entity id: "-15°C" and "+15°C" would both become ``curve_15degc``.
    ("m30", "Minus 30°C", 11399),
    ("m15", "Minus 15°C", 11400),
    ("m05", "Minus 5°C", 11401),
    ("00", "0°C", 11402),
    ("p05", "Plus 5°C", 11403),
    ("p15", "Plus 15°C", 11404),
)

_P330_7_SETTINGS: Final[list[dict[str, Any]]] = [
    *_heating_circuit_settings("c1", GROUP_CIRCUIT_1, 11000),
    *_heating_circuit_settings("c2", GROUP_CIRCUIT_2, 12000),
    # The heat curve registers answer on P330.7 although Danfoss lists no
    # parameter IDs for them. Circuit 1 starts at register 11399, circuit 2 at
    # 12399; the controller's interface shows them as parameters 11400-11405 and
    # 12400-12405. Read-only until writing them has been verified.
    *(
        _diagnostic(f"heat_curve_c{circuit}_{point}", f"Curve: {label}", addr + offset, icon="mdi:chart-bell-curve", device_group=group)
        for circuit, offset, group in ((1, 0, GROUP_CIRCUIT_1), (2, 1000, GROUP_CIRCUIT_2))
        for point, label, addr in _HEAT_CURVE_POINTS
    ),
    # Heat curve slope in tenths. Register 11174 reads 11 and 12174 reads 12,
    # which the controller's interface shows as "Heizkurve 1,1" and "1,2".
    *(
        {
            "key": f"heat_curve_slope_c{circuit}",
            "name": "Curve: Slope",
            "addr": addr,
            "type": "input",
            "scale": 0.1,
            "precision": 1,
            "icon": "mdi:chart-line",
            "entity_category": EntityCategory.DIAGNOSTIC,
            "device_group": group,
        }
        for circuit, addr, group in ((1, 11174, GROUP_CIRCUIT_1), (2, 12174, GROUP_CIRCUIT_2))
    ),
    # Master circuit (15xxx).
    _diagnostic("master_flow_min", "Limit: Flow Min", 15176, device_group=GROUP_MASTER),
    _diagnostic("master_flow_max", "Limit: Flow Max", 15177, device_group=GROUP_MASTER),
    _diagnostic("master_pump_frost_status", "Set: Pump Frost Protection (Read)", 15076, device_group=GROUP_MASTER),
    _diagnostic("master_pump_start_status", "Set: Pump Start Temperature (Read)", 15077, device_group=GROUP_MASTER),
    *(
        config
        for config in SENSORS_SETTINGS
        if config["key"].startswith("system_") and config["key"] != "system_serial_number"
    ),
    # The serial number is a 32-bit value: "Serial high part" (parameter 36,
    # register 35) and "Serial low part" (parameter 37, register 36) in Danfoss's
    # communication description. A P330.7 reads 4 and 61646, which is 323790,
    # the number its interface shows.
    {"key": "system_serial_number", "name": "System: Serial Number", "addr": 35, "count": 2, "type": "holding", "icon": "mdi:barcode", "entity_category": EntityCategory.DIAGNOSTIC},
    {"key": "system_app_subtype", "name": "System: Application Subtype", "addr": 2061, "type": "holding", "icon": "mdi:key-variant", "entity_category": EntityCategory.DIAGNOSTIC},
    # Reads 768 (0x0300), which the controller's interface shows as application
    # version 3.
    {"key": "system_app_version", "name": "System: Application Version", "addr": 2062, "type": "holding", "icon": "mdi:tag", "entity_category": EntityCategory.DIAGNOSTIC, "value_fn": lambda raw: f"{raw >> 8}.{raw & 0xFF:02d}"},
]

#: Only the room setpoints are writable: they are the ones confirmed to accept
#: writes on a P330.7. The controller's own interface allows 5...40 °C for both
#: the comfort (parameters 11180 / 12180) and the setback setpoint (11181 /
#: 12181).
_P330_7_NUMBERS: Final[list[dict[str, Any]]] = [
    {"name": f"Set: {label}", "key": f"conf_c{circuit}_{kind}", "address": address, "min": 5, "max": 40, "step": 0.5, "icon": icon, "scale": 0.1, "unit": _CELSIUS, "device_group": group}
    for circuit, base, group in ((1, 11000, GROUP_CIRCUIT_1), (2, 12000, GROUP_CIRCUIT_2))
    for kind, label, offset, icon in (
        ("comfort", "Comfort", 179, "mdi:thermometer-check"),
        ("setback", "Setback", 180, "mdi:thermometer-low"),
    )
    for address in (base + offset,)
]

APPLICATION_P330_7_PROFILE: Final = Application(
    key=APPLICATION_P330_7,
    name="P330.7",
    sensors_status=_P330_7_STATUS,
    sensors_temperature=_P330_7_TEMPERATURE,
    sensors_settings=_P330_7_SETTINGS,
    numbers=_P330_7_NUMBERS,
    movement_sensors=(
        ("M1 Movement", "valve_m1_opening", "valve_m1_closing", GROUP_MASTER),
        ("M2 Movement", "valve_m2_opening", "valve_m2_closing", GROUP_CIRCUIT_1),
        ("M3 Movement", "valve_m3_opening", "valve_m3_closing", GROUP_CIRCUIT_2),
    ),
    expected_app_key=330,
    expected_subtype=7,
)


#: Every selectable application, keyed by the value stored in the config entry.
APPLICATIONS: Final[dict[str, Application]] = {
    profile.key: profile
    for profile in (APPLICATION_A247_1_PROFILE, APPLICATION_P330_7_PROFILE)
}
