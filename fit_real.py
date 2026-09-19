"""
Attach a real cohort.

Everything else in this repository is a scaffold.  This file is where it stops
being one.  Give it a CSV of real procedures with real 12-month outcomes and it
refits the operator's constants by maximum likelihood, then reports whether the
refitted operator actually discriminates -- cross-validated, and against a
plain logistic model on the same raw features as a floor.

Required columns (one row per treated lesion):

    bed                 coronary | sfa | btk | carotid | renal | iliac
    d_prox, d_dist      reference diameters, mm (QCA, IVUS, OCT or duplex)
    length              lesion length, mm
    stenosis            diameter stenosis, 0-1
    calcium             0-1; grade/4 is fine if that is what was recorded
    tortuosity          0-1
    bifurcation, side_branch, cto, diabetes    0/1
    inflammation        0-1; hsCRP percentile is a reasonable stand-in
    runoff              0-3 for peripheral, leave 3 for coronary
    device              a key from panvas/devices.py CATALOG
    nominal_d, dev_length, n_devices
    prep                none | noncomp | scoring | atherec | ivl
    postdilate          0/1
    event_12m           0/1, clinically driven TLR or TLF within 12 months
    followup_days       optional; rows censored before 365 days are dropped

The two cohorts this was built for:

  * XINSORB 5-year BRS follow-up -- the only arm that can test whether the
    resorption term in Gamma_M is real, because it is the only device in the
    catalogue whose compliance is supposed to converge on the vessel's.
    Gamma_M(t) predicts that the BRS advantage appears only after roughly
    2 * degrade_tau, which is a falsifiable statement about years 2-5.

  * The multicentre 3D reconstruction cohort -- it carries per-lesion geometry,
    which is exactly what Gamma_G and Gamma_H need and what registry data never
    has.  Curvature and taper measured from the reconstruction should replace
    the `tortuosity` and `taper` proxies.

If the refitted operator does not beat the raw-feature floor out of sample,
that is the finding, and it should be reported as one.
"""

from __future__ import annotations
import argparse
import json
import math
import os
import sys

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, brier_score_loss
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from panvas.suitcordance import (Lesion, Plan, THETA_DEFAULT, evaluate,
                                 _THETA_PATH, _gamma_star_cache)

FIT_KEYS = ["k_comp", "k_stress", "k_fat", "drug_K", "k_short", "need_scale",
            "k_lumen", "k_strut", "nih_max_um", "beta"]
BOUNDS = [(0.05, 6.0), (0.05, 4.0), (0.2, 12.0), (0.1, 3.0), (0.1, 14.0),
          (0.6, 6.0), (0.1, 0.8), (0.02, 2.0), (80.0, 900.0), (1.0, 14.0)]

REQUIRED = ["bed", "d_prox", "d_dist", "length", "device", "nominal_d",
            "dev_length", "event_12m"]


def to_case(row) -> tuple:
    les = Lesion(
        bed=row["bed"], d_prox=float(row["d_prox"]), d_dist=float(row["d_dist"]),
        length=float(row["length"]),
        stenosis=float(row.get("stenosis", 0.75)),
        calcium=float(row.get("calcium", 0.2)),
        tortuosity=float(row.get("tortuosity", 0.2)),
        bifurcation=bool(row.get("bifurcation", 0)),
        side_branch=bool(row.get("side_branch", 0)),
        cto=bool(row.get("cto", 0)),
        diabetes=bool(row.get("diabetes", 0)),
        inflammation=float(row.get("inflammation", 0.2)),
        runoff=int(row.get("runoff", 3)))
    plan = Plan(device=row["device"], nominal_d=float(row["nominal_d"]),
                length=float(row["dev_length"]),
                prep=str(row.get("prep", "none")),
                postdilate=bool(row.get("postdilate", 0)),
                n_devices=int(row.get("n_devices", 1)))
    return les, plan


def predict(cases, theta) -> np.ndarray:
    return np.array([evaluate(l, p, horizon=380, dt=10.0, theta=theta).risk_12m
                     for l, p in cases])


