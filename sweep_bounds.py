"""
The accuracy / plausibility frontier.

A pre-submission review found the operator reproducing its 12-month endpoints
through a path that cannot happen in an artery: up to 2.4 mm of neointima per
side, and nine of twelve anchors with the hemodynamic axis pinned at its
numerical floor for most of year one. Fixing that is not a matter of one better
parameter set -- it is a trade-off, and this script measures it.

Two internal quantities can be made more or less degenerate:

    nih_max_um   the neointimal asymptote at unit drive. Unbounded it goes to
                 822 um, which with the drive multiplier implies thicknesses no
                 artery has.
    k_lumen      the width of the residual-stenosis kernel in Gamma_H. Small
                 values make the kernel so sharp that any lesion with late loss
                 is pushed onto the floor, at which point Gamma_H reports a clip
                 rather than physics.

For each setting we refit all eleven constants from scratch and report four
things: how well the anchors are reproduced, how impossible the internals are,
how much of year one the explaining axis spends on a clip, and whether the
mechanical axis is doing any work (by ablating it and refitting nothing).

Runs several full calibrations; budget half an hour.
"""

import copy
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import calibrate
import panvas.suitcordance as SC
from panvas.anchors import ALL_ANCHORS
from panvas.devices import BY_KEY
from panvas.suitcordance import (evaluate, deployed_diameter, _injury_index,
                                 _drug_effect, _neointima_um)

SETTINGS = [
    ("unbounded", (80.0, 900.0), (0.10, 0.80)),
    ("neointima bounded", (40.0, 300.0), (0.10, 0.80)),
    ("+ lumen kernel bounded", (40.0, 300.0), (0.22, 0.80)),
    ("both tight", (40.0, 220.0), (0.28, 0.80)),
]


def diagnose(theta):
    """Accuracy, plausibility, clipping, and whether Gamma_M earns its place."""
    SC._gamma_star_cache.clear()
    used = [a for a in ALL_ANCHORS if a.include]
    err = [abs(evaluate(a.lesion, a.plan, theta=theta).risk_12m - a.value) for a in used]

    worst_nih, worst_ds, clipped = 0.0, 0.0, 0
    for a in used:
        t = np.arange(0.0, 381.0, 5.0)
        dd = deployed_diameter(a.lesion, a.plan, t)
        inj = _injury_index(a.lesion, a.plan)
        de = _drug_effect(a.lesion, a.plan, t, theta)
        nih = float(_neointima_um(a.lesion, t, inj, float(de[:37].mean()),
                                  theta, float(np.mean(dd)))[-1])
        lumen = dd[-1] - 2 * (BY_KEY[a.plan.device].strut_um + nih) / 1000.0
        worst_nih = max(worst_nih, nih)
        worst_ds = max(worst_ds, 100 * (1 - lumen / a.lesion.d_ref))
        if evaluate(a.lesion, a.plan, horizon=380, dt=5.0, theta=theta).H[-1] <= 0.08:
            clipped += 1

    original = SC._gamma_M
    SC._gamma_M = lambda les, plan, t, d_dep, th: np.ones_like(t)
    SC._gamma_star_cache.clear()
    err_ablated = [abs(evaluate(a.lesion, a.plan, theta=theta).risk_12m - a.value)
                   for a in used]
    SC._gamma_M = original
    SC._gamma_star_cache.clear()

    railed = sum(1 for k in calibrate.FIT_KEYS
                 if min(abs(theta[k] - calibrate.BOUNDS[k][0]),
                        abs(theta[k] - calibrate.BOUNDS[k][1]))
                 < 0.01 * (calibrate.BOUNDS[k][1] - calibrate.BOUNDS[k][0]))

    return dict(mae=float(np.mean(err)), worst=float(np.max(err)),
                worst_nih_um=worst_nih, worst_ds_pct=worst_ds,
                clipped=clipped, railed=railed,
                mae_without_gamma_m=float(np.mean(err_ablated)),
                nih_max_um=theta["nih_max_um"], k_lumen=theta["k_lumen"])


def main():
    base = copy.deepcopy(calibrate.BOUNDS)
    rows = []
    for label, nih_bound, lumen_bound in SETTINGS:
        calibrate.BOUNDS = copy.deepcopy(base)
        calibrate.BOUNDS["nih_max_um"] = nih_bound
        calibrate.BOUNDS["k_lumen"] = lumen_bound
        print(f"\n=== fitting: {label}  nih_max_um {nih_bound}, k_lumen {lumen_bound}",
              flush=True)

        x0 = np.array([calibrate.THETA_DEFAULT[k] for k in calibrate.FIT_KEYS])
        lo = np.array([calibrate.BOUNDS[k][0] for k in calibrate.FIT_KEYS])
        hi = np.array([calibrate.BOUNDS[k][1] for k in calibrate.FIT_KEYS])
        x0 = np.clip(x0, lo, hi)

        from scipy.optimize import least_squares
        best, rng = None, np.random.default_rng(0)
        for trial in range(8):
            start = x0 if trial == 0 else lo + rng.random(len(x0)) * (hi - lo)
            res = least_squares(calibrate.residuals, start, bounds=(lo, hi),
                                xtol=1e-10, ftol=1e-10, max_nfev=2500)
            if best is None or res.cost < best.cost:
                best = res
        theta = calibrate.make_theta(best.x)
        d = diagnose(theta)
        d["label"] = label
        d["theta"] = theta
        rows.append(d)
        print(f"    MAE {d['mae']*100:.2f} pts, worst {d['worst']*100:.2f}; "
              f"neointima <= {d['worst_nih_um']:.0f} um, worst 12-mo DS "
              f"{d['worst_ds_pct']:.0f}%; Gamma_H on the clip {d['clipped']}/12; "
              f"{d['railed']}/11 constants on bounds; "
              f"MAE without Gamma_M {d['mae_without_gamma_m']*100:.2f}", flush=True)

    calibrate.BOUNDS = base
    with open("out/bounds_sweep.json", "w", encoding="utf-8") as fh:
        json.dump(rows, fh, indent=1)

    print("\n" + "=" * 92)
    print(f"{'setting':26s} {'MAE':>6s} {'worst':>6s} {'nih um':>7s} {'DS%':>5s} "
          f"{'clip':>5s} {'bnds':>5s} {'Gamma_M earns it':>17s}")
    for d in rows:
        delta = d["mae_without_gamma_m"] - d["mae"]
        verdict = ("yes, by %.2f pts" % (delta * 100)) if delta > 0.0005 else \
                  ("no, costs %.2f" % (-delta * 100)) if delta < -0.0005 else "neutral"
        print(f"{d['label']:26s} {d['mae']*100:6.2f} {d['worst']*100:6.2f} "
              f"{d['worst_nih_um']:7.0f} {d['worst_ds_pct']:5.0f} "
              f"{d['clipped']:>3d}/12 {d['railed']:>3d}/11 {verdict:>17s}")
    print("\nwritten: out/bounds_sweep.json")


if __name__ == "__main__":
    main()
