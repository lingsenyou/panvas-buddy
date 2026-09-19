"""Dump beds, devices, fitted constants and per-bed reference levels for the web workbench."""

import json
import os
import sys
from dataclasses import asdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from panvas.beds import BEDS
from panvas.devices import CATALOG, PREP
from panvas.suitcordance import (THETA, W_G, W_M, W_H, W_B, TAU_NIH, TAU_DRIVE,
                                 NIH_RADIUS_FRAC, gamma_star)

out = {
    "theta": THETA,
    "axisWeights": {"G": W_G, "M": W_M, "H": W_H, "B": W_B},
    "tauNih": TAU_NIH,
    "nihRadiusFrac": NIH_RADIUS_FRAC,
    "tauDrive": TAU_DRIVE,
    "beds": {k: asdict(v) for k, v in BEDS.items()},
    "gammaStar": {k: gamma_star(k, THETA) for k in BEDS},
    "devices": [asdict(d) for d in CATALOG],
    "prep": PREP,
}

os.makedirs("out", exist_ok=True)
with open("out/model.json", "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, separators=(",", ":"))
print("out/model.json", os.path.getsize("out/model.json"), "bytes")
print("gammaStar:", {k: round(v, 3) for k, v in out["gammaStar"].items()})
