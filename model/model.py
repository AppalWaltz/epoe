"""
EPOE — Optimization Engine
============================================================================
Implements the nonlinear constrained program documented in
docs/03_mathematical_model.md:

  max  W(x,t) = a_g*U_growth + a_h*U_health + a_e*U_equity
                + a_s*U_security - a_d*D(t) - a_b*B(debt path)
  s.t. budget identity, debt dynamics, statutory floors/ceilings,
       symbiosis floors, reallocation-capacity cap, instrument bounds.

Decision vector z (24 dims):
  z[0:18]  = delta_i, fractional change to each spending category
  z[18:24] = tax instruments [d_ind, d_corp, d_cap, payroll_cap, vat, carbon]

Solver: scipy SLSQP (Sequential Least Squares Programming), as proposed in
the source workflow document. All functions are smooth (C1) by construction.
============================================================================
"""
import numpy as np
from scipy.optimize import minimize
import data as D

CATS = list(D.SPENDING.keys())
NC = len(CATS)
TAXES = ["d_ind", "d_corp", "d_cap", "payroll_cap", "vat", "carbon"]
NT = len(TAXES)
BASE = np.array([D.SPENDING[c]["base"] for c in CATS])
BASE_REV_TOTAL = sum(v["base"] for v in D.REVENUES.values())


# ----------------------------------------------------------------- revenues
def tax_revenue_delta(tz):
    """Net NEW revenue ($B/yr) from each instrument, including behavioral
    erosion. Returns (per-instrument array, total). Smooth in tz."""
    d_ind, d_corp, d_cap, pcap, vat, carbon = tz
    T = D.TAX_INSTRUMENTS
    r = np.zeros(NT)
    # individual: static $/pt with elasticity-of-taxable-income erosion that
    # scales with the size of the rate change (linear-in-change approximation)
    r[0] = T["d_ind"]["base_per_point"] * d_ind * (1 - T["d_ind"]["eti"] * abs(d_ind) / 10.0)
    # corporate: static $/pt minus base erosion proportional to cumulative
    # statutory points moved (profit shifting / flight semi-elasticity)
    static = T["d_corp"]["base_per_point"] * d_corp
    erosion = D.REVENUES["corporate_income"]["base"] * T["d_corp"]["erosion_per_point"] \
        * d_corp * (1 + 0.04 * max(d_corp, 0.0))   # convex erosion upward
    r[1] = static - erosion
    r[2] = T["d_cap"]["max_revenue"] * d_cap
    r[3] = T["payroll_cap"]["max_revenue"] * pcap
    r[4] = T["vat"]["base"] * (vat / 100.0) * (1 - T["vat"]["erosion"])
    r[5] = T["carbon"]["tons"] * carbon * (1 - T["carbon"]["decay"] * carbon)
    return r, float(r.sum())


# ---------------------------------------------------------------- macro core
def macro(z):
    """Year-1 endogenous quantities: GDP, outlays, revenues, deficit."""
    dx = z[:NC]                       # fractional spending changes
    tz = z[NC:]
    spend = BASE * (1 + dx)
    d_spend = spend - BASE            # $B changes
    rev_delta_vec, rev_delta = tax_revenue_delta(tz)

    # Demand-side GDP response (first-year, partial-equilibrium scalarization)
    mult = np.array([D.MULT_SPEND[c] for c in CATS])
    dY_spend = float(mult @ d_spend)
    tax_mult = np.array([D.MULT_TAX[k] for k in
                         ["individual_income", "corporate_income", "cap_gains",
                          "payroll_cap", "vat", "carbon"]])
    dY_tax = float(tax_mult @ rev_delta_vec)
    Y = D.GDP_2026 + dY_spend + dY_tax

    # Revenue feedback from GDP change (avg revenue/GDP ratio ~17.5%)
    rev_feedback = 0.175 * (Y - D.GDP_2026)
    revenues = BASE_REV_TOTAL + rev_delta + rev_feedback

    prog_outlays = float(spend.sum()) + D.OFFSETTING_RECEIPTS
    outlays_y1 = prog_outlays + D.NET_INTEREST_2026   # yr-1 interest ~ predetermined
    deficit_y1 = outlays_y1 - revenues
    return dict(Y=Y, spend=spend, revenues=revenues, outlays=outlays_y1,
                deficit=deficit_y1, rev_delta_vec=rev_delta_vec,
                prog_outlays=prog_outlays)


