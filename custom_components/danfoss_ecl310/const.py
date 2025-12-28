"""Constants for the Danfoss ECL310 integration."""
from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.const import UnitOfTemperature

DOMAIN = "danfoss_ecl310"
CONF_HUB = "hub"
DEFAULT_PORT = 502
DEFAULT_SCAN_INTERVAL = 30
DEFAULT_SLAVE = 254

# --- GROUP 1: Status / Operating Modes (Every 30s) ---
SENSORS_60S = [
    # Group: Operating Mode
    {"key": "betriebsart_heizung", "name": "Mode: Heating", "addr": 4200, "type": "input", "scale": 1, "trans_key": "operating_mode", "icon": "mdi:radiator"},
    {"key": "betriebsart_ww", "name": "Mode: DHW", "addr": 4201, "type": "input", "scale": 1, "trans_key": "operating_mode", "icon": "mdi:water-boiler"},
    
    # Group: Pumps Status (0=Off, 1=On) -> Uses simple_on_off translation
    {"key": "pumpe_1", "name": "Pump: P1", "addr": 4005, "type": "input", "scale": 1, "trans_key": "simple_on_off", "icon": "mdi:pump"},
    {"key": "pumpe_2", "name": "Pump: P2", "addr": 4006, "type": "input", "scale": 1, "trans_key": "simple_on_off", "icon": "mdi:pump"},
    {"key": "pumpe_3", "name": "Pump: P3", "addr": 4007, "type": "input", "scale": 1, "trans_key": "simple_on_off", "icon": "mdi:pump"},
    
    # Group: Valves Status (0=Off, 1=On) -> Uses simple_on_off translation
    {"key": "m1_oeffnen", "name": "Valve: M1 Opening", "addr": 3999, "type": "input", "scale": 1, "trans_key": "simple_on_off", "icon": "mdi:valve-open"},
    {"key": "m1_schliessen", "name": "Valve: M1 Closing", "addr": 4000, "type": "input", "scale": 1, "trans_key": "simple_on_off", "icon": "mdi:valve-closed"},
    {"key": "m2_oeffnen", "name": "Valve: M2 Opening", "addr": 4001, "type": "input", "scale": 1, "trans_key": "simple_on_off", "icon": "mdi:valve-open"},
    {"key": "m2_schliessen", "name": "Valve: M2 Closing", "addr": 4002, "type": "input", "scale": 1, "trans_key": "simple_on_off", "icon": "mdi:valve-closed"},
    
    # Group: Manual Control (Mode for M1, M2, M3, P1, P2, P3)
    {"key": "manual_triac_m1", "name": "Valve: M1 Mode", "addr": 4059, "type": "input", "trans_key": "valve_manual_mode", "icon": "mdi:cog"},
    {"key": "manual_triac_m2", "name": "Valve: M2 Mode", "addr": 4060, "type": "input", "trans_key": "valve_manual_mode", "icon": "mdi:cog"},
    {"key": "manual_triac_m3", "name": "Valve: M3 Mode", "addr": 4061, "type": "input", "trans_key": "valve_manual_mode", "icon": "mdi:cog"},
    
    {"key": "manual_pumpe1", "name": "Pump: P1 Mode", "addr": 4065, "type": "input", "trans_key": "pump_mode", "icon": "mdi:cog"},
    {"key": "manual_pumpe2", "name": "Pump: P2 Mode", "addr": 4066, "type": "input", "trans_key": "pump_mode", "icon": "mdi:cog"},
    {"key": "manual_pumpe3", "name": "Pump: P3 Mode", "addr": 4067, "type": "input", "trans_key": "pump_mode", "icon": "mdi:cog"},
]

