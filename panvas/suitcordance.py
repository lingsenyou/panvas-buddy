"""
Suitcordance operator Gamma_sc for pan-vascular intervention.

The claim this module operationalises: device-vessel failure is not a property
of the device or of the vessel, but of the *agreement* between them, and the
same agreement operator applies in every arterial bed once the bed's own
parameters are supplied.

Four axes, each mapped to [0, 1], 1 = perfect agreement:

    Gamma_G  geometric    sizing, coverage, conformability, taper
    Gamma_M  mechanical   compliance match, wall stress, fatigue
    Gamma_H  hemodynamic  flow lumen restored, strut flow disturbance, branches
    Gamma_B  biological   antiproliferative dose vs neointimal drive, healing

    Gamma_sc = PROD_i Gamma_i ** w_i ,  sum(w_i) = 1, weights are bed-specific.

The geometric mean is deliberate: a device fails along its worst-matched axis,
and a product cannot be rescued by a high score elsewhere the way a sum can.

Everything is a function of time.  Gamma_sc(t) is evaluated on a day grid and
two scalars are read off the trajectory:

    tau_sc   the effective time constant: the time by which the trajectory has
             accumulated 63.2% of its total variation.
    D_T      the time-averaged mismatch dose, (1/T) * INTEGRAL (1 - Gamma_sc) dt

and the hazard link is

    lambda(t) = lambda0 * exp(beta * (Gamma_star - Gamma_sc(t)))

with Gamma_star the match level at which the bed's published failure rate
lambda0 was observed.

The free constants of the operator live in THETA and are NOT invented: they are
fitted in calibrate.py against published 12-month event rates across six beds.
Everything outside THETA is either a bed parameter (beds.py), a device
specification (devices.py), or a structural choice documented above.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Tuple, Optional
import json
import math
import os

import numpy as np

from .beds import BEDS
from .devices import BY_KEY, PREP

# --------------------------------------------------------------------------
# free constants of the operator (fitted; see calibrate.py)
# --------------------------------------------------------------------------
THETA_DEFAULT: Dict[str, float] = {
    "s_under": 0.090,     # sizing kernel width below the band
    "s_over": 0.110,      # sizing kernel width above the band
    "k_comp": 0.90,       # compliance-mismatch kernel
    "k_stress": 0.55,     # overstretch kernel
    "k_fat": 3.20,        # cyclic-fatigue kernel
    "drug_K": 0.60,       # drug concentration needed per unit of drive
    "k_short": 1.30,      # antiproliferative shortfall kernel
    "need_scale": 3.00,   # drive -> required suppression
    "k_lumen": 0.26,      # residual-stenosis scale in Gamma_H
    "k_strut": 0.30,      # strut flow-disturbance scale
    "nih_max_um": 260.0,  # neointimal thickness at unit drive, unsuppressed
    "beta": 3.60,         # log-hazard per unit of mismatch
    "gamma_star": 0.90,   # match level at which lambda0 was observed
}

_THETA_PATH = os.path.join(os.path.dirname(__file__), "theta.json")


def load_theta(path: Optional[str] = None) -> Dict[str, float]:
    """Fitted constants if calibration has been run, defaults otherwise."""
    p = path or _THETA_PATH
    theta = dict(THETA_DEFAULT)
    if os.path.exists(p):
        with open(p, "r", encoding="utf-8") as fh:
            theta.update(json.load(fh))
    return theta


THETA = load_theta()

# The hazard link is anchored, per bed, at the device whose published rate
# defines that bed's lambda0.  Without this the operator would be forced to
# reach the same absolute Gamma in every bed before it could reproduce that
# bed's reference-arm event rate, which it cannot and should not.
#
# WARNING about the below-the-knee entry. IN.PACT DEEP missed its primary efficacy
# endpoints (CD-TLR 9.2% against 13.1% for plain angioplasty, p = 0.291), carried a
# major-amputation signal (8.8% against 3.6%, p = 0.080), and IN.PACT Amphirion was
# withdrawn from all markets in November 2013. It is used here because it is the
# best-adjudicated 12-month CD-TLR available in that bed, NOT because it is good
# care. Gamma*(btk) comes out at 0.21 against 0.47-0.74 for the other five beds;
# read that gap as a property of the anchor, not of the bed.
# Each entry is the trial arm whose published CD-TLR defines that bed's lambda0,
# so the reference case and the bed's baseline rate always describe the same
# population. Changing one without the other silently breaks the hazard link.
REFERENCE_CASE = {
    # BIOFLOW V, ultrathin bioresorbable-polymer SES arm
    "coronary": (dict(d_prox=2.95, d_dist=2.80, length=20, calcium=0.35,
                      tortuosity=0.25, diabetes=True, inflammation=0.30),
                 dict(device="des_ultrathin", nominal_d=2.75, length=26)),
    # IN.PACT SFA, DCB arm
    "sfa":      (dict(d_prox=5.6, d_dist=5.2, length=89, calcium=0.35, tortuosity=0.2),
                 dict(device="dcb_periph", nominal_d=5.5, length=120, prep="noncomp")),
    # IN.PACT DEEP, drug-eluting balloon arm
    "btk":      (dict(d_prox=2.9, d_dist=2.6, length=100, calcium=0.45, runoff=1,
                      diabetes=True, inflammation=0.45),
                 dict(device="dcb_periph", nominal_d=2.75, length=120)),
    # ACT I, stenting arm
    "carotid":  (dict(d_prox=7.5, d_dist=5.0, length=20, calcium=0.3),
                 dict(device="car_closed", nominal_d=8.0, length=30)),
    # HERCULES / PMA P110001
    "renal":    (dict(d_prox=5.6, d_dist=5.2, length=15, calcium=0.3),
                 dict(device="bms", nominal_d=5.5, length=18)),
    # ICE trial, self-expanding nitinol arm
    "iliac":    (dict(d_prox=8.2, d_dist=7.8, length=40, calcium=0.35),
                 dict(device="se_nitinol", nominal_d=9.0, length=60)),
}

_gamma_star_cache: Dict[Tuple[str, tuple], float] = {}

# fixed structural constants (not fitted)
TAU_NIH = 120.0         # neointimal growth time constant, days
NIH_RADIUS_FRAC = 0.60  # neointima cannot exceed this fraction of the deployed radius
TAU_DRIVE = 210.0       # decay of the proliferative stimulus after injury, days
T_HORIZON = 730         # default evaluation horizon, days

# within-axis weights
W_G = dict(size=0.40, coverage=0.24, conform=0.18, taper=0.18)
W_M = dict(compliance=0.38, stress=0.34, fatigue=0.28)
W_H = dict(lumen=0.50, struts=0.32, branch=0.18)
W_B = dict(drug=0.58, healing=0.42)


@dataclass
class Lesion:
    """A lesion, described the way an operator would describe it."""
    bed: str
    d_prox: float                # proximal reference diameter, mm
    d_dist: float                # distal reference diameter, mm
    length: float                # lesion length, mm
    stenosis: float = 0.75       # diameter stenosis, fraction
    calcium: float = 0.2         # 0 none .. 1 circumferential deep calcium
    tortuosity: float = 0.2      # 0 straight .. 1 severe
    bifurcation: bool = False
    side_branch: bool = False    # a branch a covered device would lose
    cto: bool = False
    diabetes: bool = False
    inflammation: float = 0.2    # 0..1 surrogate for hsCRP / systemic drive
    runoff: int = 3              # peripheral distal runoff vessels, 0-3

    @property
    def d_ref(self) -> float:
        return 0.5 * (self.d_prox + self.d_dist)

    @property
    def taper(self) -> float:
        return max(0.0, (self.d_prox - self.d_dist) / max(self.d_prox, 1e-6))


@dataclass
class Plan:
    """What the operator proposes to do."""
    device: str                  # key into devices.BY_KEY
    nominal_d: float             # nominal device / balloon diameter, mm
    length: float                # device length, mm
    prep: str = "none"
    postdilate: bool = False     # high-pressure post-dilatation
    n_devices: int = 1


# --------------------------------------------------------------------------
# deployment mechanics
# --------------------------------------------------------------------------
def _calcium_effective(les: Lesion, plan: Plan) -> float:
    return les.calcium * (1.0 - PREP[plan.prep]["ca_relief"])


def mld_pre(les: Lesion) -> float:
    """Minimum lumen diameter before the procedure, mm.

    Until 2026-09-19 the operator declared `Lesion.stenosis` and never read it, so a
    40% and a 95% stenosis produced bit-identical output, recoil was applied to the
    balloon's diameter rather than to the acute gain (which is what recoils), and a
    1:1 balloon delivered an injury index of exactly zero -- deleting the mechanism of
    post-angioplasty restenosis. Everything downstream of this function is the fix.
    """
    return max(0.15, les.d_ref * (1.0 - float(np.clip(les.stenosis, 0.0, 0.95))))


def inflated_diameter(les: Lesion, plan: Plan) -> float:
    """How far the wall is pushed open at maximum inflation, mm."""
    ca = _calcium_effective(les, plan)
    resist = 1.0 - 0.22 * (ca ** 1.5) * (0.55 if plan.postdilate else 1.0)
    dev = BY_KEY[plan.device]
    if dev.expansion == "self":
        # a self-expanding device never reaches nominal acutely
        gap = max(0.0, plan.nominal_d - les.d_ref)
        return les.d_ref + gap * 0.55 * (1.0 - 0.40 * ca)
    return plan.nominal_d * resist


def deployed_diameter(les: Lesion, plan: Plan, t: np.ndarray) -> np.ndarray:
    """Outer deployed diameter of the device over time, mm."""
    dev = BY_KEY[plan.device]
    bed = BEDS[les.bed]
    d_ves = les.d_ref
    ca = _calcium_effective(les, plan)
    d_inflate = inflated_diameter(les, plan)
    m0 = mld_pre(les)

    if dev.expansion == "balloon":
        # a scaffold holds nearly all of the acute gain
        d0 = m0 + (d_inflate - m0) * (1.0 - dev.recoil)
        if dev.degrade_tau_d:                      # resorbable: late enlargement
            d_inf, tau = d0 * 1.05, dev.degrade_tau_d
        else:
            d_inf, tau = d0 * 1.01, bed.tau_remodel
    elif dev.expansion == "self":
        gap = max(0.0, plan.nominal_d - d_ves)
        d0 = d_inflate
        d_inf = d_ves + gap * 0.90                 # chronic outward force keeps working
        tau = 60.0
    else:
        # nothing left behind: elastic recoil takes back a fraction of the ACUTE GAIN,
        # not of the balloon's diameter. That is what recoils, and applying the
        # fraction to the diameter is why balloon lumens came out absurdly small.
        elastic = bed.compliance / 4.0
        recoil = min(0.60, dev.recoil * (0.75 + 0.45 * elastic) * (1.0 - 0.35 * ca))
        d0 = m0 + (d_inflate - m0) * (1.0 - recoil)
        d_inf = m0 + (d0 - m0) * 0.94              # constrictive remodelling
        tau = 90.0

    return d_inf + (d0 - d_inf) * np.exp(-t / tau)


def _injury_index(les: Lesion, plan: Plan) -> float:
    """Barotrauma delivered to the wall, 0..1.5.

    Driven by how far the wall was pushed open relative to its reference calibre --
    the acute gain -- plus any oversizing beyond the reference. A 1:1 balloon in a
    tight lesion therefore delivers real injury, which is the mechanism of
    post-angioplasty restenosis; before 2026-09-19 it delivered none.
    """
    dev = BY_KEY[plan.device]
    ca = _calcium_effective(les, plan)
    gain = max(0.0, (inflated_diameter(les, plan) - mld_pre(les)) / les.d_ref)
    over = max(0.0, (inflated_diameter(les, plan) - les.d_ref) / les.d_ref)
    return float(np.clip(
        (0.55 * gain + 1.65 * over) * (1.0 + 1.2 * ca)
        + PREP[plan.prep]["injury"]
        + 0.10 * plan.postdilate
        + 0.25 * (dev.strut_um / 150.0),
        0.0, 1.5))


def _drive(les: Lesion, injury: float) -> float:
    """Neointimal proliferative drive for this lesion and this injury."""
    bed = BEDS[les.bed]
    return (bed.k_neointima
            * (1.0 + 0.35 * les.diabetes)
            * (1.0 + 0.60 * injury)
            * (1.0 + 0.40 * les.inflammation))


def _drug_effect(les: Lesion, plan: Plan, t: np.ndarray, th: Dict[str, float]) -> np.ndarray:
    """Fractional suppression of neointimal drive by the device drug, over time."""
    dev = BY_KEY[plan.device]
    if dev.drug == "none" or dev.dose_ug_mm2 <= 0:
        return np.zeros_like(t)
    potency = {"paclitaxel": 1.00, "sirolimus": 1.25, "everolimus": 1.20}[dev.drug]
    bed = BEDS[les.bed]
    drive = bed.k_neointima * (1.0 + 0.35 * les.diabetes)
    conc = dev.dose_ug_mm2 * potency * np.exp(-t / dev.drug_tau_d)
    if dev.family in ("DCB", "POBA"):
        conc = conc * 0.85                          # a bolus, with no reservoir
    a = conc / (th["drug_K"] * drive)
    return a ** 1.2 / (a ** 1.2 + 1.0)


def _neointima_um(les: Lesion, t: np.ndarray, injury: float, drug_eff: float,
                  th: Dict[str, float], d_dep: float) -> np.ndarray:
    """Neointimal thickness per side over time, micrometres.

    Two bounds, both added 2026-09-19. Before them the fit put 528 um under a
    contemporary drug-eluting stent whose observed CD-TLR is 2.0%, and 2,245 um in a
    2.75 mm below-the-knee vessel -- against roughly 100 um measured by optical
    coherence tomography for a contemporary stent. Nine of twelve anchors then sat at
    the lumen clip for most of year one, so the hemodynamic axis was reporting where a
    numerical floor had been hit rather than device-vessel physics.

    NIH_RADIUS_FRAC is the physical one: neointima cannot take more than this
    fraction of the deployed radius. `nih_max_um` is bounded in calibrate.py to a
    range the OCT literature can recognise.
    """
    nih_max = th["nih_max_um"] * _drive(les, injury) * (1.0 - 0.68 * drug_eff)
    ceiling = NIH_RADIUS_FRAC * (d_dep / 2.0) * 1000.0
    nih_max = min(nih_max, ceiling)
    return nih_max * (1.0 - np.exp(-t / TAU_NIH))


# --------------------------------------------------------------------------
# the four axes
# --------------------------------------------------------------------------
def _gamma_G(les: Lesion, plan: Plan, d_dep: np.ndarray,
             th: Dict[str, float]) -> np.ndarray:
    dev, bed = BY_KEY[plan.device], BEDS[les.bed]
    d_ves = les.d_ref
    lo, hi = bed.oversize_band

    if dev.expansion == "none":
        # nothing stays behind, so the geometric question is whether the balloon
        # was sized right at inflation; what recoil then costs is charged to
        # Gamma_H as residual lumen, not twice here.
        r = np.full_like(d_dep, plan.nominal_d / d_ves)
        lo, hi = 0.95, 1.10
    else:
        r = d_dep / d_ves

    size = np.where(r < lo, np.exp(-((lo - r) / th["s_under"]) ** 2),
                    np.where(r > hi, np.exp(-((r - hi) / th["s_over"]) ** 2), 1.0))

    margin = (plan.length * plan.n_devices - les.length) / 2.0    # mm per edge
    if margin < 0:                                   # geographic miss
        cov = math.exp(-((margin / 1.8) ** 2))
    elif margin > 5.0:                               # needless edge injury
        cov = math.exp(-(((margin - 5.0) / 9.0) ** 2))
    else:
        cov = 1.0

    conf = math.exp(-2.6 * (les.tortuosity * (1.0 - dev.conformability)) ** 2)

    # one straight device cannot match both ends of a tapering vessel
    taper_load = (les.taper * (1.0 - 0.45 * (dev.expansion == "self"))
                  * min(1.0, plan.length / 40.0))
    tap = math.exp(-5.0 * taper_load ** 2)

    return (size ** W_G["size"] * cov ** W_G["coverage"]
            * conf ** W_G["conform"] * tap ** W_G["taper"])


def _gamma_M(les: Lesion, plan: Plan, t: np.ndarray, d_dep: np.ndarray,
             th: Dict[str, float]) -> np.ndarray:
    dev, bed = BY_KEY[plan.device], BEDS[les.bed]
    ca = _calcium_effective(les, plan)
    c_wall = bed.compliance * (1.0 - 0.60 * ca)

    if dev.compliance_dev is None:                  # nothing implanted: perfect match
        comp = np.ones_like(t)
    else:
        c_dev = np.full_like(t, dev.compliance_dev)
        if dev.degrade_tau_d:                       # scaffold relaxes toward the wall
            frac = 1.0 - np.exp(-t / dev.degrade_tau_d)
            c_dev = dev.compliance_dev + (c_wall - dev.compliance_dev) * frac
        mm = np.abs(c_dev - c_wall) / (c_dev + c_wall)
        comp = np.exp(-th["k_comp"] * mm ** 2)

    # Overstretch strain is the strain the wall actually saw. For a device that
    # leaves nothing behind that is the strain AT INFLATION, not after recoil.
    # Taking it after recoil made Gamma_M identically 1.0000 for every balloon at
    # every sizing, so the axis meant to carry dissection and rupture was inert for
    # exactly the devices that cause them.
    if dev.expansion == "none":
        eps = np.full_like(t, max(0.0, (inflated_diameter(les, plan) - les.d_ref)
                                  / les.d_ref))
    else:
        eps = np.maximum(0.0, (d_dep - les.d_ref) / les.d_ref)
    eps_tol = 0.115 * math.sqrt(max(c_wall, 0.4) / 4.0)
    stress = np.exp(-((eps / eps_tol) ** 2) * th["k_stress"])

    if dev.expansion == "none":
        fat = np.ones_like(t)
    else:
        load = (bed.cyclic_strain * (1.0 - dev.fatigue_resist)
                * (0.6 + 0.4 * min(1.0, plan.length * plan.n_devices / 120.0)))
        cycles = 1.0 - np.exp(-t / 365.0)           # fatigue accrues over the first year
        fat = np.exp(-th["k_fat"] * (load ** 2) * cycles)

    return comp ** W_M["compliance"] * stress ** W_M["stress"] * fat ** W_M["fatigue"]


def _gamma_H(les: Lesion, plan: Plan, t: np.ndarray, d_dep: np.ndarray,
             nih_um: np.ndarray, th: Dict[str, float]) -> np.ndarray:
    dev, bed = BY_KEY[plan.device], BEDS[les.bed]
    d_ves = les.d_ref

    d_lumen = np.maximum(d_dep - 2.0 * (dev.strut_um + nih_um) / 1000.0, 0.25)
    resid = np.clip(1.0 - d_lumen / d_ves, 0.0, 1.0)
    lumen = np.exp(-((resid / th["k_lumen"]) ** 2))

    if dev.strut_um <= 0:
        struts = np.ones_like(t)
    else:
        covered = 1.0 - np.exp(-t / (bed.tau_endo * (1.0 + 0.9 * (dev.drug != "none"))))
        raw = ((dev.strut_um / 100.0) * math.sqrt(3.0 / max(d_ves, 1.0))
               * math.sqrt(15.0 / bed.wss0))
        struts = np.exp(-th["k_strut"] * raw * (1.0 - 0.75 * covered))

    branch = 1.0
    if les.side_branch and dev.family == "COVERED":
        branch = 0.35
    elif les.bifurcation and dev.strut_um > 0:
        branch = 0.80 - 0.10 * (dev.strut_um > 120)
    if les.bed in ("sfa", "btk") and les.runoff <= 1:
        branch *= 0.80                              # nowhere for the blood to go

    return lumen ** W_H["lumen"] * struts ** W_H["struts"] * branch ** W_H["branch"]


def _gamma_B(les: Lesion, plan: Plan, t: np.ndarray, injury: float,
             drug_eff: np.ndarray, th: Dict[str, float]) -> np.ndarray:
    dev, bed = BY_KEY[plan.device], BEDS[les.bed]

    drive = _drive(les, injury)
    drive_t = 0.30 * drive + 0.70 * drive * np.exp(-t / TAU_DRIVE)
    need = np.clip(drive_t / th["need_scale"], 0.02, None)
    # a drug that outlives the stimulus is not better; what hurts is the
    # FRACTION of the proliferative drive left unopposed, not its raw size
    shortfall = np.clip(need - drug_eff, 0.0, None) / (1.0 + need)
    drug = np.exp(-th["k_short"] * shortfall ** 2)

    if dev.strut_um <= 0:
        healing = np.ones_like(t)
    else:
        window = (bed.tau_endo * (1.0 + 0.90 * (dev.drug != "none"))
                  * (1.0 + 0.55 * (dev.strut_um / 150.0)))
        h = math.exp(-((window / 260.0) ** 2))
        if dev.degrade_tau_d:
            # resorption must not outrun healing, and must eventually happen
            mismatch = abs(math.log(dev.degrade_tau_d / (6.0 * window)))
            h = h * math.exp(-0.45 * mismatch ** 2)
        healing = np.full_like(t, h)

    return drug ** W_B["drug"] * healing ** W_B["healing"]


# --------------------------------------------------------------------------
# the operator
# --------------------------------------------------------------------------
@dataclass
class SuitcordanceResult:
    t: np.ndarray
    G: np.ndarray
    M: np.ndarray
    H: np.ndarray
    B: np.ndarray
    gamma: np.ndarray
    tau_sc: float
    deficit: float               # time-averaged mismatch dose D_T
    gamma0: float
    gamma_end: float
    hazard: np.ndarray
    risk_12m: float
    risk_end: float
    weights: Tuple[float, float, float, float]

    def summary(self) -> Dict[str, float]:
        return dict(gamma0=round(self.gamma0, 3), gamma_end=round(self.gamma_end, 3),
                    tau_sc=round(self.tau_sc, 1), deficit=round(self.deficit, 3),
                    risk_12m=round(self.risk_12m, 3), risk_end=round(self.risk_end, 3),
                    G0=round(float(self.G[0]), 3), M0=round(float(self.M[0]), 3),
                    H0=round(float(self.H[0]), 3), B0=round(float(self.B[0]), 3))

    def worst_axis(self) -> str:
        means = [self.G.mean(), self.M.mean(), self.H.mean(), self.B.mean()]
        return ["G", "M", "H", "B"][int(np.argmin(means))]


_in_reference_eval = False


def gamma_star(bed_key: str, th: Dict[str, float]) -> float:
    """Match level the bed's reference device achieves, averaged over year one."""
    global _in_reference_eval
    # key on the VALUES: dict identity is recycled by the garbage collector and
    # silently served stale reference levels during calibration
    key = (bed_key, tuple(sorted(th.items())))
    if key in _gamma_star_cache:
        return _gamma_star_cache[key]
    les_kw, plan_kw = REFERENCE_CASE[bed_key]
    _in_reference_eval = True
    try:
        r = evaluate(Lesion(bed=bed_key, **les_kw), Plan(**plan_kw),
                     horizon=365, dt=5.0, theta=th)
    finally:
        _in_reference_eval = False
    val = float(np.mean(r.gamma))
    _gamma_star_cache[key] = val
    return val


