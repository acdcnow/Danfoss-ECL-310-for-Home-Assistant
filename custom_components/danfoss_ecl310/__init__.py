"""The Danfoss ECL 310 integration.

Setting up an entry asks the ``modbus`` integration for a unit on the
controller's connection rather than opening a socket of our own. Two
integrations that ask for the same host and port share one connection, so their
requests serialize behind it instead of competing for the device, and Home
Assistant closes the link when the last holder unloads.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import timedelta
import logging
from typing import Final

from modbus_connection import ModbusError, ModbusTcpParams

from homeassistant.components.modbus import async_get_unit
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DEFAULT_UNIT_ID,
    DOMAIN,
    GROUP_NAMES,
    GROUPS,
    MANUFACTURER,
    MODEL,
    NUMBER_ENTITIES,
    SENSOR_GROUPS,
)
from .device import HOLDING, DanfossEcl310, RegisterRef, build_register_refs

_LOGGER = logging.getLogger(__name__)

PLATFORMS: Final[list[Platform]] = [Platform.NUMBER, Platform.SENSOR]

#: The writable setpoints are polled alongside the status registers so the
#: sliders follow the controller promptly.
NUMBER_REFS: Final[tuple[RegisterRef, ...]] = tuple(
    RegisterRef(key=config["key"], address=config["address"], space=HOLDING)
    for config in NUMBER_ENTITIES
)


class DanfossCoordinator(DataUpdateCoordinator[dict[str, int | None]]):
    """Poll one group of registers from the controller."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        device: DanfossEcl310,
        refs: list[RegisterRef],
        name: str,
        interval: int,
    ) -> None:
        """Set up the coordinator for a single register group."""
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=f"{entry.title} {name}",
            update_interval=timedelta(seconds=interval),
        )
        self.device = device
        self._refs = tuple(refs)

    async def _async_update_data(self) -> dict[str, int | None]:
        """Read every register in this group.

        A ``ModbusError`` here means the link is down or the controller did not
        answer at all; raising :class:`UpdateFailed` marks the entities
        unavailable until the next successful poll. Reconnecting is automatic,
        so the entry must not be reloaded.
        """
        try:
            return await self.device.async_read_group(self._refs)
        except ModbusError as err:
            raise UpdateFailed(
                translation_domain=DOMAIN,
                translation_key="modbus_error",
            ) from err


@dataclass
class DanfossRuntimeData:
    """Objects the entity platforms read from."""

    device: DanfossEcl310
    #: Device information per entity group. Every entry is a child device of the
    #: controller, which the entity platform creates on its own.
    device_info: Mapping[str, dr.ChildDeviceInfo]
    status: DanfossCoordinator
    temperature: DanfossCoordinator
    settings: DanfossCoordinator

    def coordinator(self, name: str) -> DanfossCoordinator:
        """Return a coordinator by the name used in ``INTERVAL_ENTITIES``."""
        return getattr(self, name)


#: This integration's config entry, carrying its runtime data.
DanfossConfigEntry = ConfigEntry[DanfossRuntimeData]


async def async_setup_entry(hass: HomeAssistant, entry: DanfossConfigEntry) -> bool:
    """Set up a Danfoss ECL 310 from a config entry."""
    unit = async_get_unit(
        hass,
        entry,
        ModbusTcpParams(host=entry.data[CONF_HOST], port=entry.data[CONF_PORT]),
        DEFAULT_UNIT_ID,
    )
    device = DanfossEcl310(unit)

    coordinators: dict[str, DanfossCoordinator] = {}
    for name, configs, interval in SENSOR_GROUPS:
        refs = build_register_refs(configs)
        if name == "status":
            refs.extend(NUMBER_REFS)
        coordinator = DanfossCoordinator(hass, entry, device, refs, name, interval)
        # Raises ConfigEntryNotReady if the controller cannot be reached, so
        # Home Assistant retries setup instead of creating dead entities.
        await coordinator.async_config_entry_first_refresh()
        coordinators[name] = coordinator

    settings = coordinators["settings"]

    # The controller itself carries the identity and nothing else; it is the
    # parent of the group devices, which hold all the entities.
    controller = dr.async_get(hass).async_get_or_create(
        config_entry_id=entry.entry_id,
        **_controller_device_info(entry, settings.data),
    )

    entry.runtime_data = DanfossRuntimeData(
        device=device,
        device_info=_group_device_info(entry, controller.id),
        status=coordinators["status"],
        temperature=coordinators["temperature"],
        settings=settings,
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: DanfossConfigEntry) -> bool:
    """Unload a config entry.

    There is nothing to tear down here: the connection belongs to the ``modbus``
    integration, which closes it once the last entry holding a unit on it
    unloads.
    """
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


def _controller_device_info(
    entry: ConfigEntry, data: Mapping[str, int | None]
) -> dr.DeviceInfo:
    """Describe the controller to the device registry.

    The identity registers are taken from the settings coordinator, which has
    already read them, rather than from a sensor entity. Reading them from
    sensors that were disabled by default is why they never reached the registry
    before.
    """
    serial_number = data.get("system_serial_number")
    firmware = data.get("system_firmware")
    hardware = data.get("system_hardware")

    return dr.DeviceInfo(
        identifiers={(DOMAIN, entry.entry_id)},
        name=entry.title,
        manufacturer=MANUFACTURER,
        model=MODEL,
        serial_number=None if serial_number is None else str(serial_number),
        sw_version=None if firmware is None else f"{firmware >> 8}.{firmware & 0xFF:02d}",
        hw_version=None if hardware is None else f"Rev {hardware}",
        configuration_url=f"http://{entry.data[CONF_HOST]}",
    )


def _group_device_info(
    entry: ConfigEntry, controller_device_id: str
) -> dict[str, dr.ChildDeviceInfo]:
    """Build one child device per entity group.

    A child device carries no identity of its own - no manufacturer, model,
    serial number or configuration URL, only a name and a link to its parent -
    which is exactly what the device registry expects of one. The entities
    reference these through ``_attr_device_info`` and the entity platform creates
    the devices from them.
    """
    return {
        group: dr.ChildDeviceInfo(
            identifiers={(DOMAIN, f"{entry.entry_id}_{group}")},
            parent_device_id=controller_device_id,
            name=GROUP_NAMES[group],
        )
        for group in GROUPS
    }