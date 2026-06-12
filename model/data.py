"""
EPOE — Empirical Data Layer
============================================================================
Every number in this file is annotated with:
  SOURCE     : the primary, non-partisan statutory data source
  CONFIDENCE : HIGH   = taken directly from an official published total
               MEDIUM = estimated by disaggregating official totals using
                        FY2025 actuals grown to FY2026 (CBO growth rates)
               LOW    = parameter from academic literature with wide
                        uncertainty bands (always given as a range)

Baseline year: Fiscal Year 2026 (Oct 1 2025 – Sep 30 2026), current law,
per CBO, "The Budget and Economic Outlook: 2026 to 2036" (Feb 11, 2026),
https://www.cbo.gov/publication/62105

Reconciliation discipline: spending lines + net interest + offsetting
receipts are constructed to sum EXACTLY to CBO's published $7.40T outlay
total; revenue lines sum EXACTLY to CBO's published $5.60T revenue total.
The residual lines absorb disaggregation error and are flagged as such.
============================================================================
"""

# ---------------------------------------------------------------------------
# MACRO BASELINE (all HIGH confidence — CBO Feb 2026 Outlook, Tables 1-1, 1-2)
# ---------------------------------------------------------------------------
GDP_2026 = 31_800.0        # $B. Implied by outlays $7.4T = 23.3% of GDP. HIGH
OUTLAYS_2026 = 7_400.0     # $B, 23.3% GDP. HIGH (CBO)
REVENUES_2026 = 5_600.0    # $B, 17.5% GDP. HIGH (CBO)
DEFICIT_2026 = 1_800.0     # $B, 5.8% GDP (CBO rounds to $1.9T; identity gives 1.8T) HIGH
DEBT_PUBLIC_2026 = 32_100.0  # $B, ~101% GDP end-FY2026. HIGH (CBO)
NET_INTEREST_2026 = 1_030.0  # $B, ~3.3% GDP. HIGH (CBO: net interest 3.3% of GDP in 2026)

# 10-year dynamics parameters (CBO economic forecast, Feb 2026)
NOMINAL_GDP_GROWTH = 0.041   # ~2.0% real (2.2% near-term, moderating) + ~2.1% infl. HIGH/MEDIUM
EFFECTIVE_RATE_ON_DEBT = 0.0345  # avg interest on debt held by public; rises slowly. MEDIUM
MARGINAL_RATE_ON_NEW_DEBT = 0.043  # ~10yr Treasury neighborhood. MEDIUM
HORIZON = 11  # FY2026..FY2036

# FY2025 ACTUALS for reference (Treasury Final MTS, Sept 2025; CBO MBR Nov 2025)
FY2025_ACTUALS = dict(revenues=5_235.0, outlays=7_010.0, deficit=1_775.0,
                      net_interest=1_010.0)  # net interest >$1T for first time. HIGH

