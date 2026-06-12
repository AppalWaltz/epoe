/* ===========================================================================
 * EPOE — Empirical Policy Optimization Engine, client-side port
 * ===========================================================================
 * This is a FULL port of model/data.py and model/model.py to JavaScript so
 * the optimization runs entirely in the browser (GitHub Pages, no backend).
 *
 * NOT distilled: every empirical parameter, the complete 11-year debt
 * recursion, all utility components, the behavioral revenue functions, and
 * all five constraint families are identical to the Python engine.
 *
 * The ONLY substitution is the solver. SciPy's SLSQP is unavailable in the
 * browser, so the same smooth nonlinear program is solved with a standard
 * augmented-Lagrangian method (inequality constraints) over projected Adam
 * (box bounds), with central-difference gradients and the same multi-start
 * discipline. The repository ships a Node validation script
 * (dashboard/validate.js) comparing this port against the Python results
 * scenario-by-scenario.
 *
 * Sources and confidence tags for every number: see model/data.py and
 * docs/02_fiscal_baseline.md. Baseline: FY2026 current law, CBO Feb 2026
 * Outlook (https://www.cbo.gov/publication/62105).
 * =========================================================================*/
(function (root, factory) {
  var api = factory();
  if (typeof module === "object" && module && module.exports) module.exports = api;
  if (root) root.EPOE = api;   // always attach: shields against injected module shims
}(typeof self !== "undefined" ? self : (typeof window !== "undefined" ? window : this), function () {
"use strict";

/* ------------------------------------------------------------------ DATA */
const GDP_2026 = 31800.0;          // $B. HIGH (CBO)
const OUTLAYS_2026 = 7400.0;       // $B. HIGH (CBO)
const REVENUES_2026 = 5600.0;      // $B. HIGH (CBO)
const DEFICIT_2026 = 1800.0;       // $B. HIGH (CBO identity)
const DEBT_PUBLIC_2026 = 32100.0;  // $B, ~101% GDP end-FY2026. HIGH (CBO)
const NET_INTEREST_2026 = 1030.0;  // $B. HIGH (CBO)
const NOMINAL_GDP_GROWTH = 0.041;
const EFFECTIVE_RATE_ON_DEBT = 0.0345;
const MARGINAL_RATE_ON_NEW_DEBT = 0.043;
const HORIZON = 11;                // FY2026..FY2036

const SPENDING = {
  social_security:    { base: 1666, floor: 0.97, ceil: 1.10, conf: "HIGH",
    label: "Social Security (OASDI)",
    note: "FY25 actual $1,575B + CBO +$91B FY26 growth. OASI trust fund exhausted 2032 under current law." },
  medicare:           { base: 1063, floor: 0.95, ceil: 1.12, conf: "HIGH",
    label: "Medicare (net of premiums)",
    note: "FY25 $988B + CBO +$75B. ~50% of beneficiaries in privately administered Medicare Advantage." },
  medicaid_chip:      { base: 700,  floor: 0.93, ceil: 1.25, conf: "HIGH",
    label: "Medicaid & CHIP (federal share)",
    note: "FY25 $668B + CBO +$40B; P.L.119-21 cuts ~$1.2T/10yr already in baseline." },
  aca_other_health:   { base: 140,  floor: 0.90, ceil: 1.60, conf: "MEDIUM",
    label: "ACA subsidies & other health",
    note: "Premium tax credits & related; enhanced subsidies expired, enrollment falling in baseline." },
  income_security:    { base: 460,  floor: 0.93, ceil: 1.30, conf: "MEDIUM",
    label: "Income security (SNAP, SSI, EITC/CTC, UI)",
    note: "Split estimated from FY25 'other mandatory' $773B." },
  veterans:           { base: 420,  floor: 1.00, ceil: 1.15, conf: "MEDIUM",
    label: "Veterans (compensation + VA health)",
    note: "CBO FY26 growth +$49B. Floor = 1.0: cuts treated as infeasible." },
  fed_retirement:     { base: 190,  floor: 0.98, ceil: 1.05, conf: "MEDIUM",
    label: "Federal civilian & military retirement",
    note: "Contractual; near-zero one-cycle controllability." },
  other_mandatory:    { base: 320,  floor: 0.85, ceil: 1.20, conf: "LOW",
    label: "Other mandatory (student loans, agriculture)",
    note: "Student loans (+$89B FY26 re-estimate), deposit insurance, misc. Most volatile residual." },
  defense:            { base: 900,  floor: 0.85, ceil: 1.15, conf: "HIGH",
    label: "Defense (function 050)",
    note: "FY25 $893B + CR. ~half flows to contractors; symbiosis floor binds here." },
  intl_affairs:       { base: 55,   floor: 0.70, ceil: 1.40, conf: "MEDIUM",
    label: "International affairs",
    note: "State/USAID-successor operations, embassies, global health." },
  science_space:      { base: 80,   floor: 0.80, ceil: 1.50, conf: "MEDIUM",
    label: "Science & space (NSF, NASA, DOE-Science)",
    note: "Highest long-run growth spillovers per dollar in the literature." },
  health_research_ph: { base: 95,   floor: 0.80, ceil: 1.60, conf: "MEDIUM",
    label: "Health research & public health (NIH, CDC, FDA)",
    note: "Public-health infrastructure case-study lever." },
  education_training: { base: 115,  floor: 0.80, ceil: 1.50, conf: "MEDIUM",
    label: "Education & training",
    note: "Title I, IDEA, Pell (discretionary portion), workforce training." },
  transportation:     { base: 130,  floor: 0.85, ceil: 1.40, conf: "MEDIUM",
    label: "Transportation",
    note: "Highways, transit, aviation, rail (incl. IIJA tail)." },
  environment_energy: { base: 65,   floor: 0.75, ceil: 1.50, conf: "MEDIUM",
    label: "Environment & energy",
    note: "EPA, Interior operations, DOE energy programs." },
  housing_community:  { base: 90,   floor: 0.80, ceil: 1.45, conf: "MEDIUM",
    label: "Housing & community development",
    note: "HUD (Section 8, public housing), CDBG, rural development." },
  justice_homeland:   { base: 105,  floor: 0.85, ceil: 1.30, conf: "MEDIUM",
    label: "Justice & homeland security",
    note: "DOJ, federal courts, CBP/ICE (enforcement elevated in baseline)." },
  general_gov_other:  { base: 165,  floor: 0.80, ceil: 1.20, conf: "LOW",
    label: "General government & other",
    note: "Treasury/IRS ops, GSA, Congress, residual NDD. Absorbs disaggregation error." },
};
const OFFSETTING_RECEIPTS = -389.0;

const REVENUE_BASE = {
  individual_income: 2800, payroll: 1800, corporate_income: 480, customs: 330,
  excise: 100, estate_gift: 35, fed_remittances: 5, misc_fees: 50,
};

const MULT_SPEND = {
  social_security: 0.85, medicare: 0.80, medicaid_chip: 0.95,
  aca_other_health: 0.90, income_security: 1.20, veterans: 0.90,
  fed_retirement: 0.70, other_mandatory: 0.70, defense: 0.70,
  intl_affairs: 0.40, science_space: 0.60, health_research_ph: 0.70,
  education_training: 0.80, transportation: 0.90, environment_energy: 0.70,
  housing_community: 0.95, justice_homeland: 0.70, general_gov_other: 0.60,
};
const SUPPLY_GROWTH = {
  science_space: 0.00030, health_research_ph: 0.00020,
  education_training: 0.00020, transportation: 0.00020,
  environment_energy: 0.00008, housing_community: 0.00005,
};
const MULT_TAX = [-0.50, -0.35, -0.20, -0.30, -0.90, -0.60]; // ind, corp, cap, pcap, vat, carbon

const TAX_INSTRUMENTS = {
  d_ind:       { lo: -2.0, hi: 1.5,  base_per_point: 300.0, eti: 0.25,
                 label: "Individual income — Δ effective rate", unit: "pts" },
  d_corp:      { lo: -5.0, hi: 7.0,  base_per_point: 23.0, erosion_per_point: 0.012,
                 label: "Corporate income — Δ statutory rate", unit: "pts (21% baseline)" },
  d_cap:       { lo: 0.0,  hi: 1.0,  max_revenue: 120.0,
                 label: "Capital-income reform package", unit: "fraction adopted" },
  payroll_cap: { lo: 0.0,  hi: 1.0,  max_revenue: 180.0,
                 label: "Lift OASDI payroll taxable maximum", unit: "fraction adopted" },
  vat:         { lo: 0.0,  hi: 10.0, base: 12700.0, erosion: 0.15,
                 label: "Value-added tax", unit: "% rate" },
  carbon:      { lo: 0.0,  hi: 80.0, tons: 4.0, decay: 0.006,
                 label: "Carbon price", unit: "$/tCO2e" },
};

const THETA_HEALTH = { medicare: 0.8, medicaid_chip: 1.3, aca_other_health: 1.2,
  health_research_ph: 1.5, veterans: 0.6, income_security: 0.5,
  housing_community: 0.4, environment_energy: 0.3 };
const THETA_EQUITY = { income_security: 1.5, medicaid_chip: 1.2, aca_other_health: 1.0,
  education_training: 1.1, housing_community: 1.1, social_security: 0.8, veterans: 0.5 };
const THETA_SECURITY = { defense: 1.0, veterans: 0.4, justice_homeland: 0.5, intl_affairs: 0.6 };
const TAX_EQUITY = { d_ind: 0.3, d_corp: 0.5, d_cap: 1.2, payroll_cap: 1.0, vat: -0.8, carbon: -0.3 };

const SYMBIOSIS = { defense_floor_gdp: 0.025, health_private_admin_floor: 0.90,
  max_total_reallocation: 0.12 };

const CATS = Object.keys(SPENDING);
const NC = CATS.length;
const TAXES = ["d_ind", "d_corp", "d_cap", "payroll_cap", "vat", "carbon"];
const NT = TAXES.length;
const BASE = CATS.map(c => SPENDING[c].base);
const BASE_SUM = BASE.reduce((a, b) => a + b, 0);
const BASE_REV_TOTAL = Object.values(REVENUE_BASE).reduce((a, b) => a + b, 0);
const MEB = [0.35, 0.30, 0.15, 0.25, 0.20, 0.05];
const RANGES = TAXES.map(k => Math.max(Math.abs(TAX_INSTRUMENTS[k].lo),
                                       Math.abs(TAX_INSTRUMENTS[k].hi), 1e-9));

/* ------------------------------------------------------------- ENGINE */
// Net NEW revenue ($B/yr) per instrument, with behavioral erosion (1:1 port).
function taxRevenueDelta(tz) {
  const [d_ind, d_corp, d_cap, pcap, vat, carbon] = tz;
  const T = TAX_INSTRUMENTS;
  const r = new Array(NT).fill(0);
  r[0] = T.d_ind.base_per_point * d_ind * (1 - T.d_ind.eti * Math.abs(d_ind) / 10.0);
  const staticC = T.d_corp.base_per_point * d_corp;
  const erosion = REVENUE_BASE.corporate_income * T.d_corp.erosion_per_point *
                  d_corp * (1 + 0.04 * Math.max(d_corp, 0.0));
  r[1] = staticC - erosion;
  r[2] = T.d_cap.max_revenue * d_cap;
  r[3] = T.payroll_cap.max_revenue * pcap;
  r[4] = T.vat.base * (vat / 100.0) * (1 - T.vat.erosion);
  r[5] = T.carbon.tons * carbon * (1 - T.carbon.decay * carbon);
  return r;
}

// Year-1 endogenous quantities: GDP, outlays, revenues, deficit (1:1 port).
function macro(z) {
  const spend = new Array(NC);
  let dY_spend = 0, spendSum = 0;
  for (let i = 0; i < NC; i++) {
    spend[i] = BASE[i] * (1 + z[i]);
    spendSum += spend[i];
    dY_spend += MULT_SPEND[CATS[i]] * (spend[i] - BASE[i]);
  }
  const tz = z.slice(NC);
  const revVec = taxRevenueDelta(tz);
  let revDelta = 0, dY_tax = 0;
  for (let k = 0; k < NT; k++) { revDelta += revVec[k]; dY_tax += MULT_TAX[k] * revVec[k]; }
  const Y = GDP_2026 + dY_spend + dY_tax;
  const revenues = BASE_REV_TOTAL + revDelta + 0.175 * (Y - GDP_2026);
  const progOutlays = spendSum + OFFSETTING_RECEIPTS;
  const outlays = progOutlays + NET_INTEREST_2026;
  return { Y, spend, revenues, outlays, deficit: outlays - revenues,
           revVec, progOutlays };
}

// 11-year debt dynamics, identical recursion to Python (validates to CBO path).
function debtPath(z, m) {
  if (!m) m = macro(z);
  let gExtra = 0;
  for (let i = 0; i < NC; i++) {
    const sg = SUPPLY_GROWTH[CATS[i]];
    if (sg) gExtra += sg * (BASE[i] * z[i]) / 100.0;
  }
  const g = NOMINAL_GDP_GROWTH + gExtra;
  let Y = GDP_2026 * (1 + (m.Y / GDP_2026 - 1));
  let debt = DEBT_PUBLIC_2026 - DEFICIT_2026 + m.deficit;
  const primary0 = m.progOutlays - m.revenues;
  const ratios = [];
  let rEff = EFFECTIVE_RATE_ON_DEBT;
  for (let t = 0; t < HORIZON; t++) {
    ratios.push(debt / Y);
    const primary = primary0 * Math.pow(1 + g, t);
    debt = debt + primary + rEff * debt;
    Y = Y * (1 + g);
    rEff = rEff + (MARGINAL_RATE_ON_NEW_DEBT - rEff) * 0.12;
  }
  return { ratios, g };
}

// Utility components in the common unit 1.0 == $100B of social value (1:1 port).
function utilities(z, m) {
  const block = (theta) => {
    let u = 0;
    for (let i = 0; i < NC; i++) {
      const w = theta[CATS[i]];
      if (w) u += w * (BASE[i] / 100.0) * Math.log1p(z[i]);
    }
    return u;
  };
  let U_health = block(THETA_HEALTH);
  let U_equity = block(THETA_EQUITY);
  const U_security = block(THETA_SECURITY);
  for (let k = 0; k < NT; k++) U_equity += TAX_EQUITY[TAXES[k]] * m.revVec[k] / 100.0;

  let gExtra = 0;
  for (let i = 0; i < NC; i++) {
    const sg = SUPPLY_GROWTH[CATS[i]];
    if (sg) gExtra += sg * (BASE[i] * z[i]) / 100.0;
  }
  const U_growth = (m.Y - GDP_2026) / 100.0 + 25.0 * gExtra * GDP_2026 / 100.0;

  const carbon = z[NC + 5];
  const Tc = TAX_INSTRUMENTS.carbon;
  U_health += 50.0 * (Tc.tons * Tc.decay * carbon) / 100.0;  // avoided damages credit

  let dst = 0, quad = 0;
  for (let k = 0; k < NT; k++) {
    dst += MEB[k] * m.revVec[k];
    const q = z[NC + k] / RANGES[k];
    quad += q * q;
  }
  const distortion = dst / 100.0 + 0.30 * quad;
  return { U_growth, U_health, U_equity, U_security, distortion };
}

function welfare(z, alphas) {
  const m = macro(z);
  const u = utilities(z, m);
  const { ratios } = debtPath(z, m);
  const over = ratios[ratios.length - 1] - ratios[0];
  const B = Math.log1p(Math.exp(8.0 * over)) / 8.0 * 10.0;  // softplus debt penalty
  const W = alphas.growth * u.U_growth + alphas.health * u.U_health +
            alphas.equity * u.U_equity + alphas.security * u.U_security -
            alphas.distortion * u.distortion - alphas.debt * B;
  return { W, m, u, ratios, B };
}

/* -------------------------------------------------------- CONSTRAINTS */
// Inequality constraints c_j(z) >= 0, scaled to ~unit magnitude for the
// solver; rawScale converts back to native units ($B or ratio) so the
// feasibility-acceptance criterion matches the Python engine exactly.
function buildConstraints(scenario) {
  // Each constraint takes (z, m, ratios) where m = macro(z) and ratios =
  // debtPath ratios, computed ONCE per evaluation by the solver.
  const cons = [];
  if (scenario.deficit_cap_gdp != null) {
    const cap = scenario.deficit_cap_gdp;
    cons.push({ name: "deficit_cap", rawScale: 100, needs: "m",
      fun: (z, m) => (cap * GDP_2026 - m.deficit) / 100.0 });
  }
  if (scenario.debt_cap_2036 != null) {
    const cap = scenario.debt_cap_2036;
    cons.push({ name: "debt_cap_2036", rawScale: 0.1, needs: "ratios",
      fun: (z, m, ratios) => (cap - ratios[ratios.length - 1]) * 10.0 });
  }
  const iDef = CATS.indexOf("defense");
  cons.push({ name: "defense_floor", rawScale: 100, needs: "m",
    fun: (z, m) => (BASE[iDef] * (1 + z[iDef]) - SYMBIOSIS.defense_floor_gdp * m.Y) / 100.0 });
  const iMc = CATS.indexOf("medicare"), iMd = CATS.indexOf("medicaid_chip");
  const fl = SYMBIOSIS.health_private_admin_floor;
  cons.push({ name: "health_admin_floor", rawScale: 100, needs: null,
    fun: (z) => ((BASE[iMc] * (1 + z[iMc]) + BASE[iMd] * (1 + z[iMd]))
               - fl * (BASE[iMc] + BASE[iMd])) / 100.0 });
  const capRe = SYMBIOSIS.max_total_reallocation * BASE_SUM;
  cons.push({ name: "reallocation_cap", rawScale: 100, needs: null,
    fun: (z) => { let s = 0;
      for (let i = 0; i < NC; i++) { const u = BASE[i] * z[i]; s += Math.sqrt(u * u + 1e-4); }
      return (capRe - s) / 100.0; } });
  return cons;
}

function buildBounds(scenario) {
  const lo = new Array(NC + NT), hi = new Array(NC + NT);
  const tighten = scenario.feasibility_tighten != null ? scenario.feasibility_tighten : 1.0;
  for (let i = 0; i < NC; i++) {
    const s = SPENDING[CATS[i]];
    lo[i] = (s.floor - 1.0) * tighten;
    hi[i] = (s.ceil - 1.0) * tighten;
  }
  const banned = scenario.ban_instruments || [];
  const overrides = scenario.instrument_overrides || {};
  for (let k = 0; k < NT; k++) {
    const key = TAXES[k], t = TAX_INSTRUMENTS[key];
    let l = t.lo, h = t.hi;
    if (banned.includes(key)) { l = 0; h = 0; }
    if (overrides[key]) { l = overrides[key][0]; h = overrides[key][1]; }
    lo[NC + k] = l; hi[NC + k] = h;
  }
  return { lo, hi };
}

// Worst violation EXCESS beyond the per-constraint native-unit tolerance
// (matches the Python engine's acceptance convention: viol < 1.0 native unit).
function violationExcess(z, cons) {
  const m = macro(z);
  const ratios = debtPath(z, m).ratios;
  let v = 0;
  for (const c of cons) v = Math.max(v, -c.fun(z, m, ratios) * c.rawScale - 0.9);
  return Math.max(0, v);
}

function maxViolationRaw(z, cons) {
  const m = macro(z);
  const ratios = debtPath(z, m).ratios;
  let v = 0;
  for (const c of cons) v = Math.max(v, -c.fun(z, m, ratios) * c.rawScale);
  return v;  // native units: $B for fiscal constraints, ratio for debt cap
}

/* ------------------------------------------------------------- SOLVER */
// Mulberry32 PRNG — deterministic multi-starts, like the Python seed.
function rng(seed) {
  let a = seed >>> 0;
  return function () {
    a |= 0; a = (a + 0x6D2B79F5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

// Shared evaluation: compute macro + debt path ONCE, then objective and all
// constraint values from the shared parts (3-4x faster than naive evaluation).
function makeEvaluator(alphas, cons) {
  return function (z) {
    const m = macro(z);
    const u = utilities(z, m);
    const ratios = debtPath(z, m).ratios;
    const over = ratios[ratios.length - 1] - ratios[0];
    const B = Math.log1p(Math.exp(8.0 * over)) / 8.0 * 10.0;
    const f = -(alphas.growth * u.U_growth + alphas.health * u.U_health +
                alphas.equity * u.U_equity + alphas.security * u.U_security -
                alphas.distortion * u.distortion - alphas.debt * B);
    const c = new Array(cons.length);
    for (let j = 0; j < cons.length; j++) c[j] = cons[j].fun(z, m, ratios);
    return { f, c };
  };
}

// Augmented Lagrangian for inequality constraints over projected Adam.
//   minimize f(z) = -W(z)   s.t.  c_j(z) >= 0,  lo <= z <= hi
//   L(z) = f(z) + sum_j ( max(0, lam_j - mu*c_j)^2 - lam_j^2 ) / (2*mu)
function solveOne(z0, alphas, cons, lo, hi, opts) {
  const n = z0.length;
  const o = Object.assign({ outer: 9, inner: 260, lr: 0.02, mu0: 2.0,
                            muGrow: 2.6, h: 1e-5 }, opts || {});
  const evaluate = makeEvaluator(alphas, cons);
  let lam = new Array(cons.length).fill(0);
  let mu = o.mu0;
  const z = z0.slice();
  const clip = () => { for (let i = 0; i < n; i++) z[i] = Math.min(hi[i], Math.max(lo[i], z[i])); };
  clip();

  const L = (zz) => {
    const e = evaluate(zz);
    let v = e.f;
    for (let j = 0; j < cons.length; j++) {
      const t = Math.max(0, lam[j] - mu * e.c[j]);
      v += (t * t - lam[j] * lam[j]) / (2 * mu);
    }
    return v;
  };
  const descend = (fn, iters, lr0, tBase) => {
    const mAd = new Array(n).fill(0), vAd = new Array(n).fill(0);
    const b1 = 0.9, b2 = 0.999, eps = 1e-8;
    const zp = new Array(n);
    for (let it = 0; it < iters; it++) {
      for (let i = 0; i < n; i++) zp[i] = z[i];
      const grad = new Array(n);
      for (let i = 0; i < n; i++) {
        if (hi[i] - lo[i] < 1e-12) { grad[i] = 0; continue; }   // pinned dim
        const hh = o.h * Math.max(1, Math.abs(z[i]));
        const a = Math.min(hi[i], z[i] + hh), b = Math.max(lo[i], z[i] - hh);
        zp[i] = a; const fa = fn(zp);
        zp[i] = b; const fb = fn(zp);
        zp[i] = z[i];
        grad[i] = (fa - fb) / (a - b || 1e-12);
      }
      const lr = lr0 / (1 + 0.004 * (tBase + it));
      for (let i = 0; i < n; i++) {
        mAd[i] = b1 * mAd[i] + (1 - b1) * grad[i];
        vAd[i] = b2 * vAd[i] + (1 - b2) * grad[i] * grad[i];
        const mh = mAd[i] / (1 - Math.pow(b1, tBase + it + 1));
        const vh = vAd[i] / (1 - Math.pow(b2, tBase + it + 1));
        z[i] -= lr * mh / (Math.sqrt(vh) + eps);
      }
      clip();
    }
  };

  for (let outer = 0; outer < o.outer; outer++) {
    descend(L, o.inner, o.lr, outer * o.inner);
    const e = evaluate(z);
    for (let j = 0; j < cons.length; j++)
      lam[j] = Math.max(0, lam[j] - mu * e.c[j]);
    mu *= o.muGrow;
  }
  // feasibility polish: if any constraint remains violated beyond numerical
  // noise, descend on squared violation alone (W is locally flat near the
  // active surface, so this costs little welfare and restores feasibility).
  // Feasibility polish: minimal-norm Newton projection onto each violated
  // constraint surface (z += grad * excess / |grad|^2). Unlike a descent on
  // total violation, this touches ONLY the dimensions the constraint actually
  // depends on, so the welfare-optimal interior structure is preserved.
  for (let it = 0; it < 60; it++) {
    const m0 = macro(z), rat0 = debtPath(z, m0).ratios;
    let worst = -1, excess = 0;
    for (let j = 0; j < cons.length; j++) {
      const raw = -cons[j].fun(z, m0, rat0) * cons[j].rawScale - 0.85;
      if (raw > excess) { excess = raw; worst = j; }
    }
    if (worst < 0) break;
    const cj = cons[worst];
    const grad = new Array(n).fill(0);
    let g2 = 0;
    const zp = z.slice();
    for (let i = 0; i < n; i++) {
      if (hi[i] - lo[i] < 1e-12) continue;
      const hh = 1e-5 * Math.max(1, Math.abs(z[i]));
      zp[i] = z[i] + hh;
      const mp = macro(zp), rp = cj.needs === "ratios" ? debtPath(zp, mp).ratios : rat0;
      const ca = cj.fun(zp, mp, rp) * cj.rawScale;
      zp[i] = z[i];
      const c0 = cj.fun(z, m0, rat0) * cj.rawScale;
      grad[i] = (ca - c0) / hh;
      g2 += grad[i] * grad[i];
    }
    if (g2 < 1e-12) break;
    const step = (excess + 0.05) / g2;
    for (let i = 0; i < n; i++) z[i] += step * grad[i];
    clip();
  }
  return z;
}

/**
 * solveAsync(scenario, [opts]) — identical to solve(), but yields to the
 * event loop between multi-starts so a browser UI can show progress.
 */
async function solveAsync(scenario, opts) {
  opts = opts || {};
  const cons = buildConstraints(scenario);
  const { lo, hi } = buildBounds(scenario);
  const n = NC + NT;
  const rand = rng(7);
  const starts = [new Array(n).fill(0)];
  const nStarts = opts.starts != null ? opts.starts : 5;
  for (let s = 1; s < nStarts; s++) {
    const z = new Array(n);
    for (let i = 0; i < n; i++) z[i] = lo[i] + (hi[i] - lo[i]) * (0.25 + 0.5 * rand());
    starts.push(z);
  }
  let best = null;
  for (let s = 0; s < starts.length; s++) {
    if (opts.onProgress) opts.onProgress(s / starts.length, s + 1, starts.length);
    await new Promise(res => setTimeout(res, 12));   // let the UI paint
    const z = solveOne(starts[s], scenario.alphas, cons, lo, hi, opts.solver);
    const viol = maxViolationRaw(z, cons);
    const W = welfare(z, scenario.alphas).W;
    const feasible = viol < 1.0;
    if (feasible) {
      if (best === null || !best.feasible || W > best.W) best = { z, W, viol, feasible };
    } else if (best === null || (!best.feasible && viol < best.viol)) {
      best = { z, W, viol, feasible };
    }
  }
  if (opts.onProgress) opts.onProgress(1, starts.length, starts.length);
  return report(best.z, scenario, best.viol);
}

/**
 * solve(scenario, [opts]) — multi-start augmented-Lagrangian solve.
 * scenario: { alphas:{growth,health,equity,security,distortion,debt},
 *             deficit_cap_gdp, debt_cap_2036, ban_instruments,
 *             instrument_overrides, feasibility_tighten }
 * opts.onProgress(frac, label) — optional progress callback.
 * Acceptance criterion matches Python: best W with raw violation < 1.0.
 */
function solve(scenario, opts) {
  opts = opts || {};
  const cons = buildConstraints(scenario);
  const { lo, hi } = buildBounds(scenario);
  const n = NC + NT;
  const rand = rng(7);
  const starts = [new Array(n).fill(0)];
  const nStarts = opts.starts != null ? opts.starts : 5;
  for (let s = 1; s < nStarts; s++) {
    const z = new Array(n);
    for (let i = 0; i < n; i++) z[i] = lo[i] + (hi[i] - lo[i]) * (0.25 + 0.5 * rand());
    starts.push(z);
  }
  let best = null;
  for (let s = 0; s < starts.length; s++) {
    if (opts.onProgress) opts.onProgress(s / starts.length, "start " + (s + 1) + " of " + starts.length);
    const z = solveOne(starts[s], scenario.alphas, cons, lo, hi, opts.solver);
    const viol = maxViolationRaw(z, cons);
    const W = welfare(z, scenario.alphas).W;
    const feasible = viol < 1.0;   // same criterion as the Python engine
    if (feasible) {
      if (best === null || !best.feasible || W > best.W) best = { z, W, viol, feasible };
    } else if (best === null || (!best.feasible && viol < best.viol)) {
      best = { z, W, viol, feasible };
    }
  }
  if (best === null) {  // least-violating fallback (mirrors Python)
    const z = solveOne(new Array(n).fill(0), scenario.alphas, cons, lo, hi,
                       Object.assign({}, opts.solver, { outer: 10 }));
    best = { z, W: welfare(z, scenario.alphas).W, viol: maxViolationRaw(z, cons) };
  }
  if (opts.onProgress) opts.onProgress(1, "done");
  return report(best.z, scenario, best.viol);
}

function report(z, scenario, viol) {
  const m = macro(z);
  const u = utilities(z, m);
  const dp = debtPath(z, m);
  const base = debtPath(new Array(NC + NT).fill(0));
  return {
    z, scenario, maxViolation: viol != null ? viol : maxViolationRaw(z, buildConstraints(scenario)),
    macro: m, U: u, debtRatios: dp.ratios, growth: dp.g,
    baselineDebtRatios: base.ratios,
    W: welfare(z, scenario.alphas).W,
  };
}

/* ----------------------------------------------------------- PRESETS */
// The five published scenarios — exact configs from model/run_scenarios.py.
const SCENARIOS = {
  baseline: { name: "baseline", label: "CBO current-law baseline",
    alphas: { growth: 1, health: 1, equity: 1, security: 1, distortion: 1, debt: 1 },
    frozen: true },
  A_growth_capital: { name: "A_growth_capital",
    label: "A · Growth & Capital Optimization",
    alphas: { growth: 2.0, health: 0.4, equity: 0.2, security: 1.0, distortion: 2.0, debt: 1.5 },
    deficit_cap_gdp: 0.048, debt_cap_2036: 1.05,
    ban_instruments: ["vat", "carbon", "payroll_cap", "d_cap"],
    instrument_overrides: { d_ind: [-2.0, 0.0], d_corp: [-5.0, 0.0] } },
  B_social_welfare: { name: "B_social_welfare",
    label: "B · Social Welfare Maximization",
    alphas: { growth: 0.7, health: 2.0, equity: 2.0, security: 0.4, distortion: 0.5, debt: 0.8 },
    deficit_cap_gdp: 0.058, debt_cap_2036: null, ban_instruments: [] },
  C_nordic_financing: { name: "C_nordic_financing",
    label: "C · Nordic-Style Financing",
    alphas: { growth: 1.0, health: 1.8, equity: 1.5, security: 0.5, distortion: 0.8, debt: 1.2 },
    deficit_cap_gdp: 0.045, debt_cap_2036: 1.01, ban_instruments: [],
    instrument_overrides: { vat: [5.0, 10.0], d_corp: [-2.0, 1.0] } },
  D_fiscal_consolidation: { name: "D_fiscal_consolidation",
    label: "D · Deficit-First Grand Bargain",
    alphas: { growth: 1.2, health: 0.8, equity: 0.7, security: 0.8, distortion: 1.2, debt: 3.0 },
    deficit_cap_gdp: 0.040, debt_cap_2036: 0.98, ban_instruments: ["vat"],
    feasibility_tighten: 0.8 },
  E_pragmatic_pareto: { name: "E_pragmatic_pareto",
    label: "E · Pragmatic Compromise",
    alphas: { growth: 1.2, health: 1.2, equity: 1.0, security: 0.9, distortion: 1.0, debt: 1.5 },
    deficit_cap_gdp: 0.050, debt_cap_2036: 1.01, ban_instruments: ["vat"],
    feasibility_tighten: 0.6 },
};

return {
  // data layer (read-only references for the UI)
  GDP_2026, OUTLAYS_2026, REVENUES_2026, DEFICIT_2026, DEBT_PUBLIC_2026,
  NET_INTEREST_2026, OFFSETTING_RECEIPTS, HORIZON,
  SPENDING, REVENUE_BASE, TAX_INSTRUMENTS, SYMBIOSIS,
  THETA_HEALTH, THETA_EQUITY, THETA_SECURITY, TAX_EQUITY,
  CATS, TAXES, NC, NT, BASE,
  // engine
  taxRevenueDelta, macro, debtPath, utilities, welfare,
  buildConstraints, buildBounds, maxViolationRaw, violationExcess,
  solve, solveAsync, report,
  SCENARIOS,
};
}));
