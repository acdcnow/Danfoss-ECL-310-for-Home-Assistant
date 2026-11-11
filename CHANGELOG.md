# Changelog

All notable changes to this integration are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this project uses
[semantic versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **Selectable application.** The setup form has a new **Application** field. The register map is
  now a profile in the new `applications.py`; sensors, numbers and valve movement sensors are created
  from the profile of the entry. `A247.1` is the default and keeps the existing register map unchanged.
- **The setup checks the controller's application key and subtype** (registers 2060 / 2061) when a
  profile declares an expected value, and refuses a mismatch. `A247.1` declares none, so it behaves as
  before.
- **32-bit register values.** A register reference can span several registers (`count: 2`, high word
  first), block planning and decoding handle it, and sensors can carry a `state_class`
  (`total_increasing` for an energy meter). Existing entries are unaffected: they all use one register.
- **Per-entity devices.** An entry can name its device with `device_group`; the movement sensors and the
  number entities honour it. Without it the grouping is unchanged.

### Changed

- Config entries without an `application` value are treated as A247.1, so existing installs need no
  migration and keep their entity ids.
- Reconfigure keeps the entry's application and refuses a controller that runs a different one.

## [1.2.4] - 2026-11-07

### Fixed

- **`Limit: Summer Cutout` was reading the setback setpoint.** 1.2.3 moved the sensor to register
  `11180`, which holds the **setback** setpoint (Danfoss parameter `11181`, tenths of a degree), so
  a `19.0 °C` setback came through as `190`. The summer cut-out is parameter `11179`, and an ECL
  parameter *n* is served at the zero-based register *n - 1*, so the cut-out lives at **`11178`** -
  the register 1.2.2 already read. The sensor reads `11178` again and keeps the whole-degree
  decoding (`0...50 °C`, `0` = OFF) that 1.2.3 introduced.

## [1.2.3] - 2026-11-07

### Fixed

- **`Limit: Summer Cutout` was shown ten times too small** - `20 °C` on the controller appeared as
  `2.0 °C`. The limit is a **whole-degree** value in the range `0...50`, with `0` meaning **OFF**,
  not a tenth-degree setpoint, so it must not be multiplied by `0.1`. It now uses `scale: 1` and
  shows the value the controller's display shows.

### Changed

- **`Limit: Summer Cutout` now reads register `11180`** instead of `11178`. Danfoss documents the
  parameter as `11179`; `11180` is the address that answers the cut-out on the controller this
  integration was verified against.
- `Limit: Summer Cutout` no longer suggests one decimal place and is no longer decoded as a signed
  register: the limit cannot go below `0`, so the state is the plain whole-degree reading.
- **The minimum Home Assistant version is now 2026.11.0** (`hacs.json`). 1.2.0–1.2.2 required
  2026.9.0.
- **Setup and unload follow the 2026.11 config entry API.** `async_setup_entry` and
  `async_unload_entry` return `None`; a platform that cannot be unloaded raises through
  `async_unload_platforms_or_raise` instead of reporting a bare `False`.
- **The controller device is registered with `async_get_or_create_from_info`.** `DeviceInfo` and
  `ChildDeviceInfo` are dataclasses in 2026.11, so the controller's `DeviceInfo` is passed whole
  rather than unpacked into keyword arguments, and an identity register the controller did not
  answer is now left unset instead of being written as `None`.
- **The manifest declares the integration category `climate.thermostats_heating`**, so the
  integration is browsable under *Climate › Thermostats & heating*.

## [1.2.2] - 2026-10-09

### Fixed

- **`Limit: Summer Cutout` pointed at the wrong register.** It read `11189`, but the controller
  reports the summer cut-out on **`11178`**. The sensor never answered, which is why every poll
  logged `2 register(s) did not answer this cycle: flow_target_calc, summer_cutout`. It now reads
  `11178`.
- **`Temp: Flow Target (Calc)` pointed at the wrong register.** The calculated flow target is on
  **`11252`**; `11253` was off by one, so this sensor was the other half of the same *did not
  answer* warning. It now reads `11252`.
- **Three temperatures were decoded with the wrong scale** and read 10-100x too large:
  `Temp: Flow Target (Calc)` showed `246.30` instead of `24.63`, and `Temp: Outdoor (Acc.)` /
  `Temp: Reference Place` showed `1619.0` / `2463.0` instead of `16.19` / `24.63`. These are
  hundredths-of-a-degree registers, so they now use `"scale": 0.01`.

### Added

- **`Temp: Outdoor (Acc.)`** - the accumulated (filtered) outdoor temperature, register `11099`.
- **`Temp: Reference Place`** - register `11500`.
- **Pump protection and start temperatures**, registers `11076`, `11077` and `12075`. Each is
  available both as a read-only sensor and as a writable number, mirroring the comfort/setback
  pair:
  - `Set: Pump Frost Protection` / `Set: Pump Frost Protection (Read)` (`11076`)
  - `Set: Pump Start Temperature` / `Set: Pump Start Temperature (Read)` (`11077`)
  - `Set: Circ Pump Frost Protection` / `Set: Circ Pump Frost Protection (Read)` (`12075`) - the
    circulation pump's frost-protection temperature ("Pump-Zirk. Temp-Frost").

  The numbers sit on the **Controls** device, their read-backs on **Diagnostics**, and the two
  outdoor readings on **Sensors**.

### Changed

- `Temp: Flow Target (Calc)`, `Temp: Outdoor (Acc.)` and `Temp: Reference Place` now suggest
  **two** decimal places.
- The **brand images** are now the Danfoss logo: the light and dark wordmark replace the previous
  custom artwork, and the integration icon is the Danfoss "D". All six images (`logo`, `dark_logo`
  and `icon`, each with an `@2x` twin) are transparent PNGs in the sizes Home Assistant expects.

### Notes

- The two corrected sensors keep their keys, so their entity IDs and history are unchanged - only
  the register they read moved.
- The **pump** protection/start temperatures are still declared as whole degrees. If one of them
  reads 10x or 100x too large on your controller, give it the matching `"scale"` in `const.py`
  (`0.1` or `0.01`) - the same fix that was applied to the three temperatures above.
- The new pump numbers default to `-10...30 °C` (frost protection) and `-10...60 °C` (start
  temperature). Verify the permitted range for your application and adjust `min`/`max` in
  `const.py` if it differs.

## [1.2.1] - 2026-09-29

### Fixed

- **The dashboard no longer needs helper entities.** It used to read three template sensors
  (`sensor.heizung_betriebsstatus`, `sensor.heizung_regelabweichung`,
  `binary_sensor.heizung_sensorstoerung`) from `dashboards/ecl310-helpers.yaml`. If that package was
  not installed - which is easy to miss - those cards showed *entity not available* instead of the
  dashboard. The operating state now comes from the integration's own mode entities, the warning cards
  are plain `state: unavailable` conditions and the trend tile shows the flow temperature, so nothing
  on the dashboard depends on a template any more.
- `sensor.ecl310_mode_manual_pump_p1` was addressed as `..._mode_manual_pump_1` in the dashboard and
  in its preview, so that row was silently dropped.

### Changed

- `dashboards/ecl310-helpers.yaml` now contains only `input_boolean.expert_mode` - the one thing an
  integration cannot create and Lovelace cannot work without. If you installed the previous version,
  the three template sensors can be deleted (the dashboard no longer reads them).
- The dashboard's header banner was removed; the badges carry the same live values.
- `dashboards/README.md` now explains the difference between *entity not available*, *unknown* and
  *unavailable* - the second one means the controller did not answer that register.

### Notes

- The summer-cutout banner went away with the template sensors. While the controller is off for the
  summer, the operating mode tile shows **Standby**.

## [1.2.0] - 2026-09-29

The transport layer was rewritten: the controller is no longer read through the integration's own
socket but through Home Assistant's built-in **Modbus** integration.
**Home Assistant 2026.9 or newer is required** - on anything older the integration does not load.

### Added

- **Lovelace dashboard** in [`dashboards/`](dashboards): a sections view with a standard view
  (temperatures with bar gauges, setpoints, storage gauge, operating states, 72 h history) and an
  expert view (heating curve with the current operating point, curve setpoints, limits, valves and
  pumps, maintenance/diagnostics), switched by `input_boolean.expert_mode`. Ships with the helper
  package the dashboard needs and an offline preview of both views.
- **Five devices:** entities are grouped onto the controller plus the child devices *Controls*,
  *Sensors*, *Pumps*, *Configuration* and *Diagnostics*.
- **Reconfigure** flow: the controller's IP address can be changed from the integration's menu
  instead of deleting and re-adding the entry.
- The controller's **serial number, firmware and hardware revision** now reach the device registry.
  They never appeared in 1.1.x, because the sensors holding them were registered as disabled and so
  never ran.
- `strings.json`, config-flow translations and the integration's own brand images.

### Changed

- The controller is read through `homeassistant.components.modbus.async_get_unit` instead of a
  private `AsyncModbusTcpClient`, so the connection is shared with every other Modbus integration on
  the same controller.
- Registers are read in **batched blocks** (`device.py`): neighbouring addresses are one Modbus
  request, and a block that fails only blanks its own registers instead of the whole cycle.
- A controller that stops answering marks its entities `unavailable` instead of reporting no value.
- A rejected setpoint write raises a visible error instead of failing silently.
- `hacs.json` now requires Home Assistant **2026.9.0**.
- **Entity IDs and unique IDs are unchanged**, so an upgrade from 1.1.x keeps every id (and your
  history, automations and customisations). On a *fresh* install the child device's name becomes part
  of newly created entity ids - for example `number.controls_set_target_comfort` - because Home
  Assistant prefixes the device name for entities that use it. See the README for the details.

### Removed

- `modbus_client.py`, replaced by `device.py`.
- The pymodbus version juggling 1.1.x needed to stay compatible.
- The outdated claim that the integration offers Climate entities: the setpoints have always been
  `number` entities.

### Pre-releases

* `1.2.0-beta.1` (2026-09-19) - the Modbus integration rewrite, `device.py`, batched reads.
* `1.2.0-beta.2` - brand images shipped with the integration.
* `1.2.0-beta.3` (2026-09-29) - entities grouped onto five devices.

## [1.1.9] - 2026-02

### Fixed

- Manifest version and a handful of register definitions.

## [1.1.8] and earlier

Temperatures, pump and valve states and operating modes were read directly over TCP with pymodbus.
