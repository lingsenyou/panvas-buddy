"""
Inner recursion: improve the harness with the operator held fixed.

This is the ScienceBuddy inner loop, shrunk to something that runs on a laptop:

    for each step:
        diagnose which criterion costs the parent harness the most score
        propose C bounded edits aimed at it
        evaluate parent and candidates on the SAME dev tasks
        accept the best candidate only if it is valid AND strictly better

Two honest differences from the paper.  First, ScienceBuddy uses an auxiliary
language model to diagnose failures and write the edits; here the diagnoser is
a lookup table from "which criterion is bleeding score" to "which bounded edit
addresses it".  That is weaker and much more transparent, and swapping in a
model call is a drop-in replacement at `propose_edits`.  Second, an edit here is
COMPOUND -- a skill and the knob that skill reads move together -- because
switching on a skill whose threshold still excludes every case is a no-op, and
a loop that only ever proposes atomic edits stalls on the first step.

The test tasks are scored at the start and the end only, and are never used to
choose an edit.
"""

from __future__ import annotations
import copy
import json
import os
import sys
from typing import Dict, List, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from panvas.agent import HARNESS_V0, AVAILABLE_SKILLS, propose, oracle
from panvas.rubric import compose, score
from panvas.suitcordance import Lesion
from panvas.tasks import split

# knob bounds: an edit outside these is rejected as invalid
BOUNDS: Dict[str, Tuple[float, float]] = {
    "oversize_target": (0.90, 1.45),
    "length_margin_mm": (0.0, 12.0),
    "calcium_prep_threshold": (0.0, 1.10),
    "postdilate_calcium": (0.0, 1.10),
    "small_vessel_no_implant_mm": (0.0, 3.5),
    "long_lesion_flexible_mm": (40.0, 1e9),
    "require_drug_if_drive": (0.3, 1e9),
}

# compound, bounded edits: which harness change addresses which failing criterion
REMEDY: Dict[str, List[dict]] = {
    "near_optimal": [
        {"skills": ["score_and_rank"], "label": "consult the operator before choosing"},
    ],
    "prepared_calcium": [
        {"skills": ["prepare_calcium"],
         "knobs": {"calcium_prep_threshold": 0.55, "prep_choice": "scoring"},
         "label": "score heavy calcium before implanting"},
        {"skills": ["prepare_calcium"],
         "knobs": {"calcium_prep_threshold": 0.45, "prep_choice": "ivl"},
         "label": "lithotripsy from moderate calcium up"},
        {"skills": ["prepare_calcium", "post_dilate"],
         "knobs": {"calcium_prep_threshold": 0.55, "postdilate_calcium": 0.35},
         "label": "prepare, then post-dilate"},
    ],
    "covered": [
        {"knobs": {"length_margin_mm": 3.0}, "label": "3 mm edge margin"},
        {"knobs": {"length_margin_mm": 5.0}, "label": "5 mm edge margin"},
    ],
    "apposition": [
        {"knobs": {"oversize_target": 1.05}, "label": "size 5% over reference"},
        {"knobs": {"oversize_target": 1.10}, "label": "size 10% over reference"},
        {"knobs": {"sizing_rule": "prox_ref"}, "label": "size to the proximal reference"},
    ],
    "not_oversized": [
        {"knobs": {"oversize_target": 1.00}, "label": "back to 1:1 sizing"},
        {"knobs": {"sizing_rule": "distal_ref"}, "label": "size to the distal reference"},
    ],
    "antiproliferative": [
        {"skills": ["match_drug_to_drive"], "knobs": {"require_drug_if_drive": 1.2},
         "label": "demand a drug once drive exceeds 1.2"},
        {"skills": ["match_drug_to_drive"], "knobs": {"require_drug_if_drive": 0.9},
         "label": "demand a drug once drive exceeds 0.9"},
    ],
    "branch_kept": [
        {"skills": ["protect_side_branch"], "label": "never cover a branch that matters"},
    ],
    "flexion_safe": [
        {"skills": ["respect_flexion_zone"], "knobs": {"long_lesion_flexible_mm": 150.0},
         "label": "no fatigue-prone implant beyond 150 mm of SFA"},
        {"skills": ["respect_flexion_zone"], "knobs": {"long_lesion_flexible_mm": 120.0},
         "label": "no fatigue-prone implant beyond 120 mm of SFA"},
    ],
    "small_vessel": [
        {"skills": ["leave_nothing_in_small"], "knobs": {"small_vessel_no_implant_mm": 2.5},
         "label": "leave nothing behind below 2.5 mm"},
        {"skills": ["leave_nothing_in_small"], "knobs": {"small_vessel_no_implant_mm": 2.75},
         "label": "leave nothing behind below 2.75 mm"},
    ],
    "names_weak_axis": [],
}


