"""
Task generation.

In ScienceBuddy the tasks come from real researcher interactions: a request is
recorded, reconstructed into an executable task, and a rubric is composed from
the trajectory.  There is no interaction log here yet, so tasks are sampled
from a lesion distribution that spans the six beds, and the same fixed rubric
composer is applied.

When the workspace starts recording real cases, `from_case_log` replaces
`sample`: the sampler is scaffolding, the case log is the real thing.
"""

from __future__ import annotations
import json
from typing import Dict, List

import numpy as np

from .beds import BEDS, BED_KEYS
from .suitcordance import Lesion


def sample(n: int, seed: int = 0, beds: List[str] | None = None) -> List[Lesion]:
    rng = np.random.default_rng(seed)
    beds = beds or BED_KEYS
    out: List[Lesion] = []
    for _ in range(n):
        b = beds[rng.integers(len(beds))]
        bed = BEDS[b]
        d = float(rng.uniform(*bed.d_ref))
        taper = float(rng.uniform(0.0, 0.18))
        d_prox = d * (1 + taper / 2)
        d_dist = d * (1 - taper / 2)
        if b in ("sfa", "btk"):
            length = float(rng.uniform(20, 240))
        elif b == "coronary":
            length = float(rng.uniform(8, 45))
        else:
            length = float(rng.uniform(10, 60))
        out.append(Lesion(
            bed=b, d_prox=round(d_prox, 2), d_dist=round(d_dist, 2),
            length=round(length, 1),
            stenosis=float(rng.uniform(0.6, 0.95)),
            calcium=float(rng.beta(2, 3)),
            tortuosity=float(rng.beta(2, 4)),
            bifurcation=bool(rng.random() < 0.22),
            side_branch=bool(rng.random() < 0.18),
            cto=bool(rng.random() < 0.10),
            diabetes=bool(rng.random() < 0.38),
            inflammation=float(rng.beta(2, 4)),
            runoff=int(rng.integers(0, 4)),
        ))
    return out


def split(n_dev: int = 60, n_test: int = 120, seed: int = 7):
    """Development tasks drive harness edits; test tasks are never looked at."""
    return sample(n_dev, seed=seed), sample(n_test, seed=seed + 1000)


def from_case_log(path: str) -> List[Lesion]:
    """Load lesions recorded by the workspace (one JSON object per line)."""
    out = []
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            rec: Dict = json.loads(line)
            out.append(Lesion(**{k: v for k, v in rec.items()
                                 if k in Lesion.__dataclass_fields__}))
    return out
