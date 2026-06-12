# 05 — Where Americans Are Most Underserved: A Ranked, Actionable List

*This document converts the analysis of Documents 01–04 into the deliverable the project promised: a ranked list of the areas where Americans are most underserved **relative to what the evidence says a dollar can buy there**, with the specific actions that would treat each, the confidence behind each claim, and the indicators to watch. The ranking criterion is stated up front so it can be challenged.*

---

## 0. The ranking criterion, stated explicitly

An area ranks higher when three things are simultaneously true:

1. **The outcome gap is large and measured** — the United States demonstrably underperforms either its own spending level or its peer countries on a well-defined indicator (not a vibe; a published statistic with a named source).
2. **The marginal dollar is demonstrably productive** — the Marginal Value of Public Funds (MVPF) literature, CBO scoring, or equivalent quasi-experimental evidence indicates value per net-government-dollar at or above 1.0 (Hendren & Sprung-Keyser, *QJE* 2020; the Policy Impacts library at policyimpacts.org).
3. **The optimization corridor confirms it** — the recommended action appears in the optimized budget of *most or all* of the five value systems in Document 04, meaning it does not depend on adopting any single political ideology. Actions that appear only under one α-weighting are flagged as such and ranked lower regardless of how strong their single-scenario case is.

This criterion deliberately privileges *agreement across value systems* over *magnitude under one value system*. A reader who weights differently can re-rank; the inputs for doing so are all here.

---

## Rank 1 — Health-system value: the largest measured gap in American life

**The gap.** The United States devotes roughly 18% of GDP to health care — nearly twice the OECD average — yet records the lowest life expectancy among high-income peers (about 79 years), the highest rates of preventable and treatable mortality, and the worst maternal mortality in its comparison group (Commonwealth Fund, *Mirror, Mirror 2024*; *U.S. Health Care from a Global Perspective, 2026*; Peterson-KFF Health System Tracker). The countries with the *best* outcomes in those rankings — Australia, the Netherlands — spend the *smallest* share of GDP among the group. This is the single most extreme spend-versus-outcome divergence in the federal ledger, which is why this project treats it as the master case study. Confidence in the gap itself: **HIGH** (multiple independent measurement systems agree).

**Why the dollar is productive here.** The MVPF evidence is strongest precisely where current coverage is thinnest: public insurance for children and pregnant women returns more than its cost (MVPF > 1, in several designs effectively infinite because downstream tax receipts repay the outlay), and public-health infrastructure (surveillance, vaccination, maternal care) sits at the top of the measured distribution. Confidence: **MEDIUM** (the literature is strong but its external validity to marginal 2026 dollars is an inference).

**What the optimizer says.** Four of five scenarios — including the fiscal-hawk Scenario D — expand Medicaid/CHIP, ACA-side coverage, and the NIH/CDC/HRSA public-health line. Only the scenario that excludes health from its objective by premise (A) cuts them. This is the corridor criterion at its clearest.

**Specific actions, in order of evidence strength:**

- **(1a) Restore and stabilize coverage for children and pregnant/postpartum women** (Medicaid/CHIP eligibility floors, 12-month continuous eligibility, postpartum extension to 12 months nationwide). Mechanism: authorizing language in the next reconciliation or health extenders vehicle. Order of magnitude: tens of billions per year against a $700B Medicaid base — small relative to the category, top-of-distribution per-dollar value. Confidence: **HIGH** that this is the best-evidenced single health dollar.
- **(1b) Rebuild public-health and primary-care infrastructure** (CDC data modernization, HRSA community health centers, maternal-health programs in the highest-mortality states). The model's `health_research_ph` line expands 36–60% in every scenario allowed to touch it. Confidence: **MEDIUM-HIGH**.
- **(1c) Attack prices, not just coverage** — the US outcome gap is driven substantially by paying 2–4× peer prices for the same drugs, procedures, and administration. Actions: extend Medicare drug-price negotiation (IRA authority) to more molecules and earlier in lifecycle; site-neutral payment reform; surprise-billing and facility-fee enforcement. These are *budget-improving* actions — they raise no taxes and cut no benefits — and are therefore the closest thing to a free lunch in the health ledger after carbon pricing. The reason they remain undone is the subject of Document 01: the health sector is the single largest lobbying spender ($868M of the record $5.08B in 2025, OpenSecrets). Confidence in direction: **HIGH**; in achievable magnitude: **LOW-MEDIUM** (estimates of site-neutral plus negotiation expansion savings range from ~$200B to ~$500B over a decade depending on design).