def nll(x, cases, y) -> float:
    theta = dict(THETA_DEFAULT)
    theta.update({k: float(v) for k, v in zip(FIT_KEYS, x)})
    _gamma_star_cache.clear()
    p = np.clip(predict(cases, theta), 1e-5, 1 - 1e-5)
    return float(-np.sum(y * np.log(p) + (1 - y) * np.log(1 - p)))


def raw_features(df: pd.DataFrame) -> np.ndarray:
    cols = ["d_prox", "d_dist", "length", "stenosis", "calcium", "tortuosity",
            "bifurcation", "side_branch", "cto", "diabetes", "inflammation",
            "runoff", "nominal_d", "dev_length", "n_devices", "postdilate"]
    X = df.reindex(columns=cols).fillna(0.0).astype(float)
    X["ratio"] = X["nominal_d"] / (0.5 * (X["d_prox"] + X["d_dist"]))
    X["margin"] = (X["dev_length"] * X["n_devices"].clip(lower=1) - X["length"]) / 2
    return pd.concat([X, pd.get_dummies(df["device"], prefix="dev"),
                      pd.get_dummies(df["bed"], prefix="bed")],
                     axis=1).fillna(0.0).to_numpy(dtype=float)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("csv")
    ap.add_argument("--folds", type=int, default=5)
    ap.add_argument("--out", default="panvas/theta_real.json")
    args = ap.parse_args()

    df = pd.read_csv(args.csv)
    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        raise SystemExit(f"missing required columns: {missing}")
    if "followup_days" in df.columns:
        n0 = len(df)
        df = df[(df["event_12m"] == 1) | (df["followup_days"] >= 365)]
        print(f"dropped {n0 - len(df)} rows censored before 365 days")

    y = df["event_12m"].to_numpy(dtype=int)
    cases = [to_case(r) for _, r in df.iterrows()]
    Xraw = raw_features(df)
    print(f"n = {len(df)}, events = {y.sum()} ({y.mean():.3f})")
    if y.sum() < 25:
        print("WARNING: fewer than 25 events. Refitting ten constants on this "
              "cohort will overfit; treat the numbers below as descriptive.")

    skf = StratifiedKFold(n_splits=args.folds, shuffle=True, random_state=0)
    p_op = np.zeros(len(y))
    p_raw = np.zeros(len(y))
    p_prior = np.zeros(len(y))

    for k, (tr, te) in enumerate(skf.split(Xraw, y), 1):
        x0 = np.array([THETA_DEFAULT[k2] for k2 in FIT_KEYS])
        res = minimize(nll, x0, args=([cases[i] for i in tr], y[tr]),
                       method="L-BFGS-B", bounds=BOUNDS,
                       options=dict(maxiter=120))
        theta = dict(THETA_DEFAULT)
        theta.update({k2: float(v) for k2, v in zip(FIT_KEYS, res.x)})
        _gamma_star_cache.clear()
        p_op[te] = predict([cases[i] for i in te], theta)
        p_prior[te] = predict([cases[i] for i in te], THETA_DEFAULT)

        sc = StandardScaler().fit(Xraw[tr])
        lr = LogisticRegression(max_iter=3000, C=0.5).fit(sc.transform(Xraw[tr]), y[tr])
        p_raw[te] = lr.predict_proba(sc.transform(Xraw[te]))[:, 1]
        print(f"  fold {k}: operator nll {res.fun:.1f}")

    print("\nout-of-fold performance")
    for name, p in [("suitcordance, refitted", p_op),
                    ("suitcordance, literature constants", p_prior),
                    ("logistic on raw features", p_raw)]:
        p = np.clip(p, 1e-6, 1 - 1e-6)
        print(f"  {name:36s} AUC {roc_auc_score(y, p):.3f}   "
              f"Brier {brier_score_loss(y, p):.4f}")

    # final fit on everything, for deployment
    res = minimize(nll, np.array([THETA_DEFAULT[k] for k in FIT_KEYS]),
                   args=(cases, y), method="L-BFGS-B", bounds=BOUNDS,
                   options=dict(maxiter=200))
    theta = dict(THETA_DEFAULT)
    theta.update({k: float(v) for k, v in zip(FIT_KEYS, res.x)})
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(theta, fh, indent=2)
    print(f"\nrefitted constants written to {args.out}")
    print(f"copy it over {os.path.basename(_THETA_PATH)} to make it the default")


if __name__ == "__main__":
    main()
