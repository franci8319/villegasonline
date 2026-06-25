# Calculadora Leapmotor B10 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a single-file calculator (`leapmotor-b10.html`) for the Leapmotor B10's charging time, range, and charging cost, and link it from the home page grid with the Leapmotor brand emblem.

**Architecture:** One self-contained static HTML file (HTML + `<style>` + `<script>`, no build step, no framework), following the same pattern as the existing `memory.html` app. Pure calculation functions are kept separate from DOM-wiring code so they can be verified with plain Node.js `assert` checks before being wired to inputs. A new card is added to `index.html` linking to the new file.

**Tech Stack:** Vanilla HTML/CSS/JS. No dependencies, no package.json, no test framework (none exists in this repo — verification uses Node's built-in `assert` module run ad hoc, matching the repo's zero-tooling convention).

## Global Constraints

- Spec source of truth: `docs/superpowers/specs/2026-06-25-leapmotor-b10-calculadora-design.md`.
- New page lives at repo root: `leapmotor-b10.html`.
- Default car version: 65 kWh útil / 434 km WLTP / 17,3 kWh/100km consumo WLTP / 11 kW AC / 168 kW DC. Alternate version: 55 kWh útil / 361 km WLTP / 15,2 kWh/100km consumo WLTP / 11 kW AC / 140 kW DC.
- Icon asset already exists at repo root: `leapmotor-icon.png` (white emblem, transparent background) — do not regenerate it.
- Visual style matches the rest of the site: page background `#1a4a8a`, white text, system font stack (`-apple-system, BlinkMacSystemFont, "SF Pro Text", "Helvetica Neue", Arial, sans-serif`), as used in `index.html`.
- No persistence (localStorage), no build tooling, no charging-curve modeling beyond the spec's simple >80% DC warning — these are explicitly out of scope per the spec.

---

### Task 1: Page skeleton and styling for `leapmotor-b10.html`

**Files:**
- Create: `leapmotor-b10.html`

**Interfaces:**
- Produces: DOM element IDs that Task 2/3's script will read and write:
  - Car data: `#version55`, `#version65` (radio inputs, `name="version"`), `#capInput`, `#wltpRangeInput`, `#consWltpInput`
  - Charge inputs: `#curPctInput`, `#tgtPctInput`, `#chargeTypeAC`, `#chargeTypeDC` (radio inputs, `name="chargeType"`), `#chargerKwInput`, `#priceInput`
  - Charge results: `#resEnergy`, `#resPower`, `#resTime`, `#resCost`, `#resWarning`, `#resError`
  - Autonomy inputs: `#consRealInput`
  - Autonomy results: `#rangeCurWltp`, `#rangeCurReal`, `#rangeTgtWltp`, `#rangeTgtReal`
  - Script hook: empty `<script>` tag at the end of `<body>` (Task 2/3 fill it in)

- [ ] **Step 1: Create the file**

Create `leapmotor-b10.html` with this exact content:

