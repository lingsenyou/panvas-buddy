# JavaScript / Python parity check

The browser workbench re-implements the operator in JavaScript. That is a second
implementation, so it can drift from the calibrated Python one, and if it does the
public page would show numbers the paper does not support.

`build_site.py` removes most of that risk by lifting the operator source out of the
workbench verbatim rather than maintaining a second copy, but it does not prove the two
agree numerically, and it says nothing about whether the page is carrying the CURRENT
fitted constants. This check does both.

## Result, 2026-09-19 (after the refit on the audited anchor set)

Checked against the live page at <https://lingsenyou.com/suitcordance/>, i.e. what a
reader actually gets, not a local build.

First, that the page carries the current model:

| | page | Python |
|---|---|---|
| β (hazard slope) | 5.435936869408597 | 5.435937 |
| k_comp | 0.05000000000000001 | 0.05 |
| λ₀ coronary | 0.02 | 0.02 |

Then, two lesions evaluated end to end on the same grid (dt = 5, horizon = 730):

| case | Γ(0) | τ_sc (days) | risk₁₂ |
|---|---|---|---|
| coronary, ultrathin DES 3.0×28 | 0.857256 / 0.857256 | 261.120 / 261.120 | 0.016371 / 0.016371 |
| SFA, nitinol 6.0×150 + lithotripsy | 0.366967 / 0.366967 | 164.054 / 164.054 | 0.128505 / 0.128505 |

Identical to every printed digit.

## Result, 2026-09-18 (first build, superseded)

Five lesions across four beds agreed to ≤5e-7 on Γ and risk and ≤4e-4 days on τ_sc.
That build has since been replaced: the anchor audit changed the anchors, all six bed
baseline rates and the fitted constants, so those numbers no longer describe the
published page.

## How to repeat it

1. `python tests/make_js_reference.py` writes `out/js_reference.json` and
   `out/js_check.js`.
2. Open the workbench and paste `out/js_check.js` into the browser console. It calls
   the page's own `evaluateCase` and prints the per-field differences.
3. Also check `MODEL.theta.beta` and `MODEL.beds.coronary.lambda0` against
   `panvas/theta.json` and `panvas/beds.py`. Matching trajectories with stale constants
   is the failure mode that looks like success.
4. Any difference above 1e-5 on Γ, the mismatch dose or the risk means the page and the
   paper have diverged. Rebuild with `python export_model.py && python build_site.py`
   and re-check before publishing anything.

Re-run this whenever `panvas/suitcordance.py`, `panvas/theta.json`, `panvas/beds.py` or
the workbench source changes — which, after a recalibration, is all four at once.
