"""Select platform for the Danfoss ECL 310.

The operating mode of a circuit is a parameter in the PNU range 4201...4206
(Danfoss communication description, section 6.4): the register is the parameter
number minus one, so 4200 for circuit 1 and 4201 for circuit 2. The sensor
platform already reads it; this platform writes the holding register at the same
address, which is what the ``modbus.write_register`` automations did before.

Only the modes that act on a single circuit are offered. *Manual operation*
(code 0) is deliberately left out: the controller applies it to every circuit at
once, which is not what a per-circuit selector suggests.
"""

from __future__ import annotations

from typing import Any

from modbus_connection import ModbusError

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import DanfossCoordinator, DanfossRuntimeData
from .const import DOMAIN, GROUP_CONTROLS
from .device import DanfossEcl310


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the select entities for one config entry."""
    runtime: DanfossRuntimeData = entry.runtime_data

    async_add_entities(
        DanfossSelect(runtime.status, runtime.device, config, entry)
        for config in runtime.application.selects
    )


class DanfossSelect(CoordinatorEntity[DanfossCoordinator], SelectEntity):
    """A choice held in a holding register."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: DanfossCoordinator,
        device: DanfossEcl310,
        config: dict[str, Any],
        entry: ConfigEntry,
    ) -> None:
        """Describe the choice from its entry in the application profile."""
        super().__init__(coordinator)
        runtime: DanfossRuntimeData = entry.runtime_data

        self._device = device
        self._address = config["address"]
        # The value is polled with the status registers under the key of the
        # matching sensor, so no extra register is read for the selector.
        self._data_key = config["key"]
        #: Register value -> option key, and the way back.
        self._codes: dict[int, str] = config["options"]
        self._by_option = {option: code for code, option in self._codes.items()}

        self._attr_name = config["name"]
        self._attr_unique_id = f"{entry.entry_id}_select_{self._address}"
        self._attr_device_info = runtime.device_info[
            config.get("device_group", GROUP_CONTROLS)
        ]
        self._attr_translation_key = config["trans_key"]
        self._attr_options = list(self._codes.values())
        self._attr_icon = config.get("icon")

    @property
    def current_option(self) -> str | None:
        """Return the option the register holds.

        A code that is not offered (for instance manual operation, 0) has no
        option to show, so the entity reads as unknown instead of lying.
        """
        raw = self.coordinator.data.get(self._data_key)
        if raw is None:
            return None
        return self._codes.get(raw)

    async def async_select_option(self, option: str) -> None:
        """Write the chosen option to the controller."""
        code = self._by_option[option]

        try:
            await self._device.async_write_value(self._address, code)
        except ModbusError as err:
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key="write_failed",
                translation_placeholders={
                    "name": self._attr_name or self.entity_id or "mode"
                },
            ) from err

        # Show the new choice at once; the next poll confirms what the
        # controller actually took.
        data = dict(self.coordinator.data)
        data[self._data_key] = code
        self.coordinator.async_set_updated_data(data)
