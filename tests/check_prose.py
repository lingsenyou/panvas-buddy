"""
Check that the numbers written in prose still match the numbers the code produces.

This exists because the same failure happened three times. The figures are regenerated
by `rebuild_all.py`, so after a refit they are always current; the sentences that quote
them are not. On 2026-09-19 the manuscript said tau_sc = 124 and 261 days while the
figure shipped in the same folder printed 128 and 287 -- the text contradicted its own
figure, and an earlier adversarial review had itself instructed the 124/261 values, which
were correct before the Route B refit and wrong after it.

So this does not ask "does the string 128 appear somewhere". It locates the number at the
position in the sentence where the claim is made, captures it, and compares it to a live
computation. A refit that moves a value fails here with both numbers printed.

Run standalone, or as the last step of rebuild_all.py.
"""

import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from panvas.suitcordance import Lesion, Plan, evaluate, T_HORIZON

SHEN = os.path.join(os.path.dirname(ROOT), "panvas_for_shen")
MS = os.path.join(ROOT, "preprint", "manuscript.md")
BRIEF2 = os.path.join(SHEN, "00c_给GPT阅读的技术简报_v2.md")
BRIEF1 = os.path.join(SHEN, "00b_给GPT阅读的完整技术简报.md")
DEFECTS = os.path.join(ROOT, "KNOWN_DEFECTS.md")
SHENBRIEF = os.path.join(ROOT, "给沈老师_项目简报.md")
README = os.path.join(ROOT, "README.md")
ABSTRACT = os.path.join(ROOT, "preprint", "abstract_plaintext.txt")


def worked_lesion():
    """The fig1 lesion, verbatim from make_figures.fig1()."""
    les = Lesion(bed="coronary", d_prox=3.2, d_dist=2.95, length=22,
                 calcium=0.30, diabetes=True, inflammation=0.25)
    plans = {"des": Plan("des_ultrathin", 3.0, 28),
             "brs": Plan("brs_plla", 3.0, 28),
             "dcb": Plan("dcb_ptx_cor", 3.0, 26, prep="scoring"),
             "bms": Plan("bms", 3.0, 28)}
    out = {}
    for k, p in plans.items():
        for H in (365, 730):
            r = evaluate(les, p, horizon=H, dt=5.0)
            out["tau_%s_%d" % (k, H)] = r.tau_sc
            out["g0_%s" % k] = r.gamma0
            out["risk_%s" % k] = r.risk_12m
    return out


def frontier():
    rows = json.load(io.open(os.path.join(ROOT, "out", "bounds_sweep.json"),
                             encoding="utf-8"))
    return {r["label"]: r for r in rows}


def anchor_split():
    """Reference-case vs informative residuals, and the Gamma_M ablation decomposition."""
    import numpy as np
    import panvas.suitcordance as SC
    from panvas.anchors import ALL_ANCHORS
    from panvas.suitcordance import THETA, evaluate

    # the six the manuscript names as informative; the rest are their bed's reference case
    INF = {"COR-BRS-plla", "COR-BMS", "COR-POBA", "SFA-POBA", "SFA-nitinol", "BTK-POBA"}
    used = [a for a in ALL_ANCHORS if a.include]
    base = {a.name: abs(evaluate(a.lesion, a.plan, theta=THETA).risk_12m - a.value)
            for a in used}
    inf = [v for k, v in base.items() if k in INF]
    ref = [v for k, v in base.items() if k not in INF]

    orig = SC._gamma_M
    SC._gamma_M = lambda les, plan, t, d_dep, th: np.ones_like(t)
    SC._gamma_star_cache.clear()
    abl = {a.name: abs(evaluate(a.lesion, a.plan, theta=THETA).risk_12m - a.value)
           for a in used}
    SC._gamma_M = orig
    SC._gamma_star_cache.clear()

    n = len(used)
    total = (sum(abl.values()) - sum(base.values())) / n * 100
    sfa = (abl["SFA-nitinol"] - base["SFA-nitinol"]) / n * 100
    return dict(mae_all=sum(base.values()) / n * 100,
                mae_inf=sum(inf) / len(inf) * 100,
                mae_ref=sum(ref) / len(ref) * 100,
                worst=max(base.values()) * 100,
                btk_dcb=base["BTK-DCB"] * 100,
                abl_total=total, abl_sfa=sfa, abl_sfa_pct=100 * sfa / total)


