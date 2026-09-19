"""
Vascular-bed parameters for the pan-vascular suitcordance model.

All values are ORDER-OF-MAGNITUDE anchors taken from the interventional
literature, not fitted constants.  They are the model's priors; every one of
them is meant to be re-estimated once a real cohort is attached
(see fit_real.py).  Provenance is given per field so that a reviewer can
challenge any single number without touching the rest of the model.
"""

from dataclasses import dataclass, field
from typing import Tuple, Dict


@dataclass(frozen=True)
class Bed:
    key: str
    name_cn: str
    d_ref: Tuple[float, float]      # usual reference lumen diameter range, mm
    compliance: float               # wall distensibility, % diameter change / 100 mmHg
    wss0: float                     # baseline wall shear stress, dyn/cm^2
    k_neointima: float              # neointimal proliferative drive, coronary = 1.0
    cyclic_strain: float            # bending/torsion/compression burden, SFA = 1.0
    tau_endo: float                 # endothelialisation time constant, days (bare metal)
    tau_remodel: float              # vessel remodelling / embedding time constant, days
    lambda0: float                  # 12-month target-lesion-failure hazard at perfect match
    oversize_band: Tuple[float, float]   # device:vessel diameter ratio that is "right"
    # relative weight of the four suitcordance axes (G, M, H, B); normalised on use
    w_axes: Tuple[float, float, float, float] = (0.30, 0.25, 0.20, 0.25)
    notes: str = ""


BEDS: Dict[str, Bed] = {
    "coronary": Bed(
        key="coronary", name_cn="冠状动脉",
        d_ref=(2.25, 4.00), compliance=4.0, wss0=15.0,
        k_neointima=1.00, cyclic_strain=0.55, tau_endo=60.0, tau_remodel=90.0,
        lambda0=0.020, oversize_band=(0.95, 1.12),
        w_axes=(0.30, 0.22, 0.20, 0.28),
        notes="DES 12-mo TLF 4-6% in contemporary trials; cardiac-cycle bending only.",
    ),
    "sfa": Bed(
        key="sfa", name_cn="股浅动脉",
        d_ref=(4.5, 7.0), compliance=2.5, wss0=8.0,
        k_neointima=1.60, cyclic_strain=1.00, tau_endo=90.0, tau_remodel=120.0,
        lambda0=0.024, oversize_band=(1.05, 1.25),
        w_axes=(0.24, 0.36, 0.16, 0.24),
        notes="Worst mechanical environment: hip/knee flexion -> axial compression, "
              "torsion, bending. Stent fracture is a real failure mode, so the "
              "mechanical axis carries the largest weight here.",
    ),
    "btk": Bed(
        key="btk", name_cn="膝下动脉",
        d_ref=(2.0, 3.5), compliance=2.0, wss0=5.0,
        k_neointima=1.80, cyclic_strain=0.80, tau_endo=120.0, tau_remodel=150.0,
        lambda0=0.092, oversize_band=(0.95, 1.10),
        w_axes=(0.22, 0.24, 0.26, 0.28),
        notes="Low flow, small calibre, diffuse disease, CLTI patients. "
              "Restenosis rates are the highest of any bed.",
    ),
    "carotid": Bed(
        key="carotid", name_cn="颈动脉",
        d_ref=(4.5, 9.0), compliance=7.0, wss0=12.0,
        k_neointima=0.60, cyclic_strain=0.15, tau_endo=45.0, tau_remodel=90.0,
        lambda0=0.006, oversize_band=(1.10, 1.50),
        w_axes=(0.34, 0.18, 0.24, 0.24),
        notes="Deliberate large oversizing with self-expanding nitinol; "
              "dominant early risk is embolic, not restenotic.",
    ),
    "renal": Bed(
        key="renal", name_cn="肾动脉",
        d_ref=(4.0, 7.0), compliance=5.0, wss0=12.0,
        k_neointima=1.30, cyclic_strain=0.40, tau_endo=60.0, tau_remodel=90.0,
        lambda0=0.059, oversize_band=(0.95, 1.12),
        w_axes=(0.32, 0.22, 0.20, 0.26),
        notes="Ostial aorto-renal lesions; respiratory excursion drives cyclic strain.",
    ),
    "iliac": Bed(
        key="iliac", name_cn="髂动脉",
        d_ref=(6.0, 10.0), compliance=3.0, wss0=10.0,
        k_neointima=0.80, cyclic_strain=0.20, tau_endo=60.0, tau_remodel=90.0,
        lambda0=0.028, oversize_band=(0.98, 1.18),
        w_axes=(0.32, 0.24, 0.20, 0.24),
        notes="Large calibre, high flow; failures are mostly mechanical/edge.",
    ),
}

BED_KEYS = list(BEDS.keys())
