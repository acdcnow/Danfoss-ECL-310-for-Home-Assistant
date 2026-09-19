"""Number platform for the Danfoss ECL 310.

Two kinds of number entity live here: the writable setpoints that map onto a
holding register, and the virtual sliders that tune each coordinator's polling
interval without writing anything to the controller.
"""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from modbus_connection import ModbusError

from homeassistant.components.number import NumberEntity, RestoreNumber
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import DanfossCoordinator, DanfossRuntimeData
from .const import DOMAIN, INTERVAL_ENTITIES, NUMBER_ENTITIES
from .device import DanfossEcl310


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the number entities for one config entry."""
    runtime: DanfossRuntimeData = entry.runtime_data

    entities: list[NumberEntity] = [
        DanfossNumber(runtime.status, runtime.device, config, entry)
        for config in NUMBER_ENTITIES
    ]
    entities.extend(
        DanfossIntervalNumber(runtime.coordinator(config["coordinator"]), config, entry)
        for config in INTERVAL_ENTITIES
    )

    async_add_entities(entities)


class DanfossNumber(CoordinatorEntity[DanfossCoordinator], NumberEntity):
    """A setpoint held in a holding register."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: DanfossCoordinator,
        device: DanfossEcl310,
        config: dict[str, Any],
        entry: ConfigEntry,
    ) -> None:
        """Describe the setpoint from its entry in ``const.py``."""
        super().__init__(coordinator)
        runtime: DanfossRuntimeData = entry.runtime_data

        self._device = device
        self._config = config
        self._address = config["address"]
        self._data_key = config["key"]
        self._scale = config.get("scale", 1)

        self._attr_name = config["name"]
        self._attr_unique_id = f"{entry.entry_id}_number_{self._address}"
        self._attr_device_info = runtime.device_info
        self._attr_native_min_value = config["min"]
        self._attr_native_max_value = config["max"]
        self._attr_native_step = config["step"]
        self._attr_icon = config.get("icon")
        # Not every setpoint has a unit: the heat curve slope is dimensionless
        # and must not be labelled with degrees.
        self._attr_native_unit_of_measurement = config.get("unit")

    @property
    def native_value(self) -> float | None:
        """Return the current value of the register."""
        raw = self.coordinator.data.get(self._data_key)
        if raw is None:
            return None
        return float(raw) * self._scale

    async def async_set_native_value(self, value: float) -> None:
        """Write the value to the controller."""
        raw = int(round(value / self._scale))

        try:
            await self._device.async_write_value(self._address, raw)
        except ModbusError as err:
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key="write_failed",
                translation_placeholders={
                    "name": self._attr_name or self.entity_id or "setpoint"
                },
            ) from err

        # Show the new value immediately; the next poll confirms what the
        # controller actually accepted.
        data = dict(self.coordinator.data)
        data[self._data_key] = raw
        self.coordinator.async_set_updated_data(data)


class DanfossIntervalNumber(RestoreNumber):
    """A virtual slider that tunes one coordinator's polling interval."""

    _attr_has_entity_name = True
    _attr_native_unit_of_measurement = UnitOfTime.SECONDS

    def __init__(
        self,
        coordinator: DanfossCoordinator,
        config: dict[str, Any],
        entry: ConfigEntry,
    ) -> None:
        """Describe the slider from its entry in ``const.py``."""
        runtime: DanfossRuntimeData = entry.runtime_data

        self._coordinator = coordinator
        self._default_val = config["default"]

        self._attr_name = config["name"]
        self._attr_unique_id = f"{entry.entry_id}_interval_{config['key']}"
        self._attr_device_info = runtime.device_info
        self._attr_native_min_value = config["min"]
        self._attr_native_max_value = config["max"]
        self._attr_native_step = config["step"]
        self._attr_icon = config["icon"]
        self._attr_entity_category = config.get("category", EntityCategory.CONFIG)

    @property
    def native_value(self) -> float:
        """Return the interval the coordinator is currently polling at."""
        if self._coordinator.update_interval is not None:
            return self._coordinator.update_interval.total_seconds()
        return self._default_val

    async def async_set_native_value(self, value: float) -> None:
        """Apply the interval to the coordinator straight away."""
        self._coordinator.update_interval = timedelta(seconds=value)
        self.async_write_ha_state()

    async def async_added_to_hass(self) -> None:
        """Restore the interval chosen before the last restart."""
        await super().async_added_to_hass()
        if (last_data := await self.async_get_last_number_data()) is not None:
            if last_data.native_value is not None:
                self._coordinator.update_interval = timedelta(
                    seconds=last_data.native_value
                )