**Watch indicators.** Maternal mortality (CDC NCHS annual), uninsured rate (Census/CPS and NHIS quarterly), Medicare Advantage payment-benchmark audits (MedPAC reports — if MA overpayment persists above ~6–8%, the privatized-administration layer is absorbing the marginal dollar instead of patients), and life expectancy at birth versus the OECD trendline. **Tripwire:** if coverage expands but preventable-mortality does not begin converging toward peers within ~5 years, the binding constraint is prices and delivery, not coverage — shift marginal effort from 1a/1b toward 1c.

---

## Rank 2 — Retirement-system solvency: a scheduled, statutory benefit cut in 2032

**The gap.** Under current law the OASI trust fund is exhausted in 2032 (CBO, Feb 2026 Outlook), at which point benefits are cut automatically by roughly a fifth for every retiree, survivor, and dependent — the single largest scheduled reduction in American living standards on the books, and unlike most risks in this document, it is *certain* under current law. Confidence: **HIGH**.

**What the optimizer says.** Lifting the OASDI taxable maximum (the payroll cap, $176,100 in 2025) appears in **every scenario permitted to use it** — the cleanest cross-ideological convergence in the entire exercise. It raises on the order of $150–250B/yr (SSA actuaries' range; the model uses $180B), materially extends solvency, and scores progressive on incidence.

**Specific actions.** (2a) Lift or phase out the taxable maximum, with a benefit-formula bend so high earners accrue some additional benefit (precedent: the 1983 Greenspan-commission template of pairing revenue with gradual adjustments). (2b) Pair with a modest, slow long-run adjustment chosen by the enacting coalition (the model is agnostic between options; the *non-negotiable* finding is that acting before 2030 is strictly cheaper than acting after, because the trust-fund arithmetic compounds). Confidence: **HIGH** on the arithmetic, **LOW** on political timing.

**Watch indicators.** The annual SSA Trustees Report exhaustion date; any year it moves earlier than 2032 should accelerate action. **Tripwire:** if no legislation is enacted by the 2030 session, contingency planning for benefit-protection-by-general-revenue (with its own debt consequences, scoreable in this model in seconds) becomes the live question.

---

## Rank 3 — Children and family economic security: the highest-MVPF general lever

**The gap.** Child poverty roughly doubled in 2022 when the expanded Child Tax Credit lapsed (Census SPM series) — a natural experiment demonstrating that the lever works mechanically and reversibly. The US remains a peer-group outlier on child poverty. Confidence: **HIGH** (the SPM series is direct measurement).

**Why the dollar is productive.** The MVPF distribution's upper tail is dominated by investments in low-income children — health coverage, nutrition, income support, early education — where downstream earnings and tax receipts repay much of the outlay. The model encodes this as θ > 1 on `income_security` (equity) and the optimizer responds: income security expands 15–30% in scenarios B through E.

**Specific actions.** (3a) Restore a fully refundable CTC (the single best-measured anti-child-poverty instrument; ~$100B/yr order of magnitude at 2021 design). (3b) Protect SNAP and child-nutrition baselines from the cuts embedded in the 2025 reconciliation law as those provisions phase in. (3c) Expand the EITC phase-in for childless workers (small dollars, well-evidenced labor-supply margin). Confidence: **MEDIUM-HIGH** — the evidence is strong; the ranking below health and retirement reflects only that the corridor is four-of-five scenarios rather than five-of-five.

**Watch indicators.** Census SPM child-poverty release each September; SNAP participation versus eligibility (USDA). **Tripwire:** if a restored CTC shows labor-force-participation losses materially above the CBO-scored range, the design margin (phase-in rate) — not the program — is the thing to revisit.

---

## Rank 4 — Scientific research and public R&D: the long-run growth engine running below replacement

**The gap.** Federal R&D has fallen from ~1.2% of GDP in the mid-1960s to roughly 0.6–0.7% today even as the private-sector return evidence (Jones & Summers 2020; Fieldhouse & Mertens on appropriations shocks) implies social returns to public research far above the government's borrowing cost. The model's `science_space` line carries the highest supply-side growth coefficient in `data.py`. Confidence in underinvestment direction: **MEDIUM-HIGH**; in magnitude: **LOW** (returns estimates span a wide band).

**What the optimizer says.** Science expands 30–50% in every scenario whose objective includes growth or health — including the pragmatic scenario E — because it is the rare line that *raises* the GDP denominator the debt ratio is divided by.

**Specific actions.** (4a) Fund the already-authorized CHIPS & Science Act NSF/DOE-Science targets (authorization without appropriation has left a multi-billion annual gap). (4b) Restore NIH funding at least to its real-2003 peak trajectory. (4c) Protect the statistical agencies (BLS, Census, BEA) — small dollars, but every empirical claim in this repository depends on them; degraded federal statistics are an epistemic risk to evidence-based budgeting itself. Confidence: **MEDIUM**.

**Watch indicators.** Federal R&D as % of GDP (AAAS annual dashboard); NIH payline rates; statistical-agency response rates. **Tripwire:** payline rates below ~8% or a falling Census response rate are leading indicators that the knowledge pipeline and the measurement system are degrading faster than budget tables show.

---

## Rank 5 — Unpriced carbon: the only strictly Pareto-improving revenue instrument on the board

**The gap.** US emissions remain unpriced at the federal level while the EPA's own central estimate of the social cost of carbon is ~$190/tCO₂e — meaning every ton emitted transfers ~$190 of damage onto third parties at a market price of zero. This is the textbook negative externality the project's source document opened with.

**What the optimizer says.** Every scenario permitted a carbon price drives it to the model's $80/t ceiling — the optimizer treats it as the cheapest revenue in the system (marginal excess burden ≈ 0.05 versus 0.30–0.35 for income taxes) *plus* an externality credit. A Pigouvian tax is the only instrument that raises money while *correcting* a price rather than distorting one. Confidence in direction: **HIGH** (this is among the least contested propositions in all of economics); in the $/t level and coverage: **MEDIUM**.

**Specific actions.** (5a) An economy-wide upstream carbon fee starting at $40–80/t with a border adjustment (which also addresses the competitiveness/leakage objection that drives the symbiosis constraint). (5b) Rebate a substantial share per-capita to neutralize the regressivity the model's equity term penalizes (−0.3 index points per $100B unrebated). Confidence: **HIGH** on design knowledge, **LOW** on near-term enactability — which is exactly why it ranks 5th rather than higher despite the cleanest economics.

**Watch indicators.** EU CBAM implementation (it imposes a de facto carbon price on US exporters anyway, converting the question from *whether* to *who collects*); state-level program revenues (California, RGGI) as design evidence.

---

## Rank 6 — The tax-expenditure ledger: the $2.3 trillion budget nobody votes on

**The gap.** Tax expenditures — exclusions, deductions, preferential rates — total roughly $2.3T in FY2026 (JCT JCX-45-25), about 44% of all federal revenue and more than defense and nondefense discretionary spending *combined*. They are spending in economic substance, skew heavily toward the top of the income distribution (the largest items are pension exclusions, preferential capital-gains rates, and the employer health exclusion), and unlike appropriations they renew automatically without annual votes. Document 01 identifies this channel as the largest single artery of the government–business entanglement. Confidence: **HIGH** (JCT publishes the ledger annually).

**Specific actions.** (6a) Subject the ten largest tax expenditures to the same sunset-and-review discipline as discretionary programs (a process reform, ~zero direct cost). (6b) Cap the value of itemized deductions and the employer-health exclusion at a fixed rate (28%-style cap) — raising revenue mostly from the top decile while leaving rates untouched; the model's `d_cap` package is a partial stand-in. (6c) Publish a unified budget presentation in which tax expenditures appear beside outlays, so the budget resolution debates the whole $9.7T claim on resources rather than the $7.4T half. Confidence: **MEDIUM** — the revenue is real, but each line item has an organized constituency, which is the lobbying economics of Document 01 in action.

**Watch indicators.** The annual JCT estimate's growth rate versus GDP (it has outpaced it); any new expenditure enacted without a sunset is the ratchet turning again.

---

## Rank 7 — Housing affordability: large welfare stakes, weaker federal levers

**The gap.** Roughly half of renter households are cost-burdened (HUD/ACS), homelessness has reached record measured levels, and housing scarcity propagates into every other ranked area (health outcomes, child development, labor mobility). Confidence in the gap: **HIGH**.

**Why ranked 7th despite the stakes.** The binding constraint is predominantly *local land-use regulation*, which the federal budget can influence only at the margin — the model's `housing_community` line expands ~45% in scenario B but the honest annotation is that federal dollars buy less here per unit of problem than in ranks 1–4. Specific actions: (7a) expand Housing Choice Vouchers toward entitlement-funding levels (currently ~1 in 4 eligible households served — a lottery, not a safety net); (7b) condition federal infrastructure and CDBG funds on local zoning reform (the federal government's strongest lever over the actual constraint); (7c) LIHTC reform to lower per-unit cost. Confidence: **MEDIUM**.

