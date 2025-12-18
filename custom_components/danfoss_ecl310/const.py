"""Constants for the Danfoss ECL 310 integration."""
from homeassistant.helpers.entity import EntityCategory
from homeassistant.const import Platform

DOMAIN = "danfoss_ecl310"

CONF_SLAVE_ID = "slave_id"
DEFAULT_PORT = 502
DEFAULT_SLAVE_ID = 254
DEFAULT_SCAN_INTERVAL = 60

REGISTER_MAP = [
    # Climates
    {"key": "comfort_temp", "address": 11179, "type": "holding", "scale": 0.1, "platform": Platform.CLIMATE},
    {"key": "setback_temp", "address": 11180, "type": "holding", "scale": 0.1, "platform": Platform.CLIMATE},
    
    # Sensors (Input Type: input)
    {"key": "s1", "address": 10200, "type": "input", "scale": 0.01, "unit": "°C", "platform": Platform.SENSOR, "device_class": "temperature"},
    {"key": "s2", "address": 10201, "type": "input", "scale": 0.01, "unit": "°C", "platform": Platform.SENSOR, "device_class": "temperature"},
    {"key": "s3", "address": 10202, "type": "input", "scale": 0.01, "unit": "°C", "platform": Platform.SENSOR, "device_class": "temperature"},
    {"key": "s4", "address": 10203, "type": "input", "scale": 0.01, "unit": "°C", "platform": Platform.SENSOR, "device_class": "temperature"},
    {"key": "s5", "address": 10204, "type": "input", "scale": 0.01, "unit": "°C", "platform": Platform.SENSOR, "device_class": "temperature"},
    {"key": "s6", "address": 10205, "type": "input", "scale": 0.01, "unit": "°C", "platform": Platform.SENSOR, "device_class": "temperature"},
    {"key": "min_outdoor_temp", "address": 10499, "type": "input", "scale": 0.01, "unit": "°C", "platform": Platform.SENSOR},
    {"key": "max_outdoor_temp", "address": 10504, "type": "input", "scale": 0.01, "unit": "°C", "platform": Platform.SENSOR},
    {"key": "normal_water", "address": 12189, "type": "input", "scale": 0.1, "unit": "°C", "platform": Platform.SENSOR},
    {"key": "setback_water", "address": 12190, "type": "input", "scale": 0.1, "unit": "°C", "platform": Platform.SENSOR},
    {"key": "flow_min_temp", "address": 11176, "type": "input", "scale": 1.0, "unit": "°C", "platform": Platform.SENSOR},
    {"key": "flow_max_temp", "address": 11177, "type": "input", "scale": 1.0, "unit": "°C", "platform": Platform.SENSOR},
    {"key": "frost_protection", "address": 12092, "type": "input", "scale": 1.0, "unit": "°C", "platform": Platform.SENSOR},
    
    # Diagnostic (Binary & Status)
    {"key": "mode_heating", "address": 4200, "type": "input", "platform": Platform.SENSOR, "category": EntityCategory.DIAGNOSTIC},
    {"key": "mode_dhw", "address": 4201, "type": "input", "platform": Platform.SENSOR, "category": EntityCategory.DIAGNOSTIC},
    {"key": "pump_1", "address": 4005, "type": "input", "platform": Platform.BINARY_SENSOR, "category": EntityCategory.DIAGNOSTIC},
    {"key": "pump_2", "address": 4006, "type": "input", "platform": Platform.BINARY_SENSOR, "category": EntityCategory.DIAGNOSTIC},
    {"key": "pump_3", "address": 4007, "type": "input", "platform": Platform.BINARY_SENSOR, "category": EntityCategory.DIAGNOSTIC},
    {"key": "m1_opening", "address": 3999, "type": "input", "platform": Platform.BINARY_SENSOR, "category": EntityCategory.DIAGNOSTIC},
    {"key": "m1_closing", "address": 4000, "type": "input", "platform": Platform.BINARY_SENSOR, "category": EntityCategory.DIAGNOSTIC},
    {"key": "m2_opening", "address": 4001, "type": "input", "platform": Platform.BINARY_SENSOR, "category": EntityCategory.DIAGNOSTIC},
    {"key": "m2_closing", "address": 4002, "type": "input", "platform": Platform.BINARY_SENSOR, "category": EntityCategory.DIAGNOSTIC},
    {"key": "manual_triac_m1", "address": 4059, "type": "input", "platform": Platform.BINARY_SENSOR, "category": EntityCategory.DIAGNOSTIC},
    {"key": "manual_triac_m2", "address": 4060, "type": "input", "platform": Platform.BINARY_SENSOR, "category": EntityCategory.DIAGNOSTIC},
    {"key": "manual_triac_m3", "address": 4061, "type": "input", "platform": Platform.BINARY_SENSOR, "category": EntityCategory.DIAGNOSTIC},
    {"key": "manual_pump_1", "address": 4065, "type": "input", "platform": Platform.BINARY_SENSOR, "category": EntityCategory.DIAGNOSTIC},
    {"key": "manual_pump_2", "address": 4066, "type": "input", "platform": Platform.BINARY_SENSOR, "category": EntityCategory.DIAGNOSTIC},
    {"key": "manual_pump_3", "address": 4067, "type": "input", "platform": Platform.BINARY_SENSOR, "category": EntityCategory.DIAGNOSTIC},
]