# ---------------------------------------------------------------------------
# SPENDING BASELINE BY CATEGORY, FY2026 ($B)
# ---------------------------------------------------------------------------
# Disaggregation anchors (HIGH): CBO Feb 2026 — mandatory $4.5T, discretionary
# $1.9T, net interest ~$1.03T; FY2025 actuals by program (CRFB/CBO): Social
# Security $1,575B, Medicare $988B, Medicaid $668B, other health $164B, other
# mandatory $773B, defense disc. $893B, nondefense disc. $980B.
# FY2026 growth (HIGH, CBO): SS +$91B, Medicare +$75B, Medicaid +$40B,
# student loans +$89B, veterans +$49B; discretionary +$8B (continuing resolution).
#
# Fields: baseline $B | controllable in a single budget cycle? | floor (fraction
# of baseline below which a one-cycle change is treated as statutorily/
# operationally infeasible) | ceiling | confidence
SPENDING = {
    # --- Mandatory (entitlement law; changing these requires authorizing law,
    #     not just appropriations — hence tight one-cycle bounds) ---
    "social_security":      dict(base=1666.0, floor=0.97, ceil=1.10, conf="HIGH",
        note="OASDI benefits. FY25 actual $1,575B + CBO +$91B FY26 growth. "
             "OASI trust fund exhausted 2032 under current law (CBO)."),
    "medicare":             dict(base=1063.0, floor=0.95, ceil=1.12, conf="HIGH",
        note="Net of premiums. FY25 $988B + CBO +$75B. ~50% of beneficiaries "
             "now in privately administered Medicare Advantage."),
    "medicaid_chip":        dict(base=700.0,  floor=0.93, ceil=1.25, conf="HIGH",
        note="Federal share. FY25 $668B + CBO +$40B; P.L.119-21 cuts ~$1.2T "
             "over 10yr already embedded in baseline."),
    "aca_other_health":     dict(base=140.0,  floor=0.90, ceil=1.60, conf="MEDIUM",
        note="ACA premium tax credits & related; enhanced subsidies expired, "
             "enrollment falling in baseline (CBO -$79B revision)."),
    "income_security":      dict(base=460.0,  floor=0.93, ceil=1.30, conf="MEDIUM",
        note="SNAP, SSI, EITC/CTC refundable portions, UI, child nutrition. "
             "Split estimated from FY25 'other mandatory' $773B."),
    "veterans":             dict(base=420.0,  floor=1.00, ceil=1.15, conf="MEDIUM",
        note="Mandatory disability compensation + VA discretionary health. "
             "CBO FY26 growth +$49B. Floor=1.0: cuts treated as infeasible."),
    "fed_retirement":       dict(base=190.0,  floor=0.98, ceil=1.05, conf="MEDIUM",
        note="Civilian + military retirement. Contractual; near-zero "
             "one-cycle controllability."),
    "other_mandatory":      dict(base=320.0,  floor=0.85, ceil=1.20, conf="LOW",
        note="Student loans (large FY26 +$89B re-estimate), agriculture, "
             "deposit insurance, misc. Most volatile residual line."),
    # --- Discretionary (annual appropriations; controllable, subject to
    #     transition-friction bounds) ---
    "defense":              dict(base=900.0,  floor=0.85, ceil=1.15, conf="HIGH",
        note="050 function. FY25 $893B + CR. ~half flows to contractors "
             "(symbiosis constraint binds here)."),
    "intl_affairs":         dict(base=55.0,   floor=0.70, ceil=1.40, conf="MEDIUM",
        note="State/USAID-successor ops, embassies, global health."),
    "science_space":        dict(base=80.0,   floor=0.80, ceil=1.50, conf="MEDIUM",
        note="NSF, NASA, DOE Office of Science. Highest long-run growth "
             "spillovers per $ in the literature."),
    "health_research_ph":   dict(base=95.0,   floor=0.80, ceil=1.60, conf="MEDIUM",
        note="NIH, CDC, FDA, HRSA discretionary. Public-health "
             "infrastructure case-study lever."),
    "education_training":   dict(base=115.0,  floor=0.80, ceil=1.50, conf="MEDIUM",
        note="Title I, IDEA, Pell (disc. portion), workforce training."),
    "transportation":       dict(base=130.0,  floor=0.85, ceil=1.40, conf="MEDIUM",
        note="Highways, transit, aviation, rail (incl. IIJA tail)."),
    "environment_energy":   dict(base=65.0,   floor=0.75, ceil=1.50, conf="MEDIUM",
        note="EPA, Interior ops, DOE energy programs."),
    "housing_community":    dict(base=90.0,   floor=0.80, ceil=1.45, conf="MEDIUM",
        note="HUD (Sec.8, public housing), CDBG, rural development."),
    "justice_homeland":     dict(base=105.0,  floor=0.85, ceil=1.30, conf="MEDIUM",
        note="DOJ, federal courts, CBP/ICE (immigration enforcement "
             "elevated in baseline per 2025 reconciliation act)."),
    "general_gov_other":    dict(base=165.0,  floor=0.80, ceil=1.20, conf="LOW",
        note="Treasury/IRS ops, GSA, Congress, residual NDD. Absorbs "
             "disaggregation error — widest uncertainty."),
}
OFFSETTING_RECEIPTS = -389.0  # $B. Residual reconciling line so that
# sum(SPENDING) + NET_INTEREST + OFFSETTING = exactly $7,400B (CBO total).
# Includes Medicare premium offsets not netted above, spectrum, royalties.
# Confidence: line is LOW individually, but guarantees the TOTAL is HIGH.