def neointima():
    """Twelve-month neointimal thickness and diameter stenosis, per anchor."""
    import numpy as np
    from panvas.anchors import ALL_ANCHORS
    from panvas.suitcordance import (THETA, deployed_diameter, _injury_index,
                                     _drug_effect, _neointima_um)
    from panvas.devices import BY_KEY
    t = np.arange(0.0, 381.0, 5.0)
    out = {}
    for a in [x for x in ALL_ANCHORS if x.include]:
        dd = deployed_diameter(a.lesion, a.plan, t)
        de = _drug_effect(a.lesion, a.plan, t, THETA)
        nih = float(_neointima_um(a.lesion, t, _injury_index(a.lesion, a.plan),
                                  float(de[:37].mean()), THETA, float(np.mean(dd)))[-1])
        lumen = dd[-1] - 2 * (BY_KEY[a.plan.device].strut_um + nih) / 1000.0
        out[a.name] = (nih, 100 * (1 - lumen / a.lesion.d_ref))
    return out


def attenuation():
    """What a collapse on the haemodynamic axis does to the composite, in the btk bed."""
    from panvas.beds import BEDS
    b = BEDS["btk"]
    wH = b.w_axes[2] / sum(b.w_axes)
    return 2000.0 ** wH


def base_rate_brier():
    """The number experiments.py prints for the test beds' base rate."""
    txt = io.open(os.path.join(ROOT, "out", "experiments.log"), encoding="utf-8").read()
    m = re.search(r"base-rate-only Brier on the test beds: ([\d.]+)", txt)
    return float(m.group(1))


def e2_auc():
    """B's AUC at the first sample size, and A'' at the last -- the pair the
    abstract quotes for sample efficiency."""
    d = json.load(io.open(os.path.join(ROOT, "out", "experiments.json"),
                          encoding="utf-8"))["e2"]
    b = next(v for k, v in d.items() if k.startswith("B "))["auc"]
    a = next(v for k, v in d.items() if k.startswith("A'' "))["auc"]
    return {"b_n100": b[0], "a_n800": a[-1]}


W = worked_lesion()
F = frontier()
S = anchor_split()
E2 = e2_auc()
N = neointima()
TH = json.load(io.open(os.path.join(ROOT, "panvas", "theta.json"), encoding="utf-8"))

