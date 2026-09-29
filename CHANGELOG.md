# Changelog

All notable changes to this integration are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this project uses
[semantic versioning](https://semver.org/spec/v2.0.0.html).

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
