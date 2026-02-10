"""Constants for the Danfoss ECL310 integration."""
from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.const import UnitOfTemperature, EntityCategory

DOMAIN = "danfoss_ecl310"
CONF_HUB = "hub"
DEFAULT_PORT = 502
DEFAULT_SLAVE = 254

DEFAULT_INTERVAL_FAST = 30
DEFAULT_INTERVAL_TEMP = 60
DEFAULT_INTERVAL_SLOW = 600

# --- GROUP 1: Status / Operating Modes (Sensors) ---
# Prefix "Mode:" to group them alphabetically
SENSORS_60S = [
    {"key": "mode_heating", "name": "Mode: Heating", "addr": 4200, "type": "input", "scale": 1, "trans_key": "operating_mode", "icon": "mdi:radiator"},
    {"key": "mode_dhw", "name": "Mode: DHW", "addr": 4201, "type": "input", "scale": 1, "trans_key": "operating_mode", "icon": "mdi:water-boiler"},
    
    {"key": "pump_1", "name": "Mode: Pump P1", "addr": 4005, "type": "input", "scale": 1, "trans_key": "simple_on_off", "icon": "mdi:pump"},
    {"key": "pump_2", "name": "Mode: Pump P2", "addr": 4006, "type": "input", "scale": 1, "trans_key": "simple_on_off", "icon": "mdi:pump"},
    {"key": "pump_3", "name": "Mode: Pump P3", "addr": 4007, "type": "input", "scale": 1, "trans_key": "simple_on_off", "icon": "mdi:pump"},
    
    {"key": "valve_m1_opening", "name": "Mode: Valve M1 Opening", "addr": 3999, "type": "input", "scale": 1, "trans_key": "simple_on_off", "icon": "mdi:valve-open"},
    {"key": "valve_m1_closing", "name": "Mode: Valve M1 Closing", "addr": 4000, "type": "input", "scale": 1, "trans_key": "simple_on_off", "icon": "mdi:valve-closed"},
    {"key": "valve_m2_opening", "name": "Mode: Valve M2 Opening", "addr": 4001, "type": "input", "scale": 1, "trans_key": "simple_on_off", "icon": "mdi:valve-open"},
    {"key": "valve_m2_closing", "name": "Mode: Valve M2 Closing", "addr": 4002, "type": "input", "scale": 1, "trans_key": "simple_on_off", "icon": "mdi:valve-closed"},
    {"key": "valve_m3_opening", "name": "Mode: Valve M3 Opening", "addr": 4003, "type": "input", "scale": 1, "trans_key": "simple_on_off", "icon": "mdi:valve-open"},
    {"key": "valve_m3_closing", "name": "Mode: Valve M3 Closing", "addr": 4004, "type": "input", "scale": 1, "trans_key": "simple_on_off", "icon": "mdi:valve-closed"},
    
    {"key": "manual_valve_m1", "name": "Mode: Manual Valve M1", "addr": 4059, "type": "input", "trans_key": "valve_manual_mode", "icon": "mdi:cog"},
    {"key": "manual_valve_m2", "name": "Mode: Manual Valve M2", "addr": 4060, "type": "input", "trans_key": "valve_manual_mode", "icon": "mdi:cog"},
    {"key": "manual_valve_m3", "name": "Mode: Manual Valve M3", "addr": 4061, "type": "input", "trans_key": "valve_manual_mode", "icon": "mdi:cog"},
    
    {"key": "manual_pump_1", "name": "Mode: Manual Pump P1", "addr": 4065, "type": "input", "trans_key": "pump_mode", "icon": "mdi:cog"},
    {"key": "manual_pump_2", "name": "Mode: Manual Pump P2", "addr": 4066, "type": "input", "trans_key": "pump_mode", "icon": "mdi:cog"},
    {"key": "manual_pump_3", "name": "Mode: Manual Pump P3", "addr": 4067, "type": "input", "trans_key": "pump_mode", "icon": "mdi:cog"},
]

