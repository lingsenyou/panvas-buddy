"""
Emit Python reference values, and the console snippet that checks the browser
workbench against them. See tests/js_parity.md.
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from panvas.suitcordance import Lesion, Plan, evaluate

CASES = [
    ("coronary",
     dict(d_prox=3.2, d_dist=2.95, length=22, calcium=0.30, tortuosity=0.20,
          inflammation=0.25, diabetes=True),
     dict(device="des_ultrathin", nominal_d=3.0, length=28, prep="none",
          postdilate=False, n_devices=1)),
    ("coronary",
     dict(d_prox=3.0, d_dist=2.95, length=15, calcium=0.15, tortuosity=0.2,
          inflammation=0.2, diabetes=False),
     dict(device="brs_plla", nominal_d=3.0, length=23, prep="scoring",
          postdilate=True, n_devices=1)),
    ("sfa",
     dict(d_prox=5.8, d_dist=5.2, length=150, calcium=0.5, tortuosity=0.3,
          inflammation=0.25, runoff=2),
     dict(device="se_nitinol", nominal_d=6.0, length=150, prep="ivl",
          postdilate=False, n_devices=1)),
    ("btk",
     dict(d_prox=2.9, d_dist=2.6, length=100, calcium=0.45, tortuosity=0.25,
          inflammation=0.35, runoff=1, diabetes=True),
     dict(device="dcb_periph", nominal_d=2.75, length=120, prep="none",
          postdilate=False, n_devices=1)),
    ("carotid",
     dict(d_prox=7.5, d_dist=5.0, length=20, calcium=0.3, tortuosity=0.2,
          inflammation=0.2),
     dict(device="car_dual", nominal_d=8.0, length=30, prep="none",
          postdilate=True, n_devices=1)),
]

SNIPPET = """const CASES=%s;
const out = CASES.map(c => {
  const les = Object.assign({bed:c.bed}, c.les);   // c.les carries every field
  const r = evaluateCase(les, c.plan, 5, 730);
  const d = (a,b) => +Math.abs(a-b).toExponential(2);
  return {bed:c.bed, dev:c.plan.device,
          dg0:d(r.gamma[0], c.g0),
          dgend:d(r.gamma[r.gamma.length-1], c.gend),
          dtau:d(r.tau_sc, c.tau),
          ddef:d(r.deficit, c.deficit),
          drisk:d(r.risk12, c.risk12)};
});
console.table(out);
"""


def main():
    out = []
    for bed, lk, pk in CASES:
        les = Lesion(bed=bed, **lk)
        # emit EVERY field, defaults included. The JS side builds its lesion from
        # this dict, so any field left to a default on one side and set on the other
        # is a silent mismatch -- which is exactly what happened on 2026-09-19 once
        # `stenosis` started reaching the operator.
        full = {f: getattr(les, f) for f in Lesion.__dataclass_fields__ if f != "bed"}
        r = evaluate(les, Plan(**pk), horizon=730, dt=5.0)
        out.append(dict(bed=bed, les=full, plan=pk,
                        g0=round(r.gamma0, 6), gend=round(r.gamma_end, 6),
                        tau=round(r.tau_sc, 3), deficit=round(r.deficit, 6),
                        risk12=round(r.risk_12m, 6)))

    root = os.path.dirname(HERE)
    os.makedirs(os.path.join(root, "out"), exist_ok=True)
    with open(os.path.join(root, "out", "js_reference.json"), "w",
              encoding="utf-8") as fh:
        json.dump(out, fh)
    with open(os.path.join(root, "out", "js_check.js"), "w", encoding="utf-8") as fh:
        fh.write(SNIPPET % json.dumps(out))

    for c in out:
        print(f"{c['bed']:9s} {c['plan']['device']:14s} "
              f"g0={c['g0']:.5f} tau={c['tau']:7.2f} risk12={c['risk12']:.5f}")
    print("\nout/js_reference.json and out/js_check.js written; "
          "paste the snippet into the workbench console")


if __name__ == "__main__":
    main()