# name, live value, [(file, regex with ONE capture group)], tolerance, unit
CHECKS = [
    ("tau_sc DCB @730", W["tau_dcb_730"], [
        (MS, r"paclitaxel-coated balloon has τ_sc = ([\d.]+) days"),
        (BRIEF1, r"balloon has τ_sc = ([\d.]+) days"),
        (BRIEF2, r"paclitaxel-coated balloon \| [\d.]+ \| [\d.]+ \| \*\*([\d.]+) d\*\*"),
    ], 0.6, "d"),
    ("tau_sc DES @730", W["tau_des_730"], [
        (MS, r"days against ([\d.]+) for"),
        (BRIEF1, r"drug-eluting stent ([\d.]+) days"),
        (BRIEF2, r"ultrathin-strut DES \| [\d.]+ \| [\d.]+ \| \*\*([\d.]+) d\*\*"),
    ], 0.6, "d"),
    ("tau_sc DES @365", W["tau_des_365"], [
        (MS, r"returns\s+([\d.]+) days at T = 365"),
        (BRIEF1, r"gives ([\d.]+) d at T = 365"),
    ], 0.6, "d"),
    ("gamma_sc(0) DCB", W["g0_dcb"], [
        (MS, r"Γ_sc\(0\) ([\d.]+) against"),
        (BRIEF1, r"\(([\d.]+) against [\d.]+\) — distinguishable"),
        (BRIEF2, r"paclitaxel-coated balloon \| ([\d.]+) \|"),
    ], 0.002, ""),
    ("gamma_sc(0) DES", W["g0_des"], [
        (MS, r"Γ_sc\(0\) [\d.]+ against ([\d.]+)\)"),
        (BRIEF1, r"\([\d.]+ against ([\d.]+)\) — distinguishable"),
        (BRIEF2, r"ultrathin-strut DES \| ([\d.]+) \|"),
    ], 0.002, ""),
    ("README tau DCB", W["tau_dcb_730"], [
        (README, r"paclitaxel DCB ([\d.]+) d,")], 0.6, "d"),
    ("README tau BMS", W["tau_bms_730"], [
        (README, r"bare-metal stent ([\d.]+) d,")], 0.6, "d"),
    ("README tau BRS", W["tau_brs_730"], [
        (README, r"PLLA BRS" + chr(10) + r"  ([\d.]+) d,")], 0.6, "d"),
    ("README tau DES", W["tau_des_730"], [
        (README, r"ultrathin DES ([\d.]+) d\.")], 0.6, "d"),
    ("README BRS-DES gap", W["tau_des_730"] - W["tau_brs_730"], [
        (README, r"the DES \(([\d.]+) d apart\)")], 0.9, "d"),
    ("README DCB-BMS gap", W["tau_bms_730"] - W["tau_dcb_730"], [
        (README, r"bare-metal stent \(([\d.]+) d apart\)")], 0.9, "d"),
    ("README risk DCB", W["risk_dcb"], [
        (README, r"predicted risk ([\d.]+)")], 0.002, ""),
    ("README risk BMS", W["risk_bms"], [
        (README, r"against ([\d.]+)\)\. τ_sc is also")], 0.002, ""),
    ("README g0 DCB", W["g0_dcb"], [
        (README, r"Γ_sc\(0\) ([\d.]+) against 0")], 0.002, ""),
    ("CN brief tau DCB", W["tau_dcb_730"], [
        (SHENBRIEF, r"药物球囊 ([\d.]+) 天"),
        (os.path.join(SHEN, "00_先读我_项目简报.md"), r"药物球囊 ([\d.]+) 天")], 0.6, "d"),
    ("CN brief tau DES", W["tau_des_730"], [
        (SHENBRIEF, r"超薄 DES ([\d.]+) 天"),
        (os.path.join(SHEN, "00_先读我_项目简报.md"), r"超薄 DES ([\d.]+) 天")], 0.6, "d"),
    ("CN brief tau BRS", W["tau_brs_730"], [
        (SHENBRIEF, r"PLLA 支架 ([\d.]+) 天")], 0.6, "d"),
    ("MAE all anchors", S["mae_all"], [
        (MS, r"\*\*Mean absolute error ([\d.]+) percentage points\*\*")], 0.006, "pts"),
    ("MAE worst anchor", S["worst"], [
        (MS, r"residual ([\d.]+) points on COR-POBA")], 0.006, "pts"),
    ("MAE reference subset", S["mae_ref"], [
        (MS, r"Their mean residual is ([\d.]+) points"),
        (README, r"their residual is ([\d.]+) points")], 0.006, "pts"),
    ("MAE informative subset", S["mae_inf"], [
        (MS, r"the mean absolute error is \*\*([\d.]+)" + chr(10) + r"percentage points\*\*"),
        (README, r"\*\*([\d.]+) points\*\*, not the headline"),
        (DEFECTS, r"informative-subset error is ([\d.]+) points")], 0.006, "pts"),
    ("BTK-DCB reference residual", S["btk_dcb"], [
        (MS, r"BTK-DCB is off" + chr(10) + r"by ([\d.]+) points")], 0.006, "pts"),
    ("Gamma_M ablation total", S["abl_total"], [
        (MS, r"forcing Γ_M ≡ 1 at the fitted constants costs ([\d.]+) points"),
        (DEFECTS, r"removing it now costs ([\d.]+) points of MAE")], 0.006, "pts"),
    ("Gamma_M ablation, SFA-nitinol", S["abl_sfa"], [
        (MS, r"SFA-nitinol contributes ([\d.]+) points")], 0.006, "pts"),
    ("Gamma_M ablation, SFA share", S["abl_sfa_pct"], [
        (MS, r"points, ([\d.]+)%")], 0.2, "%"),
    ("neointima SFA-nitinol", N["SFA-nitinol"][0], [
        (MS, r"the ([\d.]+) µm belongs to SFA-nitinol")], 1.0, "µm"),
    ("neointima COR-DES-modern", N["COR-DES-modern"][0], [
        (MS, r"contemporary DES anchor here sits at ([\d.]+) µm")], 1.0, "µm"),
    ("neointima BTK-POBA", N["BTK-POBA"][0], [
        (MS, r"BTK-POBA: ([\d.]+) µm per side")], 1.0, "µm"),
    ("stenosis BTK-POBA", N["BTK-POBA"][1], [
        (MS, r"\*\*([\d.]+)% diameter stenosis against")], 0.6, "%"),
    ("Gamma_H attenuation, btk", attenuation(), [
        (MS, r"attenuates to a \*\*([\d.]+)-fold\*\*")], 0.05, "x"),
    ("cross-bed base-rate Brier", base_rate_brier(), [
        (MS, r"which is ([\d.]+) \(their event rate")], 0.0006, ""),
    ("abstract: MAE all", S["mae_all"], [
        (ABSTRACT, r"mean absolute error of\s+([\d.]+) percentage points")], 0.02, "pts"),
    ("abstract: Gamma_M ablation", S["abl_total"], [
        (ABSTRACT, r"removing it costs ([\d.]+)" + chr(10) + r"?\s*points")], 0.006, "pts"),
    ("abstract: AUC at n=100", E2["b_n100"], [
        (ABSTRACT, r"reached AUC ([\d.]+) at n = 100")], 0.003, ""),
    ("abstract: raw features at n=800", E2["a_n800"], [
        (ABSTRACT, r"by n = 800 \(([\d.]+)\)")], 0.003, ""),
    ("horizon T", float(T_HORIZON), [
        (MS, r"five-day grid to T = ([\d.]+) days"),
    ], 0.5, "d"),
    ("beta", TH["beta"], [
        (BRIEF2, r"beta ([\d.]+)"),
    ], 0.002, ""),
    ("nih_max_um", TH["nih_max_um"], [
        (BRIEF2, r"nih_max_um ([\d.]+)†"),
    ], 0.6, "µm"),
]

