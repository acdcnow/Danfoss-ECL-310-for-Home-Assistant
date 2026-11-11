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

from .const import (
    APPLICATION_A247_1,
    DEFAULT_INTERVAL_SETTINGS,
    DEFAULT_INTERVAL_STATUS,
    DEFAULT_INTERVAL_TEMPERATURE,
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


#: Every selectable application, keyed by the value stored in the config entry.
APPLICATIONS: Final[dict[str, Application]] = {
    profile.key: profile for profile in (APPLICATION_A247_1_PROFILE,)
}
