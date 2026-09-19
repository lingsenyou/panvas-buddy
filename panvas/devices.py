"""
Device catalogue for the pan-vascular suitcordance model.

Every entry is a *class* of device, not a specific commercial product, with
representative published characteristics.  Numbers are approximate and are
declared here so they can be audited and replaced one at a time.

Key modelling choice: a drug-coated balloon / plain balloon is represented as
a device with NO scaffold (radial_force = 0) whose compliance is by definition
the vessel's own.  That makes the classic trade-off fall out of the model
rather than being hard-coded: DCB is a perfect compliance match (high Gamma_M)
but buys nothing against recoil (low Gamma_G / Gamma_H).
"""

from dataclasses import dataclass
from typing import List, Optional, Tuple, Dict


@dataclass(frozen=True)
class Device:
    key: str
    name: str
    family: str                 # DES | BRS | BMS | SE | SE-DES | COVERED | DCB | POBA
    expansion: str              # balloon | self | none
    beds: Tuple[str, ...]
    d_range: Tuple[float, float]        # available nominal diameters, mm
    l_max: float                        # longest available length, mm
    strut_um: float                     # strut / wall thickness, um (0 for balloons)
    radial_force: float                 # scaffolding, normalised (thin-strut DES = 1.0)
    compliance_dev: Optional[float]     # %diam / 100 mmHg; None -> takes the wall's own
    conformability: float               # 0-1, ability to follow vessel curvature
    fatigue_resist: float               # 0-1, resistance to cyclic deformation
    drug: str                           # none | paclitaxel | sirolimus | everolimus
    dose_ug_mm2: float
    drug_tau_d: float                   # tissue retention time constant, days
    degrade_tau_d: Optional[float]      # scaffold resorption time constant, days
    recoil: float                       # acute elastic recoil fraction after removal
    crossing_mm: float
    note: str = ""


