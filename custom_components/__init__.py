"""Setup integration."""
from homeassistant.const import Platform
from .const import DOMAIN

PLATFORMS = [Platform.SENSOR, Platform.BINARY_SENSOR, Platform.CLIMATE]

async def async_setup_entry(hass, entry):
    """Set up entry."""
    from .coordinator import ECL310Coordinator
    coordinator = ECL310Coordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass, entry):
    """Unload entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        if hasattr(entry, "runtime_data"):
            entry.runtime_data.client.close()
    return unload_ok