# ---------------------------------------------------------------------------
# REVENUE BASELINE BY SOURCE, FY2026 ($B) — sums exactly to $5,600B (CBO)
# ---------------------------------------------------------------------------
# Anchors: FY2025 actuals (Treasury MTS): individual $2,656B, payroll $1,748B,
# corporate $452B, customs $195B, other $183B. FY2026: customs elevated by 2025
# tariff regime (CBO: tariffs -$3.0T deficits over decade ≈ $300B+/yr).
REVENUES = {
    "individual_income": dict(base=2800.0, conf="HIGH",
        note="~8.8% of GDP. Post-P.L.119-21 (OBBBA) permanent rate structure."),
    "payroll":           dict(base=1800.0, conf="HIGH",
        note="OASDI 12.4% to taxable max ($176,100 in 2025, indexed) + "
             "Medicare HI 2.9% uncapped."),
    "corporate_income":  dict(base=480.0,  conf="HIGH",
        note="21% statutory; ~13-16% average effective rate. 1.5% of GDP "
             "vs ~3.5% historical mid-century norm."),
    "customs":           dict(base=330.0,  conf="MEDIUM",
        note="Tariff regime as of CBO Nov 2025 trade-policy snapshot; "
             "legally contested — highest policy risk of any revenue line."),
    "excise":            dict(base=100.0,  conf="HIGH", note="Fuel, aviation, tobacco, health."),
    "estate_gift":       dict(base=35.0,   conf="HIGH", note="Exemption ~$15M/person post-OBBBA."),
    "fed_remittances":   dict(base=5.0,    conf="MEDIUM", note="Fed remittances still "
             "suppressed by interest paid on reserves; deferred-asset overhang."),
    "misc_fees":         dict(base=50.0,   conf="MEDIUM", note="Fees, fines, misc receipts."),
}

# ---------------------------------------------------------------------------
# FISCAL MULTIPLIERS (demand-side, first-year, dimensionless ΔY/Δspend)
# CONFIDENCE: LOW-MEDIUM. Ranges from CBO's own multiplier tables (used for
# ARRA & pandemic scoring), Ramey (2019, JEP) survey, Whalen & Reichling
# (CBO WP 2015-02). We use central values; ranges noted for sensitivity.
# ---------------------------------------------------------------------------
MULT_SPEND = {
    "social_security": 0.85, "medicare": 0.80, "medicaid_chip": 0.95,
    "aca_other_health": 0.90, "income_security": 1.20,  # liquidity-constrained households: 0.8–1.5
    "veterans": 0.90, "fed_retirement": 0.70, "other_mandatory": 0.70,
    "defense": 0.70,            # 0.5–0.9 (Ramey); high import/profit leakage
    "intl_affairs": 0.40, "science_space": 0.60, "health_research_ph": 0.70,
    "education_training": 0.80, "transportation": 0.90,  # demand side only
    "environment_energy": 0.70, "housing_community": 0.95,
    "justice_homeland": 0.70, "general_gov_other": 0.60,
}
# Long-run SUPPLY-side annual potential-growth contribution per +$100B/yr
# sustained (decimal points of growth). LOW confidence; CBO public-investment
# elasticity work, Fernald (infrastructure), Jones & Summers (R&D returns).
SUPPLY_GROWTH = {
    "science_space": 0.00030, "health_research_ph": 0.00020,
    "education_training": 0.00020, "transportation": 0.00020,
    "environment_energy": 0.00008, "housing_community": 0.00005,
    # all others ~0 on a 10-year horizon
}

# Tax multipliers (ΔY per $ of revenue raised, NEGATIVE drag on demand)
MULT_TAX = {
    "individual_income": -0.50,  # mixed incidence
    "corporate_income": -0.35,   # falls partly on capital/foreign holders short-run
    "cap_gains": -0.20, "payroll_cap": -0.30,
    "vat": -0.90,                # broad consumption hit
    "carbon": -0.60,
}

