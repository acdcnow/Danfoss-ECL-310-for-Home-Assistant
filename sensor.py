import logging
from pymodbus.client import ModbusTcpClient
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateMethod
from homeassistant.const import CONF_HOST, CONF_PORT, TEMP_CELSIUS
from .const import DOMAIN, DEFAULT_SLAVE_ID
import datetime

_LOGGER = logging.getLogger(__name__)

# DEFINIEREN SIE HIER IHRE SPEZIFISCHEN REGISTER (PNUs)
# Beispiel PNU 10200 = S1 Temperatur
DANFOSS_REGISTERS = {
    "s1_temp": {"name": "S1 Temperatur", "address": 10200, "scale": 0.01, "unit": TEMP_CELSIUS}
}

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Danfoss ECL sensors."""
    host = config_entry.data[CONF_HOST]
    port = config_entry.data[CONF_PORT]

    # Koordinator für das Polling einrichten
    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="Danfoss ECL Poller",
        update_method=UpdateMethod.SINGLE, # Wir definieren unsere eigene Update Methode
        update_interval=datetime.timedelta(seconds=30),
    )
    
    # Define how to fetch the data
    async def _async_update_data():
        client = ModbusTcpClient(host, port)
        client.connect()
        data = {}
        for key, reg in DANFOSS_REGISTERS.items():
            try:
                # Synchronen Modbus-Aufruf in den Executor verlagern
                result = await hass.async_add_executor_job(
                    client.read_input_registers, reg["address"], 1, slave=DEFAULT_SLAVE_ID
                )
                if not result.isError():
                    data[key] = result.registers[0] * reg["scale"]
                else:
                    _LOGGER.warning(f"Error reading register {reg['address']}: {result}")
            except Exception as e:
                _LOGGER.error(f"Modbus communication error: {e}")
        client.close()
        return data
        
    coordinator.update_method = _async_update_data
    await coordinator.async_config_entry_first_refresh()

    # Sensoren hinzufügen
    entities = []
    for key, reg in DANFOSS_REGISTERS.items():
        entities.append(DanfossECLSensor(coordinator, key, reg))
    
    async_add_entities(entities)


class DanfossECLSensor(SensorEntity):
    """Representation of a Danfoss ECL Sensor."""
    
    def __init__(self, coordinator, key, reg_info):
        self.coordinator = coordinator
        self._key = key
        self._reg_info = reg_info
        self._attr_name = f"Danfoss ECL {reg_info['name']}"
        self._attr_unique_id = f"danfoss_ecl_{key}"
        self._attr_unit_of_measurement = reg_info['unit']

    @property
    def state(self):
        """Return the state of the sensor."""
        # Daten kommen vom Coordinator, nicht direkt von hier
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get(self._key)

    @property
    def should_poll(self):
        """No need to poll. Coordinator polls."""
        return False

    @property
    def available(self):
        """Return if entity is available."""
        return self.coordinator.last_update_success

    async def async_added_to_hass(self):
        """When entity is added to hass."""
        self.async_on_remove(self.coordinator.async_add_listener(self.async_write_ha_state))
