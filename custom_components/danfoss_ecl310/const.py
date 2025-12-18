"""Constants for the Danfoss ECL 310 integration."""
from homeassistant.helpers.entity import EntityCategory
from homeassistant.const import Platform

DOMAIN = "danfoss_ecl310"
CONF_SLAVE_ID = "slave_id"
DEFAULT_PORT = 502
DEFAULT_SLAVE_ID = 254
DEFAULT_SCAN_INTERVAL = 60

# State mappings based on your template logic
STATE_MAP_MODE = {0: "Manual", 1: "Schedule", 2: "Comfort", 3: "Constant setback", 4: "Constant comfort"}
STATE_MAP_PUMP_BINARY = {0: "Aus", 1: "Ein"}
STATE_MAP_VALVE_BINARY = {0: "Zu", 1: "Auf"}
STATE_MAP_VALVE_MOVE = {0: "stop", 1: "Öffnen", 2: "Schließen"}
STATE_MAP_PUMP_MODUS = {0: "AUTO", 1: "OFF", 2: "ON"}
STATE_MAP_VALVE_MODUS = {0: "AUTO", 1: "STOP", 2: "SCHLIEẞEN", 3: "ÖFFNEN"}

REGISTER_MAP = [
    # Climate (Holding)
    {"key": "comfort_temp", "address": 11179, "type": "holding", "scale": 0.1, "platform": Platform.CLIMATE},
    {"key": "setback_temp", "address": 11180, "type": "holding", "scale": 0.1, "platform": Platform.CLIMATE},
    
    # Sensors with Mapped States (The Logic you requested)
    {"key": "mode_heating", "address": 4200, "type": "input", "platform": Platform.SENSOR, "map": STATE_MAP_MODE},
    {"key": "mode_dhw", "address": 4201, "type": "input", "platform": Platform.SENSOR, "map": STATE_MAP_MODE},
    
    {"key": "pump_1_status", "address": 4005, "type": "input", "platform": Platform.SENSOR, "map": STATE_MAP_PUMP_BINARY},
    {"key": "pump_3_status", "address": 4007, "type": "input", "platform": Platform.SENSOR, "map": STATE_MAP_PUMP_BINARY},
    
    {"key": "m1_status", "address": 4065, "type": "input", "platform": Platform.SENSOR, "map": STATE_MAP_VALVE_BINARY}, # Heizungsventil
    {"key": "m2_status", "address": 4066, "type": "input", "platform": Platform.SENSOR, "map": STATE_MAP_VALVE_BINARY}, # Wasserventil
    
    {"key": "manual_pumpe1", "address": 4065, "type": "input", "platform": Platform.SENSOR, "map": STATE_MAP_PUMP_MODUS},
    {"key": "manual_pumpe3", "address": 4067, "type": "input", "platform": Platform.SENSOR, "map": STATE_MAP_PUMP_MODUS},
    
    {"key": "manual_triac_m1", "address": 4059, "type": "input", "platform": Platform.SENSOR, "map": STATE_MAP_VALVE_MODUS},
    {"key": "manual_triac_m2", "address": 4060, "type": "input", "platform": Platform.SENSOR, "map": STATE_MAP_VALVE_MODUS},

    # Regular Temperature Sensors
    {"key": "s1", "address": 10200, "type": "input", "scale": 0.01, "unit": "°C", "platform": Platform.SENSOR, "device_class": "temperature"},
    {"key": "s2", "address": 10201, "type": "input", "scale": 0.01, "unit": "°C", "platform": Platform.SENSOR, "device_class": "temperature"},
    {"key": "s3", "address": 10202, "type": "input", "scale": 0.01, "unit": "°C", "platform": Platform.SENSOR, "device_class": "temperature"},
    {"key": "s4", "address": 10203, "type": "input", "scale": 0.01, "unit": "°C", "platform": Platform.SENSOR, "device_class": "temperature"},
    {"key": "s5", "address": 10204, "type": "input", "scale": 0.01, "unit": "°C", "platform": Platform.SENSOR, "device_class": "temperature"},
    {"key": "s6", "address": 10205, "type": "input", "scale": 0.01, "unit": "°C", "platform": Platform.SENSOR, "device_class": "temperature"},
]
