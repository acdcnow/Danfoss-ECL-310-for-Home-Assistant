from datetime import timedelta
from homeassistant.components.number import NumberEntity, RestoreNumber
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.const import UnitOfTemperature, EntityCategory

from .const import DOMAIN, NUMBER_ENTITIES, INTERVAL_ENTITIES

async def async_setup_entry(hass, entry, async_add_entities):
    """Setup number platform."""
    data = hass.data[DOMAIN][entry.entry_id]
    hub = data["hub"]
    
    entities = []
    
    # 1. Modbus Control Numbers (Target Temps)
    # Use fast coordinator for UI responsiveness
    coord_modbus = data["coord_60"] 
    for conf in NUMBER_ENTITIES:
        entities.append(DanfossNumber(coord_modbus, hub, conf, entry))
        
    # 2. Virtual Interval Config Numbers
    # These control the coordinators themselves
    for conf in INTERVAL_ENTITIES:
        # We need to find the specific coordinator this slider controls
        target_coordinator = data[conf["coordinator"]]
        entities.append(DanfossIntervalNumber(target_coordinator, conf, entry))
    
    async_add_entities(entities)

class DanfossNumber(CoordinatorEntity, NumberEntity):
    """Representation of a Danfoss Setpoint Slider (Modbus)."""

    _attr_has_entity_name = True

    def __init__(self, coordinator, hub, config, entry):
        super().__init__(coordinator)
        self._hub = hub
        self._entry = entry
        self._config = config
        
        self._address = config["address"]
        self._slave = config["slave"]
        
        self._attr_name = config["name"]
        self._attr_unique_id = f"{entry.entry_id}_number_{self._address}"
        
        self._attr_native_min_value = config["min"]
        self._attr_native_max_value = config["max"]
        self._attr_native_step = config["step"]
        
        self._attr_icon = config.get("icon", "mdi:thermostat")
        self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
        
        self._data_key = config["key"]
        
        # FIX: Load scale from config, default to 0.1 (old behavior for temp targets)
        self._scale = config.get("scale", 0.1)

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
        val = self.coordinator.data.get(self._data_key)
        if val is None:
            return None
        # FIX: Use dynamic scaling instead of hardcoded / 10.0
        return float(val) * self._scale

    async def async_set_native_value(self, value: float) -> None:
        # FIX: Inverse scaling for writing
        val_to_write = int(value / self._scale)
        
        success = await self._hub.write_register(
            self._address, 
            val_to_write, 
            slave_id=self._slave
        )

        if success:
            self.coordinator.data[self._data_key] = val_to_write
            self.async_write_ha_state()
            await self.coordinator.async_request_refresh()


class DanfossIntervalNumber(RestoreNumber):
    """Virtual Slider to configure Polling Interval."""
    
    _attr_has_entity_name = True
    _attr_native_unit_of_measurement = "s"

    def __init__(self, coordinator, config, entry):
        # RestoreNumber does NOT inherit from CoordinatorEntity directly in this specific way usually,
        # but here we just need access to the coordinator object to modify it.
        self._coordinator = coordinator
        self._entry = entry
        
        self._attr_name = config["name"]
        self._attr_unique_id = f"{entry.entry_id}_interval_{config['key']}"
        self._attr_native_min_value = config["min"]
        self._attr_native_max_value = config["max"]
        self._attr_native_step = config["step"]
        self._attr_icon = config["icon"]
        self._attr_entity_category = config.get("category", EntityCategory.CONFIG)
        
        self._default_val = config["default"]

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
        """Return the current interval from the coordinator."""
        if self._coordinator.update_interval:
            return self._coordinator.update_interval.total_seconds()
        return self._default_val

    async def async_set_native_value(self, value: float) -> None:
        """Update the coordinator interval immediately."""
        self._coordinator.update_interval = timedelta(seconds=value)
        self.async_write_ha_state()

    async def async_added_to_hass(self):
        """Restore last state."""
        await super().async_added_to_hass()
        last_data = await self.async_get_last_number_data()
        if last_data and last_data.native_value:
            # Apply restored value to coordinator
            self._coordinator.update_interval = timedelta(seconds=last_data.native_value)
