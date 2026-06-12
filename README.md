# The Empirical Policy Optimization Engine (EPOE)

**A fully transparent, evidence-grounded, mathematically optimized framework for the United States federal budget — built to be downloaded, challenged, and reused by any lawmaker, staffer, journalist, or citizen.**

Baseline year: **Fiscal Year 2026**, current law, anchored to the Congressional Budget Office's *Budget and Economic Outlook: 2026 to 2036* (February 11, 2026).

---

## What this is

Federal budget debates are usually conducted as contests of slogans. This project conducts one as a contest of **stated values and shared arithmetic**. It does three things:

1. **Characterizes reality without moral language.** Document `01` establishes, from primary sources, the actual structural relationship between the federal government and large-scale private enterprise — contracts, tax expenditures, lobbying, regulatory administration — treating that relationship as a *measured constraint*, not a villain or a hero.
2. **States the arithmetic.** Document `02` lays out every dollar in and every dollar out of the federal government for FY2026, with each line traced to its statutory data source and tagged with an explicit confidence rating.
3. **Optimizes, transparently, under different value systems.** Documents `03`–`04` formalize the budget as a nonlinear constrained optimization problem and then solve it under five distinct political value-weightings. The point is not that the computer picks the "right" budget. The point is that once values are stated as numbers (the α-weights), the **trade-offs become arithmetic instead of rhetoric** — and every reader can change the numbers and re-run.

Document `05` converts the analysis into a ranked, actionable list of the places where Americans are most underserved relative to what the evidence says a dollar can buy.

## What this is not

- It is **not** a partisan argument. Every scenario — including ones the authors of any given reader's party would reject — is solved with the same machinery and reported with the same honesty.
- It is **not** a line-item appropriations bill. The model operates at the **budget-function level** — the same level of granularity at which Congress itself writes its annual budget resolution under the Congressional Budget Act of 1974. The concurrent budget resolution allocates totals across ~20 budget functions; appropriations subcommittees then write line items inside those totals. This framework deliberately matches the instrument lawmakers actually vote on first. (Extending the data layer to the ~4,500 individual appropriation accounts is a mechanical, if large, extension — see *Roadmap* below.)
- It is **not** a claim of precision. Every parameter carries a confidence tag, and Document `04` includes a standing section on what to watch for and what the contingency logic is if the assumptions fail.

## Repository map

```
README.md                      ← you are here
docs/
  01_government_business_relationship.md   The measured corporate–state structure
  02_fiscal_baseline.md                    Every FY2026 dollar, sourced and rated
  03_mathematical_model.md                 The full optimization formulation
  04_scenario_results.md                   Five optimized budgets, annotated
  05_ranked_actions.md                     Ranked underserved areas + specific actions
model/
  data.py            The empirical layer — every number annotated in-line
  model.py           The optimization engine (SLSQP, smooth NLP)
  run_scenarios.py   Scenario definitions and result generation
results/
  summary.md / summary.csv          Cross-scenario comparison
  budget_<scenario>.csv             Per-scenario optimized budgets
index.html                          ← the interactive dashboard (GitHub Pages serves this)
dashboard/
  epoe-model.js      Full JavaScript port of the model (data layer + engine + solver)
  index.template.html The dashboard UI (model gets inlined at build time)
  build.py           Inlines the model into the template → writes /index.html
  validate.js        Node harness: JS port vs. Python SLSQP, scenario by scenario
```

## How to run it

```bash
pip install numpy scipy
cd model
python run_scenarios.py
```

Runtime is a few seconds. To test your own value system, copy a scenario block in `run_scenarios.py`, change the `alphas`, the constraint caps, or the banned instruments, and re-run. To challenge an empirical assumption, edit it in `data.py` — every parameter is annotated with its source and confidence — and observe how the optimal budgets move. **That sensitivity is itself the finding**: parameters whose variation reorders the conclusions are flagged in Document `04`.

## The interactive dashboard

