"""
Sanity tests for the suitcordance operator.

Runs with plain `python tests/test_operator.py` -- no pytest needed. These are
not unit tests of arithmetic; they check the properties the operator is supposed
to have, so that a refit or a reformulation cannot quietly break them.
"""

import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from panvas.beds import BEDS, BED_KEYS
from panvas.devices import BY_KEY, candidates_for
from panvas.suitcordance import (Lesion, Plan, evaluate, gamma_star, THETA,
                                 REFERENCE_CASE)
from panvas.anchors import ANCHORS
from panvas.agent import HARNESS_V0, propose, oracle

FAILURES = []


def check(name, cond, detail=""):
    if cond:
        print(f"  ok    {name}")
    else:
        print(f"  FAIL  {name}  {detail}")
        FAILURES.append(name)


COR = Lesion(bed="coronary", d_prox=3.2, d_dist=2.95, length=22,
             calcium=0.30, diabetes=True)


def test_bounds_and_composition():
    print("\nbounds and composition")
    r = evaluate(COR, Plan("des_ultrathin", 3.0, 28))
    for k, arr in zip("GMHB", [r.G, r.M, r.H, r.B]):
        check(f"Gamma_{k} within [0,1]",
              bool(np.all(arr >= 0) and np.all(arr <= 1.0 + 1e-9)),
              f"min {arr.min():.4f} max {arr.max():.4f}")
    check("Gamma_sc within [0,1]",
          bool(np.all(r.gamma >= 0) and np.all(r.gamma <= 1.0 + 1e-9)))

    w = np.array(r.weights)
    recomposed = r.G ** w[0] * r.M ** w[1] * r.H ** w[2] * r.B ** w[3]
    check("Gamma_sc is the weighted geometric mean of its axes",
          bool(np.allclose(recomposed, r.gamma, atol=1e-10)))
    check("axis weights sum to 1", abs(w.sum() - 1.0) < 1e-12)

    check("Gamma_sc never exceeds its worst axis",
          bool(np.all(r.gamma <= np.maximum.reduce([r.G, r.M, r.H, r.B]) + 1e-9)))


def test_time_constant():
    print("\ntime constant")
    r = evaluate(COR, Plan("des_ultrathin", 3.0, 28))
    check("tau_sc is finite and inside the horizon",
          np.isfinite(r.tau_sc) and 0 < r.tau_sc <= r.t[-1], f"tau_sc {r.tau_sc}")
    check("mismatch dose equals 1 - mean(Gamma) to quadrature error",
          abs(r.deficit - float(np.mean(1 - r.gamma))) < 0.01,
          f"{r.deficit:.4f} vs {float(np.mean(1 - r.gamma)):.4f}")

    # a resorbable scaffold and a balloon must not share a time constant
    brs = evaluate(COR, Plan("brs_plla", 3.0, 28))
    dcb = evaluate(COR, Plan("dcb_ptx_cor", 3.0, 26, prep="scoring"))
    check("a resorbable scaffold has a longer tau_sc than a drug-coated balloon",
          brs.tau_sc > dcb.tau_sc, f"BRS {brs.tau_sc:.0f} vs DCB {dcb.tau_sc:.0f}")


def test_no_implant_is_a_perfect_compliance_match():
    print("\nstructural consequences of the model")
    for key in ("dcb_ptx_cor", "poba"):
        r = evaluate(COR, Plan(key, 3.0, 26))
        check(f"{key}: Gamma_M compliance term is perfect (nothing implanted)",
              bool(np.allclose(r.M, 1.0, atol=1e-9)),
              f"min {r.M.min():.4f}")


def test_sizing_monotonicity():
    print("\nsizing")
    ref = COR.d_ref
    correct = evaluate(COR, Plan("des_ultrathin", 3.0, 28)).G[0]
    under = evaluate(COR, Plan("des_ultrathin", 2.25, 28)).G[0]
    over = evaluate(COR, Plan("des_ultrathin", 4.0, 28)).G[0]
    check("a correctly sized device beats a badly undersized one on Gamma_G",
          correct > under, f"{correct:.3f} vs {under:.3f}")
    check("a correctly sized device beats a badly oversized one on Gamma_G",
          correct > over, f"{correct:.3f} vs {over:.3f}")

    miss = evaluate(COR, Plan("des_ultrathin", 3.0, 14)).G[0]    # shorter than lesion
    check("geographic miss is penalised", miss < correct, f"{miss:.3f} vs {correct:.3f}")


