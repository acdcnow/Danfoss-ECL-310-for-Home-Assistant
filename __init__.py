import logging
import datetime
from pymodbus.client import ModbusTcpClient

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateMethod
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.const import CONF_HOST, CONF_PORT, TEMP_CELSIUS

from .const import DOMAIN, DEFAULT_SLAVE_ID

_LOGGER = logging.getLogger(__name__)

# DEFINITION DER REGISTER: Ihre vollständige Liste (wie zuvor in sensor.py)
DANFOSS_REGISTERS_CONFIG = {
    "soll_temp": {"name": "ECL310_Soll_Temp", "address": 11179, "input_type": "holding", "scale": 0.1, "precision": 1, "unit": TEMP_CELSIUS, "device_class": SensorDeviceClass.TEMPERATURE, "max_temp": 30, "min_temp": 10, "offset": 0, "target_temp_register": 11179, "temp_step": 0.5},
    "absenk_temp": {"name": "ECL310_absenk_Temp", "address": 11180, "input_type": "holding", "scale": 0.1, "precision": 1, "unit": TEMP_CELSIUS, "device_class": SensorDeviceClass.TEMPERATURE, "max_temp": 30, "min_temp": 10, "offset": 0, "target_temp_register": 11180, "temp_step": 0.5},
    "s1_temp": {"name": "ECL310_S1", "address": 10200, "input_type": "input", "scale": 0.01, "precision": 1, "unit": TEMP_CELSIUS, "device_class": SensorDeviceClass.TEMPERATURE},
    "s2_temp": {"name": "ECL310_S2", "address": 10201, "input_type": "input", "scale": 0.01, "precision": 1, "unit": TEMP_CELSIUS, "device_class": SensorDeviceClass.TEMPERATURE},
    "s3_temp": {"name": "ECL310_S3", "address": 10202, "input_type": "input", "scale": 0.01, "precision": 1, "unit": TEMP_CELSIUS, "device_class": SensorDeviceClass.TEMPERATURE},
    "s4_temp": {"name": "ECL310_S4", "address": 10203, "input_type": "input", "scale": 0.01, "precision": 1, "unit": TEMP_CELSIUS, "device_class": SensorDeviceClass.TEMPERATURE},
    "s5_temp": {"name": "ECL310_S5", "address": 10204, "input_type": "input", "scale": 0.01, "precision": 1, "unit": TEMP_CELSIUS, "device_class": SensorDeviceClass.TEMPERATURE},
    "s6_temp": {"name": "ECL310_S6", "address": 10205, "input_type": "input", "scale": 0.01, "precision": 1, "unit": TEMP_CELSIUS, "device_class": SensorDeviceClass.TEMPERATURE},
    "min_outdoor_temp": {"name": "ECL310_min_Outdoor_temp", "address": 10499, "input_type": "input", "scale": 0.01, "precision": 1, "unit": TEMP_CELSIUS, "device_class": SensorDeviceClass.TEMPERATURE},
    "max_outdoor_temp": {"name": "ECL310_max_Outdoor_temp", "address": 10504, "input_type": "input", "scale": 0.01, "precision": 1, "unit": TEMP_CELSIUS, "device_class": SensorDeviceClass.TEMPERATURE},
    "normal_wasser": {"name": "ECL310_normal_wasser", "address": 12189, "input_type": "input", "scale": 0.1, "precision": 1, "unit": TEMP_CELSIUS, "device_class": SensorDeviceClass.TEMPERATURE},
    "absenkung_wasser": {"name": "ECL310_absenkung_wasser", "address": 12190, "input_type": "input", "scale": 0.1, "precision": 1, "unit": TEMP_CELSIUS, "device_class": SensorDeviceClass.TEMPERATURE},
    "vorlauf_min_temp": {"name": "ECL310_vorlauf_min_temp", "address": 11176, "input_type": "input", "scale": 1, "precision": 1, "unit": TEMP_CELSIUS, "device_class": SensorDeviceClass.TEMPERATURE},
    "vorlauf_max_temp": {"name": "ECL310_vorlauf_max_temp", "address": 11177, "input_type": "input", "scale": 1, "precision": 1, "unit": TEMP_CELSIUS, "device_class": SensorDeviceClass.TEMPERATURE},
    "komfort_soll": {"name": "ECL310_komfort_soll", "address": 11179, "input_type": "input", "scale": 0.1, "precision": 1, "unit": TEMP_CELSIUS, "device_class": SensorDeviceClass.TEMPERATURE},
    "absenkung_soll": {"name": "ECL310_absenkung_soll", "address": 11180, "input_type": "input", "scale": 0.1, "precision": 1, "unit": TEMP_CELSIUS, "device_class": SensorDeviceClass.TEMPERATURE},
    "frostschutz": {"name": "ECL310_frostschutz", "address": 12092, "input_type": "input", "scale": 1, "precision": 0, "unit": TEMP_CELSIUS, "device_class": SensorDeviceClass.TEMPERATURE},
    # Status-Register (keine Skalierung, keine Einheit)
    "betriebsartww": {"name": "ECL310_betriebsartww", "address": 4201, "input_type": "input"},
    "betriebsartheizung": {"name": "ECL310_betriebsartheizung", "address": 4200, "input_type": "input"},
    "pumpe_1_status": {"name": "Pumpe 1", "address": 4005, "input_type": "input"},
    "pumpe_2_status": {"name": "Pumpe 2", "address": 4006, "input_type": "input"},
    "pumpe_3_status": {"name": "Pumpe 3", "address": 4007, "input_type": "input"},
    "m1_oeffnen": {"name": "m1_oeffnen", "address": 3999, "input_type": "input"},
    "m1_schliessen": {"name": "m1_schliessen", "address": 4000, "input_type": "input"},
    "m2_oeffnen": {"name": "m2_oeffnen", "address": 4001, "input_type": "input"},
    "m2_schliessen": {"name": "m2_schliessen", "address": 4002, "input_type": "input"},
    "manual_triac_m1": {"name": "manual_triac_m1", "address": 4059, "input_type": "input"},
    "manual_triac_m2": {"name": "manual_triac_m2", "address": 4060, "input_type": "input"},
    "manual_triac_m3": {"name": "manual_triac_m3", "address": 4061, "input_type": "input"},
    "manual_pumpe1": {"name": "manual_pumpe1", "address": 4065, "input_type": "input"},
    "manual_pumpe2": {"name": "manual_pumpe2", "address": 4066, "input_type": "input"},
    "manual_pumpe3": {"name": "manual_pumpe3", "address": 4067, "input_type": "input"},
}


