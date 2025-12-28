from homeassistant.components.climate import ClimateEntity
from homeassistant.const import UnitOfTemperature, ATTR_TEMPERATURE
from homeassistant.components.climate.const import (
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN, CLIMATE_ENTITIES

async def async_setup_entry(hass, entry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coord_600"] 
    hub = data["hub"]
    
    entities = []
    for conf in CLIMATE_ENTITIES:
        entities.append(DanfossClimate(coordinator, hub, conf, entry))
    
    async_add_entities(entities)

class DanfossClimate(CoordinatorEntity, ClimateEntity):
    """Representation of a Danfoss Thermostat."""

    _attr_hvac_modes = [HVACMode.HEAT]
    _attr_hvac_mode = HVACMode.HEAT
    _attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE
    _attr_temperature_unit = UnitOfTemperature.CELSIUS

    def __init__(self, coordinator, hub, config, entry):
        super().__init__(coordinator)
        self._hub = hub
        self._entry = entry
        
        self._address = config["address"]
        self._slave = config["slave"]
        
        self._attr_name = config["name"]
        # Unique ID is important for multi-device support
        self._attr_unique_id = f"{entry.entry_id}_climate_{self._address}"
        
        self._attr_min_temp = config["min_temp"]
        self._attr_max_temp = config["max_temp"]
        self._target_temp_step = config["step"]
        
        self._data_key = f"climate_{self._address}"

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name=self._entry.title,
            manufacturer="Danfoss",
            model="ECL 310",
        )

    @property
    def target_temperature(self):
        val = self.coordinator.data.get(self._data_key)
        if val is None:
            return None
        return float(val) / 10.0

    @property
    def current_temperature(self):
        return self.target_temperature

    async def async_set_temperature(self, **kwargs):
        temp = kwargs.get(ATTR_TEMPERATURE)
        if temp is None:
            return

        val_to_write = int(temp * 10)
        
        success = await self._hub.write_register(
            self._address, 
            val_to_write, 
            slave_id=self._slave
        )

        if success:
            self.coordinator.data[self._data_key] = val_to_write
            self.async_write_ha_state()
            await self.coordinator.async_request_refresh()