def evaluate(les: Lesion, plan: Plan, horizon: int = T_HORIZON, dt: float = 5.0,
             theta: Optional[Dict[str, float]] = None) -> SuitcordanceResult:
    th = theta or THETA
    bed = BEDS[les.bed]
    t = np.arange(0.0, horizon + dt, dt)

    d_dep = deployed_diameter(les, plan, t)
    injury = _injury_index(les, plan)
    drug_eff = _drug_effect(les, plan, t, th)
    nih = _neointima_um(les, t, injury,
                        float(np.mean(drug_eff[: max(1, int(180 / dt))])), th,
                        float(np.mean(d_dep)))

    G = np.clip(_gamma_G(les, plan, d_dep, th), 1e-4, 1.0)
    M = np.clip(_gamma_M(les, plan, t, d_dep, th), 1e-4, 1.0)
    H = np.clip(_gamma_H(les, plan, t, d_dep, nih, th), 1e-4, 1.0)
    B = np.clip(_gamma_B(les, plan, t, injury, drug_eff, th), 1e-4, 1.0)

    w = np.array(bed.w_axes, dtype=float)
    w = w / w.sum()
    gamma = G ** w[0] * M ** w[1] * H ** w[2] * B ** w[3]

    # Effective time constant: the time at which 63.2% of the trajectory's TOTAL
    # VARIATION has accumulated. 0.632 = 1 - 1/e, borrowed from the first-order time
    # constant, and that is the only thing borrowed: on a total-variation scale the
    # coefficient has no independent justification, and it makes tau_sc depend on the
    # horizon (the fig1 ultrathin DES gives 249 d at T=365 and 287 d at T=730), so T
    # must be quoted with any tau_sc. Total variation rather than a monotone approach
    # is what keeps it defined for the non-monotone trajectories this model produces --
    # but it also means a device that worsens then recovers accumulates large variation
    # with zero net change, so tau_sc conflates volatility with adaptation. Neither
    # direction is claimed to be the better property, and tau_sc does not enter the
    # hazard. Whether it carries information beyond gamma(0) is untested.
    tv = np.concatenate([[0.0], np.cumsum(np.abs(np.diff(gamma)))])
    tau_sc = float(np.interp(0.632 * tv[-1], tv, t)) if tv[-1] > 1e-9 else float("nan")

    deficit = float(np.trapezoid(1.0 - gamma, t) / (t[-1] - t[0]))

    # Hazard link. lambda0 is the 12-month CD-TLR of the bed's REFERENCE TRIAL ARM --
    # not 'best practice'. For btk it is the drug-eluting balloon arm of IN.PACT DEEP,
    # a trial that missed its primary endpoints and whose device was withdrawn in 2013
    # (KNOWN_DEFECTS D1). It is the best-adjudicated rate available in that bed, which
    # is a different claim.
    # observed at the match level the reference device actually achieves
    lam0 = -math.log(max(1e-6, 1.0 - bed.lambda0)) / 365.0
    g_star = th["gamma_star"] if _in_reference_eval else gamma_star(les.bed, th)
    lam = lam0 * np.exp(th["beta"] * (g_star - gamma))
    cumhaz = np.concatenate([[0.0], np.cumsum(0.5 * (lam[1:] + lam[:-1]) * np.diff(t))])
    risk = 1.0 - np.exp(-cumhaz)

    return SuitcordanceResult(
        t=t, G=G, M=M, H=H, B=B, gamma=gamma, tau_sc=tau_sc, deficit=deficit,
        gamma0=float(gamma[0]), gamma_end=float(gamma[-1]),
        hazard=lam, risk_12m=float(np.interp(365, t, risk)),
        risk_end=float(risk[-1]), weights=tuple(w))