def test_calcium_and_preparation():
    print("\ncalcium and preparation")
    hard = Lesion(bed="coronary", d_prox=3.2, d_dist=2.95, length=22, calcium=0.85)
    bare = evaluate(hard, Plan("des_ultrathin", 3.0, 28)).risk_12m
    prepped = evaluate(hard, Plan("des_ultrathin", 3.0, 28, prep="ivl")).risk_12m
    check("preparing heavy calcium lowers predicted risk",
          prepped < bare, f"{prepped:.3f} vs {bare:.3f}")

    soft = Lesion(bed="coronary", d_prox=3.2, d_dist=2.95, length=22, calcium=0.05)
    check("more calcium raises predicted risk, other things equal",
          evaluate(hard, Plan("des_ultrathin", 3.0, 28)).risk_12m
          > evaluate(soft, Plan("des_ultrathin", 3.0, 28)).risk_12m)


def test_drug_beats_bare():
    print("\ndrug")
    des = evaluate(COR, Plan("des_ultrathin", 3.0, 28)).risk_12m
    bms = evaluate(COR, Plan("bms", 3.0, 28)).risk_12m
    check("a drug-eluting stent beats a bare-metal stent in the same lesion",
          des < bms, f"{des:.3f} vs {bms:.3f}")


def test_reference_anchoring():
    print("\nper-bed reference anchoring")
    for b in BED_KEYS:
        g = gamma_star(b, THETA)
        check(f"{b}: Gamma* is a plausible match level", 0.05 < g < 1.0, f"{g:.3f}")
    kw_les, kw_plan = REFERENCE_CASE["coronary"]
    r = evaluate(Lesion(bed="coronary", **kw_les), Plan(**kw_plan))
    lam0 = BEDS["coronary"].lambda0
    check("the coronary reference case reproduces its own lambda0 within 2 points",
          abs(r.risk_12m - lam0) < 0.02, f"{r.risk_12m:.3f} vs {lam0:.3f}")


def test_calibration_quality():
    print("\ncalibration")
    errs = []
    for name, les, plan, obs, w, _src in ANCHORS:
        errs.append(abs(evaluate(les, plan).risk_12m - obs))
    mae = float(np.mean(errs))
    check("anchor MAE stays below 5 percentage points", mae < 0.05, f"MAE {mae:.4f}")
    check("no anchor is off by more than 25 percentage points",
          max(errs) < 0.25, f"worst {max(errs):.4f}")


def test_harness_and_oracle():
    print("\nharness")
    for bed in BED_KEYS:
        lo, hi = BEDS[bed].d_ref
        les = Lesion(bed=bed, d_prox=(lo + hi) / 2 * 1.03, d_dist=(lo + hi) / 2 * 0.97,
                     length=25 if bed == "coronary" else 60, calcium=0.35)
        plan = propose(les, HARNESS_V0)
        check(f"{bed}: the starting harness produces a usable plan",
              plan.device in BY_KEY and plan.nominal_d > 0)
        o_risk, _o_plan = oracle(les)
        check(f"{bed}: the oracle is no worse than the harness",
              o_risk <= evaluate(les, plan, horizon=380, dt=10.0).risk_12m + 1e-9)


def main():
    test_bounds_and_composition()
    test_time_constant()
    test_no_implant_is_a_perfect_compliance_match()
    test_sizing_monotonicity()
    test_calcium_and_preparation()
    test_drug_beats_bare()
    test_reference_anchoring()
    test_calibration_quality()
    test_harness_and_oracle()

    print()
    if FAILURES:
        print(f"{len(FAILURES)} check(s) FAILED: {', '.join(FAILURES)}")
        sys.exit(1)
    print("all checks passed")


if __name__ == "__main__":
    main()