```html
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Leapmotor B10 — Batería y autonomía</title>
  <link rel="icon" type="image/png" href="leapmotor-icon.png" />
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    :root {
      --bg: #1a4a8a;
      --card: rgba(255,255,255,0.08);
      --field: rgba(255,255,255,0.15);
      --text: #ffffff;
      --text-sub: rgba(255,255,255,0.65);
      --accent: #f5a623;
      --warn: #ffcc66;
      --error: #ff8a80;
    }

    html, body {
      min-height: 100dvh;
      background: var(--bg);
      color: var(--text);
      font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text",
                   "Helvetica Neue", Arial, sans-serif;
      -webkit-font-smoothing: antialiased;
    }

    header {
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 32px 24px 8px;
      text-align: center;
      gap: 4px;
    }

    .back {
      align-self: flex-start;
      color: var(--text-sub);
      text-decoration: none;
      font-size: 13px;
      margin-bottom: 12px;
    }

    header h1 { font-size: 26px; font-weight: 700; }
    header .subtitle { color: var(--text-sub); font-size: 14px; }

    main {
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 24px 16px 80px;
      gap: 20px;
    }

    .card {
      background: var(--card);
      border-radius: 16px;
      padding: 20px;
      width: min(440px, 100%);
    }

    .card h2 { font-size: 16px; margin-bottom: 14px; }

    label {
      display: block;
      font-size: 12px;
      color: var(--text-sub);
      margin-bottom: 4px;
    }

    input[type="number"] {
      width: 100%;
      padding: 9px 10px;
      border: none;
      border-radius: 8px;
      background: var(--field);
      color: var(--text);
      font-size: 15px;
      margin-bottom: 14px;
    }

    input[type="number"]::placeholder { color: var(--text-sub); }

    .radio-row { display: flex; gap: 16px; margin-bottom: 14px; }
    .radio-row label {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 13px;
      color: var(--text);
      margin-bottom: 0;
    }

    .results {
      margin-top: 6px;
      padding-top: 14px;
      border-top: 1px solid rgba(255,255,255,0.15);
    }

    .result-row {
      display: flex;
      justify-content: space-between;
      font-size: 14px;
      margin-bottom: 8px;
    }

    .result-row strong { color: var(--accent); font-weight: 700; }

    .range-compare {
      display: flex;
      justify-content: space-between;
      font-size: 13px;
      margin-bottom: 10px;
    }

    .range-compare .label { color: var(--text-sub); }

    .note {
      font-size: 12px;
      margin-top: 8px;
    }

    .note.warn { color: var(--warn); }
    .note.error { color: var(--error); }
  </style>
</head>
<body>

  <header>
    <a class="back" href="/index.html">← Villegas Online</a>
    <h1>Leapmotor B10</h1>
    <p class="subtitle">Batería y autonomía</p>
  </header>

  <main>

    <section class="card" id="sec-coche">
      <h2>Datos del coche</h2>

      <div class="radio-row">
        <label><input type="radio" id="version55" name="version" value="55" /> 55 kWh</label>
        <label><input type="radio" id="version65" name="version" value="65" checked /> 65 kWh</label>
      </div>

      <label for="capInput">Capacidad útil (kWh)</label>
      <input type="number" id="capInput" min="1" step="0.1" value="65" />

      <label for="wltpRangeInput">Autonomía WLTP (km)</label>
      <input type="number" id="wltpRangeInput" min="1" step="1" value="434" />

      <label for="consWltpInput">Consumo medio WLTP (kWh/100km)</label>
      <input type="number" id="consWltpInput" min="0.1" step="0.1" value="17.3" />
    </section>

    <section class="card" id="sec-carga">
      <h2>Carga</h2>

      <label for="curPctInput">Batería actual (%)</label>
      <input type="number" id="curPctInput" min="0" max="100" step="1" value="20" />

      <label for="tgtPctInput">Batería objetivo (%)</label>
      <input type="number" id="tgtPctInput" min="0" max="100" step="1" value="80" />

      <div class="radio-row">
        <label><input type="radio" id="chargeTypeAC" name="chargeType" value="AC" checked /> AC (hasta 11 kW)</label>
        <label><input type="radio" id="chargeTypeDC" name="chargeType" value="DC" /> DC rápida</label>
      </div>

      <label for="chargerKwInput">Potencia del punto de carga (kW)</label>
      <input type="number" id="chargerKwInput" min="0" step="0.1" placeholder="ej. 7.4, 11, 50, 150..." />

      <label for="priceInput">Precio de la luz (€/kWh) — opcional</label>
      <input type="number" id="priceInput" min="0" step="0.01" placeholder="ej. 0.15" />

      <div class="results">
        <div class="result-row"><span>Energía a cargar</span><strong id="resEnergy">—</strong></div>
        <div class="result-row"><span>Potencia efectiva</span><strong id="resPower">—</strong></div>
        <div class="result-row"><span>Tiempo estimado</span><strong id="resTime">—</strong></div>
        <div class="result-row"><span>Coste de la carga</span><strong id="resCost">—</strong></div>
        <p class="note warn" id="resWarning"></p>
        <p class="note error" id="resError"></p>
      </div>
    </section>

    <section class="card" id="sec-autonomia">
      <h2>Autonomía</h2>

      <label for="consRealInput">Consumo real (kWh/100km)</label>
      <input type="number" id="consRealInput" min="0.1" step="0.1" value="17.3" />

      <div class="results">
        <div class="range-compare">
          <span class="label">Autonomía actual — WLTP</span><strong id="rangeCurWltp">—</strong>
        </div>
        <div class="range-compare">
          <span class="label">Autonomía actual — real</span><strong id="rangeCurReal">—</strong>
        </div>
        <div class="range-compare">
          <span class="label">Autonomía objetivo — WLTP</span><strong id="rangeTgtWltp">—</strong>
        </div>
        <div class="range-compare">
          <span class="label">Autonomía objetivo — real</span><strong id="rangeTgtReal">—</strong>
        </div>
      </div>
    </section>

  </main>

  <script>
  </script>

</body>
</html>
```

