Here is a comprehensive `README.md` file for your GitHub repository. It covers installation, usage, technical details, and customization instructions.

---

# Danfoss ECL310 for Home Assistant

This is a custom integration for **Home Assistant** to monitor and control **Danfoss ECL310** district heating controllers via **Modbus TCP**.

It supports reading temperatures, pump/valve statuses, and operating modes, as well as controlling target temperatures via standard Climate entities.

## ✨ Features

* **Native Modbus TCP:** Connects directly to the controller (default port 502).
* **Multi-Device Support:** Add multiple ECL310 controllers by IP address; they will appear as separate devices in Home Assistant.
* **Climate Control:** Adjust "Comfort" and "Setback" target temperatures directly from the Lovelace UI. Changes are written back to the controller.
* **Localized:** Fully translated into **English, German, French, Italian, and Spanish**.
* **Robust Connection:** Handles different Modbus library versions and connection drops gracefully.
* **Grouped Entities:** Sensors are logically named and grouped (e.g., "Pump: P1", "Sensor: S1") for easy sorting.

## ⚙️ How it Works

The integration connects to the ECL310 using the `pymodbus` library. It sets up three data coordinators to poll the device at different intervals to optimize network traffic:

1. **Fast (30s):** Status updates (Pumps, Valves, Operating Modes) and Temperatures.
2. **Slow (600s):** Settings, Limits, and Configuration values (Read-only).

**Note:** Climate entities (Target Temperatures) are updated every 30 seconds. When you change a temperature in Home Assistant, the value is immediately written to the Modbus register.

---

## 📥 Installation

### Option 1: HACS (Recommended)

1. Open HACS in Home Assistant.
2. Go to "Integrations" > Top right menu > "Custom repositories".
3. Enter the URL of this GitHub repository.
4. Category: **Integration**.
5. Click **Add** and then install "Danfoss ECL310".
6. Restart Home Assistant.

### Option 2: Manual Installation

1. Download the `danfoss_ecl310` folder from this repository.
2. Copy the folder into your Home Assistant `config/custom_components/` directory.
3. The path should look like this: `/config/custom_components/danfoss_ecl310/__init__.py`.
4. Restart Home Assistant.

---

## 🚀 Configuration

1. Go to **Settings** -> **Devices & Services**.
2. Click **Add Integration** in the bottom right.
3. Search for **Danfoss ECL310**.
4. Enter the **IP Address** of your controller.
5. Enter the **Port** (Default is `502`).
6. Click Submit.

*To add a second device, simply repeat these steps with a different IP address.*

---

## 🛠️ Advanced: Adjusting Sensors (`const.py`)

This integration is designed to be easily extensible. All register mappings are defined in `const.py`. You do not need to touch the complex logic code to add a new sensor.

### How to add or modify a sensor:

1. Open `custom_components/danfoss_ecl310/const.py`.
2. Locate the appropriate list based on how often you want the data to update:
* `SENSORS_60S`: Status/Modes (Updates every 30s).
* `SENSORS_300S`: Temperatures (Updates every 30s).
* `SENSORS_600S`: Static settings (Updates every 10 mins).


3. Add a new line to the list dictionary.

### Sensor Configuration Structure

```python
{
    "key": "unique_internal_key",   # Must be unique per device (e.g., "return_temp")
    "name": "Displayed Name",       # e.g., "Sensor: Return Temp"
    "addr": 12345,                  # The Modbus Register Address
    "type": "input",                # "input" (Input Register) or "holding" (Holding Register)
    "scale": 0.01,                  # Multiplier (e.g., 0.01 to convert 2350 to 23.50)
    "unit": UnitOfTemperature.CELSIUS, # Optional: Unit
    "icon": "mdi:thermometer",      # Optional: Icon
    "trans_key": "simple_on_off"    # Optional: Translation key for state mapping
}

```

### Example: Adding a new Temperature Sensor

If you want to read a temperature from register `11200`:

1. Go to `SENSORS_300S` in `const.py`.
2. Add this line:
```python
{"key": "my_new_temp", "name": "Sensor: New Temp", "addr": 11200, "type": "input", "scale": 0.01, "unit": UnitOfTemperature.CELSIUS, "device_class": SensorDeviceClass.TEMPERATURE},

```


3. **Restart Home Assistant.**

### Available Translation Keys

If you are reading a status register (0/1), you can use these keys in `trans_key` to make the UI show text instead of numbers:

* `simple_on_off`: 0 = Off, 1 = On (Localized)
* `pump_mode`: 0 = Auto, 1 = Off, 2 = On
* `valve_manual_mode`: 0 = Auto, 1 = Stop, 2 = Closing, 3 = Opening

---

## 🐛 Troubleshooting

If values are not appearing or the connection fails, enable debug logging to see exactly what is happening on the Modbus connection.

Add this to your `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.danfoss_ecl310: debug
    pymodbus: debug

```

**Common Issues:**

* **"Connection failed":** Check if the IP is correct and if port 502 is open. Ensure no other system is blocking the Modbus port on the Danfoss controller.
* **Entities Unavailable:** Check the logs. If the Danfoss controller is busy or restarting, it might miss a poll cycle. The integration will automatically reconnect.

---

## 🌍 Translations

The integration is currently translated into:

* 🇺🇸 English (Default)
* 🇩🇪 German
* 🇫🇷 French
* 🇮🇹 Italian
* 🇪🇸 Spanish

The language is automatically selected based on your Home Assistant user profile settings.

## License

MIT License
