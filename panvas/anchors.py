"""
Calibration anchors: published 12-month event rates the operator has to reproduce.

REVISION 2026-09-19, after an adversarial citation audit of the first anchor set.
That audit is the most important thing in this file's history, so it is recorded
here rather than in a commit message:

  Of the 16 anchors in the first set, only three were values the primary source
  actually reports at a commensurable endpoint, and two of those three were the
  two arms of a single trial. The other thirteen were stated HIGH, by factors of
  1.0 to 5.8. Five could be reverse-engineered exactly from a DIFFERENT endpoint
  reported in the same paper -- endpoint substitution, not transcription error:

    SFA-long-bare 0.350 = 100 - 64.8, primary PATENCY loss, not TLR (31.8)
    RENAL-stent   0.140 = the one-sided 95% upper bound of 9-month binary
                          restenosis (point estimate 10.5; CD-TLR 5.9)
    CAR-stent     0.035 = the ACT I primary composite SAFETY endpoint
                          (30-day death/stroke/MI + 1-y ipsilateral stroke);
                          CD-TLR is 0.6
    COR-POBA      0.320 = 6-month ANGIOGRAPHIC restenosis in the STENT arm of
                          STRESS I -- wrong arm, wrong endpoint, wrong timepoint
    ILIAC-stent   0.045 = the midpoint of CD-TLR (2.8) and duplex restenosis (6.1)
    BTK-DCB       0.120 = the midpoint of the two TRIAL ARMS (9.2 and 13.1)

The old claim that "the endpoint is held constant throughout" was false, and has
been deleted rather than patched. Within a single trial, TLF and CD-TLR differ by
2-3x (ABSORB III: 7.8 vs 3.0; BIOFLOW V: 6.2 vs 2.0), so an anchor set that picks
whichever of the two is convenient holds nothing constant.

WHAT THIS FILE NOW DOES

  * One endpoint construct is preferred: 12-month CLINICALLY DRIVEN target lesion
    revascularisation. Where the source does not report CD-TLR, the anchor carries
    the construct it actually reports and is labelled and down-weighted.
  * Every anchor declares seven provenance fields, so no reader has to guess what
    was measured: construct, trigger, adjudication, estimator, unit, window_days,
    design.
  * Anchors whose evidence could not survive audit are still listed, with
    `include=False`, so the record of what was dropped and why is public.
  * `weight` now encodes AUDITED evidence quality, not author confidence.

WHAT IS STILL WRONG WITH IT, and belongs in any paper that uses it:

  * SFA-DCB and SFA-POBA are two arms of one trial (IN.PACT SFA); BTK-DCB and
    BTK-POBA are two arms of one trial (IN.PACT DEEP). Both are Medtronic
    paclitaxel DCB RCTs sharing sites, CEC and CD-TLR trigger definition. Four
    anchors, two trials, correlated errors -- not four independent residuals.
  * Carotid, iliac and renal have ONE anchor each, which is also that bed's
    lambda0, so those three beds are fitted trivially and carry no information
    about the operator's shape.
  * Within a bed, the device-vs-balloon contrast is same-trial and self-consistent.
    ACROSS beds it is not: coronary POBA is 1991-93, symptom-driven, no routine
    surveillance; SFA POBA is 2015, CEC-adjudicated CD-TLR. Any bed gradient the
    model learns has 22 years of era effect and a change of endpoint definition
    baked into it.
"""

from typing import Dict, List, NamedTuple
from .suitcordance import Lesion, Plan


class Anchor(NamedTuple):
    name: str
    lesion: Lesion
    plan: Plan
    value: float          # 12-month event rate, as a fraction
    weight: float         # audited evidence quality, 0-1
    include: bool         # False = kept for the record, excluded from the fit
    citation: str
    doi: str
    construct: str        # CD-TLR | TLR | TLF | TVF | patency loss | restenosis
    trigger: str          # clinical | protocol surveillance | angiographic follow-up
    adjudication: str     # independent CEC | core laboratory | none stated
    estimator: str        # Kaplan-Meier | crude
    unit: str             # patient | lesion | vessel
    window_days: int
    design: str
    note: str