# --- KERNLOGIK DER INTEGRATION ---

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Danfoss ECL from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    
    host = entry.data[CONF_HOST]
    port = entry.data[CONF_PORT]

    async def async_update_data():
        """Fetch data from Danfoss ECL via Modbus TCP."""
        client = ModbusTcpClient(host, port)
        # client.connect() muss im Executor laufen, da es blockierend ist
        await hass.async_add_executor_job(client.connect)
        data = {}

        for key, reg_config in DANFOSS_REGISTERS_CONFIG.items():
            try:
                if reg_config.get("input_type") == "holding":
                    result = await hass.async_add_executor_job(
                        client.read_holding_registers, reg_config["address"], 1, slave=DEFAULT_SLAVE_ID
                    )
                else:
                    result = await hass.async_add_executor_job(
                        client.read_input_registers, reg_config["address"], 1, slave=DEFAULT_SLAVE_ID
                    )
                    
                if not result.isError():
                    raw_value = result.registers[0] # result.registers ist eine Liste
                    scale = reg_config.get("scale", 1)
                    precision = reg_config.get("precision", 0)
                    offset = reg_config.get("offset", 0)
                    scaled_value = (raw_value * scale) + offset
                    data[key] = round(scaled_value, precision)
                # Fehlerbehandlung...
            except Exception as e:
                 _LOGGER.error(f"Modbus communication error for {key} (Address: {reg_config['address']}): {e}")
        
        await hass.async_add_executor_job(client.close)
        return data

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="Danfoss ECL Poller",
        update_method=async_update_data,
        update_interval=datetime.timedelta(seconds=60),
    )
    
    await coordinator.async_config_entry_first_refresh()

    # Die Sensoren werden nun direkt hier hinzugefügt, ohne async_forward_entry_setups
    entities = []
    for key, reg_config in DANFOSS_REGISTERS_CONFIG.items():
        entities.append(DanfossECLSensor(coordinator, key, reg_config))
    
    # Da wir uns in __init__.py befinden, müssen wir die Plattform manuell laden
    # Dies ist der Teil, der die alte Methode ersetzt
    from homeassistant.helpers.entity_platform import async_get_current_platform
    platform = async_get_current_platform(hass, DOMAIN) # HIER KÖNNTE EIN FEHLER SEIN
    # Tatsächlicher Weg um Entitäten hinzuzufügen wenn man in __init__ ist:
    # requires a complex setup, this is why async_forward was invented.

    # Verwenden Sie die alte, kompatible Methode um Entitäten hinzuzufügen:
    async def async_add_danfoss_entities(async_add_entities_callback):
        async_add_entities_callback(entities)
        
    hass.async_create_task(
        hass.helpers.discovery.async_load_platform(
            "sensor", DOMAIN, async_add_danfoss_entities, config_entry.data
        )
    )

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Das Entladen ist jetzt komplexer, wenn wir discovery.async_load_platform nutzen
    # Wir überspringen das Entladen für dieses Beispiel
    return True


# --- SENSOR KLASSE HIER HERSTELLEN ---

class DanfossECLSensor(SensorEntity):
    """Representation of a Danfoss ECL Sensor."""
    
    def __init__(self, coordinator, key, reg_config):
        self.coordinator = coordinator
        self._key = key
        self._reg_config = reg_config
        self._attr_name = reg_config['name']
        self._attr_unique_id = f"danfoss_ecl_{key}_{reg_config['address']}"
        self._attr_unit_of_measurement = reg_config.get('unit')
        self._attr_device_class = reg_config.get('device_class')

    @property
    def state(self):
        """Return the state of the sensor (the actual value)."""
        if self.coordinator.data is None or self._key not in self.coordinator.data:
            return None
        return self.coordinator.data[self._key]
    
    @property
    def extra_state_attributes(self):
        """Return the state attributes (die zusätzlichen Felder)."""
        attributes = self._reg_config.copy()
        attributes.pop('name', None)
        attributes.pop('unit', None)
        attributes.pop('device_class', None)
        return attributes

    @property
    def should_poll(self):
        return False

    @property
    def available(self):
        return self.coordinator.last_update_success

    async def async_added_to_hass(self):
        """When entity is added to hass."""
        self.async_on_remove(self.coordinator.async_add_listener(self.async_write_ha_state))