**Watch indicators.** HUD point-in-time homelessness counts; rent-to-income ratios in the ACS; housing-unit completions versus household formation.

---

## Rank 8 — Administrative capacity and program delivery: the meta-lever

**The gap.** Several of the actions above fail in practice not for lack of money but for lack of state capacity: IRS service levels determine whether a restored CTC reaches eligible families; SSA staffing determines disability-determination backlogs; procurement capacity determines whether infrastructure dollars become assets or cost overruns. The model encodes this as constraint C4 — the 12% reallocation-capacity cap — and that constraint **binds in every scenario**, which is the mathematical way of saying delivery capacity, not ideology, is often the active limit. Confidence: **MEDIUM-HIGH**.

**Specific actions.** (8a) Multi-year (not annual) funding for IRS modernization and taxpayer service — CBO scores IRS funding as *revenue-positive* (roughly $2 returned per $1 over a decade through closing the ~$600B/yr gross tax gap), making it, with carbon pricing and health-price reform, the third budget-improving item on this list. (8b) Direct-file expansion and automatic-enrollment plumbing for EITC/CTC. (8c) Federal hiring-pipeline reform for procurement and actuarial roles. **Watch indicators:** IRS phone-answer and audit-coverage rates; SSA backlog statistics; the share of enacted infrastructure funds actually outlaid each year.

