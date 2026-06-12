/* EPOE — JS-port validation harness.
 * Runs all five scenarios through the JavaScript engine (dashboard/epoe-model.js)
 * and prints headline numbers for side-by-side comparison with the Python
 * SLSQP results in results/summary.csv.
 *
 * Run:  node dashboard/validate.js
 */
const EPOE = require("./epoe-model.js");

function fmt(x, d = 0) { return Number(x).toFixed(d); }

// Baseline sanity check: debt recursion must reproduce CBO 101% -> ~121%.
const base = EPOE.debtPath(new Array(EPOE.NC + EPOE.NT).fill(0));
console.log("Baseline debt path check: " +
  fmt(base.ratios[0] * 100) + "% (2026) -> " +
  fmt(base.ratios[base.ratios.length - 1] * 100) + "% (2036)  [CBO: 101 -> 120]");
console.log("");

const order = ["A_growth_capital", "B_social_welfare", "C_nordic_financing",
               "D_fiscal_consolidation", "E_pragmatic_pareto"];
console.log("scenario                 outlays  revenue  deficit  %GDP  debt36  Uh     Ue     Ug     viol");
for (const name of order) {
  const t0 = Date.now();
  const r = EPOE.solve(EPOE.SCENARIOS[name]);
  const m = r.macro, u = r.U;
  console.log(
    name.padEnd(24) +
    fmt(m.outlays).padStart(7) + fmt(m.revenues).padStart(9) +
    fmt(m.deficit).padStart(9) +
    (fmt(m.deficit / EPOE.GDP_2026 * 100, 1) + "%").padStart(7) +
    (fmt(r.debtRatios[r.debtRatios.length - 1] * 100) + "%").padStart(7) +
    fmt(u.U_health, 1).padStart(7) + fmt(u.U_equity, 1).padStart(7) +
    fmt(u.U_growth, 1).padStart(7) +
    fmt(r.maxViolation, 2).padStart(7) +
    "   (" + ((Date.now() - t0) / 1000).toFixed(1) + "s)");
}
console.log("\nPython SLSQP reference (results/summary.csv):");
console.log("A: 6857/5526/1332 4.2% 107%  Uh -1.9 Ue -2.2 Ug -5.8");
console.log("B: 8211/6663/1548 4.9% 111%  Uh +5.9 Ue +11.0 Ug +6.0");
console.log("C: 8211/7017/1194 3.8% 101%  Uh +6.3 Ue +5.3 Ug +2.4");
console.log("D: 7695/6591/1103 3.5%  98%  Uh +4.3 Ue +8.7 Ug +2.0");
console.log("E: 7801/6603/1198 3.8% 101%  Uh +4.5 Ue +8.3 Ug +2.0");