# --- GROUP 2: Temperatures S1 - S6 (Every 30s) ---
SENSORS_300S = [
    {"key": "s1_temp", "name": "Sensor: S1 (Outdoor)", "addr": 10200, "type": "input", "scale": 0.01, "unit": UnitOfTemperature.CELSIUS, "device_class": SensorDeviceClass.TEMPERATURE, "precision": 1},
    {"key": "s2_temp", "name": "Sensor: S2 (Room)", "addr": 10201, "type": "input", "scale": 0.01, "unit": UnitOfTemperature.CELSIUS, "device_class": SensorDeviceClass.TEMPERATURE, "precision": 1},
    {"key": "s3_temp", "name": "Sensor: S3 (Flow)", "addr": 10202, "type": "input", "scale": 0.01, "unit": UnitOfTemperature.CELSIUS, "device_class": SensorDeviceClass.TEMPERATURE, "precision": 1},
    {"key": "s4_temp", "name": "Sensor: S4 (DHW)", "addr": 10203, "type": "input", "scale": 0.01, "unit": UnitOfTemperature.CELSIUS, "device_class": SensorDeviceClass.TEMPERATURE, "precision": 1},
    {"key": "s5_temp", "name": "Sensor: S5", "addr": 10204, "type": "input", "scale": 0.01, "unit": UnitOfTemperature.CELSIUS, "device_class": SensorDeviceClass.TEMPERATURE, "precision": 1},
    {"key": "s6_temp", "name": "Sensor: S6", "addr": 10205, "type": "input", "scale": 0.01, "unit": UnitOfTemperature.CELSIUS, "device_class": SensorDeviceClass.TEMPERATURE, "precision": 1},
]

# --- GROUP 3: Settings & Limits (Every 600s) ---
SENSORS_600S = [
    {"key": "min_outdoor", "name": "Limit: Min Outdoor", "addr": 10499, "type": "input", "scale": 0.01, "unit": UnitOfTemperature.CELSIUS, "device_class": SensorDeviceClass.TEMPERATURE},
    {"key": "max_outdoor", "name": "Limit: Max Outdoor", "addr": 10504, "type": "input", "scale": 0.01, "unit": UnitOfTemperature.CELSIUS, "device_class": SensorDeviceClass.TEMPERATURE},
    {"key": "frostschutz", "name": "Limit: Frost Protection", "addr": 12092, "type": "input", "scale": 1, "unit": UnitOfTemperature.CELSIUS, "device_class": SensorDeviceClass.TEMPERATURE},
    
    {"key": "vl_min_temp", "name": "Limit: Flow Min", "addr": 11176, "type": "input", "scale": 1, "unit": UnitOfTemperature.CELSIUS, "device_class": SensorDeviceClass.TEMPERATURE},
    {"key": "vl_max_temp", "name": "Limit: Flow Max", "addr": 11177, "type": "input", "scale": 1, "unit": UnitOfTemperature.CELSIUS, "device_class": SensorDeviceClass.TEMPERATURE},
    
    # Updated: Removed 'Readonly' text. These reflect the current value of the register.
    {"key": "komfort_soll", "name": "Target: Comfort", "addr": 11179, "type": "input", "scale": 0.1, "unit": UnitOfTemperature.CELSIUS, "device_class": SensorDeviceClass.TEMPERATURE},
    {"key": "absenkung_soll", "name": "Target: Setback", "addr": 11180, "type": "input", "scale": 0.1, "unit": UnitOfTemperature.CELSIUS, "device_class": SensorDeviceClass.TEMPERATURE},
    
    {"key": "normal_wasser", "name": "Target: DHW Normal", "addr": 12189, "type": "input", "scale": 0.1, "unit": UnitOfTemperature.CELSIUS, "device_class": SensorDeviceClass.TEMPERATURE},
    {"key": "absenk_wasser", "name": "Target: DHW Setback", "addr": 12190, "type": "input", "scale": 0.1, "unit": UnitOfTemperature.CELSIUS, "device_class": SensorDeviceClass.TEMPERATURE},
]

# Climate Entities (Thermostats)
# These allow WRITING to the registers 11179 and 11180
CLIMATE_ENTITIES = [
    {
        "name": "ECL310 Target Temp",
        "key": "climate_target",
        "address": 11179,
        "slave": DEFAULT_SLAVE,
        "min_temp": 10,
        "max_temp": 30,
        "step": 0.5,
    },
    {
        "name": "ECL310 Setback Temp",
        "key": "climate_absenk",
        "address": 11180,
        "slave": DEFAULT_SLAVE,
        "min_temp": 10,
        "max_temp": 30,
        "step": 0.5,
    }
]