# --- GROUP 2: Temperatures (Sensors) ---
# Prefix "Temp:" to group them
SENSORS_300S = [
    {"key": "temp_s1_outdoor", "name": "Temp: Outdoor (S1)", "addr": 10200, "type": "input", "scale": 0.01, "unit": UnitOfTemperature.CELSIUS, "device_class": SensorDeviceClass.TEMPERATURE, "precision": 1},
    {"key": "temp_s2_room", "name": "Temp: Room (S2)", "addr": 10201, "type": "input", "scale": 0.01, "unit": UnitOfTemperature.CELSIUS, "device_class": SensorDeviceClass.TEMPERATURE, "precision": 1},
    {"key": "temp_s3_flow", "name": "Temp: Flow (S3)", "addr": 10202, "type": "input", "scale": 0.01, "unit": UnitOfTemperature.CELSIUS, "device_class": SensorDeviceClass.TEMPERATURE, "precision": 1},
    {"key": "temp_s4_dhw", "name": "Temp: DHW (S4)", "addr": 10203, "type": "input", "scale": 0.01, "unit": UnitOfTemperature.CELSIUS, "device_class": SensorDeviceClass.TEMPERATURE, "precision": 1},
    {"key": "temp_s5", "name": "Temp: S5", "addr": 10204, "type": "input", "scale": 0.01, "unit": UnitOfTemperature.CELSIUS, "device_class": SensorDeviceClass.TEMPERATURE, "precision": 1},
    {"key": "temp_s6", "name": "Temp: S6", "addr": 10205, "type": "input", "scale": 0.01, "unit": UnitOfTemperature.CELSIUS, "device_class": SensorDeviceClass.TEMPERATURE, "precision": 1},
    
    {"key": "flow_target_calc", "name": "Temp: Flow Target (Calc)", "addr": 11253, "type": "input", "scale": 0.1, "unit": UnitOfTemperature.CELSIUS, "device_class": SensorDeviceClass.TEMPERATURE, "icon": "mdi:thermostat-auto"},
    
    # Limits displayed as Temps? No, better group as Limit
    {"key": "return_limit_day", "name": "Limit: Return (Day)", "addr": 11181, "type": "input", "scale": 0.1, "unit": UnitOfTemperature.CELSIUS, "device_class": SensorDeviceClass.TEMPERATURE, "icon": "mdi:arrow-left-bold-outline"},
    {"key": "return_limit_night", "name": "Limit: Return (Night)", "addr": 11182, "type": "input", "scale": 0.1, "unit": UnitOfTemperature.CELSIUS, "device_class": SensorDeviceClass.TEMPERATURE, "icon": "mdi:arrow-left-bold-outline"},
    {"key": "summer_cutout", "name": "Limit: Summer Cutout", "addr": 11189, "type": "input", "scale": 0.1, "unit": UnitOfTemperature.CELSIUS, "device_class": SensorDeviceClass.TEMPERATURE, "icon": "mdi:weather-sunny-off"},
]

# --- GROUP 3: Settings & Info (Sensors) ---
# Prefix "Limit:"
SENSORS_600S = [
    {"key": "limit_outdoor_min", "name": "Limit: Min Outdoor", "addr": 10499, "type": "input", "scale": 0.01, "unit": UnitOfTemperature.CELSIUS, "device_class": SensorDeviceClass.TEMPERATURE, "entity_category": EntityCategory.DIAGNOSTIC},
    {"key": "limit_outdoor_max", "name": "Limit: Max Outdoor", "addr": 10504, "type": "input", "scale": 0.01, "unit": UnitOfTemperature.CELSIUS, "device_class": SensorDeviceClass.TEMPERATURE, "entity_category": EntityCategory.DIAGNOSTIC},
    {"key": "limit_frost", "name": "Limit: Frost Protection", "addr": 12092, "type": "input", "scale": 1, "unit": UnitOfTemperature.CELSIUS, "device_class": SensorDeviceClass.TEMPERATURE, "entity_category": EntityCategory.DIAGNOSTIC},
    {"key": "limit_flow_min", "name": "Limit: Flow Min", "addr": 11176, "type": "input", "scale": 1, "unit": UnitOfTemperature.CELSIUS, "device_class": SensorDeviceClass.TEMPERATURE, "entity_category": EntityCategory.DIAGNOSTIC},
    {"key": "limit_flow_max", "name": "Limit: Flow Max", "addr": 11177, "type": "input", "scale": 1, "unit": UnitOfTemperature.CELSIUS, "device_class": SensorDeviceClass.TEMPERATURE, "entity_category": EntityCategory.DIAGNOSTIC},
    
    # Read-only feedback
    {"key": "target_flow_status", "name": "Set: Flow Target (Read)", "addr": 11179, "type": "input", "scale": 0.1, "unit": UnitOfTemperature.CELSIUS, "device_class": SensorDeviceClass.TEMPERATURE, "entity_category": EntityCategory.DIAGNOSTIC},
    {"key": "target_setback_status", "name": "Set: Setback Target (Read)", "addr": 11180, "type": "input", "scale": 0.1, "unit": UnitOfTemperature.CELSIUS, "device_class": SensorDeviceClass.TEMPERATURE, "entity_category": EntityCategory.DIAGNOSTIC},
    {"key": "target_dhw", "name": "Set: DHW Normal (Read)", "addr": 12189, "type": "input", "scale": 0.1, "unit": UnitOfTemperature.CELSIUS, "device_class": SensorDeviceClass.TEMPERATURE, "entity_category": EntityCategory.DIAGNOSTIC},
    {"key": "target_dhw_setback", "name": "Set: DHW Setback (Read)", "addr": 12190, "type": "input", "scale": 0.1, "unit": UnitOfTemperature.CELSIUS, "device_class": SensorDeviceClass.TEMPERATURE, "entity_category": EntityCategory.DIAGNOSTIC},
    
    # System Info (Hidden)
    {"key": "system_serial_number", "name": "Serialnumber", "addr": 36, "type": "holding", "scale": 1, "icon": "mdi:barcode"},
    {"key": "system_app_key", "name": "Application Key", "addr": 2060, "type": "holding", "scale": 1, "icon": "mdi:key-variant"},
    {"key": "system_firmware", "name": "System Firmware", "addr": 34, "type": "holding", "scale": 1, "icon": "mdi:chip"},
    {"key": "system_hardware", "name": "Hardware Revision", "addr": 33, "type": "holding", "scale": 1, "icon": "mdi:chip"},
    {"key": "system_modbus_addr", "name": "Modbus Addr", "addr": 37, "type": "holding", "scale": 1, "icon": "mdi:network"},
]

