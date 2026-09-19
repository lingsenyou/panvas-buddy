# JavaScript / Python parity check

The browser workbench re-implements the operator in JavaScript. That is a second
implementation, so it can drift, and if it does the public page shows numbers the paper
does not support.

`build_site.py` removes most of that risk by lifting the operator source out of the
workbench rather than maintaining a second copy, but it does not prove the two agree
numerically, and it says nothing about whether the page is carrying the CURRENT fitted
constants. This check does both, against the live page rather than a local build.

## Result, 2026-09-19, after the structural repairs and refit

Constants first, because matching trajectories with stale constants is the failure that
looks like success:

| | published page | Python |
|---|---|---|
| nih_max_um | 299.99999198414577 | 300.0 |
| k_lumen | 0.1481197551583594 | 0.148120 |
| β | 6.14905607326079 | 6.149056 |
| NIH_RADIUS_FRAC | 0.6 | 0.6 |
| `mldPre` present | yes | — |

Then three lesions end to end (dt = 5, horizon = 730). Largest absolute differences:

| case | ΔΓ(0) | ΔΓ(730) | Δτ_sc (days) | Δ dose | Δ risk₁₂ |
|---|---|---|---|---|---|
| coronary, ultrathin DES | 2.2e-7 | 3.8e-7 | 4.0e-4 | 8.4e-8 | 1.4e-7 |
| coronary, PLLA BRS + scoring + post-dil | 2.8e-8 | 4.3e-7 | 2.3e-4 | 4.9e-7 | 7.6e-8 |
| SFA, nitinol + lithotripsy | 4.7e-7 | 4.2e-7 | 7.2e-5 | 4.3e-7 | 1.2e-7 |

Agreement to the precision the six-decimal reference can resolve.

## Two things this check caught, both worth keeping

**A stale page.** The first run after the refit returned `nih_max_um` 822 and no
`nihRadiusFrac` at all — the pre-repair constants — because GitHub Pages had not finished
deploying and the browser was holding a cached copy. Re-requesting with a cache-busting
query fixed it. **Always check the constants, not only the trajectories**, and re-check
after a deploy rather than before.

**An inconsistent harness.** The second run still differed by about 0.5%, which looked
like a port bug and was not: the JavaScript side was constructing its lesion with
`stenosis: 0.8` from a hard-coded defaults object while Python used the dataclass default
of 0.75. That had been harmless for weeks, because `stenosis` was declared and never
read. The moment it started reaching the operator it became a silent mismatch between the
two implementations *of the test*.

`tests/make_js_reference.py` now emits **every** lesion field, defaults included, and the
snippet builds its lesion only from what the reference supplies. A parity check whose two
sides disagree about a default is worse than no parity check, because it reports a
difference that is not there and hides one that is.

## How to repeat it

1. `python tests/make_js_reference.py` writes `out/js_reference.json` and
   `out/js_check.js`.
2. Open the workbench, hard-reload it, and paste `out/js_check.js` into the console.
3. Check `MODEL.theta.nih_max_um`, `MODEL.theta.beta` and `MODEL.nihRadiusFrac` against
   `panvas/theta.json` and `panvas/suitcordance.py` before believing any trajectory.
4. Any difference above 1e-5 on Γ, the mismatch dose or the risk means the page and the
   paper have diverged. `python rebuild_all.py`, push, wait for the deploy, re-check.

Re-run whenever the operator, its constants, the bed parameters or the workbench source
change — which, after a recalibration, is all four at once.
