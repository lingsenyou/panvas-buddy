"""Figures for the preprint."""

import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from panvas.suitcordance import Lesion, Plan, evaluate

OUT = "out/figures"
os.makedirs(OUT, exist_ok=True)

AX = ["#0a6d9e", "#c2692a", "#7a5ea8", "#2f8f5b"]
DEV_COLS = ["#0a6d9e", "#c2692a", "#2f8f5b", "#4a5560"]
INK, MUTED, HAIR = "#10151b", "#6c7884", "#dbe1e6"

# plain Unicode rather than mathtext: renders identically in DejaVu Sans and
# keeps the source free of escape sequences
G_M_LABEL = "Γ_M"
G_H_LABEL = "Γ_H"
G_G, G_M, G_H, G_B, G_SC, TAU = "Γ_G", "Γ_M", "Γ_H", "Γ_B", \
                                "Γ_sc", "τ_sc"

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 8,
    "axes.edgecolor": MUTED, "axes.labelcolor": INK, "text.color": INK,
    "xtick.color": MUTED, "ytick.color": MUTED, "axes.linewidth": 0.8,
    "xtick.major.width": 0.8, "ytick.major.width": 0.8,
    "figure.dpi": 200, "savefig.dpi": 300, "savefig.bbox": "tight",
})


