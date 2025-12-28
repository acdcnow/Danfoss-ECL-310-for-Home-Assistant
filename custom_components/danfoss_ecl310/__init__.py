import asyncio
import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

# Import constants and lists from const.py
from .const import (
    DOMAIN,
    SENSORS_60S,
    SENSORS_300S,
    SENSORS_600S,
    CLIMATE_ENTITIES,
    DEFAULT_SLAVE,
)
from .modbus_client import DanfossModbusHub

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor", "climate"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Sets up the integration."""
    host = entry.data[CONF_HOST]
    port = entry.data[CONF_PORT]
    
    _LOGGER.debug(f"Setup Danfoss ECL310 integration for {host}:{port}")

    # Initialize and connect Hub
    hub = DanfossModbusHub(host, port)
    await hub.connect()

    # ------------------------------------------------------------------
    # Helper function for Coordinators
    # ------------------------------------------------------------------
    async def create_coordinator(interval, sensors, name_suffix):
        async def async_update_data():
            """Data fetch logic."""
            data = {}
            
            # 1. Read standard sensors
            for sens in sensors:
                val = await hub.read_register(
                    sens["addr"], 
                    DEFAULT_SLAVE, 
                    input_type=sens["type"]
                )
                data[sens["key"]] = val

            # 2. Read Climate (Thermostat) data
            # We read climate data with every 30-second cycle (interval 30),
            # so thermostats in HA are responsive.
            if interval == 30: 
                for clim in CLIMATE_ENTITIES:
                    # Climate usually uses Holding Registers for reading
                    val = await hub.read_register(
                        clim["address"], 
                        clim["slave"], 
                        input_type="holding"
                    )
                    data[f"climate_{clim['address']}"] = val

            return data

        # Create Coordinator
        coordinator = DataUpdateCoordinator(
            hass,
            _LOGGER,
            name=f"danfoss_ecl310_{name_suffix}",
            update_method=async_update_data,
            update_interval=timedelta(seconds=interval),
        )

        # First refresh immediately
        await coordinator.async_config_entry_first_refresh()
        return coordinator

    # ------------------------------------------------------------------
    # Create Coordinators (Intervals defined here)
    # ------------------------------------------------------------------
    
    # Group 1 (Status): 30 seconds
    _LOGGER.info("Creating coordinator for Status (30s)...")
    coord_60 = await create_coordinator(30, SENSORS_60S, "fast_30s")
    
    # Group 2 (Temperatures): 30 seconds
    _LOGGER.info("Creating coordinator for Temperatures (30s)...")
    coord_300 = await create_coordinator(30, SENSORS_300S, "temp_30s")
    
    # Group 3 (Settings/Limits): 600 seconds
    # These change rarely, so we reduce bus load here.
    _LOGGER.info("Creating coordinator for Settings (600s)...")
    coord_600 = await create_coordinator(600, SENSORS_600S, "settings_600s")

    # ------------------------------------------------------------------
    # Store in hass.data
    # ------------------------------------------------------------------
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "hub": hub,
        # Keep internal keys so sensor.py can find them
        "coord_60": coord_60,
        "coord_300": coord_300,
        "coord_600": coord_600
    }

    # Load platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Removes the integration (On Delete or Reload)."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        data = hass.data[DOMAIN].pop(entry.entry_id)
        
        # IMPORTANT: No 'await' here, as close() is now synchronous.
        data["hub"].close()
        
    return unload_ok
