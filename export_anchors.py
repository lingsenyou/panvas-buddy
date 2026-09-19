"""
Dump the anchor set with full provenance, and what the operator predicts for each.

The provenance fields are not decoration. The first version of this anchor set
mixed five endpoint constructs under one heading and thirteen of its sixteen
values turned out not to be what the cited papers report. Carrying the construct,
trigger, adjudication and analysis unit next to every number is what makes that
kind of error visible instead of invisible.
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from panvas.anchors import ALL_ANCHORS, audit_summary
from panvas.suitcordance import evaluate, THETA

rows = []
for a in ALL_ANCHORS:
    r = evaluate(a.lesion, a.plan, theta=THETA)
    rows.append(dict(
        name=a.name, bed=a.lesion.bed, device=a.plan.device,
        observed=a.value, predicted=round(r.risk_12m, 4), weight=a.weight,
        included=a.include,
        gamma0=round(r.gamma0, 3), tau=round(r.tau_sc),
        construct=a.construct, trigger=a.trigger, adjudication=a.adjudication,
        estimator=a.estimator, unit=a.unit, window_days=a.window_days,
        design=a.design, citation=a.citation, doi=a.doi, source=a.note,
    ))

os.makedirs("out", exist_ok=True)
with open("out/anchors.json", "w", encoding="utf-8") as fh:
    json.dump(rows, fh, ensure_ascii=False, indent=1)

used = [r for r in rows if r["included"]]
errs = [abs(r["observed"] - r["predicted"]) for r in used]
summary = audit_summary()
summary["mae_in_fit"] = round(sum(errs) / len(errs), 4)
summary["max_err_in_fit"] = round(max(errs), 4)
with open("out/anchor_audit.json", "w", encoding="utf-8") as fh:
    json.dump(summary, fh, ensure_ascii=False, indent=1)

print(f"{len(rows)} anchors ({len(used)} in the fit, {len(rows)-len(used)} excluded)")
print(f"MAE over the fitted anchors {summary['mae_in_fit']:.4f}, "
      f"worst {summary['max_err_in_fit']:.4f}")
print("constructs in the fit:", ", ".join(summary["constructs_in_fit"]))
for r in rows:
    flag = " " if r["included"] else "x"
    print(f" {flag} {r['name']:16s} {r['observed']*100:6.1f}% obs  "
          f"{r['predicted']*100:6.1f}% pred  w={r['weight']:.2f}  {r['construct']}")