# ---------------------------------------------------------------------------
# REVENUE INSTRUMENTS — empirical behavioral parameters
# ---------------------------------------------------------------------------
TAX_INSTRUMENTS = {
    # change in avg effective individual rate, percentage points of taxable base
    "d_ind": dict(lo=-2.0, hi=1.5,
        base_per_point=300.0,   # $B static revenue per +1pt effective rate. MEDIUM
        eti=0.25,               # elasticity of taxable income (Saez-Slemrod-Giertz
                                # survey central 0.12–0.40). LOW
        note="Behavioral erosion via ETI; net = static*(1 - eti*rate_proxy)."),
    "d_corp": dict(lo=-5.0, hi=7.0,         # statutory points around 21% (28% ceiling)
        base_per_point=23.0,    # $B static per statutory point (480/21). MEDIUM
        erosion_per_point=0.012,# 1.2%/pt profit-shifting+flight semi-elasticity
                                # (Heckemeyer-Overesch meta ~0.8–1.5). LOW
        note="Laffer boundary emerges endogenously from erosion term."),
    "d_cap": dict(lo=0.0, hi=1.0,
        max_revenue=120.0,      # $B/yr: cap-gains-at-death + rate alignment,
                                # post-realization-elasticity (JCT-style). LOW
        note="0..1 = fraction of a full capital-income reform package."),
    "payroll_cap": dict(lo=0.0, hi=1.0,
        max_revenue=180.0,      # $B/yr: eliminate OASDI taxable max w/ benefit
                                # offsets (SSA actuaries range 150–250). MEDIUM
        note="Also extends OASI trust-fund solvency — credited in equity."),
    "vat": dict(lo=0.0, hi=10.0,            # rate, %
        base=12_700.0,          # ~40% of GDP taxable base after exemptions. MEDIUM
        erosion=0.15,           # evasion/exemption erosion. LOW
        note="Nordic-style financing instrument; regressive — equity penalty."),
    "carbon": dict(lo=0.0, hi=80.0,         # $/tCO2e
        tons=4.0,               # billions tCO2e covered net of leakage. MEDIUM
        decay=0.006,            # fractional emissions decline per $/t. LOW
        note="Revenue = rate*tons*(1-decay*rate); internalizes externality."),
}

# ---------------------------------------------------------------------------
# WELL-BEING WEIGHTS θ_i  (social value per marginal $, normalized; informed
# by MVPF literature — Hendren & Sprung-Keyser QJE 2020 — and Commonwealth
# Fund / OECD outcome gaps). CONFIDENCE: LOW — these are the ethically loaded
# parameters; scenarios vary the α-weights ON TOP of these, and the docs
# instruct readers to challenge them.
# ---------------------------------------------------------------------------
THETA_HEALTH = {  # contribution to health-outcomes index
    "medicare": 0.8, "medicaid_chip": 1.3, "aca_other_health": 1.2,
    "health_research_ph": 1.5, "veterans": 0.6, "income_security": 0.5,
    "housing_community": 0.4, "environment_energy": 0.3,
}
THETA_EQUITY = {  # contribution to distributional index
    "income_security": 1.5, "medicaid_chip": 1.2, "aca_other_health": 1.0,
    "education_training": 1.1, "housing_community": 1.1,
    "social_security": 0.8, "veterans": 0.5,
}
THETA_GROWTH_PUBINV = {  # already in SUPPLY_GROWTH; weights for U_growth shaping
    "science_space": 1.4, "transportation": 1.0, "education_training": 1.0,
    "health_research_ph": 0.9, "environment_energy": 0.5,
}
THETA_SECURITY = {"defense": 1.0, "veterans": 0.4, "justice_homeland": 0.5,
                  "intl_affairs": 0.6}

# Tax-side equity effects (index points per $100B raised; sign = progressive +)
TAX_EQUITY = {"d_ind": 0.3, "d_corp": 0.5, "d_cap": 1.2, "payroll_cap": 1.0,
              "vat": -0.8, "carbon": -0.3}

# ---------------------------------------------------------------------------
# SYMBIOSIS CONSTRAINTS (the corporate-state entanglement, made explicit)
# Evidence layer: lobbying $5.08B record in 2025 (OpenSecrets); tax
# expenditures $2.3T FY2026 = 44% of revenues (JCT/CBO); ~$0.75T/yr federal
# contracts (USAspending); ~half of Medicare privately administered.
# ---------------------------------------------------------------------------
SYMBIOSIS = dict(
    defense_floor_gdp=0.025,     # defense >= 2.5% GDP: industrial-base floor
    health_private_admin_floor=0.90,  # medicare+medicaid can't fall >10% in one
                                      # cycle without insurer/provider shock
    max_total_reallocation=0.12, # no more than 12% of programmatic spend may
                                 # move in one cycle (administrative capacity)
)
