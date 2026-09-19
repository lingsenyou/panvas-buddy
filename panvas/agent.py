"""
The device-selection agent, and the editable harness that drives it.

This mirrors the ScienceBuddy separation: the *model* is the suitcordance
operator (panvas/suitcordance.py, constants fitted in calibrate.py), and the
*harness* is everything that decides how the model is used -- the sizing rule,
the thresholds, which skills are switched on.  The harness is data, not code,
so it can be edited, versioned, validated and rolled back without retraining
anything.

A harness is a plain dict:

    instructions   free text shown to a human reviewer, no effect on behaviour
    skills         named procedures that are switched on or off
    policy         the numeric knobs the skills read

`propose(lesion, harness)` is deterministic: same lesion and same harness give
the same plan, which is what makes the inner loop's accept/reject rule sound.
"""

from __future__ import annotations
from copy import deepcopy
from typing import Dict, List, Optional, Tuple

from .beds import BEDS
from .devices import CATALOG, BY_KEY, candidates_for, PREP
from .suitcordance import Lesion, Plan, evaluate

# --------------------------------------------------------------------------
# the starting harness
# --------------------------------------------------------------------------
HARNESS_V0: Dict = {
    "version": "v0",
    "instructions": (
        "Choose one device and size it. Prefer the smallest intervention that "
        "restores the lumen. Do not implant what the vessel cannot carry."
    ),
    "skills": [
        "size_from_reference",
        "cover_the_lesion",
    ],
    "policy": {
        "sizing_rule": "mean_ref",        # mean_ref | distal_ref | prox_ref
        "oversize_target": 1.00,          # multiple of the chosen reference
        "length_margin_mm": 2.0,          # per edge
        "calcium_prep_threshold": 1.10,   # above this calcium, prepare the lesion
        "prep_choice": "noncomp",
        "postdilate_calcium": 1.10,       # above this calcium, post-dilate
        "small_vessel_no_implant_mm": 0.0,  # below this diameter, leave nothing
        "long_lesion_flexible_mm": 1e9,   # above this length, demand fatigue resistance
        "require_drug_if_drive": 1e9,     # above this neointimal drive, demand a drug
        "search_top_k": 1,                # how many candidates to score before choosing
    },
}

# skills that can be switched on by the inner loop
AVAILABLE_SKILLS = [
    "size_from_reference",
    "cover_the_lesion",
    "prepare_calcium",            # reads calcium_prep_threshold / prep_choice
    "post_dilate",                # reads postdilate_calcium
    "leave_nothing_in_small",     # reads small_vessel_no_implant_mm
    "respect_flexion_zone",       # reads long_lesion_flexible_mm
    "match_drug_to_drive",        # reads require_drug_if_drive
    "score_and_rank",             # reads search_top_k: actually use the operator
    "protect_side_branch",        # never cover a branch that matters
]


def _reference_diameter(les: Lesion, rule: str) -> float:
    if rule == "distal_ref":
        return les.d_dist
    if rule == "prox_ref":
        return les.d_prox
    return les.d_ref


def _neointimal_drive(les: Lesion) -> float:
    bed = BEDS[les.bed]
    return (bed.k_neointima * (1.0 + 0.35 * les.diabetes)
            * (1.0 + 0.40 * les.inflammation))


def _size_device(dev, d_target: float) -> Optional[float]:
    """Nearest available nominal diameter, in 0.25 mm steps, inside the range."""
    lo, hi = dev.d_range
    d = round(d_target * 4.0) / 4.0
    d = min(max(d, lo), hi)
    if d < lo - 1e-9 or d > hi + 1e-9:
        return None
    return d