def evaluate_harness(cases: List[Lesion], harness: Dict
                     ) -> Tuple[float, Dict[str, float]]:
    """Mean rubric score, and how much score each criterion is costing."""
    total = 0.0
    loss: Dict[str, float] = {}
    for les in cases:
        plan = propose(les, harness)
        orisk, _ = oracle(les)
        s, detail = score(les, plan, orisk)
        total += s
        crits = compose(les)
        den = sum(w for _, w, _ in crits)
        for k, w, _ in crits:
            loss[k] = loss.get(k, 0.0) + w * (1.0 - detail[k]) / den
    n = len(cases)
    return total / n, {k: v / n for k, v in loss.items()}


def valid(harness: Dict, cases: List[Lesion]) -> bool:
    for s in harness["skills"]:
        if s not in AVAILABLE_SKILLS:
            return False
    for k, (lo, hi) in BOUNDS.items():
        v = harness["policy"].get(k)
        if isinstance(v, (int, float)) and not (lo <= v <= hi):
            return False
    if harness["policy"]["sizing_rule"] not in ("mean_ref", "distal_ref", "prox_ref"):
        return False
    try:                                    # it must actually run on every case
        for les in cases[:8]:
            propose(les, harness)
    except Exception:
        return False
    return True


def _apply(harness: Dict, remedy: dict) -> Dict | None:
    cand = copy.deepcopy(harness)
    changed = False
    for s in remedy.get("skills", []):
        if s not in cand["skills"]:
            cand["skills"].append(s)
            changed = True
    for k, v in remedy.get("knobs", {}).items():
        if cand["policy"].get(k) != v:
            cand["policy"][k] = v
            changed = True
    return cand if changed else None


def propose_edits(loss: Dict[str, float], harness: Dict, tried: set,
                  n: int = 4) -> List[Tuple[str, Dict]]:
    """Bounded edits, aimed first at whatever is costing the most score."""
    out: List[Tuple[str, Dict]] = []
    for crit, _cost in sorted(loss.items(), key=lambda kv: -kv[1]):
        for i, remedy in enumerate(REMEDY.get(crit, [])):
            tag = f"{crit}#{i}"
            if tag in tried:
                continue
            cand = _apply(harness, remedy)
            if cand is None:
                tried.add(tag)
                continue
            out.append((f"{crit}: {remedy['label']}", cand))
            tried.add(tag)
            if len(out) >= n:
                return out
    return out


def main() -> None:
    dev, test = split(n_dev=60, n_test=120)
    harness = copy.deepcopy(HARNESS_V0)

    print("scoring the starting harness ...")
    dev_score, loss = evaluate_harness(dev, harness)
    test_start, _ = evaluate_harness(test, harness)
    print(f"  dev  {dev_score:.4f}   test {test_start:.4f}")
    print("  score lost to: " + ", ".join(
        f"{k}={v:.3f}" for k, v in sorted(loss.items(), key=lambda kv: -kv[1])[:5]))

    history = [dict(step=0, label="H0 (starting harness)", dev=round(dev_score, 4),
                    skills=list(harness["skills"]))]
    tried: set = set()

    for step in range(1, 9):
        cands = propose_edits(loss, harness, tried, n=4)
        if not cands:
            print(f"\nstep {step}: the diagnoser has no untried edit left")
            break
        print(f"\nstep {step}: {len(cands)} candidates")
        best = None
        for label, cand in cands:
            if not valid(cand, dev):
                print(f"   [invalid] {label}")
                continue
            s, l2 = evaluate_harness(dev, cand)
            delta = s - dev_score
            print(f"   {'ACCEPT' if delta > 0 else '      '} {label:58s} "
                  f"dev {s:.4f}  delta {delta:+.4f}")
            if delta > 0 and (best is None or s > best[1]):
                best = (label, s, cand, l2)
        if best is None:
            print("   no candidate improved; trying the next criterion")
            continue
        label, dev_score, harness, loss = best
        harness["version"] = f"v{step}"
        history.append(dict(step=step, label=label, dev=round(dev_score, 4),
                            skills=list(harness["skills"])))

    test_end, _ = evaluate_harness(test, harness)
    print("\n" + "=" * 76)
    print(f"held-out test rubric score  {test_start:.4f} -> {test_end:.4f}"
          f"   ({test_end - test_start:+.4f})")
    print(f"dev rubric score            {history[0]['dev']:.4f} -> {dev_score:.4f}")
    print("\nharness trajectory")
    for h in history:
        print(f"   step {h['step']}  dev {h['dev']:.4f}  {h['label']}")
    print("\nfinal skills: " + ", ".join(harness["skills"]))

    out = dict(history=history, test_start=test_start, test_end=test_end,
               final_harness=harness)
    os.makedirs("out", exist_ok=True)
    with open("out/harness_evolution.json", "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)
    with open("harness/harness_final.json", "w", encoding="utf-8") as fh:
        json.dump(harness, fh, indent=2, ensure_ascii=False)
    print("\nwritten: out/harness_evolution.json, harness/harness_final.json")


if __name__ == "__main__":
    main()
