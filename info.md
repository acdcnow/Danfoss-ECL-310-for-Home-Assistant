# Danfoss ECL 310

Monitor and control a **Danfoss ECL310** district heating controller over **Modbus TCP**, using
Application 247.1 (V01).

Reads temperatures, pump and valve states and operating modes, and writes the heating curve and
setpoints back to the controller.

> **Requires Home Assistant 2026.9 or newer**, and the built-in **Modbus** integration. The
> controller is always addressed on Modbus unit 254, which is fixed by Danfoss and needs no
> configuration.

## At a glance

- **Shared Modbus connection.** The controller is read through Home Assistant's own Modbus
  integration, so this integration never opens a competing socket and other Modbus integrations can
  talk to the same controller.
- **Five devices, cleanly separated.** The controller itself, plus child devices for **Controls**,
  **Sensors**, **Pumps**, **Configuration** and **Diagnostics**, so entities are not all piled onto
  one page.
- **Setpoint control** for comfort and setback temperatures and the heat curve, written straight to
  the controller.
- **Honest error reporting.** A rejected write raises a visible error, and a controller that stops
  answering marks its entities unavailable instead of quietly reporting nothing.
- **Localized** into English, German, French, Italian and Spanish.
- **One icon, shipped with the integration** — no entry in the brands repository needed.

## Installation

### HACS

1. Open HACS and add this repository under **Custom repositories**, category **Integration**.
2. Install **Danfoss ECL310** and restart Home Assistant.

### Manual

Copy `custom_components/danfoss_ecl310/` into your Home Assistant `config/custom_components/`
directory and restart.

## Configuration

**Settings → Devices & Services → Add Integration → Danfoss ECL310**, then enter the controller's
IP address and port (default `502`). The connection is verified before the entry is created, so a
wrong address is reported rather than leaving you with a dead device.

Add a second controller by repeating this with a different IP address. To move an existing entry to
a new address, use **Reconfigure** on the integration's menu — there is no need to delete and
re-add it.

## Current pre-release

The **1.2.0** line is a testing build: it moves the integration onto Home Assistant's own Modbus
integration and requires **2026.9 or newer**. See the
[releases page](https://github.com/acdcnow/Danfoss-ECL-310-for-Home-Assistant/releases) for the
changelog and install notes for the beta.

## Full documentation

The [README](https://github.com/acdcnow/Danfoss-ECL-310-for-Home-Assistant#readme) covers the
device layout, how to add registers in `const.py`, and troubleshooting.

## Issues

Report problems on the
[issue tracker](https://github.com/acdcnow/Danfoss-ECL-310-for-Home-Assistant/issues) with debug
logging enabled:

```yaml
logger:
  default: info
  logs:
    custom_components.danfoss_ecl310: debug
    modbus_connection: debug
```

*Not affiliated with Danfoss. "Danfoss" and "ECL" are used only to identify the hardware this
integration controls.*
