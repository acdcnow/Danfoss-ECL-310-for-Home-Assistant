import asyncio
import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    DOMAIN,
    SENSORS_60S,
    SENSORS_300S,
    SENSORS_600S,
    CLIMATE_ENTITIES,
    DEFAULT_SLAVE,
    # New Constants
    DEFAULT_INTERVAL_FAST,
    DEFAULT_INTERVAL_TEMP,
    DEFAULT_INTERVAL_SLOW,
)
from .modbus_client import DanfossModbusHub

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor", "number"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Sets up the integration."""
    host = entry.data[CONF_HOST]
    port = entry.data[CONF_PORT]
    
    _LOGGER.debug(f"Setup Danfoss ECL310 integration for {host}:{port}")

    hub = DanfossModbusHub(host, port)
    await hub.connect()

    async def create_coordinator(interval, sensors, name_suffix):
        async def async_update_data():
            data = {}
            
            # 1. Read standard sensors
            for sens in sensors:
                val = await hub.read_register(
                    sens["addr"], 
                    DEFAULT_SLAVE, 
                    input_type=sens["type"]
                )
                data[sens["key"]] = val

            # 2. Read Number Entities (Target Temps) only on fast loop
            # We assume the fast loop (default 30s) handles responsiveness
            if interval == DEFAULT_INTERVAL_FAST: 
                # Import NUMBER_ENTITIES locally to avoid circular imports if any
                from .const import NUMBER_ENTITIES
                for num in NUMBER_ENTITIES:
                    val = await hub.read_register(
                        num["address"], 
                        num["slave"], 
                        input_type="holding"
                    )
                    data[num["key"]] = val

            return data

        coordinator = DataUpdateCoordinator(
            hass,
            _LOGGER,
            name=f"danfoss_ecl310_{name_suffix}",
            update_method=async_update_data,
            # Start with default interval
            update_interval=timedelta(seconds=interval),
        )

        await coordinator.async_config_entry_first_refresh()
        return coordinator

    # Create Coordinators using the constants
    
    # Group 1 (Status): Default 30s
    _LOGGER.info(f"Creating coordinator for Status ({DEFAULT_INTERVAL_FAST}s default)...")
    coord_60 = await create_coordinator(DEFAULT_INTERVAL_FAST, SENSORS_60S, "fast_30s")
    
    # Group 2 (Temperatures): Default 30s
    _LOGGER.info(f"Creating coordinator for Temperatures ({DEFAULT_INTERVAL_TEMP}s default)...")
    coord_300 = await create_coordinator(DEFAULT_INTERVAL_TEMP, SENSORS_300S, "temp_30s")
    
    # Group 3 (Settings/Limits): Default 600s
    _LOGGER.info(f"Creating coordinator for Settings ({DEFAULT_INTERVAL_SLOW}s default)...")
    coord_600 = await create_coordinator(DEFAULT_INTERVAL_SLOW, SENSORS_600S, "settings_600s")

    hass.data.setdefault(DOMAIN, {})
    # Store keys exactly as expected by number.py
    hass.data[DOMAIN][entry.entry_id] = {
        "hub": hub,
        "coord_60": coord_60,
        "coord_300": coord_300,
        "coord_600": coord_600
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        data = hass.data[DOMAIN].pop(entry.entry_id)
        data["hub"].close()
        
    return unload_ok