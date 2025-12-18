"""Sensor platform for ECL 310."""
from homeassistant.components.sensor import SensorEntity
from .entity import ECL310BaseEntity
from .const import REGISTER_MAP, Platform

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up sensor entities."""
    coordinator = entry.runtime_data
    async_add_entities([
        ECL310Sensor(coordinator, entry, reg) 
        for reg in REGISTER_MAP if reg["platform"] == Platform.SENSOR
    ])

class ECL310Sensor(ECL310BaseEntity, SensorEntity):
    """Representation of an ECL 310 temperature or mode sensor."""

    def __init__(self, coordinator, entry, description):
        """Initialize the sensor."""
        super().__init__(coordinator, entry, description)
        self._attr_native_unit_of_measurement = description.get("unit")
        self._attr_device_class = description.get("device_class")

    @property
    def native_value(self):
        """Return the value reported by the sensor."""
        val = self.coordinator.data.get(self.desc["address"])
        if val is None:
            return None
        return round(val * self.desc.get("scale", 1.0), 2)