def despine(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


def place_labels(ax, items, x, gap_frac=0.062, dx=5):
    """Right-edge labels pushed apart so they never sit on top of one another.

    items: list of (y, text, colour, fontsize, weight)
    """
    y0, y1 = ax.get_ylim()
    gap = (y1 - y0) * gap_frac
    items = sorted(items, key=lambda it: -it[0])
    for i in range(1, len(items)):
        if items[i - 1][0] - items[i][0] < gap:
            items[i] = (items[i - 1][0] - gap,) + items[i][1:]
    drop = y0 - items[-1][0]
    if drop > 0:
        items = [(it[0] + drop,) + it[1:] for it in items]
    for yy, txt, col, fs, wt in items:
        ax.annotate(txt, (x, yy), xytext=(dx, 0), textcoords="offset points",
                    color=col, fontsize=fs, fontweight=wt, va="center")


# ---------------------------------------------------------------- figure 1
def fig1():
    les = Lesion(bed="coronary", d_prox=3.2, d_dist=2.95, length=22,
                 calcium=0.30, diabetes=True, inflammation=0.25)
    plans = [
        ("Ultrathin DES", Plan("des_ultrathin", 3.0, 28)),
        ("PLLA BRS 150 um", Plan("brs_plla", 3.0, 28)),
        ("Paclitaxel DCB", Plan("dcb_ptx_cor", 3.0, 26, prep="scoring")),
        ("Bare-metal stent", Plan("bms", 3.0, 28)),
    ]
    fig, axes = plt.subplots(1, 2, figsize=(7.4, 2.8),
                             gridspec_kw={"width_ratios": [1.1, 1]})

    a = axes[0]
    a.set_ylim(0, 1.03)
    r = evaluate(les, plans[0][1])
    labs = []
    for arr, c, lab in zip([r.G, r.M, r.H, r.B], AX, [G_G, G_M, G_H, G_B]):
        a.plot(r.t, arr, color=c, lw=1.7)
        labs.append((float(arr[-1]), lab, c, 8, "normal"))
    a.plot(r.t, r.gamma, color=INK, lw=2.5)
    labs.append((float(r.gamma[-1]), G_SC, INK, 8.5, "bold"))
    place_labels(a, labs, r.t[-1])
    a.axvline(r.tau_sc, color=MUTED, ls=(0, (4, 3)), lw=1)
    a.annotate(f"{TAU} = {r.tau_sc:.0f} d", (r.tau_sc, 0.05), xytext=(5, 0),
               textcoords="offset points", color=MUTED, fontsize=7.5)
    a.set_xlim(0, 900)
    a.set_xticks([0, 180, 365, 545, 730])
    a.set_xlabel("days")
    a.set_ylabel("agreement")
    a.set_title("a   Four axes, ultrathin DES", loc="left", fontsize=8.5, pad=6)
    despine(a)

    b = axes[1]
    b.set_ylim(0, 1.03)
    labs = []
    for (lab, plan), c in zip(plans, DEV_COLS):
        rr = evaluate(les, plan)
        b.plot(rr.t, rr.gamma, lw=1.9, color=c)
        labs.append((float(rr.gamma[-1]),
                     f"{lab}\n{TAU} {rr.tau_sc:.0f} d", c, 6.8, "normal"))
    place_labels(b, labs, 730, gap_frac=0.155)
    b.set_xlim(0, 1290)
    b.set_xticks([0, 365, 730])
    b.set_xlabel("days")
    b.set_ylabel(G_SC)
    b.set_title("b   Same lesion, four strategies", loc="left", fontsize=8.5, pad=6)
    despine(b)

    fig.tight_layout()
    fig.savefig(f"{OUT}/fig1_trajectories.png")
    plt.close(fig)
    print("fig1")


# ---------------------------------------------------------------- figure 2
def fig2():
    rows = json.load(open("out/anchors.json", encoding="utf-8"))
    beds = sorted({r["bed"] for r in rows})
    cmap = {b: c for b, c in zip(beds, ["#0a6d9e", "#c2692a", "#7a5ea8",
                                        "#2f8f5b", "#a8332a", "#4a5560"])}
    fig, ax = plt.subplots(figsize=(3.7, 3.5))
    lo, hi = 0.004, 0.68
    ax.plot([lo, hi], [lo, hi], color=MUTED, lw=1, zorder=0)
    ax.plot([lo, hi], [lo * 1.5, hi * 1.5], color=HAIR, lw=0.9, ls=(0, (3, 3)), zorder=0)
    ax.plot([lo, hi], [lo / 1.5, hi / 1.5], color=HAIR, lw=0.9, ls=(0, (3, 3)), zorder=0)
    used = [r for r in rows if r.get("included", True)]
    dropped = [r for r in rows if not r.get("included", True)]
    for r in dropped:                      # excluded from the fit: hollow
        ax.scatter(r["observed"], r["predicted"], s=34, facecolor="none",
                   edgecolor=cmap[r["bed"]], linewidth=1.1, alpha=.7, zorder=2)
    for r in used:
        ax.scatter(r["observed"], r["predicted"], s=16 + 48 * r["weight"],
                   color=cmap[r["bed"]], alpha=.88, edgecolor="white", linewidth=.6,
                   zorder=3)
    worst = max(used, key=lambda r: abs(r["observed"] - r["predicted"]))
    ax.annotate(worst["name"], (worst["observed"], worst["predicted"]),
                xytext=(-7, -11), textcoords="offset points", fontsize=6.5,
                color=MUTED, ha="right")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(lo, hi)
    ax.set_ylim(lo, hi)
    ticks = [0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5]
    ax.set_xticks(ticks)
    ax.set_yticks(ticks)
    ax.set_xticklabels([("%g%%" % (t*100)) for t in ticks])
    ax.set_yticklabels([("%g%%" % (t*100)) for t in ticks])
    ax.minorticks_off()
    ax.set_xlabel("published 12-month event rate")
    ax.set_ylabel("operator prediction")
    mae = np.mean([abs(r["observed"] - r["predicted"]) for r in used])
    ax.set_title(f"{len(used)} anchors in the fit, six beds, one parameter set\n"
                 f"MAE {mae * 100:.1f} percentage points; hollow = excluded from "
                 f"the fit;\ndashed lines are 1.5-fold", loc="left", fontsize=7.4,
                 pad=6)
    handles = [plt.Line2D([], [], marker="o", ls="", color=cmap[b], markersize=5,
                          label=b) for b in beds]
    ax.legend(handles=handles, fontsize=6.5, frameon=False, loc="upper left",
              handletextpad=.2, borderpad=0, labelspacing=.25)
    despine(ax)
    fig.tight_layout()
    fig.savefig(f"{OUT}/fig2_calibration.png")
    plt.close(fig)
    print("fig2")


# ---------------------------------------------------------------- figure 3
def fig3():
    e = json.load(open("out/experiments.json", encoding="utf-8"))
    fig, axes = plt.subplots(1, 2, figsize=(7.4, 2.8))

    keys = ["A   raw + bed one-hot (tree)", "A'' raw + bed physiology (linear)",
            "B   suitcordance, 4 numbers (linear)"]
    cols = {keys[0]: MUTED, keys[1]: "#c2692a", keys[2]: "#0a6d9e"}
    short = {keys[0]: "raw features, tree", keys[1]: "raw + bed physiology, linear",
             keys[2]: "suitcordance, 4 numbers"}

    a = axes[0]
    a.set_ylim(0.68, 0.83)
    labs = []
    for k in keys:
        d = e["e2"][k]
        a.plot(d["sizes"], d["auc"], "-o", ms=3.5, lw=1.7, color=cols[k])
        labs.append((d["auc"][-1], short[k], cols[k], 6.8, "normal"))
    place_labels(a, labs, 800, gap_frac=0.085)
    a.set_xscale("log")
    a.set_xticks([100, 200, 400, 800])
    a.set_xticklabels(["100", "200", "400", "800"])
    a.minorticks_off()
    a.set_xlim(88, 2600)
    a.set_xlabel("training procedures")
    a.set_ylabel("AUC, held out")
    a.set_title("a   Sample efficiency, coronary", loc="left", fontsize=8.5, pad=6)
    despine(a)

    b = axes[1]
    vals = [e["e1"][k]["auc_cross"] for k in keys]
    b.barh(range(len(keys)), vals, height=.5, color=[cols[k] for k in keys])
    for i, v in enumerate(vals):
        b.text(v + .004, i, f"{v:.3f}", va="center", fontsize=7.5, color=INK)
    b.set_yticks(range(len(keys)))
    b.set_yticklabels([short[k] for k in keys], fontsize=7)
    b.set_xlim(0.5, 0.73)
    b.set_xticks([0.5, 0.55, 0.6, 0.65, 0.7])
    b.set_xlabel("AUC on four held-out beds")
    lo, hi = e["e1"]["auc_diff_ci"]
    b.set_title(f"b   Cross-bed transfer: the claim that did not hold\n"
                f"operator vs bed physiology  {vals[2] - vals[1]:+.3f} AUC "
                f"(95% CI {lo:+.3f}, {hi:+.3f})", loc="left", fontsize=8, pad=6)
    b.invert_yaxis()
    despine(b)

    fig.tight_layout()
    fig.savefig(f"{OUT}/fig3_experiments.png")
    plt.close(fig)
    print("fig3")




# ---------------------------------------------------------------- figure 4
def fig4():
    """The accuracy / plausibility frontier: what physiology costs."""
    rows = json.load(open("out/bounds_sweep.json", encoding="utf-8"))
    short = ["no bounds", "neointima", "+ lumen", "both tight"]
    mae = [r["mae"] * 100 for r in rows]
    clip = [r["clipped"] for r in rows]
    nih = [r["worst_nih_um"] for r in rows]
    delta = [(r["mae_without_gamma_m"] - r["mae"]) * 100 for r in rows]
    x = list(range(len(rows)))

    fig, axes = plt.subplots(1, 3, figsize=(7.8, 2.8))
    a, b, c = axes

    a.plot(x, mae, "-o", color="#a8332a", ms=5, lw=1.8)
    for i, v in enumerate(mae):
        a.annotate(f"{v:.2f}", (i, v), xytext=(0, 7), textcoords="offset points",
                   ha="center", fontsize=7, color=INK)
    a.set_ylim(0, max(mae) * 1.30)
    a.set_ylabel("anchor MAE, points")
    a.set_title("a   what plausibility costs", loc="left", fontsize=8.5, pad=6)

    b.plot(x, nih, "-o", color="#0a6d9e", ms=5, lw=1.8)
    b.set_ylabel("worst neointima, um", color="#0a6d9e")
    b.tick_params(axis="y", colors="#0a6d9e")
    b.set_ylim(0, max(nih) * 1.30)
    b.axhspan(0, 150, color="#2f8f5b", alpha=.12)
    b.annotate("OCT range, contemporary stent", (-0.38, 205), fontsize=6.2,
               color="#2f8f5b")
    b2 = b.twinx()
    b2.plot(x, clip, "-s", color="#c2692a", ms=4.5, lw=1.6)
    b2.set_ylabel("anchors on the " + G_H_LABEL + " floor", color="#c2692a",
                  fontsize=7.5)
    b2.tick_params(axis="y", colors="#c2692a")
    b2.set_ylim(0, 12)
    b2.spines["top"].set_visible(False)
    b.set_title("b   how impossible the internals are", loc="left", fontsize=8.5,
                pad=6)

    cols = ["#2f8f5b" if v > 0.05 else "#9aa4ad" for v in delta]
    c.bar(x, delta, width=.55, color=cols)
    for i, v in enumerate(delta):
        c.annotate(f"{v:+.2f}", (i, v), xytext=(0, 4 if v >= 0 else -11),
                   textcoords="offset points", ha="center", fontsize=7, color=INK)
    c.axhline(0, color=MUTED, lw=1)
    c.set_ylim(min(delta) - .15, max(delta) * 1.5 + .1)
    c.set_ylabel("MAE cost of removing " + G_M_LABEL)
    c.set_title("c   does the mechanical axis earn its place", loc="left",
                fontsize=8.5, pad=6)

    for ax in (a, b, c):
        ax.set_xticks(x)
        ax.set_xticklabels(short, fontsize=7.2)
        ax.set_xlim(-0.45, len(rows) - 0.55)
        despine(ax)
    fig.tight_layout()
    fig.savefig(f"{OUT}/fig4_frontier.png")
    plt.close(fig)
    print("fig4")


if __name__ == "__main__":
    fig1()
    fig2()
    fig3()
    fig4()
    print("written to", OUT)