A: List[Anchor] = [

    # ------------------------------------------------------------- coronary
    Anchor(
        "COR-DES-modern",
        Lesion(bed="coronary", d_prox=2.95, d_dist=2.80, length=20, calcium=0.35,
               tortuosity=0.25, diabetes=True, inflammation=0.30),
        Plan(device="des_ultrathin", nominal_d=2.75, length=26),
        0.020, 0.90, True,
        "Kandzari DE, Mauri L, Koolen JJ, et al; BIOFLOW V Investigators. "
        "Ultrathin, bioresorbable polymer sirolimus-eluting stents versus thin, "
        "durable polymer everolimus-eluting stents in patients undergoing "
        "coronary revascularisation (BIOFLOW V). Lancet 2017;390(10105):1843-1852.",
        "10.1016/S0140-6736(17)32249-3",
        "CD-TLR", "clinical", "independent CEC", "crude", "patient", 365,
        "randomised trial, ultrathin bioresorbable-polymer SES arm",
        "The first anchor set put 4.5% here. That value appears nowhere in "
        "BIOFLOW V, for any arm or endpoint. The trial's CD-TLR is 2.0% and its "
        "TLF is 6.2%. Note also that this cohort is 74% ACC/AHA B2/C lesions, "
        "51% ACS and 35% diabetic, so it anchors a CONTEMPORARY ALL-COMERS "
        "population, not the simple-lesion stratum the old anchor claimed. The "
        "lesion above was changed to match the trial, not the other way round.",
    ),

    Anchor(
        "COR-BRS-plla",
        Lesion(bed="coronary", d_prox=3.0, d_dist=2.95, length=15, calcium=0.15,
               inflammation=0.2),
        Plan(device="brs_plla", nominal_d=3.0, length=23),
        0.030, 0.90, True,
        "Ellis SG, Kereiakes DJ, Metzger DC, et al; ABSORB III Investigators. "
        "Everolimus-eluting bioresorbable scaffolds for coronary artery disease. "
        "N Engl J Med 2015;373(20):1905-1915.",
        "10.1056/NEJMoa1509038",
        "CD-TLR", "clinical", "independent CEC", "crude", "patient", 365,
        "randomised pivotal IDE trial, Absorb arm",
        "ABSORB III reports both: TLF 7.8% and ischemia-driven TLR 3.0% at one "
        "year. The old anchor used 7.8%. Under a CD-TLR rule the correct value "
        "is 3.0%, because TLF here is dominated by periprocedural target-vessel "
        "MI (6.0%), not by revascularisation. Device is first-generation Absorb "
        "(157 um), withdrawn in 2017; this is a 1-year number and says nothing "
        "about the years 1-3 excess that trial later showed.",
    ),

    Anchor(
        "COR-BMS",
        Lesion(bed="coronary", d_prox=3.05, d_dist=2.90, length=18, calcium=0.30,
               inflammation=0.35),
        Plan(device="bms", nominal_d=3.0, length=24),
        0.098, 0.75, True,
        "Urban P, Meredith IT, Abizaid A, et al; LEADERS FREE Investigators. "
        "Polymer-free drug-coated coronary stents in patients at high bleeding "
        "risk. N Engl J Med 2015;373(21):2038-2047.",
        "10.1056/NEJMoa1503943",
        "CD-TLR", "clinical", "independent CEC", "crude", "patient", 390,
        "randomised trial, bare-metal comparator arm",
        "Old anchor 16%, which came from the bare-metal trials of the 1990s that "
        "mandated routine follow-up angiography; oculostenotic-reflex TLR is a "
        "different construct and cannot sit in a CD-TLR column. Window is 390 "
        "days, not 365. Population is high-bleeding-risk, mean age 75.7, one "
        "month of DAPT, and no protocol angiography, so this is a floor for "
        "bare-metal CD-TLR rather than a general value. LEADERS FREE III gives "
        "10.6% for the same design, which supports ~10% rather than ~16%.",
    ),

    Anchor(
        "COR-POBA",
        Lesion(bed="coronary", d_prox=3.1, d_dist=3.0, length=12, calcium=0.20,
               inflammation=0.25),
        Plan(device="poba", nominal_d=3.0, length=20),
        0.170, 0.55, True,
        "George CJ, Baim DS, Brinker JA, et al. One-year follow-up of the Stent "
        "Restenosis (STRESS I) Study. Am J Cardiol 1998;81(7):860-865.",
        "10.1016/s0002-9149(98)00004-6",
        "symptom-driven TLR", "clinical", "none stated", "crude", "patient", 365,
        "randomised trial, balloon-angioplasty arm",
        "Old anchor 32%, which is the 6-month ANGIOGRAPHIC restenosis rate of the "
        "STENT arm of the same trial -- wrong arm, wrong endpoint, wrong "
        "timepoint. The balloon arm's 1-year symptom-driven TLR is 17%. Enrolled "
        "1991-93 in >=3.0 mm vessels with discrete lesions. 'Symptom-driven' "
        "without routine angiography biases this DOWN relative to a modern "
        "CEC-adjudicated CD-TLR, in the opposite direction to the "
        "surveillance-driven anchors below. It carries 22 years of era effect "
        "against the peripheral anchors and should not be read as a clean "
        "cross-bed contrast.",
    ),

    # ----------------------------------------------------------------- SFA
    Anchor(
        "SFA-DCB",
        Lesion(bed="sfa", d_prox=5.6, d_dist=5.2, length=89, calcium=0.35,
               tortuosity=0.2, runoff=3),
        Plan(device="dcb_periph", nominal_d=5.5, length=120, prep="noncomp"),
        0.024, 1.00, True,
        "Tepe G, Laird J, Schneider P, et al; IN.PACT SFA Trial Investigators. "
        "Drug-coated balloon versus standard percutaneous transluminal "
        "angioplasty for the treatment of superficial femoral and popliteal "
        "peripheral artery disease: 12-month results from the IN.PACT SFA "
        "randomized trial. Circulation 2015;131(5):495-502.",
        "10.1161/CIRCULATIONAHA.114.011004",
        "CD-TLR", "clinical", "independent CEC", "crude", "patient", 365,
        "randomised trial, DCB arm",
        "Survived audit unchanged. Shares its trial, sites, CEC and CD-TLR "
        "trigger definition with SFA-POBA below: these are two arms, not two "
        "independent anchors.",
    ),

    Anchor(
        "SFA-POBA",
        Lesion(bed="sfa", d_prox=5.6, d_dist=5.2, length=89, calcium=0.35,
               tortuosity=0.2, runoff=3),
        Plan(device="poba", nominal_d=5.5, length=120),
        0.206, 1.00, True,
        "Tepe G, Laird J, Schneider P, et al; IN.PACT SFA Trial Investigators. "
        "Circulation 2015;131(5):495-502.",
        "10.1161/CIRCULATIONAHA.114.011004",
        "CD-TLR", "clinical", "independent CEC", "crude", "patient", 365,
        "randomised trial, PTA control arm",
        "Survived audit unchanged. The same arm's primary patency loss is 47.6%, "
        "which is what an endpoint substitution here would have produced.",
    ),

    Anchor(
        "SFA-nitinol",
        Lesion(bed="sfa", d_prox=5.6, d_dist=5.2, length=64, calcium=0.35,
               runoff=3),
        Plan(device="se_nitinol", nominal_d=6.0, length=90),
        0.127, 0.70, True,
        "Laird JR, Katzen BT, Scheinert D, et al; RESILIENT Investigators. "
        "Nitinol stent implantation versus balloon angioplasty for lesions in "
        "the superficial femoral and proximal popliteal arteries of patients "
        "with claudication. Circ Cardiovasc Interv 2010;3(3):267-276.",
        "10.1161/CIRCINTERVENTIONS.109.903468",
        "TLR", "clinical", "none stated", "Kaplan-Meier", "patient", 365,
        "randomised trial, nitinol stent arm",
        "Freedom from TLR 87.3% at 12 months, i.e. 12.7%. The paper does not use "
        "the words 'clinically driven', so this is all-cause TLR and is an upper "
        "bound on CD-TLR, not the same construct.",
    ),

    # ----------------------------------------------------------------- BTK
    Anchor(
        "BTK-DCB",
        Lesion(bed="btk", d_prox=2.9, d_dist=2.6, length=100, calcium=0.45,
               runoff=1, diabetes=True, inflammation=0.45),
        Plan(device="dcb_periph", nominal_d=2.75, length=120),
        0.092, 0.70, True,
        "Zeller T, Baumgartner I, Scheinert D, et al; IN.PACT DEEP Trial "
        "Investigators. Drug-eluting balloon versus standard balloon angioplasty "
        "for infrapopliteal arterial revascularization in critical limb "
        "ischemia: 12-month results from the IN.PACT DEEP randomized trial. "
        "J Am Coll Cardiol 2014;64(15):1568-1576.",
        "10.1016/j.jacc.2014.06.1198",
        "CD-TLR", "clinical", "independent CEC", "crude", "patient", 365,
        "randomised trial, drug-eluting balloon arm",
        "Old anchor 12%, which is the midpoint of this trial's two arms (9.2 and "
        "13.1). Averaging two arms is not an anchor. Rutherford 4-6 CLI, so "
        "death and major amputation compete with revascularisation and pull "
        "CD-TLR down for reasons that are not device-vessel matching.",
    ),

    Anchor(
        "BTK-POBA",
        Lesion(bed="btk", d_prox=2.9, d_dist=2.6, length=100, calcium=0.45,
               runoff=1, diabetes=True, inflammation=0.45),
        Plan(device="poba", nominal_d=2.75, length=120),
        0.131, 0.70, True,
        "Zeller T, Baumgartner I, Scheinert D, et al; IN.PACT DEEP Trial "
        "Investigators. J Am Coll Cardiol 2014;64(15):1568-1576.",
        "10.1016/j.jacc.2014.06.1198",
        "CD-TLR", "clinical", "independent CEC", "crude", "patient", 365,
        "randomised trial, standard PTA arm",
        "Old anchor 25%. Actual 13.1% (14/107). Same trial as BTK-DCB.",
    ),

    # -------------------------------------------------- single-anchor beds
    Anchor(
        "CAR-stent",
        Lesion(bed="carotid", d_prox=7.5, d_dist=5.0, length=20, calcium=0.30),
        Plan(device="car_closed", nominal_d=8.0, length=30),
        0.006, 0.60, True,
        "Rosenfield K, Matsumura JS, Chaturvedi S, et al; ACT I Investigators. "
        "Randomized trial of stent versus surgery for asymptomatic carotid "
        "stenosis. N Engl J Med 2016;374(11):1011-1020.",
        "10.1056/NEJMoa1515706",
        "CD-TLR", "clinical", "independent CEC", "Kaplan-Meier", "patient", 365,
        "randomised trial, stenting arm",
        "Old anchor 3.5%, which is ACT I's primary composite SAFETY endpoint "
        "(30-day death/stroke/MI plus 1-year ipsilateral stroke). The word "
        "'restenosis' does not appear in that paper. True CD-TLR is 0.6%. At "
        "0.6% this anchor is not distinguishable from zero and carries almost no "
        "information: the carotid bed may simply not be calibratable on a CD-TLR "
        "scale, because its informative endpoint is duplex restenosis. Weight "
        "lowered accordingly, and the bed is fitted trivially.",
    ),

    Anchor(
        "ILIAC-stent",
        Lesion(bed="iliac", d_prox=8.2, d_dist=7.8, length=40, calcium=0.35),
        Plan(device="se_nitinol", nominal_d=9.0, length=60),
        0.028, 0.70, True,
        "Krankenberg H, Zeller T, Ingwersen M, et al. Self-expanding versus "
        "balloon-expandable stents for iliac artery occlusive disease: the "
        "randomized ICE trial. JACC Cardiovasc Interv 2017;10(16):1694-1704.",
        "10.1016/j.jcin.2017.05.015",
        "CD-TLR", "clinical", "independent CEC", "Kaplan-Meier", "patient", 365,
        "randomised trial, self-expanding nitinol arm",
        "Old anchor 4.5%, which is the midpoint of CD-TLR (2.8%) and duplex "
        "restenosis (6.1%). Only anchor in this bed, so the bed is fitted "
        "trivially.",
    ),

    Anchor(
        "RENAL-stent",
        Lesion(bed="renal", d_prox=5.6, d_dist=5.2, length=15, calcium=0.30),
        Plan(device="bms", nominal_d=5.5, length=18),
        0.059, 0.45, True,
        "US FDA Center for Devices and Radiological Health. Summary of Safety "
        "and Effectiveness Data, PMA P110001, RX Herculink Elite Renal Stent "
        "System (HERCULES trial). 2011. SSED Table 14.",
        "",
        "CD-TLR", "clinical", "core laboratory", "Kaplan-Meier", "lesion", 312,
        "single-arm pivotal IDE study, regulatory dossier",
        "Old anchor 14%, which is the one-sided 95% upper bound of the 9-month "
        "binary restenosis rate (point estimate 10.5%). Clinically indicated TLR "
        "is 5.9% (95% CI 2.6-9.2) through 312 days. There is no 12-month "
        "revascularisation endpoint in this dossier at all; the 12-month visit "
        "collected blood pressure, medication, adverse events and creatinine. "
        "Analysis is per-LESION (241 lesions, 202 subjects), not per patient, and "
        "the SSED and IFU are the same dataset, not two sources. Weight low and "
        "the bed is fitted trivially.",
    ),

    # ==================================================================
    # EXCLUDED FROM THE FIT -- kept so that what was dropped is on the record
    # ==================================================================
    Anchor(
        "COR-undersized",
        Lesion(bed="coronary", d_prox=3.6, d_dist=3.4, length=18, calcium=0.2),
        Plan(device="des_ultrathin", nominal_d=2.75, length=24),
        0.0386, 0.0, False,
        "Lee SH, Jin X, Lee YJ, et al. Validation of intravascular "
        "ultrasound-defined optimal stent expansion criteria for favorable "
        "1-year clinical outcomes. JACC Cardiovasc Interv 2025;18(18):2197-2205.",
        "10.1016/j.jcin.2025.07.024",
        "TVF", "clinical", "independent CEC", "Kaplan-Meier", "vessel", 365,
        "post hoc analysis of randomised trials",
        "DROPPED. Old anchor 20%, an author estimate. The best available source "
        "is a triple mismatch: the endpoint is vessel-level TVF (includes "
        "non-target-lesion TVR); the construct is stent under-EXPANSION against "
        "an absolute 5.5 mm2 MSA cut-off, not under-SIZING of diameter, and an "
        "absolute cut-off confounds a sizing error with a small vessel; and the "
        "devices are mixed second-generation DES, not the ultrathin class. "
        "Retained only as an author prior with no formal elicitation.",
    ),

    Anchor(
        "SFA-long-bare",
        Lesion(bed="sfa", d_prox=5.8, d_dist=5.0, length=242, calcium=0.45,
               tortuosity=0.35, runoff=2),
        Plan(device="se_nitinol", nominal_d=6.0, length=200, n_devices=2),
        0.318, 0.0, False,
        "Bosiers M, Deloose K, Callaert J, et al. Results of the Protege "
        "EverFlex 200-mm-long nitinol stent (ev3) in TASC C and D "
        "femoropopliteal lesions (DURABILITY-200). J Vasc Surg "
        "2011;54(4):1042-1050.",
        "10.1016/j.jvs.2011.03.272",
        "TLR", "protocol surveillance", "none stated", "Kaplan-Meier", "patient", 365,
        "two-centre single-arm study",
        "DROPPED from the fit. Old anchor 0.350 = 100 - 64.8, which is primary "
        "PATENCY loss, not TLR. The available TLR (31.8%) is triggered by "
        "protocol duplex surveillance (PSVR > 2.4) with no independent "
        "adjudication, so it is an upper bound on CD-TLR by a different "
        "mechanism than every other anchor. Mean lesion 242 mm, 27% popliteal "
        "involvement, 29% CLI, single arm, two centres.",
    ),

    Anchor(
        "COR-DES-complex",
        Lesion(bed="coronary", d_prox=2.9, d_dist=2.5, length=32, calcium=0.50,
               diabetes=True, inflammation=0.4),
        Plan(device="des_ultrathin", nominal_d=2.75, length=38, prep="noncomp"),
        0.057, 0.0, False,
        "Park SH, Han JK, Yang S, et al. Biodegradable polymer versus "
        "polymer-free ultrathin sirolimus-eluting stents in complex PCI "
        "(HOST-IDEA post hoc). J Am Heart Assoc 2026;15(5):e043441.",
        "10.1161/JAHA.125.043441",
        "TLF", "clinical", "independent CEC", "crude", "patient", 365,
        "post hoc, propensity-matched subgroup",
        "DROPPED from the fit. Old anchor 12%, an author estimate. The real "
        "number is a TLF composite (5.7%), not CD-TLR, in a post hoc "
        "propensity-matched complex-PCI subgroup of 336 patients with 19 events "
        "and a hazard-ratio upper bound of 11.26. Kept for a sensitivity "
        "analysis, not for the primary fit.",
    ),

    Anchor(
        "COR-DCB-small",
        Lesion(bed="coronary", d_prox=2.5, d_dist=2.4, length=16, calcium=0.2),
        Plan(device="dcb_ptx_cor", nominal_d=2.5, length=20, prep="noncomp"),
        0.044, 0.0, False,
        "Tang Y, Qiao S, Su X, et al; RESTORE SVD China Investigators. "
        "Drug-coated balloon versus drug-eluting stent for small-vessel disease: "
        "the RESTORE SVD China randomized trial. JACC Cardiovasc Interv "
        "2018;11(23):2381-2392.",
        "10.1016/j.jcin.2018.09.009",
        "TLF", "clinical", "independent CEC", "crude", "patient", 365,
        "randomised trial, DCB arm, secondary endpoint",
        "DROPPED from the fit. Old anchor 8%, an author estimate. The real "
        "number is 4.4% TLF -- about five events in 116 patients -- as a "
        "secondary endpoint of a trial powered for 9-month in-segment percent "
        "diameter stenosis, in lesions pre-selected by successful predilatation. "
        "Kept for a sensitivity analysis.",
    ),
]