# Modbus Settings (NUMBER ENTITIES / SLIDERS)
# Prefix "Set:" or "Curve:"
NUMBER_ENTITIES = [
    {"name": "Set: Target Comfort", "key": "conf_target_comfort", "address": 11179, "slave": DEFAULT_SLAVE, "min": 10, "max": 30, "step": 0.5, "icon": "mdi:thermometer-check", "scale": 0.1},
    {"name": "Set: Target Setback", "key": "conf_target_setback", "address": 11180, "slave": DEFAULT_SLAVE, "min": 10, "max": 30, "step": 0.5, "icon": "mdi:thermometer-low", "scale": 0.1},
    {"name": "Curve: Slope", "key": "heat_curve_slope", "address": 11174, "slave": DEFAULT_SLAVE, "min": 0.1, "max": 2.5, "step": 0.1, "icon": "mdi:chart-line", "scale": 0.1},
    
    # Heat Curve Coordinates
    # Scale 1 because these are Integers (e.g. 50 = 50°C)
    {"name": "Curve: -30°C", "key": "heat_curve_m30", "address": 11399, "slave": DEFAULT_SLAVE, "min": 0, "max": 90, "step": 1, "icon": "mdi:chart-bell-curve", "scale": 1},
    {"name": "Curve: -15°C", "key": "heat_curve_m15", "address": 11400, "slave": DEFAULT_SLAVE, "min": 0, "max": 90, "step": 1, "icon": "mdi:chart-bell-curve", "scale": 1},
    {"name": "Curve: -5°C",  "key": "heat_curve_m05", "address": 11401, "slave": DEFAULT_SLAVE, "min": 0, "max": 90, "step": 1, "icon": "mdi:chart-bell-curve", "scale": 1},
    {"name": "Curve: 0°C",   "key": "heat_curve_00",  "address": 11402, "slave": DEFAULT_SLAVE, "min": 0, "max": 90, "step": 1, "icon": "mdi:chart-bell-curve", "scale": 1},
    {"name": "Curve: +5°C",  "key": "heat_curve_p05", "address": 11403, "slave": DEFAULT_SLAVE, "min": 0, "max": 90, "step": 1, "icon": "mdi:chart-bell-curve", "scale": 1},
    {"name": "Curve: +15°C", "key": "heat_curve_p15", "address": 11404, "slave": DEFAULT_SLAVE, "min": 0, "max": 90, "step": 1, "icon": "mdi:chart-bell-curve", "scale": 1},
]

INTERVAL_ENTITIES = [
    {"key": "interval_fast", "name": "Interval: Status", "coordinator": "coord_60", "default": DEFAULT_INTERVAL_FAST, "icon": "mdi:timer-refresh", "category": EntityCategory.CONFIG, "min": 15, "max": 600, "step": 5},
    {"key": "interval_temp", "name": "Interval: Temp", "coordinator": "coord_300", "default": DEFAULT_INTERVAL_TEMP, "icon": "mdi:timer-refresh", "category": EntityCategory.CONFIG, "min": 15, "max": 600, "step": 5},
    {"key": "interval_settings", "name": "Interval: Settings", "coordinator": "coord_600", "default": DEFAULT_INTERVAL_SLOW, "icon": "mdi:timer-refresh", "category": EntityCategory.CONFIG, "min": 15, "max": 600, "step": 5},
]

CLIMATE_ENTITIES = []