---

## 9. What deliberately did *not* make the list, and why

Honesty about omissions is part of the method. **Defense posture** is excluded not because it is unimportant but because the evidence base for "underserved" runs through classified threat assessment this framework cannot audit; the model treats defense via the symbiosis floor and lets scenarios express values above it. **Broad student-debt relief** scores poorly on the MVPF criterion relative to ranks 1–4 (benefits skew toward higher-lifetime-income households) even though targeted relief for defrauded and low-balance borrowers scores well. **General infrastructure beyond the IIJA tail** ranks below science on measured returns. Readers who disagree are invited to do exactly what this repository exists for: change the θ-weights and the evidence parameters in `model/data.py`, re-run, and publish the diff.

## 10. The one-paragraph version for a lawmaker's office

Three actions are supported by essentially every value system this engine can express — expanded public-health and child-health investment, payroll-cap reform ahead of the 2032 OASI exhaustion, and carbon pricing — and three more are budget-*improving* rather than budget-costing: health-price reform, IRS capacity, and tax-expenditure review. A coalition that enacted only the intersection of this list with its own values would still, per the arithmetic of Document 04, leave the country measurably better served than the current-law baseline, which is — it bears repeating — the most radical option on the table: 121% debt-to-GDP by 2036 with the largest measured health-outcome gap in the developed world left untreated.
