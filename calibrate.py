"""
Fit the free constants of the suitcordance operator to the published anchors.

Residuals are taken on the log-odds of the 12-month event rate, so a model that
predicts 4% where 2% was observed is penalised about as much as one that
predicts 40% where 20% was observed.

This is calibration, not validation.  Sixteen anchors and eleven free constants
means the fit is not a test of the model; it only establishes that the operator
CAN reproduce the published spread of outcomes with one shared parameter set
across six arterial beds.  A real test needs held-out patient-level data
(fit_real.py).
"""

import json
import math
import os
import sys

import numpy as np
from scipy.optimize import least_squares

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from panvas.suitcordance import THETA_DEFAULT, risk_12m, _THETA_PATH
from panvas.anchors import ANCHORS

# constants that are fitted, with bounds
FIT_KEYS = ["s_under", "k_comp", "k_stress", "k_fat", "drug_K", "k_short",
            "need_scale", "k_lumen", "k_strut", "nih_max_um", "beta"]
BOUNDS = {
    "s_under": (0.04, 0.25), "k_comp": (0.05, 6.0), "k_stress": (0.05, 4.0),
    "k_fat": (0.20, 12.0), "drug_K": (0.10, 3.0), "k_short": (0.10, 14.0),
    "need_scale": (0.60, 6.0), "k_lumen": (0.10, 0.80), "k_strut": (0.02, 2.0),
    "nih_max_um": (40.0, 300.0), "beta": (1.0, 14.0),
}


def logit(p: float) -> float:
    p = min(max(p, 1e-4), 1 - 1e-4)
    return math.log(p / (1 - p))


def make_theta(x) -> dict:
    th = dict(THETA_DEFAULT)
    for k, v in zip(FIT_KEYS, x):
        th[k] = float(v)
    return th


def residuals(x) -> np.ndarray:
    th = make_theta(x)
    out = []
    for _name, les, plan, obs, w, _src in ANCHORS:
        pred = risk_12m(les, plan, theta=th)
        out.append(w * (logit(pred) - logit(obs)))
    return np.array(out)


def main() -> None:
    x0 = np.array([THETA_DEFAULT[k] for k in FIT_KEYS], dtype=float)
    lo = np.array([BOUNDS[k][0] for k in FIT_KEYS])
    hi = np.array([BOUNDS[k][1] for k in FIT_KEYS])

    best = None
    rng = np.random.default_rng(0)
    for trial in range(12):                     # multistart: the surface is not convex
        start = x0 if trial == 0 else lo + rng.random(len(x0)) * (hi - lo)
        try:
            res = least_squares(residuals, start, bounds=(lo, hi),
                                xtol=1e-10, ftol=1e-10, max_nfev=4000)
        except Exception as exc:                # pragma: no cover
            print("  start", trial, "failed:", exc)
            continue
        cost = float(res.cost)
        if best is None or cost < best.cost:
            best = res
        print(f"  start {trial:2d}  cost {cost:.4f}")

    theta = make_theta(best.x)
    with open(_THETA_PATH, "w", encoding="utf-8") as fh:
        json.dump(theta, fh, indent=2)

    print("\nfitted constants")
    for k in FIT_KEYS:
        print(f"  {k:12s} {THETA_DEFAULT[k]:8.3f} -> {theta[k]:8.3f}")

    print("\nanchor fit (12-month event rate)")
    print(f"  {'anchor':18s} {'observed':>9s} {'predicted':>10s} {'Gamma0':>8s} "
          f"{'tau_sc':>7s} {'worst':>6s}")
    from panvas.suitcordance import evaluate
    err = []
    for name, les, plan, obs, w, _src in ANCHORS:
        r = evaluate(les, plan, theta=theta)
        err.append(abs(r.risk_12m - obs))
        print(f"  {name:18s} {obs:9.3f} {r.risk_12m:10.3f} {r.gamma0:8.3f} "
              f"{r.tau_sc:7.0f} {r.worst_axis():>6s}")
    print(f"\n  mean absolute error {np.mean(err):.4f}   max {np.max(err):.4f}")
    print(f"  written to {_THETA_PATH}")


if __name__ == "__main__":
    main()