# frontier table: MAE and worst anchor, in every document that prints the table
ROWLABEL = {"unbounded": "unbounded", "neointima bounded": "neointima bounded",
            "+ lumen kernel bounded": r"\+ lumen kernel bounded",
            "both tight": "both tight"}
for lab, pat in ROWLABEL.items():
    r = F[lab]
    for col, key, tol in (("MAE", "mae", 0.006), ("worst", "worst", 0.006)):
        grp = 1 if col == "MAE" else 2
        rx = r"\|\s*%s\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|" % pat
        places = [(MS, rx), (DEFECTS, rx)]
        CHECKS.append(("frontier %s / %s" % (lab, col), r[key] * 100.0,
                       [(f, rx if grp == 1 else rx) for f, rx in places],
                       tol * 100, "pts"))
        CHECKS[-1] = CHECKS[-1][:2] + (places, tol * 100, "pts", grp)


def run():
    bad, checked, missing = [], 0, []
    for chk in CHECKS:
        name, live, places, tol, unit = chk[0], chk[1], chk[2], chk[3], chk[4]
        grp = chk[5] if len(chk) > 5 else 1
        for path, rx in places:
            if not os.path.exists(path):
                missing.append((name, os.path.basename(path), "file absent"))
                continue
            txt = io.open(path, encoding="utf-8").read()
            m = re.search(rx, txt)
            if m is None:
                missing.append((name, os.path.basename(path), "pattern not found"))
                continue
            written = float(m.group(grp))
            checked += 1
            if abs(written - live) > tol:
                bad.append((name, os.path.basename(path), written, live, unit))

    for name, f, w, l, u in bad:
        print("STALE  %-34s %-36s prose %s  live %.4g %s" % (name, f, w, l, u))
    for name, f, why in missing:
        print("SKIP   %-34s %-36s %s" % (name, f, why))
    print()
    print("%d numeric claims verified, %d stale, %d not located"
          % (checked, len(bad), len(missing)))
    if bad:
        print()
        print("A stale claim means the prose disagrees with the code. Fix the prose "
              "(or the code), then re-run. Do not widen the tolerance.")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(run())