- [ ] **Step 2: Visually verify the skeleton**

Open `leapmotor-b10.html` directly in a browser (double-click the file, or use the `run` skill if available).

Expected: page shows a blue background, three cards ("Datos del coche", "Carga", "Autonomía") with the fields listed above, all results show `—` placeholders, and the "← Villegas Online" link is visible at the top. No calculations happen yet — that's expected, there is no script logic yet.

- [ ] **Step 3: Commit**

```bash
git add leapmotor-b10.html
git commit -m "feat: add Leapmotor B10 calculator page skeleton"
```

---

### Task 2: Pure calculation functions

**Files:**
- Modify: `leapmotor-b10.html` (fill the empty `<script>` tag from Task 1)

**Interfaces:**
- Consumes: nothing (pure functions, no DOM access)
- Produces (used by Task 3's DOM wiring):
  - `kwhToCharge(curPct, tgtPct, capacityKwh) -> number`
  - `maxChargerKw(chargeType, version) -> number`
  - `effectivePowerKw(chargerKw, chargeType, version) -> number`
  - `chargeTimeHours(energyKwh, powerKw) -> number`
  - `rangeKm(pct, capacityKwh, consumptionKwh100km) -> number`
  - `chargeCost(energyKwh, pricePerKwh) -> number`
  - `formatTime(hoursFloat) -> string`
  - `formatNumber(n, decimals) -> string`

- [ ] **Step 1: Write a temporary Node verification script (not committed)**

Create a scratch file at `C:\Users\Villegas\AppData\Local\Temp\claude\e--ANTIGRAVITY-villegasonline\7b8da8f9-ec5c-4d64-92f0-91f51c9692d0\scratchpad\leapmotor-calc-test.mjs` with this content:

```javascript
import assert from 'node:assert';

function kwhToCharge(curPct, tgtPct, capacityKwh) {
  return (tgtPct - curPct) / 100 * capacityKwh;
}

function maxChargerKw(chargeType, version) {
  if (chargeType === 'AC') return 11;
  return version === '55' ? 140 : 168;
}

function effectivePowerKw(chargerKw, chargeType, version) {
  return Math.min(chargerKw, maxChargerKw(chargeType, version));
}

function chargeTimeHours(energyKwh, powerKw) {
  return energyKwh / powerKw;
}

function rangeKm(pct, capacityKwh, consumptionKwh100km) {
  return pct / 100 * capacityKwh / consumptionKwh100km * 100;
}

function chargeCost(energyKwh, pricePerKwh) {
  return energyKwh * pricePerKwh;
}

function formatTime(hoursFloat) {
  if (!isFinite(hoursFloat) || hoursFloat <= 0) return '—';
  const totalMin = Math.round(hoursFloat * 60);
  const h = Math.floor(totalMin / 60);
  const m = totalMin % 60;
  return h > 0 ? `${h} h ${m} min` : `${m} min`;
}

// kwhToCharge
assert.strictEqual(kwhToCharge(20, 80, 65), 39);

// effectivePowerKw
assert.strictEqual(effectivePowerKw(50, 'DC', '65'), 50);
assert.strictEqual(effectivePowerKw(200, 'DC', '65'), 168);
assert.strictEqual(effectivePowerKw(200, 'DC', '55'), 140);
assert.strictEqual(effectivePowerKw(22, 'AC', '65'), 11);

// chargeTimeHours
assert.strictEqual(chargeTimeHours(39, 50), 0.78);

// rangeKm
assert.ok(Math.abs(rangeKm(80, 65, 17.3) - 300.578) < 0.01);

// chargeCost
assert.strictEqual(chargeCost(39, 0.15), 5.85);

// formatTime
assert.strictEqual(formatTime(0.78), '47 min');
assert.strictEqual(formatTime(1.25), '1 h 15 min');
assert.strictEqual(formatTime(NaN), '—');
assert.strictEqual(formatTime(Infinity), '—');
assert.strictEqual(formatTime(0), '—');

console.log('ALL CALC TESTS PASSED');
```

- [ ] **Step 2: Run it and confirm it fails first (sanity check the script runs)**

Run: `node "C:\Users\Villegas\AppData\Local\Temp\claude\e--ANTIGRAVITY-villegasonline\7b8da8f9-ec5c-4d64-92f0-91f51c9692d0\scratchpad\leapmotor-calc-test.mjs"`

Expected: `ALL CALC TESTS PASSED` (the functions above are already correct, so this should pass immediately — if any assertion throws, fix the function it tests before moving on).

- [ ] **Step 3: Add `formatNumber` and re-run**

`formatNumber` is needed for displaying kWh/km/€ with Spanish-style decimal commas, consistent with `index.html`'s use of `toLocaleString('es')`. Append to the same scratch file, above the `console.log` line:

```javascript
function formatNumber(n, decimals) {
  if (!isFinite(n)) return '—';
  return n.toLocaleString('es-ES', { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
}

assert.strictEqual(formatNumber(39, 1), '39,0');
assert.strictEqual(formatNumber(300.578, 0), '301');
assert.strictEqual(formatNumber(NaN, 1), '—');
```

Run: `node "C:\Users\Villegas\AppData\Local\Temp\claude\e--ANTIGRAVITY-villegasonline\7b8da8f9-ec5c-4d64-92f0-91f51c9692d0\scratchpad\leapmotor-calc-test.mjs"`

Expected: `ALL CALC TESTS PASSED`

- [ ] **Step 4: Paste the verified functions into `leapmotor-b10.html`**

Replace the empty `<script>\n  </script>` at the end of `<body>` with:

```html
  <script>
    // ── Pure calculation functions ──────────────────────────────────────────
    function kwhToCharge(curPct, tgtPct, capacityKwh) {
      return (tgtPct - curPct) / 100 * capacityKwh;
    }

    function maxChargerKw(chargeType, version) {
      if (chargeType === 'AC') return 11;
      return version === '55' ? 140 : 168;
    }

    function effectivePowerKw(chargerKw, chargeType, version) {
      return Math.min(chargerKw, maxChargerKw(chargeType, version));
    }

    function chargeTimeHours(energyKwh, powerKw) {
      return energyKwh / powerKw;
    }

    function rangeKm(pct, capacityKwh, consumptionKwh100km) {
      return pct / 100 * capacityKwh / consumptionKwh100km * 100;
    }

    function chargeCost(energyKwh, pricePerKwh) {
      return energyKwh * pricePerKwh;
    }

    function formatTime(hoursFloat) {
      if (!isFinite(hoursFloat) || hoursFloat <= 0) return '—';
      const totalMin = Math.round(hoursFloat * 60);
      const h = Math.floor(totalMin / 60);
      const m = totalMin % 60;
      return h > 0 ? `${h} h ${m} min` : `${m} min`;
    }

    function formatNumber(n, decimals) {
      if (!isFinite(n)) return '—';
      return n.toLocaleString('es-ES', { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
    }
  </script>
```

- [ ] **Step 5: Verify the page still loads with no console errors**

Open `leapmotor-b10.html` in a browser, open devtools console.

Expected: no errors logged, page looks identical to Task 1 (the functions are defined but nothing calls them yet).

- [ ] **Step 6: Commit**

```bash
git add leapmotor-b10.html
git commit -m "feat: add pure calculation functions for Leapmotor B10 calculator"
```

---

### Task 3: DOM wiring, live recalculation, and validations

**Files:**
- Modify: `leapmotor-b10.html` (extend the `<script>` block from Task 2)

**Interfaces:**
- Consumes: all functions produced by Task 2 (`kwhToCharge`, `effectivePowerKw`, `chargeTimeHours`, `rangeKm`, `chargeCost`, `formatTime`, `formatNumber`) and all element IDs produced by Task 1.
- Produces: a `recalculate()` function wired to every input's `input`/`change` event, run once on load.

- [ ] **Step 1: Append the DOM-wiring code**

Add this directly before the closing `</script>` tag added in Task 2:

```javascript
    // ── Version presets ──────────────────────────────────────────────────────
    const VERSIONS = {
      '55': { capacity: 55, wltpRange: 361, wltpConsumption: 15.2 },
      '65': { capacity: 65, wltpRange: 434, wltpConsumption: 17.3 },
    };

    const el = (id) => document.getElementById(id);

    function applyVersionPreset() {
      const version = el('version55').checked ? '55' : '65';
      const preset = VERSIONS[version];
      el('capInput').value = preset.capacity;
      el('wltpRangeInput').value = preset.wltpRange;
      el('consWltpInput').value = preset.wltpConsumption;
      el('consRealInput').value = preset.wltpConsumption;
    }

    function currentVersion() {
      return el('version55').checked ? '55' : '65';
    }

    function recalculate() {
      const curPct = parseFloat(el('curPctInput').value);
      const tgtPct = parseFloat(el('tgtPctInput').value);
      const capacity = parseFloat(el('capInput').value);
      const consWltp = parseFloat(el('consWltpInput').value);
      const consReal = parseFloat(el('consRealInput').value);
      const chargerKw = parseFloat(el('chargerKwInput').value);
      const price = parseFloat(el('priceInput').value);
      const chargeType = el('chargeTypeAC').checked ? 'AC' : 'DC';
      const version = currentVersion();

      // Validation: target must be greater than current
      if (!(tgtPct > curPct)) {
        el('resError').textContent = 'El objetivo debe ser mayor que el nivel actual.';
        el('resEnergy').textContent = '—';
        el('resPower').textContent = '—';
        el('resTime').textContent = '—';
        el('resCost').textContent = '—';
        el('resWarning').textContent = '';
        el('rangeCurWltp').textContent = '—';
        el('rangeCurReal').textContent = '—';
        el('rangeTgtWltp').textContent = '—';
        el('rangeTgtReal').textContent = '—';
        return;
      }
      el('resError').textContent = '';

      const energy = kwhToCharge(curPct, tgtPct, capacity);
      el('resEnergy').textContent = `${formatNumber(energy, 1)} kWh`;

      if (chargerKw > 0) {
        const power = effectivePowerKw(chargerKw, chargeType, version);
        const hours = chargeTimeHours(energy, power);
        el('resPower').textContent = `${formatNumber(power, 1)} kW`;
        el('resTime').textContent = formatTime(hours);
      } else {
        el('resPower').textContent = '—';
        el('resTime').textContent = '—';
      }

      if (price > 0) {
        el('resCost').textContent = `${formatNumber(chargeCost(energy, price), 2)} €`;
      } else {
        el('resCost').textContent = '—';
      }

      el('resWarning').textContent = (chargeType === 'DC' && tgtPct > 80)
        ? 'La carga rápida DC se ralentiza a partir del 80%, el tiempo real puede ser algo mayor.'
        : '';

      el('rangeCurWltp').textContent = `${formatNumber(rangeKm(curPct, capacity, consWltp), 0)} km`;
      el('rangeCurReal').textContent = `${formatNumber(rangeKm(curPct, capacity, consReal), 0)} km`;
      el('rangeTgtWltp').textContent = `${formatNumber(rangeKm(tgtPct, capacity, consWltp), 0)} km`;
      el('rangeTgtReal').textContent = `${formatNumber(rangeKm(tgtPct, capacity, consReal), 0)} km`;
    }

    document.querySelectorAll('#version55, #version65').forEach((radio) => {
      radio.addEventListener('change', () => { applyVersionPreset(); recalculate(); });
    });

    document.querySelectorAll(
      '#capInput, #wltpRangeInput, #consWltpInput, #curPctInput, #tgtPctInput, ' +
      '#chargerKwInput, #priceInput, #consRealInput'
    ).forEach((input) => input.addEventListener('input', recalculate));

    document.querySelectorAll('#chargeTypeAC, #chargeTypeDC').forEach((radio) => {
      radio.addEventListener('change', recalculate);
    });

    recalculate();
```

- [ ] **Step 2: Verify scenario A — default values**

Open `leapmotor-b10.html` in a browser. With the default values (65 kWh, 20% → 80%, AC, charger power empty, price empty):

Expected: "Energía a cargar" shows `39,0 kWh`, "Potencia efectiva" and "Tiempo estimado" show `—` (no charger power entered yet), "Coste de la carga" shows `—`. Autonomy rows (curPct=20%, tgtPct=80%, capacity=65 kWh, consumption=17.3 kWh/100km for both WLTP and real since they default to the same value): "Autonomía actual" shows `75 km` / `75 km`, "Autonomía objetivo" shows `301 km` / `301 km`.

- [ ] **Step 3: Verify scenario B — AC charging**

Type `7.4` into "Potencia del punto de carga".

Expected: "Potencia efectiva" shows `7,4 kW`, "Tiempo estimado" shows `5 h 16 min` (39 kWh / 7.4 kW = 5.27h).

- [ ] **Step 4: Verify scenario C — DC fast charging over 80%**

Click "DC rápida", set "Batería objetivo" to `90`, set charger power to `150`.

Expected: "Potencia efectiva" shows `150,0 kW` (under the 168 kW cap), warning note appears: "La carga rápida DC se ralentiza a partir del 80%...".

- [ ] **Step 5: Verify scenario D — invalid target**

Set "Batería objetivo" to `10` (lower than "Batería actual" = 20).

Expected: error note "El objetivo debe ser mayor que el nivel actual." appears, all result fields show `—`.

- [ ] **Step 6: Verify scenario E — version switch**

Set objetivo back to `80`, click "55 kWh" radio.

Expected: "Capacidad útil" becomes `55`, "Autonomía WLTP" becomes `361`, "Consumo medio WLTP" and "Consumo real" both become `15.2`, results recalculate automatically without needing to touch any other field.

- [ ] **Step 7: Verify scenario F — cost**

Type `0.15` into "Precio de la luz".

Expected: "Coste de la carga" shows a non-`—` euro value (energy × 0.15).

- [ ] **Step 8: Commit**

```bash
git add leapmotor-b10.html
git commit -m "feat: wire up live recalculation and validations for Leapmotor B10 calculator"
```

---

### Task 4: Add the app card to `index.html`

**Files:**
- Modify: `index.html:248` (insert before the `<!-- Nueva app aquí ↓ -->` comment)

**Interfaces:**
- Consumes: `leapmotor-icon.png` (already exists at repo root, committed in the design-spec commit).
- Produces: nothing consumed by later tasks (this is the last task).

- [ ] **Step 1: Insert the new card**

In `index.html`, find this block (around line 246-248):

```html
        <span class="app-name">Inversión</span>
      </a>

      <!-- Nueva app aquí ↓ -->
```

Replace it with:

```html
        <span class="app-name">Inversión</span>
      </a>

      <a class="app" href="/leapmotor-b10.html">
        <div class="app-icon" style="background: linear-gradient(145deg, #2b2b2b, #000000);">
          <img src="leapmotor-icon.png" alt="Leapmotor" style="width: 58%; height: 58%; object-fit: contain;" />
        </div>
        <span class="app-name">Leapmotor B10</span>
      </a>

      <!-- Nueva app aquí ↓ -->
```

Note: the `.app-icon svg { width: 52%; height: 52%; }` rule in the page's `<style>` only targets `svg` children, so it doesn't affect this `<img>` — the inline `style` on the `<img>` tag controls its size instead.

- [ ] **Step 2: Visually verify**

Open `index.html` in a browser.

Expected: a new app icon appears after "Inversión" with a black gradient background and the white Leapmotor emblem centered in it, labeled "Leapmotor B10". Clicking it navigates to `leapmotor-b10.html`.

- [ ] **Step 3: Commit**

```bash
git add index.html
git commit -m "feat: add Leapmotor B10 calculator card to home page"
```

---

## Self-Review Notes

- **Spec coverage:** version selector + presets (Task 3 Step 1 `VERSIONS`/`applyVersionPreset`), all "Carga" inputs/outputs (Task 1 fields + Task 3 `recalculate`), all "Autonomía" outputs comparing WLTP vs real (Task 3 `recalculate` range rows), cost calc (Task 3), >80% DC warning (Task 3), target≤current validation (Task 3), empty/zero charger power → `—` (Task 3), index card with brand icon (Task 4). All spec sections are covered.
- **Placeholder scan:** no TBD/TODO; all code blocks are complete and runnable as written.
- **Type consistency:** `chargeType` is always the string `'AC'` or `'DC'` across Task 2 and Task 3; `version` is always the string `'55'` or `'65'` (matches `VERSIONS` object keys and `maxChargerKw`'s second branch). Element IDs in Task 3's `el(...)` calls match exactly the IDs defined in Task 1.
