"""Climate platform for ECL 310."""
from homeassistant.components.climate import ClimateEntity, ClimateEntityFeature, HVACMode
from homeassistant.const import UnitOfTemperature
from .entity import ECL310BaseEntity
from .const import REGISTER_MAP, Platform

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up climate entities."""
    coordinator = entry.runtime_data
    async_add_entities([
        ECL310Climate(coordinator, entry, reg) 
        for reg in REGISTER_MAP if reg["platform"] == Platform.CLIMATE
    ])

class ECL310Climate(ECL310BaseEntity, ClimateEntity):
    """Control the setpoint of the ECL 310."""

    _attr_hvac_modes = [HVACMode.HEAT]
    _attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE
    _attr_temperature_unit = UnitOfTemperature.CELSIUS

    @property
    def target_temperature(self):
        """Return the current target temperature."""
        val = self.coordinator.data.get(self.desc["address"])
        return val * 0.1 if val is not None else None

    @property
    def current_temperature(self):
        """Use S3 flow temperature as feedback for current temperature."""
        val = self.coordinator.data.get(10202)
        return val * 0.01 if val is not None else None

    @property
    def hvac_mode(self):
        """Always return heating mode."""
        return HVACMode.HEAT

    async def async_set_temperature(self, **kwargs):
        """Set a new target temperature."""
        temp = kwargs.get("temperature")
        if temp:
            # Scale up for Modbus (0.1 scale means multiply by 10)
            await self.coordinator.write_register(self.desc["address"], temp * 10)
