# Dashboard

A ready-to-use Lovelace dashboard for the `danfoss_ecl310` integration, built for
**Home Assistant 2026.9** (`sections` view).

Two views in one file, switched with a helper:

| | |
| --- | --- |
| **Standard view** (`input_boolean.expert_mode = off`) | live temperatures as tiles with bar gauges, setpoints with sliders, DHW gauge, operating states, conditional warnings, 72 h history |
| **Expert view** (`input_boolean.expert_mode = on`) | everything above **plus** the heating curve chart, all curve setpoints, limits, valves/pumps and maintenance/diagnostics |

![Standard view](preview/screenshot-standard.jpg)

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

### 0. Match the entity ids to your device

The entity ids in both files assume the integration was added with the device name
**`ECL310`**, which produces ids like `sensor.ecl310_temp_flow_s3`.

If your device is called differently (e.g. `ECL 1` → `sensor.ecl_1_temp_flow_s3`),
replace every `ecl310` with your own slug in both YAML files - a plain
find & replace in your editor is the safest way, because the files contain
`°C` and `·` characters that PowerShell 5.1 mangles when it re-encodes a file.

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

* The setpoints are written through the `number.*` entities of the integration.
* If you switch to the **1.2.0 development line** of this integration, a few
  diagnostic entity ids change and have to be updated in the expert sections:

  | old (`main`) | new (`dev/v1.2.0`) |
  | --- | --- |
  | `number.ecl310_interval_temp` | `number.ecl310_interval_temperature` |
  | `sensor.ecl310_serialnumber` | `sensor.ecl310_system_serial_number` |
  | `sensor.ecl310_application_key` | `sensor.ecl310_system_application_key` |
  | `sensor.ecl310_hardware_revision` | `sensor.ecl310_system_hardware_revision` |
  | `sensor.ecl310_modbus_addr` | `sensor.ecl310_system_modbus_address` |

* The three diagnostic sensors (`serialnumber`, `application_key`,
  `hardware_revision`, `modbus_addr`) are disabled by default in the integration;
  enable them in Settings → Devices & Services → the device → *Entities* if you
  want the *Maintenance & diagnostics* section to show values.
