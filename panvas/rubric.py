"""
Rubric composer and scorer.

Follows the ScienceBuddy pattern: a FIXED composer derives task-specific
criteria from the case, each criterion carries a non-negative weight, and the
task score is the weighted mean of criterion satisfaction

    R(plan) = SUM_c w_c * v_c(plan) / SUM_c w_c ,   v_c in [0, 1]

The composer is fixed on purpose.  If the composer could be edited by the same
loop that optimises the harness, the loop would learn to rewrite its own exam.
"""

from __future__ import annotations
from typing import Dict, List, Tuple

from .beds import BEDS
from .devices import BY_KEY
from .suitcordance import Lesion, Plan, evaluate

Criterion = Tuple[str, float, str]      # key, weight, human description


def compose(les: Lesion) -> List[Criterion]:
    """Criteria this particular lesion deserves to be judged on."""
    c: List[Criterion] = [
        ("near_optimal", 1.20,
         "12-month risk within 1.5 percentage points of the best the catalogue allows"),
        ("apposition", 0.90, "Gamma_G at deployment >= 0.75"),
        ("covered", 1.00, "device covers the lesion with a non-negative edge margin"),
        ("not_oversized", 1.00, "device:vessel ratio stays inside the bed's band + 0.15"),
        ("names_weak_axis", 0.35, "the plan reports which axis is worst"),
    ]
    if les.calcium >= 0.55:
        c.append(("prepared_calcium", 1.00,
                  "heavy calcium is modified before anything is implanted"))
    if les.diabetes or les.length >= 25 or BEDS[les.bed].k_neointima >= 1.5:
        c.append(("antiproliferative", 0.80,
                  "a high-drive lesion gets an antiproliferative device"))
    if les.side_branch:
        c.append(("branch_kept", 1.00, "a branch that matters is not covered"))
    if les.bed == "sfa" and les.length >= 150:
        c.append(("flexion_safe", 0.80,
                  "a long femoropopliteal lesion is not bridged with a fatigue-prone implant"))
    if les.d_ref <= 2.5:
        c.append(("small_vessel", 0.60,
                  "a small vessel is considered for a no-implant strategy"))
    return c


def score(les: Lesion, plan: Plan, oracle_risk: float) -> Tuple[float, Dict[str, float]]:
    """Weighted rubric score in [0, 1], plus the per-criterion satisfactions."""
    r = evaluate(les, plan, horizon=380, dt=10.0)
    dev = BY_KEY[plan.device]
    bed = BEDS[les.bed]
    d_ratio = plan.nominal_d / les.d_ref
    margin = (plan.length * plan.n_devices - les.length) / 2.0

    v: Dict[str, float] = {}
    gap = r.risk_12m - oracle_risk
    v["near_optimal"] = 1.0 if gap <= 0.015 else max(0.0, 1.0 - (gap - 0.015) / 0.10)
    v["apposition"] = 1.0 if float(r.G[0]) >= 0.75 else float(r.G[0]) / 0.75
    v["covered"] = 1.0 if margin >= 0.0 else max(0.0, 1.0 + margin / 5.0)
    hi = bed.oversize_band[1] + 0.15
    v["not_oversized"] = 1.0 if d_ratio <= hi else max(0.0, 1.0 - (d_ratio - hi) / 0.25)
    v["names_weak_axis"] = 1.0        # the agent always reports it, see agent.describe
    v["prepared_calcium"] = 1.0 if (plan.prep != "none" or dev.strut_um == 0) else 0.0
    v["antiproliferative"] = 1.0 if dev.drug != "none" else 0.0
    v["branch_kept"] = 0.0 if dev.family == "COVERED" else 1.0
    v["flexion_safe"] = 1.0 if (dev.strut_um == 0 or dev.fatigue_resist >= 0.90) else 0.35
    v["small_vessel"] = 1.0 if dev.strut_um == 0 else 0.5

    crits = compose(les)
    num = sum(w * v[k] for k, w, _ in crits)
    den = sum(w for _, w, _ in crits)
    return num / den, {k: v[k] for k, _, _ in crits}


def score_many(cases, harness, propose_fn, oracle_fn) -> Tuple[float, List[Dict]]:
    """Mean rubric score over a set of cases, plus a per-case record."""
    rows, total = [], 0.0
    for les in cases:
        plan = propose_fn(les, harness)
        orisk, _ = oracle_fn(les)
        s, detail = score(les, plan, orisk)
        total += s
        rows.append(dict(bed=les.bed, device=plan.device, score=round(s, 4),
                         detail=detail))
    return total / max(1, len(cases)), rows
