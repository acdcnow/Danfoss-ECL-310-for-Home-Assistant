# Dashboard for application P330.7

Dashboard for an ECL 310 running **application P330.7** (master circuit + two heating
circuits with M-Bus meters). Needs the `danfoss_ecl310` integration with application
**P330.7** selected. Built from built-in Home Assistant cards plus the
[Plotly Graph Card](https://github.com/dbuezas/lovelace-plotly-graph-card) (HACS) for the heating curves.

| File | Purpose |
|---|---|
| `ecl310-p330-7-dashboard.yaml` | The dashboard, two views: **ECL 310** (circuits and meters; with the expert switch also heating curves, parameters, system) and **Hydraulik** (live hydraulic diagram) |
| `ecl310-p330-7-helpers.yaml` | `input_boolean.expert_mode` (Standard/Expert switch) and two template sensors (actual - target flow) for the Hydraulik view. If you already use `dashboards/ecl310-helpers.yaml`, remove the `input_boolean` block - both dashboards share the switch |

## Install

1. Install the **Plotly Graph Card** from HACS (Frontend).
2. Install the helpers: copy `ecl310-p330-7-helpers.yaml` to `<config>/packages/ecl310_p330_7.yaml`
   and reload template entities (or create the two template helpers in the UI, see the comments in the file).
3. Create a dashboard, open the raw configuration editor and paste `ecl310-p330-7-dashboard.yaml`.
4. The entity ids assume the device name **"ECL 1"** (`sensor.ecl_1_...`). If your device has another
   name, replace every `ecl_1` with your own slug - in both files.

## What it shows

**Standard** (`input_boolean.expert_mode` off): master circuit, both heating circuits with history, meters.
**Expert** (switch on, tap the "Expertenansicht" badge in the first section): additionally the heating-curve graphs,
all curve points, limits, influences and manual modes per circuit, and the system information.

- **Heating curves** as a graph, clipped to the minimum/maximum flow temperature like the controller does,
  with the current target (diamond) and actual flow (circle) at the current outdoor temperature.
  Below each graph: slope, current curve value, controller target and actual value.
- **Hydraulik**: pipes coloured by pump state (red flow, blue return, grey when the pump is off), valve
  arrows while a valve moves, pumps, temperatures, meters. The actual flow turns orange when it is more
  than 5 K off target.