# The fit consumes tuples in the historical order; `include` gates membership.
ANCHORS = [(a.name, a.lesion, a.plan, a.value, a.weight, a.citation)
           for a in A if a.include]

ALL_ANCHORS = A
EXCLUDED = [a for a in A if not a.include]


def provenance_table() -> str:
    head = ("| anchor | value | w | construct | trigger | adjudication | unit | "
            "window (d) | source |")
    rows = [head, "|---|---|---|---|---|---|---|---|---|"]
    for a in A:
        flag = "" if a.include else " *(excluded)*"
        short = a.citation.split(".")[0]
        rows.append(f"| {a.name}{flag} | {a.value:.3f} | {a.weight:.2f} | "
                    f"{a.construct} | {a.trigger} | {a.adjudication} | {a.unit} | "
                    f"{a.window_days} | {short} |")
    return "\n".join(rows)


def audit_summary() -> Dict[str, object]:
    return {
        "n_total": len(A),
        "n_in_fit": len(ANCHORS),
        "n_excluded": len(EXCLUDED),
        "constructs_in_fit": sorted({a.construct for a in A if a.include}),
        "trials_contributing_two_arms": ["IN.PACT SFA", "IN.PACT DEEP"],
        "beds_with_one_anchor": ["carotid", "iliac", "renal"],
    }
