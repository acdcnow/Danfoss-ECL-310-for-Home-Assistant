# Danfoss ECL310 for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![Maintainer](https://img.shields.io/badge/maintainer-acdcnow-blue)](https://github.com/acdcnow)
[![Version](https://img.shields.io/badge/version-1.2.0--beta.2-green)]()

![Danfoss ECL 310](custom_components/danfoss_ecl310/brand/logo.png)

This is a custom integration for **Home Assistant** to monitor and control **Danfoss ECL310** district heating controllers via **Modbus TCP**.
Using Application 247.1 (V01)

It supports reading temperatures, pump/valve statuses, and operating modes, as well as writing target temperatures and the heat curve back to the controller.

## ⚠️ Requirements

* Home Assistant **2026.9** or newer.
* The built-in **Modbus** integration (installed automatically as a dependency). It does not need any YAML configuration of its own.

The controller is always addressed on Modbus unit **254**, which is fixed by Danfoss for application 247.1 and therefore is not asked for during setup.

## 🧪 Pre-release: v1.2.0-beta.2

This branch is published as the GitHub **pre-release** `v1.2.0-beta.2`. It is a testing build: see the [release notes](https://github.com/acdcnow/Danfoss-ECL-310-for-Home-Assistant/releases/tag/v1.2.0-beta.2) for the full changelog and what is worth checking.

> **⚠️ Home Assistant 2026.9 or newer is required.** The integration now reads the controller through Home Assistant's own Modbus integration (`async_get_unit`, introduced in 2026.9) instead of opening its own socket. On an older Home Assistant the integration will not load at all.

### Installing the test build

HACS hides pre-releases unless you have opted into beta versions, so the most reliable route is a manual install:

1. Download the archive for the tag:
   `https://github.com/acdcnow/Danfoss-ECL-310-for-Home-Assistant/archive/refs/tags/v1.2.0-beta.2.zip`
2. Unzip it and replace your existing `config/custom_components/danfoss_ecl310/` folder with the `custom_components/danfoss_ecl310/` folder from the archive.
3. Restart Home Assistant.

If you would rather stay inside HACS, enable pre-release/beta versions in the HACS settings and redownload the integration — HACS will then offer `v1.2.0-beta.2`.

### Rolling back

Entity IDs and unique IDs are unchanged, so reverting is safe: redownload **1.1.9** in HACS (or put the previous folder back) and restart Home Assistant. Your history, names and customisations are preserved.

### What is worth checking

* The controller's device page now shows a **serial number, firmware and hardware revision**. These never appeared in 1.1.9, because the sensors that held them were registered as disabled and so never ran.
* **Temperatures, pump and valve states** read the same as before, but they are now explicitly requested from unit 254 rather than relying on a Modbus keyword that recent versions of the underlying library had removed.
* Changing **Set: Target Comfort** / **Set: Target Setback** reaches the controller, and a rejected write now raises a visible error instead of failing silently.
* If you run another Modbus integration against the same controller, both should keep working — they now share a single connection instead of competing for it.
* **Reconfigure** on the integration's ⋮ menu lets you change the controller's IP without deleting and re-adding the entry.

Please report anything that looks wrong on the [issue tracker](https://github.com/acdcnow/Danfoss-ECL-310-for-Home-Assistant/issues), with debug logging enabled (see [Troubleshooting](#-troubleshooting)).

## ✨ Features

* **Shared Modbus connection:** The integration asks Home Assistant's Modbus integration for a unit on your controller instead of opening its own socket, so it never competes with other Modbus integrations for the device.
* **Multi-Device Support:** Add multiple ECL310 controllers by IP address; they will appear as separate devices in Home Assistant.
* **Setpoint Control:** Adjust "Comfort" and "Setback" target temperatures and the heating curve directly from the Lovelace UI. Changes are written back to the controller, and the controller's own response is reported if a write fails.
* **Localized:** Fully translated into **English, German, French, Italian, and Spanish**.
* **Robust Connection:** Dropped links are re-established automatically, and a controller that stops answering marks its entities unavailable instead of silently reporting no value.
* **Grouped Entities:** Sensors are logically named and grouped (e.g., "Mode: Pump P1", "Temp: Outdoor (S1)") for easy sorting.

## ⚙️ How it Works

The integration reads the controller through the Home Assistant **Modbus** integration, which owns the TCP connection. Three data coordinators poll the device at different intervals, and each poll batches neighbouring registers into a single Modbus request to keep the traffic on the bus low:

1. **Status (30s):** Pumps, valves, operating modes and the writable setpoints.
2. **Temperature (60s):** Sensor readings and temperature limits.
3. **Settings (600s):** Static configuration and system information.

Every interval is adjustable at runtime through the *Interval:* number entities.

**Note:** Setpoints are polled on the fastest interval. When you change a value in Home Assistant it is written to the Modbus register immediately and shown right away; the next poll confirms what the controller accepted.

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

The connection is verified before the entry is created, so a wrong IP is reported as *Failed to connect* rather than creating a broken device.

*To add a second device, simply repeat these steps with a different IP address. To point an existing entry at a new address, use the **Reconfigure** option on the integration's menu — there is no need to delete and re-add it.*

---

## 🛠️ Advanced: Adjusting Sensors (`const.py`)

This integration is designed to be easily extensible. All register mappings are defined in `const.py`. You do not need to touch the complex logic code to add a new sensor.

### How to add or modify a sensor:

1. Open `custom_components/danfoss_ecl310/const.py`.
2. Locate the appropriate list based on how often you want the data to update:
   * `SENSORS_STATUS`: Status/Modes (default 30s).
   * `SENSORS_TEMPERATURE`: Temperatures (default 60s).
   * `SENSORS_SETTINGS`: Static settings and system info (default 600s).
3. Add a new line to the list dictionary.
4. **Restart Home Assistant.**

### Sensor Configuration Structure

```python
{
    "key": "unique_internal_key",   # Must be unique per device (e.g., "return_temp")
    "name": "Displayed Name",       # e.g., "Temp: Return"
    "addr": 12345,                  # The Modbus Register Address
    "type": "input",                # "input" (Input Register) or "holding" (Holding Register)
    "signed": True,                 # Optional: decode as a negative-capable int16. Default False.
    "scale": 0.01,                  # Optional: multiplier (e.g. 0.01 turns 2350 into 23.50). Default 1.
    "unit": UnitOfTemperature.CELSIUS,        # Optional: Unit
    "device_class": SensorDeviceClass.TEMPERATURE,  # Optional: Device class
    "icon": "mdi:thermometer",      # Optional: Icon
    "entity_category": EntityCategory.DIAGNOSTIC,   # Optional: "Diagnostic"/"Config" grouping
    "precision": 1,                 # Optional: suggested number of decimals
    "trans_key": "simple_on_off"    # Optional: Translation key for state mapping
}
```

> **`signed` matters.** Only registers that can genuinely hold a negative number should set it. Temperatures do; counters, status codes, serial numbers and firmware revisions do not, and marking one of those as signed turns e.g. a serial number of `50000` into `-15536`.

### Example: Adding a new Temperature Sensor

If you want to read a temperature from register `11200`:

1. Go to `SENSORS_TEMPERATURE` in `const.py`.
2. Add this line:
```python
{"key": "my_new_temp", "name": "Temp: New", "addr": 11200, "type": "input", "signed": True, "scale": 0.01, "unit": UnitOfTemperature.CELSIUS, "device_class": SensorDeviceClass.TEMPERATURE},
```
3. **Restart Home Assistant.**

### Available Translation Keys

If you are reading a status register (0/1), you can use these keys in `trans_key` to make the UI show text instead of numbers:

* `operating_mode`: 0 = Standby, 1 = Schedule, 2 = Comfort, 3 = Setback, 4 = Frost Protection, 5 = Manual
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
    modbus_connection: debug
    pymodbus: debug
```

**Common Issues:**

* **"Failed to connect" during setup:** Check that the IP is correct and that port 502 is reachable. Make sure no other Modbus client is holding the controller's single available session.
* **Entities unavailable:** The controller did not answer a poll — usually because it is busy or restarting. The integration reconnects by itself; there is no need to reload the integration.
* **Values still show as "Unknown" after upgrading from 1.1.x:** The *System:* sensors used to be registered as disabled. Entities that already exist keep the state they were created with, so enable them once under **Settings → Devices & Services → Entities** if you want to see them.
* **Setting the comfort temperature has no effect at the top of the range:** The setpoint range defaults to 10–90 °C. Verify the permitted range for your application in the controller and adjust `min`/`max` in `const.py` if it differs.

---

## 🌍 Translations

The integration is currently translated into:

* us English (Default)
* 🇩🇪 German
* 🇫🇷 French
* 🇮🇹 Italian
* 🇪🇸 Spanish

The language is automatically selected based on your Home Assistant user profile settings.

---

## 🧩 Project layout

| File | Responsibility |
| --- | --- |
| `__init__.py` | Entry setup, the three coordinators, and the device registry entry. |
| `device.py` | Everything that knows the controller's registers. No Home Assistant imports, so it is testable against a mock bus. |
| `const.py` | The declarative register and entity map. |
| `sensor.py` / `number.py` | The entities. |
| `config_flow.py` | Setup and reconfigure flows. |
| `brand/` | The integration's own icon and logo. Home Assistant reads these directly, so no entry in the brands repository is needed. |
