"""Sensor platform for the Danfoss ECL 310."""

from __future__ import annotations

from typing import Any, Final

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import DanfossCoordinator, DanfossRuntimeData
from .const import GROUP_SENSORS, SENSOR_GROUPS, device_group_for_sensor

#: Valve travel is derived from the two per-valve status registers, so it is not
#: a register of its own.
MOVEMENT_SENSORS: Final[tuple[tuple[str, str, str], ...]] = (
    ("M1 Movement", "valve_m1_opening", "valve_m1_closing"),
    ("M2 Movement", "valve_m2_opening", "valve_m2_closing"),
    ("M3 Movement", "valve_m3_opening", "valve_m3_closing"),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the sensors for one config entry."""
    runtime: DanfossRuntimeData = entry.runtime_data

    entities = [
        DanfossSensor(
            runtime.coordinator(group),
            config,
            entry,
            device_group_for_sensor(config),
        )
        for group, configs, _ in SENSOR_GROUPS
        for config in configs
    ]
    entities.extend(
        DanfossMovementSensor(runtime.status, name, opening, closing, entry)
        for name, opening, closing in MOVEMENT_SENSORS
    )

    async_add_entities(entities)


class DanfossSensor(CoordinatorEntity[DanfossCoordinator], SensorEntity):
    """A register-backed sensor."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: DanfossCoordinator,
        config: dict[str, Any],
        entry: ConfigEntry,
        device_group: str,
    ) -> None:
        """Describe the sensor from its entry in ``const.py``."""
        super().__init__(coordinator)
        runtime: DanfossRuntimeData = entry.runtime_data

        self._config = config
        self._key = config["key"]
        self._scale = config.get("scale", 1)

        self._attr_name = config["name"]
        self._attr_unique_id = f"{entry.entry_id}_{self._key}"
        self._attr_device_info = runtime.device_info[device_group]
        self._attr_device_class = config.get("device_class")
        self._attr_native_unit_of_measurement = config.get("unit")
        self._attr_icon = config.get("icon")
        self._attr_translation_key = config.get("trans_key")
        self._attr_suggested_display_precision = config.get("precision")
        self._attr_entity_category = config.get("entity_category")
        self._attr_entity_registry_enabled_default = config.get(
            "enabled_default", True
        )

    @property
    def native_value(self) -> Any:
        """Return the register value, scaled and decoded."""
        raw = self.coordinator.data.get(self._key)
        if raw is None:
            return None

        if (value_fn := self._config.get("value_fn")) is not None:
            return value_fn(raw)

        value: int | float = raw * self._scale if self._scale != 1 else raw

        if self._attr_translation_key is not None:
            # The state translations are keyed by the plain status code
            # ("0", "1", ...), so an integral float must not become "0.0".
            if isinstance(value, float) and value.is_integer():
                value = int(value)
            return str(value)

        return value


class DanfossMovementSensor(CoordinatorEntity[DanfossCoordinator], SensorEntity):
    """Valve travel, derived from the opening and closing status registers."""

    _attr_has_entity_name = True
    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = ["opening", "closing", "stop"]
    _attr_translation_key = "movement_state"

    def __init__(
        self,
        coordinator: DanfossCoordinator,
        name: str,
        opening_key: str,
        closing_key: str,
        entry: ConfigEntry,
    ) -> None:
        """Set up the sensor from its two status registers."""
        super().__init__(coordinator)
        runtime: DanfossRuntimeData = entry.runtime_data

        self._opening_key = opening_key
        self._closing_key = closing_key

        self._attr_name = name
        self._attr_unique_id = f"{entry.entry_id}_move_{opening_key}"
        self._attr_device_info = runtime.device_info[GROUP_SENSORS]

    @property
    def native_value(self) -> str:
        """Return where the valve is currently travelling."""
        if self.coordinator.data.get(self._opening_key) == 1:
            return "opening"
        if self.coordinator.data.get(self._closing_key) == 1:
            return "closing"
        return "stop"