CATALOG: List[Device] = [
    # ---------------- coronary ----------------
    Device("des_ultrathin", "Ultrathin-strut DES (60 um, sirolimus)", "DES", "balloon",
           ("coronary",), (2.25, 4.0), 40, 60, 1.00, 0.30, 0.80, 0.90,
           "sirolimus", 1.4, 90, None, 0.03, 1.05,
           "Contemporary workhorse; thin struts minimise flow disturbance."),
    Device("des_thin", "Thin-strut DES (81 um, everolimus)", "DES", "balloon",
           ("coronary", "renal", "btk"), (2.25, 4.0), 48, 81, 1.00, 0.30, 0.75, 0.88,
           "everolimus", 1.0, 90, None, 0.03, 1.10, ""),
    Device("brs_plla", "PLLA BRS, 150 um (XINSORB-class)", "BRS", "balloon",
           ("coronary",), (2.5, 3.5), 33, 150, 0.62, 0.80, 0.55, 0.70,
           "sirolimus", 1.4, 90, 900, 0.06, 1.45,
           "Compliance converges to the wall as the scaffold resorbs; the price "
           "is a thick strut for the first year."),
    Device("brs_thin", "Next-generation thin BRS (100 um)", "BRS", "balloon",
           ("coronary",), (2.5, 4.0), 36, 100, 0.72, 0.70, 0.62, 0.75,
           "sirolimus", 1.4, 90, 730, 0.05, 1.25, ""),
    Device("dcb_ptx_cor", "Coronary DCB (paclitaxel 3.0 ug/mm2)", "DCB", "none",
           ("coronary", "btk"), (2.0, 4.0), 40, 0, 0.00, None, 1.00, 1.00,
           "paclitaxel", 3.0, 45, None, 0.28, 0.85,
           "Leaves nothing behind: no compliance mismatch, no scaffolding either."),
    Device("dcb_siro_cor", "Coronary sirolimus DCB", "DCB", "none",
           ("coronary", "btk"), (2.0, 4.0), 40, 0, 0.00, None, 1.00, 1.00,
           "sirolimus", 3.5, 30, None, 0.28, 0.90, ""),
    Device("bms", "Bare-metal stent", "BMS", "balloon",
           ("coronary", "renal", "iliac"), (2.5, 5.0), 38, 110, 1.00, 0.30, 0.70, 0.85,
           "none", 0.0, 1, None, 0.03, 1.15, "Comparator arm."),

    # ---------------- peripheral ----------------
    Device("se_nitinol", "Self-expanding nitinol stent", "SE", "self",
           ("sfa", "iliac", "renal"), (5.0, 10.0), 200, 200, 0.28, 1.50, 0.85, 0.72,
           "none", 0.0, 1, None, 0.02, 1.80, ""),
    Device("se_ptx", "Paclitaxel-eluting nitinol stent", "SE-DES", "self",
           ("sfa", "iliac"), (5.0, 8.0), 200, 200, 0.30, 1.50, 0.85, 0.74,
           "paclitaxel", 3.0, 120, None, 0.02, 1.85, ""),
    Device("se_interwoven", "Interwoven nitinol stent", "SE", "self",
           ("sfa",), (4.5, 7.5), 150, 250, 0.60, 1.10, 0.70, 0.96,
           "none", 0.0, 1, None, 2.00, 2.10,
           "Built for the flexion zone: highest fatigue resistance in the catalogue."),
    Device("covered", "ePTFE covered stent-graft", "COVERED", "self",
           ("sfa", "iliac"), (5.0, 13.0), 250, 300, 0.45, 0.60, 0.65, 0.80,
           "none", 0.0, 1, None, 0.02, 2.60,
           "Excludes the wall from the lumen: no in-stent neointima, but edge "
           "hyperplasia and side-branch loss."),
    Device("dcb_periph", "Peripheral DCB (paclitaxel 3.5 ug/mm2)", "DCB", "none",
           ("sfa", "btk", "iliac"), (2.0, 7.0), 250, 0, 0.00, None, 1.00, 1.00,
           "paclitaxel", 3.5, 90, None, 0.30, 1.10, ""),
    Device("poba", "Plain balloon angioplasty", "POBA", "none",
           ("coronary", "sfa", "btk", "iliac", "renal"), (1.5, 12.0), 300, 0,
           0.00, None, 1.00, 1.00, "none", 0.0, 1, None, 0.32, 0.80, ""),

    # ---------------- carotid ----------------
    Device("car_closed", "Closed-cell carotid nitinol stent", "SE", "self",
           ("carotid",), (6.0, 10.0), 40, 180, 0.32, 1.40, 0.60, 0.90,
           "none", 0.0, 1, None, 0.02, 1.70, ""),
    Device("car_dual", "Dual-layer micromesh carotid stent", "SE", "self",
           ("carotid",), (6.0, 10.0), 60, 200, 0.34, 1.30, 0.70, 0.90,
           "none", 0.0, 1, None, 0.02, 1.90,
           "Micromesh traps plaque; denser mesh is a hemodynamic cost."),
]

BY_KEY: Dict[str, Device] = {d.key: d for d in CATALOG}


# --- lesion preparation -----------------------------------------------------
# Preparation does not implant anything; it changes how the wall responds.
# ca_relief: fraction of the calcium-driven compliance penalty that is removed.
# injury:    extra barotrauma added to the biological injury term.
PREP: Dict[str, Dict[str, float]] = {
    "none":     {"ca_relief": 0.00, "injury": 0.00, "label": "无预处理"},
    "noncomp":  {"ca_relief": 0.20, "injury": 0.05, "label": "非顺应性球囊"},
    "scoring":  {"ca_relief": 0.45, "injury": 0.10, "label": "切割/棘突球囊"},
    "atherec":  {"ca_relief": 0.65, "injury": 0.18, "label": "旋磨/旋切"},
    "ivl":      {"ca_relief": 0.75, "injury": 0.04, "label": "血管内冲击波(IVL)"},
}


def candidates_for(bed: str, d_ves: float) -> List[Device]:
    """Devices that are licensed for this bed and can be sized to this vessel."""
    out = []
    for d in CATALOG:
        if bed not in d.beds:
            continue
        # a device is sizeable if the vessel sits inside its diameter range
        # once the bed's intended oversizing is applied
        if d.d_range[0] <= d_ves * 1.45 and d.d_range[1] >= d_ves * 0.95:
            out.append(d)
    return out