`index.html` is a self-contained, zero-dependency page that runs the **complete model in the browser** — the full data layer, the behavioral revenue functions, the endogenous-GDP block, the 11-year debt recursion, and all five constraint families. Nothing is distilled or precomputed; when you press *Solve*, your machine solves the same smooth nonlinear program the Python engine solves. Set the six α-weights, choose the fiscal ceilings and political-feasibility band, decide which revenue instruments are on the table, and solve — or start from any of the five published scenarios and depart from there. A solve takes a few seconds on a laptop.

The one substitution: SciPy's SLSQP does not exist in a browser, so the JavaScript engine uses a multi-start **augmented-Lagrangian method** (projected Adam inner loop, minimal-norm Newton feasibility polish) on the identical objective, constraints, and bounds. The port is validated head-to-head against the Python engine by `dashboard/validate.js` (`node dashboard/validate.js`); headline results match the published SLSQP solutions to within ~$10B on every scenario, and scenario E is reproduced exactly.

To modify the dashboard, edit `dashboard/epoe-model.js` (engine) or `dashboard/index.template.html` (UI), then rebuild:

```bash
python dashboard/build.py     # regenerates /index.html with the model inlined
node dashboard/validate.js    # re-checks the JS engine against the Python results
```

### Publishing on GitHub Pages

```bash
git init && git add -A && git commit -m "EPOE: framework, scenarios, dashboard"
git branch -M main
git remote add origin https://github.com/<your-username>/epoe.git
git push -u origin main
```

Then on GitHub: **Settings → Pages → Build and deployment → Source: "Deploy from a branch" → Branch: `main`, folder: `/ (root)` → Save.** Within a minute or two the dashboard is live at `https://<your-username>.github.io/epoe/`, and the relative links in its footer resolve to the documents and source files in the same repository.

## Epistemics statement

This framework practices three disciplines throughout. **Provenance:** no number appears without a source. **Calibrated confidence:** HIGH means an official published total; MEDIUM means a disaggregation of official totals; LOW means an academic parameter with a wide band — and LOW-confidence parameters are exactly the ones subjected to sensitivity analysis. **Falsifiability:** Document `04` ends with explicit tripwires — observable indicators that would mean the model's assumptions are failing, and what the prepared fallback is.

## Roadmap

1. **Account-level extension.** Ingest OMB's Public Budget Database (outlays by account, FY1962–present, machine-readable) to push the decision vector from 18 categories to ~4,500 accounts.
2. **Dashboard. ✅ Shipped** — `index.html`, a static GitHub Pages dashboard with α-weight sliders. It exceeded the original plan: it solves the *full* model client-side (nothing distilled), validated against the Python engine by `dashboard/validate.js`.
3. **Stochastic extension.** Replace point parameters with distributions; report optimized budgets as ranges (robust optimization).
4. **Annual refresh.** Each February's CBO Outlook re-anchors `data.py`; the framework is built to produce successive budgets indefinitely.

## Primary sources (the load-bearing ones)

- CBO, *The Budget and Economic Outlook: 2026 to 2036* (Feb 2026) — https://www.cbo.gov/publication/62105
- U.S. Treasury, *Final Monthly Treasury Statement, FY2025* — https://fiscaldata.treasury.gov/static-data/published-reports/mts/MonthlyTreasuryStatement_202509.pdf
- OMB, *Historical Tables* — https://www.whitehouse.gov/omb/budget/historical-tables/
- Joint Committee on Taxation, *Estimates of Federal Tax Expenditures FY2025–2029* (JCX-45-25) — https://www.jct.gov/publications/2025/jcx-45-25/
- OpenSecrets, federal lobbying database — https://www.opensecrets.org/federal-lobbying
- USAspending.gov, federal award data — https://www.usaspending.gov
- Commonwealth Fund, *Mirror, Mirror 2024* and *U.S. Health Care from a Global Perspective 2026* — https://www.commonwealthfund.org
- Hendren & Sprung-Keyser, "A Unified Welfare Analysis of Government Policies," *QJE* (2020) — the Marginal Value of Public Funds library: https://policyimpacts.org