def check_plan(les: Lesion, plan: Plan) -> None:
    """Raise if a plan is not physically expressible with the device it names.

    The renal reference case ran for weeks on a bare-metal stent sized 0.5 mm beyond
    the top of its own catalogue range, because nothing looked. Called from the
    tests and from calibrate.py so that it cannot happen again unnoticed.
    """
    dev = BY_KEY.get(plan.device)
    if dev is None:
        raise ValueError(f"unknown device {plan.device!r}")
    if les.bed not in dev.beds:
        raise ValueError(f"{plan.device} is not licensed for the {les.bed} bed")
    lo, hi = dev.d_range
    if not (lo - 1e-9 <= plan.nominal_d <= hi + 1e-9):
        raise ValueError(f"{plan.device}: nominal_d {plan.nominal_d} outside its "
                         f"catalogue range {dev.d_range}")
    if plan.length <= 0 or plan.length > dev.l_max + 1e-9:
        raise ValueError(f"{plan.device}: length {plan.length} outside (0, {dev.l_max}]")
    if plan.prep not in PREP:
        raise ValueError(f"unknown lesion preparation {plan.prep!r}")


def risk_12m(les: Lesion, plan: Plan, theta: Optional[Dict[str, float]] = None) -> float:
    return evaluate(les, plan, horizon=380, dt=10.0, theta=theta).risk_12m
