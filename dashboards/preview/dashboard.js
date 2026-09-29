/* =============================================================================
   Danfoss ECL 310 - dashboard preview
   -----------------------------------------------------------------------------
   Renders the exact card tree of  dashboards/ecl310-dashboard.yaml  with a fake
   `hass` (one static snapshot of realistic values) and the real Home Assistant
   design tokens, so the layout can be reviewed without a Home Assistant server.

   What is faithful:
     * card types, names, colours, column spans, features and visibility rules
     * the plotly-graph configuration: its $fn expressions are evaluated against
       the simulated states, so the curve is drawn from the numbers in the YAML
     * the three template entities of ecl310-helpers.yaml are re-evaluated with
       their real Jinja templates whenever the states change
   What is approximated:
     * hand built stand-ins for the HA cards (tile, entities, gauge, graph)
     * the history data is generated, not recorded
   ========================================================================== */
(() => {
  "use strict";

  const MDI = window.MDI || {};
  const FALLBACK_ICON = "M12,2A10,10 0 1,0 22,12 10,10 0 0,0 12,2Z";

  /* ==========================================================================
     1. Simulated entity states
     --------------------------------------------------------------------------
     [state, { n: friendly name, u: unit, p: display precision, dc: device class,
               icon: integration icon, lc: minutes since last change }]
     ========================================================================== */
  const RAW = {
    "input_boolean.expert_mode": ["off", { n: "Heizung Expertenmodus", icon: "account-hard-hat", lc: 420 }],

    /* --- Temperaturen (Abfrage 60 s) --- */
    "sensor.ecl310_temp_outdoor_s1": ["4.3", { n: "Außentemperatur (S1)", u: "°C", p: 1, dc: "temperature", icon: "thermometer", lc: 1 }],
    "sensor.ecl310_temp_room_s2": ["47.9", { n: "Nutzwasser (S2)", u: "°C", p: 1, dc: "temperature", icon: "thermometer", lc: 2 }],
    "sensor.ecl310_temp_flow_s3": ["38.7", { n: "Vorlauf (S3)", u: "°C", p: 1, dc: "temperature", icon: "thermometer", lc: 1 }],
    "sensor.ecl310_temp_dhw_s4": ["51.6", { n: "Warmwasser (S4)", u: "°C", p: 1, dc: "temperature", icon: "thermometer", lc: 4 }],
    "sensor.ecl310_temp_s5": ["33.9", { n: "Temp: S5", u: "°C", p: 1, dc: "temperature", icon: "thermometer", lc: 3 }],
    "sensor.ecl310_temp_s6": ["29.4", { n: "Temp: S6", u: "°C", p: 1, dc: "temperature", icon: "thermometer", lc: 3 }],
    "sensor.ecl310_temp_flow_target_calc": ["40.5", { n: "Vorlauf Soll (berechnet)", u: "°C", p: 1, dc: "temperature", icon: "thermometer-auto", lc: 1 }],

    /* --- Grenzwerte --- */
    "sensor.ecl310_limit_return_day": ["25.0", { n: "Rücklaufbegrenzung Tag", u: "°C", p: 1, dc: "temperature", icon: "arrow-left-bold-outline", lc: 2880 }],
    "sensor.ecl310_limit_return_night": ["22.0", { n: "Rücklaufbegrenzung Nacht", u: "°C", p: 1, dc: "temperature", icon: "arrow-left-bold-outline", lc: 2880 }],
    "sensor.ecl310_limit_summer_cutout": ["18.0", { n: "Sommerabschaltung", u: "°C", p: 1, dc: "temperature", icon: "weather-sunny-off", lc: 2880 }],
    "sensor.ecl310_limit_frost_protection": ["5.0", { n: "Frostschutzgrenze", u: "°C", p: 1, dc: "temperature", icon: "snowflake", lc: 2880 }],
    "sensor.ecl310_limit_flow_min": ["20", { n: "Vorlauf Minimum", u: "°C", p: 0, dc: "temperature", icon: "thermometer-low", lc: 2880 }],
    "sensor.ecl310_limit_flow_max": ["65", { n: "Vorlauf Maximum", u: "°C", p: 0, dc: "temperature", icon: "thermometer-check", lc: 2880 }],
    "sensor.ecl310_limit_min_outdoor": ["-20", { n: "Außentemperatur Minimum", u: "°C", p: 0, dc: "temperature", icon: "thermometer-low", lc: 2880 }],
    "sensor.ecl310_limit_max_outdoor": ["30", { n: "Außentemperatur Maximum", u: "°C", p: 0, dc: "temperature", icon: "thermometer-check", lc: 2880 }],

    /* --- Rückmeldungen der Sollwerte --- */
    "sensor.ecl310_set_flow_target_read": ["21.0", { n: "Set: Flow Target (Read)", u: "°C", p: 1, dc: "temperature", lc: 1440 }],
    "sensor.ecl310_set_setback_target_read": ["17.0", { n: "Set: Setback Target (Read)", u: "°C", p: 1, dc: "temperature", lc: 1440 }],
    "sensor.ecl310_set_dhw_normal_read": ["52.0", { n: "Set: DHW Normal (Read)", u: "°C", p: 1, dc: "temperature", lc: 1440 }],
    "sensor.ecl310_set_dhw_setback_read": ["45.0", { n: "Set: DHW Setback (Read)", u: "°C", p: 1, dc: "temperature", lc: 1440 }],

    /* --- Betriebsarten (Übersetzungen wie in der Integration) --- */
    "sensor.ecl310_mode_heating": ["2", { n: "Mode: Heating", icon: "radiator", lc: 190 }],
    "sensor.ecl310_mode_dhw": ["1", { n: "Mode: DHW", icon: "water-boiler", lc: 240 }],
    "sensor.ecl310_mode_pump_p1": ["1", { n: "Mode: Pump P1", icon: "pump", lc: 240 }],
    "sensor.ecl310_mode_pump_p2": ["0", { n: "Mode: Pump P2", icon: "pump", lc: 4320 }],
    "sensor.ecl310_mode_pump_p3": ["0", { n: "Mode: Pump P3", icon: "pump", lc: 4320 }],
    "sensor.ecl310_mode_valve_m1_opening": ["0", { n: "Mode: Valve M1 Opening", icon: "valve-open", lc: 12 }],
    "sensor.ecl310_mode_valve_m1_closing": ["0", { n: "Mode: Valve M1 Closing", icon: "valve-closed", lc: 12 }],
    "sensor.ecl310_mode_manual_valve_m1": ["0", { n: "Mode: Manual Valve M1", icon: "cog", lc: 4320 }],
    "sensor.ecl310_mode_manual_pump_p1": ["0", { n: "Mode: Manual Pump P1", icon: "cog", lc: 4320 }],
    "sensor.ecl310_m1_movement": ["stop", { n: "M1 Movement", icon: "valve", lc: 12 }],
    "sensor.ecl310_m2_movement": ["stop", { n: "M2 Movement", icon: "valve", lc: 4320 }],
    "sensor.ecl310_m3_movement": ["stop", { n: "M3 Movement", icon: "valve", lc: 4320 }],

    /* --- Stellglieder --- */
    "number.ecl310_set_target_comfort": ["21.0", { n: "Set: Target Comfort", u: "°C", p: 1, icon: "thermometer-check", min: 10, max: 30, lc: 1440 }],
    "number.ecl310_set_target_setback": ["17.0", { n: "Set: Target Setback", u: "°C", p: 1, icon: "thermometer-low", min: 10, max: 30, lc: 1440 }],
    "number.ecl310_curve_slope": ["0.8", { n: "Curve: Slope", p: 1, icon: "chart-line", min: 0.1, max: 2.5, lc: 2880 }],
    "number.ecl310_curve_30degc": ["55", { n: "Curve: -30°C", p: 0, icon: "chart-bell-curve", min: 0, max: 90, lc: 2880 }],
    "number.ecl310_curve_15degc": ["48", { n: "Curve: -15°C", p: 0, icon: "chart-bell-curve", min: 0, max: 90, lc: 2880 }],
    "number.ecl310_curve_5degc": ["43", { n: "Curve: -5°C", p: 0, icon: "chart-bell-curve", min: 0, max: 90, lc: 2880 }],
    "number.ecl310_curve_0degc": ["40", { n: "Curve: 0°C", p: 0, icon: "chart-bell-curve", min: 0, max: 90, lc: 2880 }],
    "number.ecl310_curve_5degc_2": ["36", { n: "Curve: +5°C", p: 0, icon: "chart-bell-curve", min: 0, max: 90, lc: 2880 }],
    "number.ecl310_curve_15degc_2": ["30", { n: "Curve: +15°C", p: 0, icon: "chart-bell-curve", min: 0, max: 90, lc: 2880 }],
    "number.ecl310_interval_status": ["30", { n: "Interval: Status", p: 0, icon: "timer-refresh", min: 15, max: 600, lc: 4320 }],
    "number.ecl310_interval_temp": ["60", { n: "Interval: Temp", p: 0, icon: "timer-refresh", min: 15, max: 600, lc: 4320 }],
    "number.ecl310_interval_settings": ["600", { n: "Interval: Settings", p: 0, icon: "timer-refresh", min: 15, max: 600, lc: 4320 }],

    /* --- Geräte-Informationen --- */
    "sensor.ecl310_serialnumber": ["0192-4471", { n: "Serialnumber", icon: "barcode", lc: 4320 }],
    "sensor.ecl310_system_firmware": ["1.14", { n: "System Firmware", icon: "chip", lc: 4320 }],
    "sensor.ecl310_hardware_revision": ["Rev 3", { n: "Hardware Revision", icon: "chip", lc: 4320 }],
    "sensor.ecl310_application_key": ["ECL310-3.0", { n: "Application Key", icon: "key-variant", lc: 4320 }],
    "sensor.ecl310_modbus_addr": ["254", { n: "Modbus Addr", icon: "network", lc: 4320 }],

  };

  /* State translations of the danfoss_ecl310 integration (de.json) */
  const ENUM = {
    "sensor.ecl310_mode_heating": { 0: "Standby", 1: "Zeitplan", 2: "Komfort", 3: "Absenkung", 4: "Frostschutz", 5: "Manuell" },
    "sensor.ecl310_mode_dhw": { 0: "Standby", 1: "Zeitplan", 2: "Komfort", 3: "Absenkung", 4: "Frostschutz", 5: "Manuell" },
    "sensor.ecl310_mode_pump_p1": { 0: "Aus", 1: "Ein" },
    "sensor.ecl310_mode_pump_p2": { 0: "Aus", 1: "Ein" },
    "sensor.ecl310_mode_pump_p3": { 0: "Aus", 1: "Ein" },
    "sensor.ecl310_mode_valve_m1_opening": { 0: "Aus", 1: "Ein" },
    "sensor.ecl310_mode_valve_m1_closing": { 0: "Aus", 1: "Ein" },
    "sensor.ecl310_mode_manual_valve_m1": { 0: "Auto", 1: "Stop", 2: "Schließen", 3: "Öffnen" },
    "sensor.ecl310_mode_manual_pump_p1": { 0: "Auto", 1: "Manuell Ein", 2: "Manuell Aus" },
    "sensor.ecl310_m1_movement": { opening: "Öffnet", closing: "Schließt", stop: "Stop" },
    "sensor.ecl310_m2_movement": { opening: "Öffnet", closing: "Schließt", stop: "Stop" },
    "sensor.ecl310_m3_movement": { opening: "Öffnet", closing: "Schließt", stop: "Stop" },
  };

  const S = {};
  for (const [id, [state, a]] of Object.entries(RAW)) {
    S[id] = { entity_id: id, state, attributes: Object.assign({ friendly_name: id }, a) };
  }

  /* ==========================================================================
     2. Formatting helpers
     ========================================================================== */
  const esc = (s) =>
    String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

  const raw = (id) => (S[id] ? S[id].state : "unknown");

  function display(id) {
    const st = S[id];
    if (!st) return "unbekannt";
    if (st.state === "unavailable" || st.state === "unknown") return "Nicht verfügbar";
    const table = ENUM[id];
    if (table && table[st.state] !== undefined) return table[st.state];
    if (id.startsWith("binary_sensor")) return st.state === "on" ? "Problem" : "OK";
    const a = st.attributes;
    const n = Number(st.state);
    if (st.state !== "" && !Number.isNaN(n)) {
      const text = a.p != null ? n.toFixed(a.p) : st.state;
      return a.u ? `${text} ${a.u}` : text;
    }
    return st.state;
  }

  function relative(minutes) {
    if (minutes == null) return "";
    if (minutes < 1) return "gerade eben";
    if (minutes < 60) {
      const m = Math.round(minutes);
      return `vor ${m} Minute${m === 1 ? "" : "n"}`;
    }
    const h = Math.round(minutes / 60);
    if (h < 24) return `vor ${h} Stunde${h === 1 ? "" : "n"}`;
    const d = Math.round(h / 24);
    return `vor ${d} Tag${d === 1 ? "" : "en"}`;
  }

  const svgIcon = (name, size, color) => {
    const path = MDI[name] || FALLBACK_ICON;
    const style = color ? ` style="fill:${color}"` : "";
    return `<svg viewBox="0 0 24 24" width="${size}" height="${size}"${style} aria-hidden="true"><path d="${path}"></path></svg>`;
  };

  const UI_COLORS = new Set([
    "primary", "accent", "red", "pink", "purple", "deep-purple", "indigo", "blue", "light-blue", "cyan",
    "teal", "green", "light-green", "lime", "yellow", "amber", "orange", "deep-orange", "brown",
    "grey", "blue-grey", "black", "white",
  ]);

  const INACTIVE = ["unavailable", "unknown", "none", "", "off", "closed", "locked", "idle", "standby", "0"];

  /** Mirrors HA's stateActive(): inactive entities lose their custom colour. */
  function stateActive(id) {
    const st = S[id];
    if (!st) return false;
    if (id.startsWith("binary_sensor")) return st.state === "on";
    if (st.attributes.dc === "temperature") return !Number.isNaN(Number(st.state));
    return !INACTIVE.includes(st.state);
  }

  function entityColor(id, custom) {
    const active = stateActive(id);
    if (!active) return "var(--state-inactive-color)";
    if (custom) return UI_COLORS.has(custom) ? `var(--${custom}-color)` : custom;
    const st = S[id];
    if (st && st.attributes.dc === "temperature") return "var(--state-icon-color)";
    if (st && ENUM[id]) return "var(--state-icon-color)";
    return "var(--state-icon-color)";
  }

  /* ==========================================================================
     3. Mini Jinja (only what this dashboard uses)
     ========================================================================== */
  const num = (v, d = 0) => {
    const n = parseFloat(v);
    return Number.isNaN(n) ? Number(d) : n;
  };
  const T = {
    S: (id) => (S[id] ? S[id].state : "unknown"),          // states('x') -> raw state
    F: (id, d) => num(S[id] && S[id].state, d),             // states('x') | float(d)
    I: (id, d) => Math.trunc(num(S[id] && S[id].state, d)),
    A: (id, attr) => (S[id] ? S[id].attributes[attr] : undefined),
    HV: (id) => !!S[id] && !["unavailable", "unknown", "none", ""].includes(S[id].state),
  };
  const FILTERS = {
    float: (v, d) => num(v, d === undefined ? 0 : d),
    int: (v, d) => Math.trunc(num(v, d === undefined ? 0 : d)),
    round: (v, p) => Number(num(v).toFixed(p === undefined ? 0 : p)),
    abs: (v) => Math.abs(num(v)),
    default: (v, d) => (v === undefined || v === null || v === "" || v === "unknown" || v === "unavailable" ? d : v),
  };

  function translate(expr) {
    return String(expr)
      .replace(/states\(\s*'([^']+)'\s*\)\s*\|\s*float\(\s*(-?[\d.]*)\s*\)/g, (m, id, d) => `F(${JSON.stringify(id)},${d === "" ? 0 : d})`)
      .replace(/states\(\s*'([^']+)'\s*\)\s*\|\s*int\(\s*(-?\d*)\s*\)/g, (m, id, d) => `I(${JSON.stringify(id)},${d === "" ? 0 : d})`)
      .replace(/state_attr\(\s*'([^']+)'\s*,\s*'([^']+)'\s*\)/g, (m, id, a) => `A(${JSON.stringify(id)},${JSON.stringify(a)})`)
      .replace(/states\(\s*'([^']+)'\s*\)/g, (m, id) => `S(${JSON.stringify(id)})`)
      .replace(/has_value\(\s*'([^']+)'\s*\)/g, (m, id) => `HV(${JSON.stringify(id)})`)
      .replace(/\band\b/g, "&&")
      .replace(/\bor\b/g, "||")
      .replace(/(^|[(=<>!]\s*)not\s+/g, "$1!")
      .replace(/\bTrue\b/g, "true")
      .replace(/\bFalse\b/g, "false")
      // Jinja inline conditional:  A if C else B  ->  (C ? A : B)
      .replace(/([^;]+?)\s+if\s+([^;]+?)\s+else\s+([^;]+)/, "($2 ? $1 : $3)");
  }

  /** Evaluates a Jinja expression (with or without {{ }}) against the fake states. */
  function renderTemplate(input) {
    let expr = String(input).trim().replace(/^\{\{-?\s*/, "").replace(/\s*-?\}\}$/, "");
    const chain = translate(expr).split("|");
    let code = chain[0];
    let value;
    try {
      value = new Function("S", "F", "I", "A", "HV", `return (${code});`)(T.S, T.F, T.I, T.A, T.HV);
    } catch (err) {
      console.warn("template failed:", expr, err.message);
      return "";
    }
    for (const step of chain.slice(1)) {
      const m = step.trim().match(/^([a-z_]+)\((.*)\)$/i);
      if (!m) continue;
      const args = m[2].trim() === "" ? [] : m[2].split(",").map((x) => x.trim().replace(/^['"]|['"]$/g, ""));
      if (FILTERS[m[1]]) value = FILTERS[m[1]](value, ...args);
    }
    return value;
  }

  function conditionMet(c) {
    if (!c) return true;
    const type = c.condition || (c.entity ? "state" : null);
    switch (type) {
      case "state": {
        const st = S[c.entity] ? S[c.entity].state : "unavailable";
        return Array.isArray(c.state) ? c.state.map(String).includes(st) : String(c.state) === st;
      }
      case "numeric_state": {
        const v = num(S[c.entity] && S[c.entity].state, NaN);
        if (Number.isNaN(v)) return false;
        if (c.above !== undefined && !(v > Number(c.above))) return false;
        if (c.below !== undefined && !(v < Number(c.below))) return false;
        return true;
      }
      case "template":
        return !!renderTemplate(c.value_template);
      case "and":
        return (c.conditions || []).every(conditionMet);
      case "or":
        return (c.conditions || []).some(conditionMet);
      case "not":
        return !(c.conditions || []).every(conditionMet);
      default:
        return true;
    }
  }

  const visible = (list) => !list || list.every(conditionMet);

  /* ==========================================================================
     4. Generated history (realistic, deterministic, ends at the live value)
     ========================================================================== */
  const OUT = (h) => 4.3 + 3.8 * Math.sin((2 * Math.PI * h) / 24) + 1.0 * Math.sin((2 * Math.PI * h) / 7.5) + 0.5 * Math.sin((2 * Math.PI * h) / 3.1);
  const TGT = (h) => 40.5 - 1.7 * (OUT(h) - 4.3);
  const FLW = (h) =>
    0.78 * TGT(h) + 0.22 * TGT(h - 1.5) - 1.8 + 0.45 * Math.sin((2 * Math.PI * h) / 5.5) + 0.22 * Math.sin((2 * Math.PI * h) / 1.9);
  const DEV = (h) => FLW(h) - TGT(h);
  const DHW = (h) => 51.6 - 6.2 * ((((-h % 7) + 7) % 7) / 7);

  const GENERATORS = {
    "sensor.ecl310_temp_outdoor_s1": OUT,
    "sensor.ecl310_temp_flow_s3": FLW,
    "sensor.ecl310_temp_flow_target_calc": TGT,
    "sensor.ecl310_temp_dhw_s4": DHW,
  };

  function generic(h) {
    return 6.5 * Math.sin((2 * Math.PI * h) / 26) + 2.2 * Math.sin((2 * Math.PI * h) / 6.4) + 1.1 * Math.sin((2 * Math.PI * h) / 2.3);
  }

  /** [[hoursBeforeNow, value], ...] - always ends exactly on the current state. */
  function series(id, hours, stepMin = 15) {
    const st = S[id];
    if (!st) return [];
    const current = num(st.state, NaN);
    const base = GENERATORS[id] || generic;
    const n = Math.round((hours * 60) / stepMin);
    const pts = [];
    for (let i = n; i >= 0; i--) {
      const h = -(i * stepMin) / 60;
      const v = GENERATORS[id] ? base(h) : current + (base(h) - base(0)) * 0.06;
      pts.push([h, v]);
    }
    return pts;
  }

  const fmtNum = (v, p = 1) => Number(v).toFixed(p);

  /* ==========================================================================
     5. SVG building blocks
     ========================================================================== */
  const PALETTE = ["#4269d0", "#efb118", "#ff725c", "#6cc5b0", "#3ca951", "#ff8ab7", "#a463f2", "#97bbf5"];

  function axisTicks(min, max, step) {
    const out = [];
    for (let v = Math.ceil(min / step) * step; v <= max + 1e-9; v += step) out.push(Number(v.toFixed(6)));
    return out;
  }

  /**
   * Multi series line chart on a shared y axis (used by the history-graph card).
   * series: [{ name, color, pts: [[hours, value]] }]
   */
  function lineChart(seriesList, opts = {}) {
    const w = 1000;
    const padL = 52;
    const padR = 14;
    const padT = 10;
    const xLabels = opts.xLabels || ["-72 h", "-48 h", "-24 h", "jetzt"];
    const padB = 26;
    const h = opts.height || 240;
    const plotW = w - padL - padR;
    const plotH = h - padT - padB;

    const values = seriesList.flatMap((s) => s.pts.map((p) => p[1]));
    let yMin = Math.min(...values);
    let yMax = Math.max(...values);
    const span = Math.max(yMax - yMin, 1);
    yMin = Math.floor((yMin - span * 0.08) / 5) * 5;
    yMax = Math.ceil((yMax + span * 0.08) / 5) * 5;
    const step = (yMax - yMin) / 5 > 12 ? 20 : (yMax - yMin) / 5 > 6 ? 10 : 5;

    const hoursMin = Math.min(...seriesList.flatMap((s) => s.pts.map((p) => p[0])));
    const xPos = (hour) => padL + ((hour - hoursMin) / (0 - hoursMin)) * plotW;
    const yPos = (v) => padT + ((yMax - v) / (yMax - yMin)) * plotH;

    const parts = [];
    parts.push(`<rect x="${padL}" y="${padT}" width="${plotW}" height="${plotH}" fill="none"/>`);
    for (const tick of axisTicks(yMin, yMax, step)) {
      const y = yPos(tick);
      parts.push(
        `<line x1="${padL}" y1="${y.toFixed(1)}" x2="${w - padR}" y2="${y.toFixed(1)}" stroke="var(--divider-color)" stroke-width="1"/>`
      );
      parts.push(
        `<text x="${padL - 8}" y="${(y + 3.5).toFixed(1)}" text-anchor="end" font-size="11" fill="var(--secondary-text-color)">${tick}</text>`
      );
    }
    for (let i = 0; i < xLabels.length; i++) {
      const x = padL + (i / (xLabels.length - 1)) * plotW;
      parts.push(
        `<text x="${x.toFixed(1)}" y="${h - 8}" text-anchor="${i === 0 ? "start" : i === xLabels.length - 1 ? "end" : "middle"}" font-size="11" fill="var(--secondary-text-color)">${xLabels[i]}</text>`
      );
    }
    for (const s of seriesList) {
      const d = s.pts.map(([hh, v], i) => `${i === 0 ? "M" : "L"}${xPos(hh).toFixed(1)},${yPos(v).toFixed(1)}`).join(" ");
      parts.push(
        `<path d="${d}" fill="none" stroke="${s.color}" stroke-width="${s.width || 2}" stroke-linejoin="round" stroke-linecap="round"/>`
      );
    }
    return `<svg class="chart" viewBox="0 0 ${w} ${h}" xmlns="http://www.w3.org/2000/svg">${parts.join("")}</svg>`;
  }

  /** Sparkline for the tile trend-graph feature. */
  function sparkline(id, hours, color) {
    const pts = series(id, hours, 30);
    if (pts.length < 2) return "";
    const w = 300;
    const h = 40;
    const values = pts.map((p) => p[1]);
    const min = Math.min(...values);
    const max = Math.max(...values);
    const span = max - min || 1;
    const x = (i) => (i / (pts.length - 1)) * w;
    const y = (v) => h - 4 - ((v - min) / span) * (h - 10);
    const line = pts.map((p, i) => `${i === 0 ? "M" : "L"}${x(i).toFixed(1)},${y(p[1]).toFixed(1)}`).join(" ");
    const area = `${line} L${w},${h} L0,${h} Z`;
    const gid = `spark-${id.replace(/[^a-z0-9]/gi, "")}`;
    return `<svg viewBox="0 0 ${w} ${h}" preserveAspectRatio="none">
      <defs><linearGradient id="${gid}" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" style="stop-color:${color};stop-opacity:.35"/>
        <stop offset="100%" style="stop-color:${color};stop-opacity:0"/>
      </linearGradient></defs>
      <path d="${area}" fill="url(#${gid})"/>
      <path d="${line}" fill="none" stroke="${color}" stroke-width="2.4" stroke-linejoin="round" stroke-linecap="round"/>
    </svg>`;
  }

  /** Plotly replacement for the heating curve - driven by the plotly config itself. */
  function curveChart(cfg) {
    const w = 1000;
    const h = 420;
    const padL = 62;
    const padR = 20;
    const padT = 16;
    const padB = 118;

    const xRange = cfg.layout.xaxis.range; // [12, -32] -> left to right
    const yRange = cfg.layout.yaxis.range; // [20, 60]
    const xLeft = Number(xRange[0]);
    const xRight = Number(xRange[1]);
    const yMin = Number(yRange[0]);
    const yMax = Number(yRange[1]);
    const plotW = w - padL - padR;
    const plotH = h - padT - padB;

    const xPos = (v) => padL + ((v - xLeft) / (xRight - xLeft)) * plotW;
    const yPos = (v) => padT + ((yMax - v) / (yMax - yMin)) * plotH;

    const stateOf = (fn) => {
      const m = String(fn).match(/states\['([^']+)'\]/);
      return m ? num(S[m[1]] && S[m[1]].state, NaN) : NaN;
    };
    const list = (arr) => (arr || []).map((v) => (typeof v === "string" && v.includes("$fn") ? stateOf(v) : Number(v)));

    const parts = [];
    const series = [];

    for (const e of cfg.entities) {
      const xs = list(e.x);
      const ys = list(e.y);
      if (!xs.length || xs.length !== ys.length || xs.some(Number.isNaN) || ys.some(Number.isNaN)) continue;
      const pts = xs.map((x, i) => ({ x: xPos(x), y: yPos(ys[i]), vx: x, vy: ys[i] }));
      series.push({
        name: e.name,
        color: (e.line && e.line.color) || (e.marker && e.marker.color) || "#888",
        show: e.showlegend !== false,
        mode: e.mode || "lines",
        dash: (e.line && e.line.dash) || null,
        width: (e.line && e.line.width) || 2,
        marker: e.marker || null,
        text: e.text || null,
        textposition: e.textposition || "top center",
        textfont: e.textfont || { size: 10, color: "var(--secondary-text-color)" },
        fill: e.fill ? e.fillcolor || "rgba(0,0,0,.08)" : null,
        pts,
        smooth: e.line && e.line.shape === "spline",
      });
    }

    /* grid + axes */
    for (const tick of axisTicks(xRight, xLeft, Number(cfg.layout.xaxis.dtick || 5))) {
      const x = xPos(tick);
      parts.push(`<line x1="${x.toFixed(1)}" y1="${padT}" x2="${x.toFixed(1)}" y2="${padT + plotH}" stroke="rgba(127,127,127,0.18)" stroke-width="1"/>`);
      parts.push(`<text x="${x.toFixed(1)}" y="${padT + plotH + 20}" text-anchor="middle" font-size="12" fill="var(--secondary-text-color)">${tick}</text>`);
    }
    for (const tick of axisTicks(yMin, yMax, 10)) {
      const y = yPos(tick);
      parts.push(`<line x1="${padL}" y1="${y.toFixed(1)}" x2="${w - padR}" y2="${y.toFixed(1)}" stroke="rgba(127,127,127,0.18)" stroke-width="1"/>`);
      parts.push(`<text x="${padL - 10}" y="${(y + 4).toFixed(1)}" text-anchor="end" font-size="12" fill="var(--secondary-text-color)">${tick}</text>`);
    }
    parts.push(`<line x1="${padL}" y1="${padT + plotH}" x2="${w - padR}" y2="${padT + plotH}" stroke="var(--divider-color)" stroke-width="1"/>`);
    parts.push(`<line x1="${padL}" y1="${padT}" x2="${padL}" y2="${padT + plotH}" stroke="var(--divider-color)" stroke-width="1"/>`);
    parts.push(`<text x="${padL + plotW / 2}" y="${padT + plotH + 44}" text-anchor="middle" font-size="13" fill="var(--primary-text-color)">${esc(cfg.layout.xaxis.title.text)}</text>`);
    parts.push(
      `<text x="20" y="${padT + plotH / 2}" text-anchor="middle" font-size="13" fill="var(--primary-text-color)" transform="rotate(-90 20 ${padT + plotH / 2})">${esc(cfg.layout.yaxis.title.text)}</text>`
    );

    /* area fills first, then lines and markers */
    const smooth = (pts) => {
      if (pts.length < 3) return `M${pts.map((p) => `${p.x.toFixed(1)},${p.y.toFixed(1)}`).join(" L")}`;
      let d = `M${pts[0].x.toFixed(1)},${pts[0].y.toFixed(1)}`;
      for (let i = 0; i < pts.length - 1; i++) {
        const p0 = pts[i - 1] || pts[i];
        const p1 = pts[i];
        const p2 = pts[i + 1];
        const p3 = pts[i + 2] || pts[i + 1];
        const c1x = p1.x + (p2.x - p0.x) / 6;
        const c1y = p1.y + (p2.y - p0.y) / 6;
        const c2x = p2.x - (p3.x - p1.x) / 6;
        const c2y = p2.y - (p3.y - p1.y) / 6;
        d += ` C${c1x.toFixed(1)},${c1y.toFixed(1)} ${c2x.toFixed(1)},${c2y.toFixed(1)} ${p2.x.toFixed(1)},${p2.y.toFixed(1)}`;
      }
      return d;
    };

    let gradientDone = false;
    for (const s of series) {
      const line = smooth(s.pts);
      if (s.fill) {
        parts.push(`<path d="${line} L${s.pts[s.pts.length - 1].x.toFixed(1)},${padT + plotH} L${s.pts[0].x.toFixed(1)},${padT + plotH} Z" fill="${s.fill}"/>`);
      }
      if (s.mode.includes("lines")) {
        const dash = s.dash ? ` stroke-dasharray="${s.dash === "dot" ? "3 4" : "7 6"}"` : "";
        parts.push(`<path d="${line}" fill="none" stroke="${s.color}" stroke-width="${s.width}" stroke-linecap="round" stroke-linejoin="round"${dash}/>`);
      }
      if (s.mode.includes("markers") && s.marker) {
        const color = s.marker.color || s.color;
        for (const p of s.pts) {
          if (s.marker.symbol === "diamond") {
            const r = (s.marker.size || 10) * 0.72;
            parts.push(
              `<polygon points="${p.x.toFixed(1)},${(p.y - r).toFixed(1)} ${(p.x + r).toFixed(1)},${p.y.toFixed(1)} ${p.x.toFixed(1)},${(p.y + r).toFixed(1)} ${(p.x - r).toFixed(1)},${p.y.toFixed(1)}" fill="${color}" stroke="${(s.marker.line && s.marker.line.color) || "none"}" stroke-width="1.5"/>`
            );
          } else if (s.marker.symbol === "circle-open") {
            parts.push(`<circle cx="${p.x.toFixed(1)}" cy="${p.y.toFixed(1)}" r="${((s.marker.size || 10) * 0.5).toFixed(1)}" fill="none" stroke="${color}" stroke-width="3"/>`);
          } else {
            parts.push(`<circle cx="${p.x.toFixed(1)}" cy="${p.y.toFixed(1)}" r="${((s.marker.size || 8) * 0.5).toFixed(1)}" fill="${color}"/>`);
          }
        }
      }
      if (s.mode.includes("text") && s.text) {
        s.pts.forEach((p, i) => {
          if (s.text[i] === undefined) return;
          parts.push(
            `<text x="${p.x.toFixed(1)}" y="${(p.y - 11).toFixed(1)}" text-anchor="middle" font-size="${s.textfont.size}" fill="${s.textfont.color}">${esc(s.text[i])}</text>`
          );
        });
      }
    }

    /* legend, two rows like plotly's horizontal legend */
    const legend = series.filter((s) => s.show);
    const perRow = Math.ceil(legend.length / 2) || 1;
    legend.forEach((s, i) => {
      const row = Math.floor(i / perRow);
      const col = i % perRow;
      const x = padL + col * 210;
      const y = padT + plotH + 70 + row * 20;
      const dashed = s.dash ? `<line x1="${x}" y1="${y}" x2="${x + 18}" y2="${y}" stroke="${s.color}" stroke-width="2.5" stroke-dasharray="${s.dash === "dot" ? "3 4" : "7 6"}"/>` : "";
      parts.push(`<circle cx="${x + 9}" cy="${y}" r="5" fill="${s.color}"/>${dashed}`);
      parts.push(`<text x="${x + 26}" y="${y + 4}" font-size="12" fill="var(--secondary-text-color)">${esc(s.name)}</text>`);
    });

    return `<div class="chart-card">
      <svg class="chart" viewBox="0 0 ${w} ${h}" xmlns="http://www.w3.org/2000/svg">${parts.join("")}</svg>
    </div>`;
  }

  /** Gauge card (arc + needle + segments). */
  function gaugeSvg(cfg) {
    const min = Number(cfg.min ?? 0);
    const max = Number(cfg.max ?? 100);
    const value = Math.min(Math.max(num(S[cfg.entity] && S[cfg.entity].state, min), min), max);
    const cx = 110;
    const cy = 105;
    const r = 78;
    const stroke = 13;
    const start = 135;
    const sweep = 270;
    const angle = (v) => start + ((v - min) / (max - min)) * sweep;
    const point = (a, radius) => {
      const rad = (a * Math.PI) / 180;
      return [cx + radius * Math.cos(rad), cy + radius * Math.sin(rad)];
    };
    const arc = (from, to, radius, width, color, opacity) => {
      const [x1, y1] = point(from, radius);
      const [x2, y2] = point(to, radius);
      const large = Math.abs(to - from) > 180 ? 1 : 0;
      return `<path d="M${x1.toFixed(1)},${y1.toFixed(1)} A${radius},${radius} 0 ${large} 1 ${x2.toFixed(1)},${y2.toFixed(1)}" fill="none" stroke="${color}" stroke-width="${width}" stroke-linecap="butt"${opacity ? ` opacity="${opacity}"` : ""}/>`;
    };

    const parts = [];
    if (cfg.segments && cfg.segments.length) {
      const segs = cfg.segments.slice().sort((a, b) => a.from - b.from);
      segs.forEach((s, i) => {
        const to = i + 1 < segs.length ? segs[i + 1].from : max;
        parts.push(arc(angle(s.from), angle(to), r, stroke, s.color, 0.45));
      });
    } else {
      parts.push(arc(start, start + sweep, r, stroke, "var(--divider-color)"));
      parts.push(arc(start, angle(value), r, stroke, "var(--primary-color)"));
    }

    if (cfg.needle) {
      const [nx, ny] = point(angle(value), r - 16);
      const [bx, by] = point(angle(value) + 180, 12);
      parts.push(`<line x1="${bx.toFixed(1)}" y1="${by.toFixed(1)}" x2="${nx.toFixed(1)}" y2="${ny.toFixed(1)}" stroke="var(--primary-text-color)" stroke-width="3" stroke-linecap="round"/>`);
      parts.push(`<circle cx="${cx}" cy="${cy}" r="6" fill="var(--primary-text-color)"/>`);
    }

    const [lx, ly] = point(start + sweep + 14, r);
    const [rx, ry] = point(start - 14, r);
    parts.push(`<text x="${lx.toFixed(1)}" y="${(ly + 12).toFixed(1)}" font-size="11" fill="var(--secondary-text-color)" text-anchor="middle">${min}</text>`);
    parts.push(`<text x="${rx.toFixed(1)}" y="${(ry + 12).toFixed(1)}" font-size="11" fill="var(--secondary-text-color)" text-anchor="middle">${max}</text>`);
    parts.push(
      `<text x="${cx}" y="${cy + 46}" text-anchor="middle" font-size="30" font-weight="400" fill="var(--primary-text-color)">${esc(display(cfg.entity))}</text>`
    );
    parts.push(
      `<text x="${cx}" y="${cy + 68}" text-anchor="middle" font-size="13" fill="var(--secondary-text-color)">${esc(cfg.name || "")}</text>`
    );

    return `<div class="gauge-card"><svg viewBox="0 0 220 190" xmlns="http://www.w3.org/2000/svg">${parts.join("")}</svg></div>`;
  }

  /* ==========================================================================
     6. Card renderers
     ========================================================================== */
  function headingBadge(b) {
    if (!visible(b.visibility)) return "";
    if (b.type === "button") {
      return `<span class="h-badge">${svgIcon(b.icon, 14)}<span>${esc(b.text || "")}</span></span>`;
    }
    const id = b.entity;
    const color = b.color === "state" || !b.color ? "var(--state-icon-color)" : UI_COLORS.has(b.color) ? `var(--${b.color}-color)` : b.color;
    const name = b.show_name ? esc(b.name || (S[id] && S[id].attributes.friendly_name) || id) : "";
    const state = b.show_state ? `<span>${esc(display(id))}</span>` : "";
    return `<span class="h-badge">${svgIcon(iconFor(id, b), 14, color)}${name ? `<span>${name}</span>` : ""}${state}</span>`;
  }

  function iconFor(id, cfg = {}) {
    if (cfg.icon) return cfg.icon.replace("mdi:", "");
    const st = S[id];
    if (st && st.attributes.icon) return st.attributes.icon;
    if (st && st.attributes.dc === "temperature") return "thermometer";
    if (id && id.startsWith("binary_sensor")) return "alert-circle-outline";
    if (id && id.startsWith("number")) return "cog";
    return "information-outline";
  }

  function heading(c) {
    const style = c.heading_style || "title";
    const badges = (c.badges || []).map(headingBadge).join("");
    return `<div class="ha-card heading-card">
      <div class="heading-row">
        <div class="heading-title ${style}">
          ${c.icon ? svgIcon(c.icon.replace("mdi:", ""), 18) : ""}
          <p>${esc(c.heading || "")}</p>
        </div>
        ${badges ? `<div class="heading-badges">${badges}</div>` : ""}
      </div>
    </div>`;
  }

  function feature(f, id, color) {
    if (f.type === "bar-gauge") {
      const v = num(S[id] && S[id].state, NaN);
      const min = Number(f.min ?? 0);
      const max = Number(f.max ?? 100);
      const pct = Number.isNaN(v) ? 0 : Math.min(100, Math.max(0, ((v - min) / (max - min)) * 100));
      return `<div class="feature bar-gauge" style="--feature-color:${color}">
        <div class="fill" style="width:${pct.toFixed(1)}%"></div><div class="bg"></div>
      </div>`;
    }
    if (f.type === "trend-graph") {
      return `<div class="feature trend" style="--feature-color:${color}">${sparkline(id, f.hours_to_show || 24, color)}</div>`;
    }
    if (f.type === "numeric-input") {
      const a = S[id].attributes;
      const v = num(S[id].state, 0);
      const min = Number(f.min ?? a.min ?? 0);
      const max = Number(f.max ?? a.max ?? 100);
      const pct = ((v - min) / (max - min)) * 100;
      return `<div class="feature slider" style="--feature-color:${color}">
        <button class="np" aria-hidden="true">−</button>
        <div class="track">
          <div class="fill" style="width:${pct.toFixed(1)}%"></div>
          <div class="thumb" style="left:${pct.toFixed(1)}%"></div>
          <span class="value">${esc(display(id))}</span>
        </div>
        <button class="np" aria-hidden="true">+</button>
      </div>`;
    }
    return "";
  }

  function tile(c) {
    const id = c.entity;
    const st = S[id];
    if (!st) return "";
    const color = entityColor(id, c.color);
    const name = c.name || st.attributes.friendly_name;
    const vertical = !!c.vertical;
    const features = (c.features || []).map((f) => feature(f, id, color)).join("");
    return `<div class="ha-card tile ${vertical ? "vertical" : ""}" style="--tile-color:${color}">
      <div class="tile-content">
        <div class="tile-icon">${svgIcon(iconFor(id, c), 24, color)}</div>
        <div class="tile-info">
          <span class="tile-name">${esc(name)}</span>
          ${c.hide_state ? "" : `<span class="tile-state">${esc(display(id))}</span>`}
        </div>
      </div>
      ${features ? `<div class="tile-features">${features}</div>` : ""}
    </div>`;
  }

  function entityRow(r) {
    if (r.type === "divider") return `<div class="row-divider"></div>`;
    if (r.type === "section") return `<div class="row-section">${esc(r.label || "")}</div>`;
    const id = r.entity;
    const st = S[id];
    if (!st) return "";
    const a = st.attributes;
    const name = r.name || a.friendly_name;
    const icon = iconFor(id, r);
    const iconColor = stateActive(id) ? "var(--state-icon-color)" : "var(--state-inactive-color)";
    const secondary = r.secondary_info === "last-changed" ? relative(a.lc) : "";

    let valueHtml;
    if (id.startsWith("number")) {
      const v = num(st.state, 0);
      const min = Number(a.min ?? 0);
      const max = Number(a.max ?? 100);
      const pct = Math.min(100, Math.max(0, ((v - min) / (max - min)) * 100));
      valueHtml = `<div class="slider">
        <div class="rail"><div class="fill" style="width:${pct.toFixed(1)}%"></div><div class="thumb" style="left:${pct.toFixed(1)}%"></div></div>
        <span class="state">${esc(display(id))}</span>
      </div>`;
    } else {
      valueHtml = `<span class="state">${esc(display(id))}</span>`;
    }

    return `<div class="entity-row">
      <span class="icon">${svgIcon(icon, 24, iconColor)}</span>
      <div class="info">
        <span class="name">${esc(name)}</span>
        ${secondary ? `<span class="secondary">${esc(secondary)}</span>` : ""}
      </div>
      ${valueHtml}
    </div>`;
  }

  function entities(c) {
    return `<div class="ha-card entities-card">
      ${c.title ? `<div class="card-header">${esc(c.title)}</div>` : ""}
      ${c.entities.map(entityRow).join("")}
    </div>`;
  }

  function historyGraph(c) {
    const list = c.entities.map((e, i) => {
      const id = typeof e === "string" ? e : e.entity;
      const name = (typeof e === "object" && e.name) || (S[id] && S[id].attributes.friendly_name) || id;
      return { name, color: PALETTE[i % PALETTE.length], pts: series(id, c.hours_to_show || 24, 15) };
    });
    return `<div class="ha-card chart-card">
      ${lineChart(list, { height: 250, xLabels: [`-${c.hours_to_show} h`, `-${Math.round(c.hours_to_show / 3) * 2} h`, `-${Math.round(c.hours_to_show / 3)} h`, "jetzt"] })}
      <div class="chart-legend">
        ${list.map((s) => `<span class="item"><span class="chip" style="background:${s.color}"></span>${esc(s.name)}</span>`).join("")}
      </div>
    </div>`;
  }

  function markdownCard(c) {
    let body = String(c.content || "");
    body = body.replace(/\{\{([^}]+)\}\}/g, (m, expr) => esc(renderTemplate(expr)));
    body = body
      .replace(/&amp;nbsp;/g, "&nbsp;")
      .replace(/\*\*(.+?)\*\*/g, "<b>$1</b>")
      .replace(/\*(.+?)\*/g, "<i>$1</i>");
    const html = body
      .split(/\n{2,}/)
      .map((block) => {
        const t = block.trim();
        if (/^###\s+/.test(t)) return `<h3>${t.replace(/^###\s+/, "")}</h3>`;
        if (!t) return "";
        return `<p>${t.replace(/\n/g, " ")}</p>`;
      })
      .join("");
    return `<div class="ha-card markdown-card${c.text_only ? " text-only" : ""}">${html}</div>`;
  }

  function gridCard(c) {
    return `<div class="card-grid" style="grid-template-columns:repeat(${c.columns || 2},minmax(0,1fr))">
      ${c.cards.filter((x) => visible(x.visibility)).map(renderCard).join("")}
    </div>`;
  }

  function renderCard(c) {
    if (!c || !visible(c.visibility)) return "";
    switch (c.type) {
      case "heading": return heading(c);
      case "tile": return tile(c);
      case "entities": return entities(c);
      case "gauge": return `<div class="ha-card">${gaugeSvg(c)}</div>`;
      case "history-graph": return historyGraph(c);
      case "markdown": return markdownCard(c);
      case "conditional":
        return (c.conditions || []).every(conditionMet) ? renderCard(c.card) : "";
      case "grid": return gridCard(c);
      case "custom:plotly-graph": return `<div class="ha-card">${curveChart(c)}</div>`;
      default: return `<div class="ha-card unknown">Card type “${esc(c.type)}” is not rendered by the preview.</div>`;
    }
  }

  function badge(b) {
    if (!visible(b.visibility)) return "";
    const id = b.entity;
    const st = S[id];
    const color = b.color === "state" || !b.color ? "var(--state-icon-color)" : UI_COLORS.has(b.color) ? `var(--${b.color}-color)` : b.color;
    const showName = b.show_name !== false;
    const showState = b.show_state !== false;
    const name = b.name || (st && st.attributes.friendly_name) || id;
    return `<div class="badge">
      ${svgIcon(iconFor(id, b), 18, color)}
      ${showName ? `<span class="badge-label">${esc(name)}</span>` : ""}
      ${showState && st ? `<span class="badge-state">${esc(display(id))}</span>` : ""}
    </div>`;
  }

  /* ==========================================================================
     7. The dashboard (mirrors heizung-dashboard.yaml)
     ========================================================================== */
  const EXPERT = [{ condition: "state", entity: "input_boolean.expert_mode", state: "on" }];
  const STANDARD = [{ condition: "state", entity: "input_boolean.expert_mode", state: "off" }];

  /**
   * Copy of the custom:plotly-graph configuration in the YAML. The renderer
   * evaluates its $fn expressions against the simulated states, so the curve is
   * drawn from the six curve entities - exactly like the real card does.
   */
  const PLOTLY_CURVE = () => ({
    type: "custom:plotly-graph",
    title: "Außentemperatur → Vorlauf-Sollwert",
    refresh_interval: 30,
    hours_to_show: "current_day",
    layout: {
      height: 340,
      legend: { orientation: "h", x: 0, y: -0.2 },
      xaxis: { title: { text: "Außentemperatur in °C" }, range: [12, -32], dtick: 5 },
      yaxis: { title: { text: "Vorlauf-Soll in °C" }, range: [20, 60] },
    },
    entities: [
      {
        entity: "",
        name: "Kennlinie",
        mode: "lines+markers+text",
        text: ["-30°", "-15°", "-5°", "0°", "+5°", "+15°"],
        textposition: "top center",
        textfont: { size: 10, color: "#e74c3c" },
        line: { shape: "spline", color: "#e74c3c", width: 3 },
        marker: { size: 7, color: "#e74c3c" },
        fillcolor: "rgba(231,76,60,0.10)",
        fill: "tozeroy",
        x: ["-30", "-15", "-5", "0", "5", "15"],
        y: [
          "$fn ({ hass }) => parseFloat(hass.states['number.ecl310_curve_30degc'].state)",
          "$fn ({ hass }) => parseFloat(hass.states['number.ecl310_curve_15degc'].state)",
          "$fn ({ hass }) => parseFloat(hass.states['number.ecl310_curve_5degc'].state)",
          "$fn ({ hass }) => parseFloat(hass.states['number.ecl310_curve_0degc'].state)",
          "$fn ({ hass }) => parseFloat(hass.states['number.ecl310_curve_5degc_2'].state)",
          "$fn ({ hass }) => parseFloat(hass.states['number.ecl310_curve_15degc_2'].state)",
        ],
      },
      {
        entity: "",
        name: "Soll-Projektion",
        showlegend: false,
        mode: "lines",
        line: { color: "rgba(52,152,219,0.45)", width: 1, dash: "dash" },
        x: ["-32", "12"],
        y: [
          "$fn ({ hass }) => parseFloat(hass.states['sensor.ecl310_temp_flow_target_calc'].state)",
          "$fn ({ hass }) => parseFloat(hass.states['sensor.ecl310_temp_flow_target_calc'].state)",
        ],
      },
      {
        entity: "",
        name: "Betriebspunkt Soll",
        mode: "markers",
        marker: { size: 12, color: "#3498db", symbol: "diamond", line: { width: 1, color: "#ffffff" } },
        x: ["$fn ({ hass }) => parseFloat(hass.states['sensor.ecl310_temp_outdoor_s1'].state)"],
        y: ["$fn ({ hass }) => parseFloat(hass.states['sensor.ecl310_temp_flow_target_calc'].state)"],
      },
      {
        entity: "",
        name: "Vorlauf Ist",
        mode: "markers",
        marker: { size: 11, color: "#e67e22", symbol: "circle-open", line: { width: 3, color: "#e67e22" } },
        x: ["$fn ({ hass }) => parseFloat(hass.states['sensor.ecl310_temp_outdoor_s1'].state)"],
        y: ["$fn ({ hass }) => parseFloat(hass.states['sensor.ecl310_temp_flow_s3'].state)"],
      },
      {
        entity: "",
        name: "Regelabweichung",
        mode: "lines",
        line: { color: "#9b59b6", width: 2, dash: "dot" },
        x: [
          "$fn ({ hass }) => parseFloat(hass.states['sensor.ecl310_temp_outdoor_s1'].state)",
          "$fn ({ hass }) => parseFloat(hass.states['sensor.ecl310_temp_outdoor_s1'].state)",
        ],
        y: [
          "$fn ({ hass }) => parseFloat(hass.states['sensor.ecl310_temp_flow_target_calc'].state)",
          "$fn ({ hass }) => parseFloat(hass.states['sensor.ecl310_temp_flow_s3'].state)",
        ],
      },
    ],
  });

  const DASHBOARD = {
    title: "Heizung H.P.S.",
    subtitle: "Fussbodenheizung · Danfoss ECL 310 · Modbus TCP",
    badges: [
      { type: "entity", entity: "input_boolean.expert_mode", name: "Expert", icon: "mdi:account-hard-hat", color: "deep-purple", show_name: true, show_state: false, visibility: STANDARD },
      { type: "entity", entity: "input_boolean.expert_mode", name: "Standard", icon: "mdi:eye-outline", color: "blue", show_name: true, show_state: false, visibility: EXPERT },
      { type: "entity", entity: "sensor.ecl310_mode_heating", name: "Heizkreis", color: "green", show_name: true, show_state: true },
      { type: "entity", entity: "sensor.ecl310_temp_outdoor_s1", name: "Außen", color: "cyan", show_name: true, show_state: true },
      { type: "entity", entity: "sensor.ecl310_temp_flow_s3", name: "Vorlauf", color: "deep-orange", show_name: true, show_state: true },
      { type: "entity", entity: "sensor.ecl310_temp_dhw_s4", name: "Warmwasser", color: "red", show_name: true, show_state: true },
    ],
    sections: [
      /* ---- 1) Plant overview ---- */
      {
        column_span: 2,
        cards: [
          {
            type: "heading", heading: "Anlagenübersicht", icon: "mdi:home-thermometer",
            badges: [
              { type: "entity", entity: "sensor.ecl310_mode_heating", color: "state", show_state: true },
              { type: "entity", entity: "sensor.ecl310_mode_dhw", color: "state", show_state: true },
            ],
          },
          {
            type: "grid", columns: 2, square: false, cards: [
              { type: "tile", entity: "sensor.ecl310_temp_outdoor_s1", name: "Außen (S1)", color: "cyan", features: [{ type: "bar-gauge", min: -20, max: 40 }] },
              { type: "tile", entity: "sensor.ecl310_temp_flow_s3", name: "Vorlauf Ist (S3)", color: "deep-orange", features: [{ type: "bar-gauge", min: 0, max: 90 }] },
              { type: "tile", entity: "sensor.ecl310_temp_flow_target_calc", name: "Vorlauf Soll (berechnet)", icon: "mdi:thermostat-auto", color: "amber", features: [{ type: "bar-gauge", min: 0, max: 90 }] },
              { type: "tile", entity: "sensor.ecl310_temp_flow_s3", name: "Vorlauf-Verlauf (24 h)", icon: "mdi:chart-timeline-variant", color: "deep-orange", features: [{ type: "trend-graph", hours_to_show: 24 }] },
              { type: "tile", entity: "sensor.ecl310_temp_room_s2", name: "Nutzwasser (S2)", color: "teal", features: [{ type: "bar-gauge", min: 0, max: 90 }] },
              { type: "tile", entity: "sensor.ecl310_temp_dhw_s4", name: "Warmwasser (S4)", color: "red", features: [{ type: "bar-gauge", min: 0, max: 90 }] },
            ],
          },
        ],
      },

      /* ---- 2) Setpoints ---- */
      {
        cards: [
          { type: "heading", heading: "Sollwerte", icon: "mdi:tune-variant" },
          { type: "tile", entity: "number.ecl310_set_target_comfort", name: "Komfort", color: "orange", features: [{ type: "numeric-input", style: "slider" }] },
          { type: "tile", entity: "number.ecl310_set_target_setback", name: "Absenkung", color: "blue", features: [{ type: "numeric-input", style: "slider" }] },
        ],
      },

      /* ---- 3) Domestic hot water ---- */
      {
        cards: [
          { type: "heading", heading: "Warmwasser", icon: "mdi:water-boiler", badges: [{ type: "entity", entity: "sensor.ecl310_mode_dhw", show_state: true }] },
          {
            type: "gauge", entity: "sensor.ecl310_temp_dhw_s4", name: "Speichertemperatur (S4)", min: 0, max: 90, needle: true,
            segments: [
              { from: 0, color: "var(--disabled-text-color)" },
              { from: 45, color: "var(--info-color)" },
              { from: 55, color: "var(--success-color)" },
              { from: 70, color: "var(--warning-color)" },
            ],
          },
          {
            type: "entities", title: "Sollwerte", entities: [
              { entity: "sensor.ecl310_set_dhw_normal_read", name: "Warmwasser Normal", secondary_info: "last-changed" },
              { entity: "sensor.ecl310_set_dhw_setback_read", name: "Warmwasser Absenkung", secondary_info: "last-changed" },
            ],
          },
        ],
      },

      /* ---- 4) Operation & messages ---- */
      {
        column_span: 2,
        cards: [
          { type: "heading", heading: "Betrieb & Meldungen", icon: "mdi:bell-ring-outline" },
          { type: "tile", entity: "sensor.ecl310_mode_heating", name: "Betriebsart Heizkreis", icon: "mdi:radiator", vertical: false },
          {
            type: "conditional", conditions: [{ condition: "state", entity: "sensor.ecl310_mode_heating", state: "4" }],
            card: { type: "markdown", content: "### ❄️ Frostschutz aktiv\nDie Anlage hält nur noch die Mindesttemperatur." },
          },
          {
            type: "conditional", conditions: [{ condition: "state", entity: "sensor.ecl310_temp_outdoor_s1", state: "unavailable" }],
            card: { type: "markdown", content: "### ⚠️ Außenfühler S1 nicht verfügbar\nOhne S1 kann die Heizkurve nicht rechnen und der Regler fährt auf einen Ersatzwert." },
          },
          {
            type: "conditional", conditions: [{ condition: "state", entity: "sensor.ecl310_temp_flow_s3", state: "unavailable" }],
            card: { type: "markdown", content: "### ⚠️ Vorlauffühler S3 nicht verfügbar\nDer Vorlauf ist der wichtigste Messwert der Regelung." },
          },
          {
            type: "grid", columns: 2, square: false, cards: [
              {
                type: "entities", title: "Betriebsarten", entities: [
                  { entity: "sensor.ecl310_mode_heating", name: "Heizung" },
                  { entity: "sensor.ecl310_mode_dhw", name: "Warmwasser" },
                  { entity: "sensor.ecl310_mode_pump_p1", name: "Umwälzpumpe P1" },
                ],
              },
              {
                type: "entities", title: "Mischer M1", entities: [
                  { entity: "sensor.ecl310_m1_movement", name: "Bewegung" },
                  { entity: "sensor.ecl310_mode_valve_m1_opening", name: "Ventil öffnet" },
                  { entity: "sensor.ecl310_mode_valve_m1_closing", name: "Ventil schließt" },
                ],
              },
            ],
          },
        ],
      },

      /* ---- 5) Temperature history ---- */
      {
        column_span: 2,
        cards: [
          { type: "heading", heading: "Temperaturverlauf", icon: "mdi:chart-timeline-variant", badges: [{ type: "button", icon: "mdi:clock-outline", text: "72 Stunden" }] },
          {
            type: "history-graph", hours_to_show: 72, refresh_interval: 0, entities: [
              { entity: "sensor.ecl310_temp_outdoor_s1", name: "Außen (S1)" },
              { entity: "sensor.ecl310_temp_flow_s3", name: "Vorlauf (S3)" },
              { entity: "sensor.ecl310_temp_flow_target_calc", name: "Vorlauf Soll" },
              { entity: "sensor.ecl310_temp_dhw_s4", name: "Warmwasser (S4)" },
            ],
          },
        ],
      },

      /* ---- 6) Heating curve (expert) ---- */
      {
        column_span: 2, visibility: EXPERT,
        cards: [
          {
            type: "heading", heading: "Heizkurve", icon: "mdi:chart-bell-curve",
            badges: [
              { type: "entity", entity: "number.ecl310_curve_slope", show_state: true },
              { type: "entity", entity: "sensor.ecl310_temp_flow_target_calc", show_state: true },
            ],
          },
          PLOTLY_CURVE(),
        ],
      },

      /* ---- 7) System parameters (expert) ---- */
      {
        column_span: 2, visibility: EXPERT,
        cards: [
          { type: "heading", heading: "Systemparameter", icon: "mdi:cog-outline" },
          { type: "heading", heading: "Kennlinien-Stützpunkte", heading_style: "subtitle", icon: "mdi:chart-bell-curve-cumulative" },
          {
            type: "entities", entities: [
              { entity: "number.ecl310_curve_30degc", name: "bei −30 °C", secondary_info: "last-changed" },
              { entity: "number.ecl310_curve_15degc", name: "bei −15 °C", secondary_info: "last-changed" },
              { entity: "number.ecl310_curve_5degc", name: "bei −5 °C", secondary_info: "last-changed" },
              { entity: "number.ecl310_curve_0degc", name: "bei 0 °C", secondary_info: "last-changed" },
              { entity: "number.ecl310_curve_5degc_2", name: "bei +5 °C", secondary_info: "last-changed" },
              { entity: "number.ecl310_curve_15degc_2", name: "bei +15 °C", secondary_info: "last-changed" },
              { entity: "number.ecl310_curve_slope", name: "Steigung", secondary_info: "last-changed" },
            ],
          },
          { type: "heading", heading: "Grenzwerte", heading_style: "subtitle", icon: "mdi:speedometer-slow" },
          {
            type: "entities", entities: [
              { entity: "sensor.ecl310_limit_return_day", name: "Rücklaufbegrenzung Tag", secondary_info: "last-changed" },
              { entity: "sensor.ecl310_limit_return_night", name: "Rücklaufbegrenzung Nacht", secondary_info: "last-changed" },
              { entity: "sensor.ecl310_limit_summer_cutout", name: "Sommerabschaltung", secondary_info: "last-changed" },
              { entity: "sensor.ecl310_limit_frost_protection", name: "Frostschutzgrenze", secondary_info: "last-changed" },
              { type: "divider" },
              { entity: "sensor.ecl310_limit_flow_min", name: "Vorlauf Minimum" },
              { entity: "sensor.ecl310_limit_flow_max", name: "Vorlauf Maximum" },
              { entity: "sensor.ecl310_limit_min_outdoor", name: "Außentemperatur Minimum" },
              { entity: "sensor.ecl310_limit_max_outdoor", name: "Außentemperatur Maximum" },
            ],
          },
          { type: "heading", heading: "Ventile & Pumpen", heading_style: "subtitle", icon: "mdi:valve" },
          {
            type: "entities", entities: [
              { entity: "sensor.ecl310_mode_pump_p2", name: "Pumpe P2" },
              { entity: "sensor.ecl310_mode_pump_p3", name: "Pumpe P3" },
              { type: "divider" },
              { entity: "sensor.ecl310_m2_movement", name: "Mischer M2" },
              { entity: "sensor.ecl310_m3_movement", name: "Mischer M3" },
              { entity: "sensor.ecl310_mode_manual_valve_m1", name: "Handbetrieb Ventil M1" },
              { entity: "sensor.ecl310_mode_manual_pump_p1", name: "Handbetrieb Pumpe P1" },
            ],
          },
        ],
      },

      /* ---- 8) Maintenance & diagnostics (expert) ---- */
      {
        column_span: 4, visibility: EXPERT,
        cards: [
          { type: "heading", heading: "Wartung & Diagnose", icon: "mdi:stethoscope" },
          { type: "heading", heading: "Abfrageintervalle", heading_style: "subtitle", icon: "mdi:timer-refresh-outline" },
          {
            type: "grid", columns: 3, square: false, cards: [
              { type: "tile", entity: "number.ecl310_interval_status", name: "Status (s)", icon: "mdi:timer-refresh", features: [{ type: "numeric-input", style: "slider" }] },
              { type: "tile", entity: "number.ecl310_interval_temp", name: "Temperaturen (s)", icon: "mdi:timer-refresh", features: [{ type: "numeric-input", style: "slider" }] },
              { type: "tile", entity: "number.ecl310_interval_settings", name: "Einstellungen (s)", icon: "mdi:timer-refresh", features: [{ type: "numeric-input", style: "slider" }] },
            ],
          },
          { type: "heading", heading: "Geräte-Informationen", heading_style: "subtitle", icon: "mdi:information-outline" },
          {
            type: "entities", entities: [
              { entity: "sensor.ecl310_serialnumber", name: "Seriennummer", secondary_info: "last-changed" },
              { entity: "sensor.ecl310_system_firmware", name: "Firmware" },
              { entity: "sensor.ecl310_hardware_revision", name: "Hardware-Revision" },
              { entity: "sensor.ecl310_application_key", name: "Application Key" },
              { entity: "sensor.ecl310_modbus_addr", name: "Modbus-Adresse" },
            ],
          },
        ],
      },
    ],
  };

  /* ==========================================================================
     8. Render + wiring
     ========================================================================== */
  function render() {
    const view = document.getElementById("view");
    const sections = DASHBOARD.sections.filter((s) => visible(s.visibility));
    view.innerHTML = `
      <div class="ha-header">
        <div>
          <h1>${esc(DASHBOARD.title)}</h1>
          <div class="subtitle">${esc(DASHBOARD.subtitle)}</div>
        </div>
        <div class="ha-badges">${DASHBOARD.badges.map(badge).join("")}</div>
      </div>
      <div class="ha-container">
        ${sections
          .map(
            (s) =>
              `<div class="ha-section sp-${Math.min(s.column_span || 1, 4)}">${s.cards
                .filter((c) => visible(c.visibility))
                .map(renderCard)
                .join("")}</div>`
          )
          .join("")}
      </div>`;

    const expert = S["input_boolean.expert_mode"].state === "on";
    for (const b of document.querySelectorAll("#mode-switch button")) {
      b.classList.toggle("active", (b.dataset.mode === "on") === expert);
    }
    document.getElementById("mode-value").textContent = expert ? "on" : "off";
    document.getElementById("section-count").textContent = String(sections.length);
  }

  document.getElementById("mode-switch").addEventListener("click", (ev) => {
    const btn = ev.target.closest("button");
    if (!btn) return;
    S["input_boolean.expert_mode"].state = btn.dataset.mode;
    render();
  });

  /* Test bench: push the state set into a scenario so the conditionals can be checked */
  const PRISTINE = {};
  for (const [id, st] of Object.entries(S)) PRISTINE[id] = st.state;

  const SCENARIOS = {
    normal() {},
    fault() {
      S["sensor.ecl310_temp_flow_s3"].state = "unavailable";
    },
    summer() {
      S["sensor.ecl310_temp_outdoor_s1"].state = "21.4";
      S["sensor.ecl310_mode_heating"].state = "0";
      S["sensor.ecl310_temp_flow_target_calc"].state = "20.0";
      S["sensor.ecl310_temp_flow_s3"].state = "24.6";
    },
  };

  document.getElementById("scenario-switch").addEventListener("click", (ev) => {
    const btn = ev.target.closest("button");
    if (!btn) return;
    for (const [id, v] of Object.entries(PRISTINE)) S[id].state = v;
    (SCENARIOS[btn.dataset.scenario] || SCENARIOS.normal)();
    for (const b of document.querySelectorAll("#scenario-switch button")) {
      b.classList.toggle("active", b === btn);
    }
    render();
  });

  document.getElementById("theme-toggle").addEventListener("click", (ev) => {
    document.body.classList.toggle("dark");
    const dark = document.body.classList.contains("dark");
    ev.target.textContent = dark ? "☀︎ Light" : "☾ Dark";
  });

  render();
  document.body.dataset.ready = "true";
})();