def debt_path(z, m=None):
    """10-year debt dynamics holding the policy *shape* fixed: program spending
    and new-revenue instruments grow with nominal GDP; interest is endogenous:
      D_{t+1} = D_t + (primary deficit_t) + r_t * D_t
    Supply-side: public-investment changes add to potential growth g."""
    if m is None:
        m = macro(z)
    dx = z[:NC]
    g_extra = sum(D.SUPPLY_GROWTH.get(c, 0.0) * (BASE[i] * dx[i]) / 100.0
                  for i, c in enumerate(CATS))
    g = D.NOMINAL_GDP_GROWTH + g_extra
    Y = D.GDP_2026 * (1 + (m["Y"] / D.GDP_2026 - 1))   # yr-1 level effect
    debt = D.DEBT_PUBLIC_2026 - D.DEFICIT_2026 + m["deficit"]  # adjust end-26 stock
    primary0 = m["prog_outlays"] - m["revenues"]               # primary deficit yr1
    ratios = []
    r_eff = D.EFFECTIVE_RATE_ON_DEBT
    for t in range(D.HORIZON):
        ratios.append(debt / Y)
        primary = primary0 * (1 + g) ** t          # scales with economy
        interest = r_eff * debt
        debt = debt + primary + interest
        Y = Y * (1 + g)
        # effective rate drifts toward marginal rate as stock rolls over
        r_eff = r_eff + (D.MARGINAL_RATE_ON_NEW_DEBT - r_eff) * 0.12
    return np.array(ratios), g


# --------------------------------------------------------------- well-being
def utilities(z, m):
    """Concave utility components. ln-form: zero at baseline, diminishing
    returns to increases, convex penalty for cuts."""
    dx = z[:NC]
    tz = z[NC:]

    def block(theta):
        u = 0.0
        for i, c in enumerate(CATS):
            w = theta.get(c, 0.0)
            if w:
                u += w * (BASE[i] / 100.0) * np.log1p(dx[i])
        return u

    U_health = block(D.THETA_HEALTH)
    U_equity = block(D.THETA_EQUITY)
    U_security = block(D.THETA_SECURITY)

    # tax-side distributional effects
    rev_vec = m["rev_delta_vec"]
    for k, key in enumerate(TAXES):
        U_equity += D.TAX_EQUITY[key] * rev_vec[k] / 100.0

    # growth utility — COMMON UNIT: 1.0 == $100B of social value.
    # Demand-level effect in $100B + capitalized supply-side effect: a
    # permanent potential-growth increment g_extra compounds; the decade's
    # cumulative extra output ≈ 55·g_extra·Y ≈ (years 1..10 summed); we use a
    # conservative capitalization factor of 25 to reflect discounting and
    # estimate uncertainty.
    dY_100B = (m["Y"] - D.GDP_2026) / 100.0
    g_extra = sum(D.SUPPLY_GROWTH.get(c, 0.0) * (BASE[i] * dx[i]) / 100.0
                  for i, c in enumerate(CATS))
    U_growth = dY_100B + 25.0 * g_extra * D.GDP_2026 / 100.0

    # carbon externality credit: damages avoided. EPA (2023) central SC-CO2
    # ≈ $190/t; we credit a conservative $50/t of avoided damages on the
    # ~ rate·decay·tons abated, in $100B units, into the health component.
    carbon = tz[5]
    T = D.TAX_INSTRUMENTS["carbon"]
    abated = T["tons"] * T["decay"] * carbon          # Gt abated
    U_health += 50.0 * abated / 100.0

    # Distortion (deadweight loss), SAME UNIT: marginal excess burden (MEB)
    # per dollar of revenue, signed (tax cuts reduce DWL), plus a small
    # quadratic for curvature. MEBs from Saez-Slemrod-Giertz / CBO / Dahlby:
    # individual 0.35, corporate 0.30, cap-income 0.15 (post-elasticity),
    # payroll-cap 0.25, VAT 0.20 (broad base = efficient), carbon 0.05
    # (Pigouvian — corrective, near-zero net burden).
    MEB = np.array([0.35, 0.30, 0.15, 0.25, 0.20, 0.05])
    # curvature: quadratic in NORMALIZED intensity (z/range) so the penalty
    # is unit-consistent across instruments measured in pts, %, and $/t
    ranges = np.array([max(abs(D.TAX_INSTRUMENTS[k]["lo"]),
                           abs(D.TAX_INSTRUMENTS[k]["hi"]), 1e-9)
                       for k in TAXES])
    qnorm = np.asarray(tz) / ranges
    Dst = float(MEB @ rev_vec) / 100.0 + 0.30 * float(qnorm @ qnorm)
    return U_growth, U_health, U_equity, U_security, Dst


def objective(z, alphas):
    m = macro(z)
    Ug, Uh, Ue, Us, Dst = utilities(z, m)
    ratios, _ = debt_path(z, m)
    # debt burden: penalize terminal ratio above its 2026 level (smoothplus)
    over = ratios[-1] - ratios[0]
    B = np.log1p(np.exp(8.0 * over)) / 8.0 * 10.0   # softplus, scaled
    a = alphas
    W = (a["growth"] * Ug + a["health"] * Uh + a["equity"] * Ue
         + a["security"] * Us - a["distortion"] * Dst - a["debt"] * B)
    return -W   # minimize


