import logging
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Danfoss ECL from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    
    # Speichern der Konfigurationsdaten (IP, Port) im HA-Speicher
    hass.data[DOMAIN][entry.entry_id] = entry.data
    
    # Lade die Sensor-Plattform VORWÄRTS WEITERGELEITET
    # Korrigierte Methode: async_forward_entry_setup (Singular)
    await hass.async_forward_entry_setup(entry, "sensor")
    
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Entladen der Sensor-Plattform
    # Korrigierte Methode: async_forward_entry_setup (Singular)
    unload_ok = await hass.async_unload_entry_setup(entry, "sensor")
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
