from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo
from .const import DOMAIN, SENSORS_60S, SENSORS_300S, SENSORS_600S

async def async_setup_entry(hass, entry, async_add_entities):
    """Sets up sensors for a specific Config Entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    
    entities = []

    # Create sensors from lists
    for conf in SENSORS_60S:
        entities.append(DanfossSensor(data["coord_60"], conf, entry))
    
    for conf in SENSORS_300S:
        entities.append(DanfossSensor(data["coord_300"], conf, entry))
        
    for conf in SENSORS_600S:
        entities.append(DanfossSensor(data["coord_600"], conf, entry))

    # The virtual movement sensors
    entities.append(DanfossMovementSensor(data["coord_60"], "M1 Movement", "m1_oeffnen", "m1_schliessen", entry))
    entities.append(DanfossMovementSensor(data["coord_60"], "M2 Movement", "m2_oeffnen", "m2_schliessen", entry))

    async_add_entities(entities)


class DanfossSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, config, entry):
        super().__init__(coordinator)
        self._config = config
        self._entry = entry
        
        self._key = config["key"]
        self._attr_name = config["name"]
        
        # Unique ID
        self._attr_unique_id = f"{entry.entry_id}_{self._key}"
        
        self._scale = config.get("scale", 1)
        
        # IMPORTANT: Initialize ALL _attr_ variables safely using .get()
        # If the key does not exist, None is set. This prevents AttributeError.
        self._attr_device_class = config.get("device_class")
        self._attr_native_unit_of_measurement = config.get("unit")
        self._attr_icon = config.get("icon")
        self._attr_translation_key = config.get("trans_key")
        self._attr_suggested_display_precision = config.get("precision")

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name=self._entry.title,
            manufacturer="Danfoss",
            model="ECL 310",
            configuration_url=f"http://{self._entry.data['host']}",
        )

    @property
    def native_value(self):
        val = self.coordinator.data.get(self._key)
        if val is None:
            return None
        
        # Apply scaling (e.g. divide temperature by 100)
        if self._scale != 1:
            return float(val) * self._scale
        
        # If a translation key exists, return the string (for modes 0, 1, 2...)
        if self._attr_translation_key:
            return str(val)
            
        return val


class DanfossMovementSensor(CoordinatorEntity, SensorEntity):
    """Special sensor for movement (combines two registers)."""
    def __init__(self, coordinator, name, open_key, close_key, entry):
        super().__init__(coordinator)
        self._open_key = open_key
        self._close_key = close_key
        self._entry = entry
        
        self._attr_name = name
        self._attr_unique_id = f"{entry.entry_id}_move_{open_key}"
        self._attr_translation_key = "movement_state"

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name=self._entry.title,
            manufacturer="Danfoss",
            model="ECL 310",
        )

    @property
    def native_value(self):
        is_opening = self.coordinator.data.get(self._open_key) == 1
        is_closing = self.coordinator.data.get(self._close_key) == 1
        
        if is_opening:
            return "opening"
        elif is_closing:
            return "closing"
        return "stop"
