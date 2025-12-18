"""Binary sensor platform for ECL 310."""
from homeassistant.components.binary_sensor import BinarySensorEntity
from .entity import ECL310BaseEntity
from .const import REGISTER_MAP, Platform

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up binary sensor entities."""
    coordinator = entry.runtime_data
    async_add_entities([
        ECL310Binary(coordinator, entry, reg) 
        for reg in REGISTER_MAP if reg["platform"] == Platform.BINARY_SENSOR
    ])

class ECL310Binary(ECL310BaseEntity, BinarySensorEntity):
    """Representation of an ECL 310 binary state (e.g. Pump running)."""

    @property
    def is_on(self):
        """Return true if the binary sensor is on."""
        val = self.coordinator.data.get(self.desc["address"])
        return val > 0 if val is not None else None