def propose(les: Lesion, harness: Dict) -> Plan:
    """Turn a lesion into a plan, using only what the harness switches on."""
    pol = harness["policy"]
    skills = set(harness["skills"])

    d_ref = _reference_diameter(les, pol["sizing_rule"])
    bed = BEDS[les.bed]

    # what the device diameter should be
    target = d_ref * pol["oversize_target"]
    if "size_from_reference" not in skills:
        target = d_ref

    # how long it should be
    margin = pol["length_margin_mm"] if "cover_the_lesion" in skills else 0.0
    length = les.length + 2.0 * margin

    # lesion preparation
    prep = "none"
    if "prepare_calcium" in skills and les.calcium >= pol["calcium_prep_threshold"]:
        prep = pol["prep_choice"]
    postdil = ("post_dilate" in skills and les.calcium >= pol["postdilate_calcium"])

    # which devices are admissible at all
    pool = candidates_for(les.bed, les.d_ref)
    drive = _neointimal_drive(les)

    def admissible(dev) -> bool:
        if "leave_nothing_in_small" in skills and \
                les.d_ref < pol["small_vessel_no_implant_mm"] and dev.strut_um > 0:
            return False
        if "respect_flexion_zone" in skills and \
                les.length > pol["long_lesion_flexible_mm"] and \
                dev.strut_um > 0 and dev.fatigue_resist < 0.90:
            return False
        if "match_drug_to_drive" in skills and drive > pol["require_drug_if_drive"] \
                and dev.drug == "none":
            return False
        if "protect_side_branch" in skills and les.side_branch and dev.family == "COVERED":
            return False
        return True

    pool = [d for d in pool if admissible(d)] or candidates_for(les.bed, les.d_ref)

    # without score_and_rank the agent never consults the operator: it takes the
    # first admissible device, which is how a fixed protocol behaves
    if "score_and_rank" not in skills:
        dev = pool[0]
        nd = _size_device(dev, target if dev.expansion != "self"
                          else d_ref * max(1.0, bed.oversize_band[0]))
        return Plan(device=dev.key, nominal_d=nd or dev.d_range[0],
                    length=min(length, dev.l_max), prep=prep, postdilate=postdil)

    best: Optional[Tuple[float, Plan]] = None
    for dev in pool:
        # self-expanding devices are deliberately oversized; the bed says by how much
        if dev.expansion == "self":
            band_mid = 0.5 * (bed.oversize_band[0] + bed.oversize_band[1])
            t = d_ref * max(band_mid, pol["oversize_target"])
        else:
            t = target
        nd = _size_device(dev, t)
        if nd is None:
            continue
        n_dev = 1
        L = min(length, dev.l_max)
        if L < length - 1e-6:                   # needs more than one device
            n_dev = max(1, int(round(length / dev.l_max)))
            L = min(dev.l_max, length / n_dev)
        plan = Plan(device=dev.key, nominal_d=nd, length=L, prep=prep,
                    postdilate=postdil, n_devices=n_dev)
        r = evaluate(les, plan, horizon=380, dt=10.0)
        score = -r.risk_12m
        if best is None or score > best[0]:
            best = (score, plan)

    assert best is not None, "no admissible device for this lesion"
    return best[1]


# --------------------------------------------------------------------------
# oracle: the best plan the catalogue can offer, used only to score rubrics
# --------------------------------------------------------------------------
_ORACLE_CACHE: Dict[tuple, Tuple[float, Plan]] = {}


def oracle(les: Lesion) -> Tuple[float, Plan]:
    """Lowest 12-month risk reachable with any catalogue device, any sizing."""
    key = (les.bed, round(les.d_prox, 2), round(les.d_dist, 2), round(les.length, 1),
           round(les.calcium, 2), round(les.tortuosity, 2), les.diabetes,
           les.side_branch, les.bifurcation, les.runoff, round(les.inflammation, 2))
    if key in _ORACLE_CACHE:
        return _ORACLE_CACHE[key]

    bed = BEDS[les.bed]
    best: Optional[Tuple[float, Plan]] = None
    for dev in candidates_for(les.bed, les.d_ref):
        for mult in (0.92, 0.98, 1.02, 1.06, 1.12, 1.20, 1.30, 1.42):
            nd = _size_device(dev, les.d_ref * mult)
            if nd is None:
                continue
            for margin in (0.0, 2.0, 4.0):
                want = les.length + 2 * margin
                n_dev = max(1, int(round(want / dev.l_max)) if want > dev.l_max else 1)
                L = min(dev.l_max, want / n_dev)
                for prep in ("none", "scoring", "ivl"):
                    for pd in (False, True):
                        plan = Plan(device=dev.key, nominal_d=nd, length=L, prep=prep,
                                    postdilate=pd, n_devices=n_dev)
                        r = evaluate(les, plan, horizon=380, dt=10.0)
                        if best is None or r.risk_12m < best[0]:
                            best = (r.risk_12m, plan)
    assert best is not None
    _ORACLE_CACHE[key] = best
    return best


def describe(les: Lesion, plan: Plan) -> Dict:
    """What the agent hands back to the researcher."""
    r = evaluate(les, plan)
    dev = BY_KEY[plan.device]
    axis_names = {"G": "几何/贴壁", "M": "力学/顺应性", "H": "血流动力学", "B": "生物学/药物"}
    worst = r.worst_axis()
    return {
        "device": dev.name,
        "size": f"{plan.nominal_d:.2f} x {plan.length:.0f} mm"
                + (f" x{plan.n_devices}" if plan.n_devices > 1 else ""),
        "prep": PREP[plan.prep]["label"],
        "postdilate": plan.postdilate,
        "gamma0": round(r.gamma0, 3),
        "gamma_12m": round(float(r.gamma[len(r.gamma) // 2]), 3),
        "tau_sc_days": round(r.tau_sc),
        "risk_12m": round(r.risk_12m, 3),
        "worst_axis": worst,
        "worst_axis_cn": axis_names[worst],
        "axes": {k: round(float(v[0]), 3) for k, v in
                 zip("GMHB", [r.G, r.M, r.H, r.B])},
    }
