"""
EPOE — Scenario Runner
============================================================================
Defines the political-perspective scenarios (the alpha-weight vectors and
constraint sets from docs/04), solves each, and writes:
  results/budget_<scenario>.csv     line-item optimized budget
  results/summary.csv               cross-scenario comparison
  results/summary.md                human-readable comparison table

Run:  python run_scenarios.py
============================================================================
"""
import csv, os
import numpy as np
import data as D
import model as M

OUT = os.path.join(os.path.dirname(__file__), "..", "results")
os.makedirs(OUT, exist_ok=True)

SCENARIOS = [
    dict(name="A_growth_capital",
         label="Growth & Capital Optimization (limited-government leaning)",
         alphas=dict(growth=2.0, health=0.4, equity=0.2, security=1.0,
                     distortion=2.0, debt=1.5),
         deficit_cap_gdp=0.048, debt_cap_2036=1.05,
         ban_instruments=("vat", "carbon", "payroll_cap", "d_cap"),
         # political coherence: this coalition does not raise income or
         # corporate rates — consolidation must come from the spending side
         instrument_overrides={"d_ind": (-2.0, 0.0), "d_corp": (-5.0, 0.0)}),
    dict(name="B_social_welfare",
         label="Social Welfare Maximization (social-democratic leaning)",
         alphas=dict(growth=0.7, health=2.0, equity=2.0, security=0.4,
                     distortion=0.5, debt=0.8),
         deficit_cap_gdp=0.058, debt_cap_2036=None,
         ban_instruments=()),
    dict(name="C_nordic_financing",
         label="Universalist with Consumption Financing (Nordic-style)",
         alphas=dict(growth=1.0, health=1.8, equity=1.5, security=0.5,
                     distortion=0.8, debt=1.2),
         deficit_cap_gdp=0.045, debt_cap_2036=1.01,
         ban_instruments=(),
         # structural premise of this scenario: finance like the Nordics —
         # broad consumption tax mandated (VAT >= 5%), corporate kept low
         instrument_overrides={"vat": (5.0, 10.0), "d_corp": (-2.0, 1.0)}),
    dict(name="D_fiscal_consolidation",
         label="Deficit-First Grand Bargain (fiscal-hawk bipartisan)",
         alphas=dict(growth=1.2, health=0.8, equity=0.7, security=0.8,
                     distortion=1.2, debt=3.0),
         deficit_cap_gdp=0.040, debt_cap_2036=0.98,
         ban_instruments=("vat",),
         feasibility_tighten=0.8),
    dict(name="E_pragmatic_pareto",
         label="Pragmatic Compromise (highest joint-passage likelihood)",
         alphas=dict(growth=1.2, health=1.2, equity=1.0, security=0.9,
                     distortion=1.0, debt=1.5),
         deficit_cap_gdp=0.050, debt_cap_2036=1.01,
         ban_instruments=("vat",),
         feasibility_tighten=0.6),   # changes limited to 60% of statutory range
]


def write_budget_csv(r):
    z = r["z"]; m = r["macro"]
    path = os.path.join(OUT, f"budget_{r['scenario']}.csv")
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["category", "baseline_$B", "optimized_$B", "change_$B",
                    "change_pct", "confidence", "note"])
        for i, c in enumerate(M.CATS):
            b = M.BASE[i]; v = m["spend"][i]
            w.writerow([c, f"{b:.0f}", f"{v:.0f}", f"{v-b:+.0f}",
                        f"{z[i]*100:+.1f}%", D.SPENDING[c]["conf"],
                        D.SPENDING[c]["note"]])
        w.writerow(["offsetting_receipts", f"{D.OFFSETTING_RECEIPTS:.0f}",
                    f"{D.OFFSETTING_RECEIPTS:.0f}", "+0", "0.0%", "LOW",
                    "Reconciling line to CBO total"])
        w.writerow(["net_interest", f"{D.NET_INTEREST_2026:.0f}",
                    f"{D.NET_INTEREST_2026:.0f}", "+0", "0.0%", "HIGH",
                    "Endogenous in out-years via debt path"])
        w.writerow([])
        w.writerow(["tax_instrument", "setting", "net_new_revenue_$B"])
        rv = m["rev_delta_vec"]
        units = ["pts effective indiv rate", "pts statutory corp rate",
                 "fraction of cap-income package", "fraction of payroll-cap lift",
                 "VAT rate %", "carbon $/tCO2e"]
        for k, key in enumerate(M.TAXES):
            w.writerow([key, f"{z[M.NC+k]:.2f} {units[k]}", f"{rv[k]:+.0f}"])
    return path


def main():
    rows = []
    for sc in SCENARIOS:
        r = M.solve(sc)
        write_budget_csv(r)
        m = r["macro"]; ratios = r["debt_ratios"]
        rows.append(dict(
            scenario=sc["name"], label=sc["label"], converged=r["success"],
            outlays=m["outlays"], revenues=m["revenues"], deficit=m["deficit"],
            deficit_gdp=m["deficit"] / D.GDP_2026 * 100,
            gdp_effect=m["Y"] - D.GDP_2026,
            debt_gdp_2026=ratios[0] * 100, debt_gdp_2036=ratios[-1] * 100,
            U_growth=r["U"]["growth"], U_health=r["U"]["health"],
            U_equity=r["U"]["equity"], U_security=r["U"]["security"],
            distortion=r["U"]["distortion"], W=r["W"]))
        print(f"[{sc['name']}] converged={r['success']}  "
              f"deficit=${m['deficit']:.0f}B ({m['deficit']/D.GDP_2026*100:.1f}% GDP)  "
              f"debt/GDP 2036={ratios[-1]*100:.0f}%")

    with open(os.path.join(OUT, "summary.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)

    # Baseline reference row for the markdown table
    base_ratios, _ = M.debt_path(np.zeros(M.NC + M.NT))
    with open(os.path.join(OUT, "summary.md"), "w") as f:
        f.write("# EPOE Scenario Results — FY2026 optimized budgets\n\n")
        f.write("| Scenario | Outlays $B | Revenues $B | Deficit $B | Deficit %GDP "
                "| Debt/GDP 2036 | U_health | U_equity | U_growth |\n")
        f.write("|---|---|---|---|---|---|---|---|---|\n")
        f.write(f"| **CBO current-law baseline** | {D.OUTLAYS_2026:.0f} | "
                f"{D.REVENUES_2026:.0f} | {D.DEFICIT_2026:.0f} | "
                f"{D.DEFICIT_2026/D.GDP_2026*100:.1f}% | "
                f"{base_ratios[-1]*100:.0f}% | 0 | 0 | 0 |\n")
        for r in rows:
            f.write(f"| {r['label']} | {r['outlays']:.0f} | {r['revenues']:.0f} | "
                    f"{r['deficit']:.0f} | {r['deficit_gdp']:.1f}% | "
                    f"{r['debt_gdp_2036']:.0f}% | {r['U_health']:+.1f} | "
                    f"{r['U_equity']:+.1f} | {r['U_growth']:+.1f} |\n")
    print("\nWrote results/ summary.md, summary.csv and per-scenario budget CSVs.")


if __name__ == "__main__":
    main()
