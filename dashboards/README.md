# Dashboard

A ready-to-use Lovelace dashboard for the `danfoss_ecl310` integration, built for
**Home Assistant 2026.9** (`sections` view).

Two views in one file, switched with a helper:

| | |
| --- | --- |
| **Standard view** (`input_boolean.expert_mode = off`) | live temperatures as tiles with bar gauges, setpoints with sliders, DHW gauge, operating states, conditional warnings, 72 h history |
| **Expert view** (`input_boolean.expert_mode = on`) | everything above **plus** the heating curve chart, all curve setpoints, limits, valves/pumps and maintenance/diagnostics |

![Standard view](preview/screenshot-standard.jpg)

![Expert view](preview/screenshot-expert.jpg)

## Files

| File | Purpose |
| --- | --- |
| `ecl310-dashboard.yaml` | the dashboard view - paste this into the dashboard |
| `ecl310-helpers.yaml` | Home Assistant package: `input_boolean.expert_mode` + 3 template entities the dashboard reads (`sensor.heizung_betriebsstatus`, `sensor.heizung_regelabweichung`, `binary_sensor.heizung_sensorstoerung`) |
| `preview/index.html` | offline preview of the dashboard - open it in a browser, no Home Assistant needed |
| `preview/fetch_icons.py` | regenerates `preview/icons.js` (Material Design Icons used by the preview) |
| `examples/legacy-vertical-stack-example.yaml` | the previous minimal example, kept for reference |

## Requirements

* Home Assistant **2026.9** or newer - the dashboard uses the `sections` view,
  card `grid_options`, section `visibility` and the tile features `bar-gauge`,
  `trend-graph` and `numeric-input`.
* The HACS frontend card **[plotly-graph-card](https://github.com/dbuezas/lovelace-plotly-graph-card)**
  for the expert section "Heating curve". Everything else is built-in.
* The helpers from `ecl310-helpers.yaml`.

## Install

### 0. Match the entity ids to the integration

The dashboard addresses the entities of the integration, and how those ids look depends on whether
your install is older or newer than 1.2.0:

| Your install | Entity ids look like | What to do |
| --- | --- | --- |
| **Upgraded from 1.1.x** | `sensor.ecl310_temp_flow_s3`, `number.ecl310_set_target_comfort` | Nothing - both files already match. Entity ids are stored when an entity is first registered and never change, so an upgraded install keeps the ids it had. |
| **Fresh 1.2.0 install** | `sensor.sensors_temp_flow_s3`, `number.controls_set_target_comfort` | Replace the prefix in both YAML files (table below). |

On a fresh install the entity id carries the **child device's name** (Home Assistant prefixes the
device name for entities that use it), so the prefix is the group rather than the controller:

| Device | Prefix | Entities the dashboard uses from it |
| --- | --- | --- |
| Controls | `controls_` | `set_target_comfort`, `set_target_setback`, `curve_slope` and the six `curve_*` inputs |
| Sensors | `sensors_` | temperatures, operating modes, valve travel, movement, return and summer limits |
| Pumps | `pumps_` | `mode_pump_p1..p3`, `mode_manual_pump_p1..p3` |
| Configuration | `configuration_` | `interval_status`, `interval_temp` |
| Diagnostics | `diagnostics_` | the limits, the setpoint read-backs and the system information |

Two things to keep in mind while replacing:

* Use a plain **find & replace in your editor**. PowerShell 5.1 re-encodes a file it rewrites and
  mangles the `°C` and `·` characters these files contain.
* Six entities were **renamed** in 1.2.0 as well (they moved to the *Diagnostics* device), so on a
  fresh install their suffix differs too:

  | Upgraded from 1.1.x | Fresh 1.2.0 install |
  | --- | --- |
  | `number.ecl310_interval_temp` | `number.configuration_interval_temperature` |
  | `sensor.ecl310_serialnumber` | `sensor.diagnostics_system_serial_number` |
  | `sensor.ecl310_application_key` | `sensor.diagnostics_system_application_key` |
  | `sensor.ecl310_system_firmware` | `sensor.diagnostics_system_firmware` |
  | `sensor.ecl310_hardware_revision` | `sensor.diagnostics_system_hardware_revision` |
  | `sensor.ecl310_modbus_addr` | `sensor.diagnostics_system_modbus_address` |

Every value the dashboard shows is read by the integration itself: the register map in
`custom_components/danfoss_ecl310/const.py` is the only source, and nothing beyond the three helpers
in `ecl310-helpers.yaml` has to be added on top of it.

### 1. Install the helpers

1. Copy `ecl310-helpers.yaml` to `<config>/packages/ecl310.yaml`
   (create the folder if it does not exist).
2. Enable packages once in `configuration.yaml`:

   ```yaml
   homeassistant:
     packages: !include_dir_named packages
   ```

3. Developer Tools → YAML → *Check configuration* → restart Home Assistant.

Afterwards `input_boolean.expert_mode` exists and is `off`.

### 2. Create the dashboard

**Option A - UI (recommended)**

1. Settings → Dashboards → *Add dashboard* → choose *New dashboard from scratch*
   → title e.g. `Heizung` → create.
2. Open it → pencil icon (edit) → ⋮ → **Raw configuration editor**.
3. Replace the whole content with `ecl310-dashboard.yaml` → *Save*.

**Option B - YAML mode**

1. Save the file as `<config>/lovelace/ecl310.yaml`.
2. Register the dashboard in `configuration.yaml`:

   ```yaml
   lovelace:
     dashboards:
       ecl310:
         mode: yaml
         title: Heizung
         icon: mdi:heating-coil
         show_in_sidebar: true
         filename: lovelace/ecl310.yaml
   ```

3. In YAML mode the view has to be nested, so wrap it:

   ```yaml
   views:
     - # ... content of ecl310-dashboard.yaml, starting at "type: sections"
   ```

### 3. Switch views

The badge in the header toggles `input_boolean.expert_mode`:

* **Expert** (shown while `off`) → click it to reveal the three expert sections.
* **Standard** (shown while `on`) → click it to go back.

Because the helper has no `initial:`, the last state survives a restart.

## Preview

Open `preview/index.html` in a browser. It renders the same card tree with sample
values, a Standard/Expert switch and three scenarios (*Normal*, *Sensor fault*,
*Summer*) to check the conditional warning cards. It needs no network access.

The preview is a hand-built stand-in for the real cards - it is meant for layout
review, not as a pixel-perfect copy of Lovelace.

## Customising

| Want to change | Where |
| --- | --- |
| Title, subtitle, path, icon | the top of `ecl310-dashboard.yaml` |
| Card labels (they are German) | any `name:` in the cards |
| Which temperatures are shown | swap the entities in the "Plant overview" grid |
| Move the view switch to another helper | replace `input_boolean.expert_mode` in the two badges and in the three `visibility:` blocks |
| Thresholds of the warnings (summer cutout, sensor fault) | `ecl310-helpers.yaml`, section *Derived values* |

### Notes

* The setpoints are written through the `number.*` entities of the integration (the integration has
  no climate entity).
* **No CSS is needed.** The dashboard is built from built-in cards only: there is no `card-mod`
  block, no custom theme and no extra stylesheet to install. `preview/dashboard.css` belongs to the
  preview page, not to the dashboard.
* The tile features `bar-gauge`, `trend-graph` and `numeric-input` and the section `visibility` are
  2026.9 features; on older Home Assistant the tiles fall back to plain cards without their gauges.
* The `System:` sensors are **disabled by default** by the integration. Enable them once under
  **Settings → Devices & Services → Entities** if you want the *Maintenance & diagnostics* section to
  show a serial number, firmware and so on.
