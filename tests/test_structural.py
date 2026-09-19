"""
Regression tests for the structural defects fixed on 19 September 2026.

Each of these encodes a property the operator did NOT have until that date. They
exist so that a refit, a reformulation or a careless edit cannot quietly restore
the old behaviour, which in every case produced numbers that looked reasonable at
the endpoint and were wrong underneath.

Run through tests/test_operator.py, which supplies the `check` reporter.
"""

import numpy as np

from panvas.anchors import ALL_ANCHORS
from panvas.suitcordance import (Lesion, Plan, evaluate, check_plan, mld_pre,
                                 inflated_diameter, deployed_diameter,
                                 NIH_RADIUS_FRAC, THETA,
                                 _injury_index, _drug_effect, _neointima_um,
                                 REFERENCE_CASE)


def _plan_validity(check):
    print("\nplan validity")
    bad = []
    for a in ALL_ANCHORS:
        try:
            check_plan(a.lesion, a.plan)
        except ValueError as exc:
            bad.append(f"{a.name}: {exc}")
    for bed, (lk, pk) in REFERENCE_CASE.items():
        try:
            check_plan(Lesion(bed=bed, **lk), Plan(**pk))
        except ValueError as exc:
            bad.append(f"REFERENCE[{bed}]: {exc}")
    check("every anchor and reference case names a device it can physically be",
          not bad, "; ".join(bad))

    caught = False
    try:
        check_plan(Lesion(bed="renal", d_prox=5.6, d_dist=5.2, length=15),
                   Plan("bms", 99.0, 18))
    except ValueError:
        caught = True
    check("check_plan rejects a diameter outside the catalogue range", caught)


def _balloon_mechanics(check):
    """The axis that carries dissection must not be inert for balloons."""
    print("\nmechanical axis on balloons")
    les = Lesion(bed="btk", d_prox=2.9, d_dist=2.9, length=60, calcium=0.5,
                 stenosis=0.80)
    at_size = evaluate(les, Plan("poba", 2.90, 70)).M.min()
    mid = evaluate(les, Plan("poba", 3.30, 70)).M.min()
    over = evaluate(les, Plan("poba", 3.75, 70)).M.min()
    check("a 1:1 balloon is not charged overstretch", at_size > 0.99, f"{at_size:.4f}")
    check("a grossly oversized balloon is charged overstretch",
          over < 0.75, f"{over:.4f}")
    check("Gamma_M falls monotonically as a balloon is oversized",
          at_size > mid > over, f"{at_size:.3f} > {mid:.3f} > {over:.3f}")


def _stenosis_reaches_the_operator(check):
    print("\nstenosis severity")
    mild = Lesion(bed="coronary", d_prox=3.0, d_dist=3.0, length=15, stenosis=0.40)
    tight = Lesion(bed="coronary", d_prox=3.0, d_dist=3.0, length=15, stenosis=0.95)
    plan = Plan("des_ultrathin", 3.0, 20)
    r_mild = evaluate(mild, plan).risk_12m
    r_tight = evaluate(tight, plan).risk_12m
    check("a tighter lesion carries more predicted risk", r_tight > r_mild,
          f"{r_tight:.5f} against {r_mild:.5f}")
    check("pre-procedure MLD follows the stenosis",
          mld_pre(tight) < mld_pre(mild) < 3.0,
          f"{mld_pre(tight):.2f} < {mld_pre(mild):.2f}")

    inj = _injury_index(tight, Plan("poba", 3.0, 20))
    check("a 1:1 balloon in a tight lesion delivers real barotrauma",
          inj > 0.1, f"injury index {inj:.3f}")


def _recoil_takes_back_gain_not_diameter(check):
    print("\nrecoil")
    les = Lesion(bed="sfa", d_prox=5.5, d_dist=5.5, length=80, stenosis=0.80)
    d0 = float(deployed_diameter(les, Plan("poba", 5.5, 100), np.array([0.0]))[0])
    m0 = mld_pre(les)
    inflate = inflated_diameter(les, Plan("poba", 5.5, 100))
    check("a balloon's acute result sits between the pre-procedure MLD and inflation",
          m0 < d0 < inflate, f"{m0:.2f} < {d0:.2f} < {inflate:.2f}")
    resid = 1 - d0 / les.d_ref
    check("plain angioplasty leaves a plausible residual stenosis (10-45%)",
          0.10 < resid < 0.45, f"{resid:.0%}")


def _neointima_is_physiological(check):
    print("\nneointimal magnitude")
    worst = (0.0, "", 0.0)
    for a in ALL_ANCHORS:
        if not a.include:
            continue
        dd = float(np.mean(deployed_diameter(a.lesion, a.plan,
                                             np.arange(0.0, 381.0, 10.0))))
        inj = _injury_index(a.lesion, a.plan)
        de = _drug_effect(a.lesion, a.plan, np.arange(0.0, 181.0, 5.0), THETA)
        nih = float(_neointima_um(a.lesion, np.array([1e6]), inj,
                                  float(de.mean()), THETA, dd)[0])
        frac = nih / (dd / 2.0 * 1000.0)
        if nih > worst[0]:
            worst = (nih, a.name, frac)
    check("no anchor implies more than 900 um of neointima per side",
          worst[0] < 900, f"worst {worst[1]} {worst[0]:.0f} um")
    check("no anchor's neointima exceeds the radius ceiling",
          worst[2] <= NIH_RADIUS_FRAC + 1e-6, f"{worst[2]:.3f}")


# Known, measured, and NOT fixed: six anchors still reach the Gamma_H floor within
# the first year, so for those six the hemodynamic axis reports a clip rather than
# physics. It was nine of twelve before the structural fixes of 2026-09-19, and one
# of twelve at the tightest setting in sweep_bounds.py -- which costs 1.95 points of
# MAE and switches the mechanical axis off. Six is where the shipped constants sit.
#
# This asserts the measured number rather than the number we want, so a regression is
# caught while the defect stays visible. Writing it as <= 2 and letting it fail, or as
# <= 12 and letting it pass, would both be worse. See KNOWN_DEFECTS.md D2; the target
# is <= 2 and reaching it is open work.
GAMMA_H_CLIP_KNOWN = 6


def _gamma_h_is_not_living_on_a_clip(check):
    print("\nGamma_H clipping (known defect, see KNOWN_DEFECTS.md D2)")
    clipped = [a.name for a in ALL_ANCHORS if a.include
               and evaluate(a.lesion, a.plan, horizon=380, dt=5.0).H[-1] <= 0.08]
    check(f"no more anchors on the Gamma_H floor than the {GAMMA_H_CLIP_KNOWN} "
          f"already documented",
          len(clipped) <= GAMMA_H_CLIP_KNOWN, f"{len(clipped)} of 12: {clipped}")
    if len(clipped) < GAMMA_H_CLIP_KNOWN:
        print(f"  note  {len(clipped)} of 12 now, down from {GAMMA_H_CLIP_KNOWN}. "
              f"Lower GAMMA_H_CLIP_KNOWN so the gain is locked in.")


def run(check):
    _plan_validity(check)
    _balloon_mechanics(check)
    _stenosis_reaches_the_operator(check)
    _recoil_takes_back_gain_not_diameter(check)
    _neointima_is_physiological(check)
    _gamma_h_is_not_living_on_a_clip(check)
