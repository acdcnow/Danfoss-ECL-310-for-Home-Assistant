from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo
from .const import DOMAIN

# Example: If you define a BINARY_SENSORS list in const.py later
# from .const import BINARY_SENSORS 

async def async_setup_entry(hass, entry, async_add_entities):
    """Setup binary sensors."""
    data = hass.data[DOMAIN][entry.entry_id]
    
    entities = []
    
    # Example logic, if you define binary sensors in const.py later:
    # for conf in BINARY_SENSORS:
    #     entities.append(DanfossBinarySensor(data["coord_60"], conf, entry))
    
    async_add_entities(entities)

class DanfossBinarySensor(CoordinatorEntity, BinarySensorEntity):
    def __init__(self, coordinator, config, entry):
        super().__init__(coordinator)
        self._config = config
        self._entry = entry
        
        self._key = config["key"]
        self._attr_name = config["name"]
        self._attr_unique_id = f"{entry.entry_id}_{self._key}"
        
        # Safely get optional attributes
        self._attr_device_class = config.get("device_class")
        self._attr_icon = config.get("icon")

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name=self._entry.title,
            manufacturer="Danfoss",
            model="ECL 310",
        )

    @property
    def is_on(self):
        val = self.coordinator.data.get(self._key)
        # If value is 1 -> On, otherwise Off
        return val == 1