# --------------------------------------------------------------- constraints
def build_constraints(scenario):
    cons = []
    # deficit ceiling (year 1, % of baseline GDP)
    if scenario.get("deficit_cap_gdp") is not None:
        cap = scenario["deficit_cap_gdp"]
        cons.append(dict(type="ineq",
                         fun=lambda z, cap=cap: cap * D.GDP_2026 - macro(z)["deficit"]))
    # terminal debt/GDP ceiling
    if scenario.get("debt_cap_2036") is not None:
        cap = scenario["debt_cap_2036"]
        cons.append(dict(type="ineq",
                         fun=lambda z, cap=cap: cap - debt_path(z)[0][-1]))
    # symbiosis: defense industrial-base floor (share of endogenous GDP)
    i_def = CATS.index("defense")
    cons.append(dict(type="ineq", fun=lambda z:
                     BASE[i_def] * (1 + z[i_def])
                     - D.SYMBIOSIS["defense_floor_gdp"] * macro(z)["Y"]))
    # symbiosis: private-administration shock floor on medicare+medicaid
    i_mc, i_md = CATS.index("medicare"), CATS.index("medicaid_chip")
    fl = D.SYMBIOSIS["health_private_admin_floor"]
    cons.append(dict(type="ineq", fun=lambda z:
                     (BASE[i_mc] * (1 + z[i_mc]) + BASE[i_md] * (1 + z[i_md]))
                     - fl * (BASE[i_mc] + BASE[i_md])))
    # administrative reallocation capacity: sum |Δx_i| <= cap * programmatic
    # (smooth |u| ≈ sqrt(u²+ε) so SLSQP's linesearch has usable gradients)
    cap_re = D.SYMBIOSIS["max_total_reallocation"] * BASE.sum()
    cons.append(dict(type="ineq", fun=lambda z:
                     cap_re - np.sum(np.sqrt((BASE * z[:NC]) ** 2 + 1e-4))))
    return cons


def bounds(scenario):
    b = []
    tighten = scenario.get("feasibility_tighten", 1.0)  # 1.0 = statutory bounds
    for c in CATS:
        s = D.SPENDING[c]
        lo, hi = s["floor"] - 1.0, s["ceil"] - 1.0
        b.append((lo * tighten, hi * tighten))
    overrides = scenario.get("instrument_overrides", {})
    for k in TAXES:
        t = D.TAX_INSTRUMENTS[k]
        lo, hi = t["lo"], t["hi"]
        if k in scenario.get("ban_instruments", ()):
            lo = hi = 0.0
        if k in overrides:
            lo, hi = overrides[k]
        b.append((lo, hi))
    return b


def _max_violation(z, cons):
    return max([0.0] + [-c["fun"](z) for c in cons])


def solve(scenario, verbose=False):
    """Multi-start SLSQP: start from the baseline plus several perturbed
    points; keep the best near-feasible solution. SLSQP can report a benign
    'positive directional derivative' exit when pinned to an active
    constraint surface — we accept such points if constraint violation is
    numerically negligible (<$1B-equivalent)."""
    rng = np.random.default_rng(7)
    bnds = bounds(scenario)
    cons = build_constraints(scenario)
    starts = [np.zeros(NC + NT)]
    lo = np.array([b[0] for b in bnds]); hi = np.array([b[1] for b in bnds])
    for _ in range(4):
        starts.append(lo + (hi - lo) * rng.uniform(0.25, 0.75, size=NC + NT))
    best = None
    for z0 in starts:
        res = minimize(objective, z0, args=(scenario["alphas"],),
                       method="SLSQP", bounds=bnds, constraints=cons,
                       options=dict(maxiter=800, ftol=1e-10))
        viol = _max_violation(res.x, cons)
        ok = res.success or viol < 1.0
        if ok and (best is None or -res.fun > best["W"]):
            best = dict(z=res.x, W=-res.fun, msg=res.message,
                        success=True, viol=viol)
    if best is None:   # fall back to least-violating attempt
        res = minimize(objective, np.zeros(NC + NT), args=(scenario["alphas"],),
                       method="SLSQP", bounds=bnds, constraints=cons,
                       options=dict(maxiter=2000, ftol=1e-8))
        best = dict(z=res.x, W=-res.fun, msg=res.message, success=res.success,
                    viol=_max_violation(res.x, cons))
    m = macro(best["z"])
    ratios, g = debt_path(best["z"], m)
    Ug, Uh, Ue, Us, Dst = utilities(best["z"], m)
    return dict(scenario=scenario["name"], success=best["success"],
                msg=best["msg"], max_violation=best["viol"],
                z=best["z"], macro=m, debt_ratios=ratios, growth=g,
                U=dict(growth=Ug, health=Uh, equity=Ue, security=Us,
                       distortion=Dst), W=best["W"])
