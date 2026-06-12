# 02 — The Fiscal Baseline: Every Dollar In, Every Dollar Out (FY2026)

*The real numbers, from the statutory scorekeepers, with confidence ratings. This document is the data contract for `model/data.py`: anything asserted there is defended here.*

---

## 1. The closed books: FY2025 actuals

Fiscal Year 2025 (October 1, 2024 – September 30, 2025) is the last fully closed year, per the Treasury's Final Monthly Treasury Statement and CBO's reconciliation:

| Quantity | FY2025 Actual | Source |
|---|---|---|
| Total receipts | **$5.235 trillion** | Treasury Final MTS (Sept 2025) |
| Total outlays | **$7.010 trillion** | Treasury Final MTS |
| Deficit | **$1.775 trillion** (≈5.8% GDP) | Treasury; Treasury *Financial Report* FY2025 |
| Net interest | **>$1.0 trillion — first time in history** | CBO Monthly Budget Review, Nov 2025 |

Receipts by source, FY2025 actual ($B): individual income **2,656**; payroll **1,748**; corporate income **452**; customs duties **195** (sharply elevated by the 2025 tariff regime — nearly triple FY2024's $77B); all other **183**. Outlays by program, FY2025 actual ($B): Social Security **1,575**; Medicare **988**; Medicaid **668**; other federal health (ACA, CHIP) **164**; other mandatory **773**; defense discretionary **893**; nondefense discretionary **980**; net interest **~970–1,010** (gross-vs-net presentation differs across tables). *(Sources: Treasury MTS; CBO; CRFB tabulation of the February 2026 baseline.)*

Two FY2025 anomalies a careful reader should know about, because they distort naive year-over-year comparisons: the Department of Education's outlays *fell 87 percent*, dominated by a one-time $131B downward re-estimate after the 2025 reconciliation act restructured student loans; and FDIC outlays swung $68B negative as failed-bank assets were liquidated. Neither represents a real change in services delivered. This is why the model's baseline is built on CBO's forward FY2026 projection rather than naive extrapolation of FY2025.

## 2. The open year: FY2026 current-law baseline (the model's anchor)

From CBO's *Budget and Economic Outlook: 2026 to 2036* (February 11, 2026), reflecting laws in place as of January 14, 2026:

| Quantity | FY2026 Baseline | % of GDP | Confidence |
|---|---|---|---|
| Revenues | **$5.6 trillion** | 17.5% | HIGH |
| Outlays | **$7.4 trillion** | 23.3% | HIGH |
| Deficit | **~$1.8–1.9 trillion** | 5.8% | HIGH |
| Mandatory outlays | **$4.5 trillion** (+$362B, +9%) | — | HIGH |
| Discretionary outlays | **$1.9 trillion** (+$8B; continuing resolution) | — | HIGH |
| Net interest | **~$1.03 trillion** | 3.3% | HIGH |
| Debt held by the public, end-FY2026 | **~$32.1 trillion** | ~101% | HIGH |
| Implied GDP | **~$31.8 trillion** | — | HIGH (derived) |

The decade trajectory under current law: deficits grow from 5.8% of GDP (2026) to **6.7%** (2036); debt held by the public reaches **120% of GDP by 2036**, surpassing the 1946 record (106%) around 2030; the deficit total for 2026–2035 is **$23.1 trillion**; and the Social Security OASI trust fund is **exhausted in 2032** — at which point, under current law, benefits are cut automatically to match incoming payroll revenue. Net interest grows from 3.3% to **4.6% of GDP**, while the *primary* deficit actually shrinks (2.6% → 2.1%): the debt problem is increasingly an interest-compounding problem, which is what makes early action mathematically cheaper than late action.

Three policy shocks moved this baseline relative to a year earlier (CBO's decomposition): the 2025 reconciliation act (P.L. 119-21) **added $4.7 trillion** to ten-year deficits; the 2025 tariff regime **subtracted $3.0 trillion**; immigration-related administrative actions **added $0.5 trillion**. The tariff line carries the highest legal risk of any revenue source in the baseline — it has been actively litigated — and the model treats `customs` accordingly (MEDIUM confidence, stress-tested in Document 04).

## 3. Where the model's category table comes from

CBO publishes HIGH-confidence *totals* (mandatory, discretionary, net interest; revenues by major source) but the public summary does not carve FY2026 into the 18 categories the optimizer manipulates. The disaggregation procedure, fully reproducible: start from FY2025 actuals by program; apply CBO's published FY2026 growth increments (Social Security +$91B → **$1,666B**; Medicare +$75B → **$1,063B**; Medicaid +$40B → **$700B** [rounded]; student loans +$89B; veterans +$49B; discretionary held ~flat by the CR); split nondefense discretionary across ten functional lines using OMB Historical Tables function shares; and close the identity with an explicit reconciling line (`offsetting_receipts = −$389B`) so the eighteen lines plus net interest sum to **exactly $7,400B**. Revenues are handled identically, summing to exactly $5,600B. Consequence for interpretation: **totals inherit CBO's HIGH confidence; individual category splits are MEDIUM; the two residual lines (`other_mandatory`, `general_gov_other`, `offsetting_receipts`) are LOW and are deliberately given the widest uncertainty treatment.** Every line's rating and rationale is written next to the number in `model/data.py`.

## 4. The income side, structurally

Federal revenue is, to first order, a tax on labor: individual income taxes (~50%) plus payroll taxes (~32%) are both predominantly levied on wages, while corporate income tax contributes ~8.6% of revenue (≈1.5% of GDP, versus a mid-20th-century norm above 3%). The deficit is financed by issuing Treasury securities — the $1.8T flow that becomes the $32T stock, on which the >$1T interest line is paid, completing the loop that the debt-dynamics equation in Document 03 formalizes. Two structural facts deserve a lawmaker's attention because they are arithmetic, not ideology. First, the JCT's $2.3T of annual tax expenditures means the *effective* tax code is roughly 30% smaller than the statutory one; base-broadening is therefore a mathematically real third option beside "raise rates" and "cut spending." Second, the payroll tax stops at the taxable maximum ($176,100 in 2025, indexed), which is why earnings above it — the fastest-growing slice of national income — contribute nothing to the OASI fund whose 2032 exhaustion the baseline projects. Whether to change either fact is a values question (and the scenarios in Document 04 disagree about it); *that* both facts exist is not.

## 5. Standing corrections to the source document

For the intellectual-honesty record, the project's source sketch contained baseline figures that this document supersedes or confirms: revenues $5.6T ✓ (confirmed); outlays $7.4T ✓; deficit $1.9T ✓; debt held by the public "$32.1T baseline" — **confirmed, with the clarification** that this is the projected *end-of-FY2026* stock (~101% of GDP), not a prior-year figure; "Corporate income taxes $452B" was the FY2025 *actual* — the FY2026 baseline is ~$480B; and "Customs & other fees ~$380B" conflated customs (~$330B) with other receipts. The sketch's structure survived contact with the primary sources essentially intact, which is to its credit.
