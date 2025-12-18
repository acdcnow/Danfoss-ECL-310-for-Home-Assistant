"""Sensor platform with native state mapping."""
from homeassistant.components.sensor import SensorEntity
from .entity import ECL310BaseEntity
from .const import REGISTER_MAP, Platform

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = entry.runtime_data
    async_add_entities([
        ECL310Sensor(coordinator, entry, reg) 
        for reg in REGISTER_MAP if reg["platform"] == Platform.SENSOR
    ])

class ECL310Sensor(ECL310BaseEntity, SensorEntity):
    def __init__(self, coordinator, entry, description):
        super().__init__(coordinator, entry, description)
        self._attr_native_unit_of_measurement = description.get("unit")
        self._attr_device_class = description.get("device_class")

    @property
    def native_value(self):
        raw_val = self.coordinator.data.get(self.desc["address"])
        if raw_val is None:
            return None
        
        # If a map exists, return the mapped string value
        if "map" in self.desc:
            return self.desc["map"].get(raw_val, f"Unknown ({raw_val})")
        
        # Otherwise return the scaled numeric value
        return round(raw_val * self.desc.get("scale", 1.0), 2)
