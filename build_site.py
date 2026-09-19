"""
Build the public page for lingsenyou.com/suitcordance/.

The style block and the whole operator are lifted verbatim out of the private
workbench source, so the public page cannot drift from the calibrated model.
Only the chrome and the UI text differ, and the feedback form (which needs the
artifact runtime) is replaced by the calibration table and the limitations.
"""

import html
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "app", "workbench.src.html")
TPL = os.path.join(HERE, "app", "site.tpl.html")
OUT = os.path.abspath(os.path.join(
    HERE, "..", "lingsenyou_wcj_20260916", "lingsenyou.github.io", "suitcordance", "index.html"))

DEVNAME = {}


def extract(src: str) -> tuple:
    style = re.search(r"<style>\n(.*?)\n</style>", src, re.S)
    assert style, "style block not found"
    start = src.index('"use strict";') + len('"use strict";')
    end = src.index("/* ---------------------------------------------------------------\n   state and UI")
    return style.group(1).strip(), src[start:end].strip()


def anchors_table() -> str:
    rows = json.load(open(os.path.join(HERE, "out", "anchors.json"), encoding="utf-8"))
    bed = {"coronary": "Coronary", "sfa": "Femoropopliteal", "btk": "Below the knee",
           "carotid": "Carotid", "renal": "Renal", "iliac": "Iliac"}
    out = ['<div class="scroll"><table class="anchors"><thead><tr>'
           '<th>Anchor</th><th>Bed</th><th>Observed</th><th>Predicted</th>'
           '<th>Γsc</th><th>Endpoint construct</th><th>Trigger</th><th>Unit</th>'
           '<th>Window</th><th>Trust</th></tr></thead><tbody>']
    for r in rows:
        mark = "" if r.get("included", True) else ' style="opacity:.55"'
        name = html.escape(r["name"]) + ("" if r.get("included", True)
                                         else " <em>(excluded)</em>")
        pred = (f'{r["predicted"]*100:.1f}%' if r.get("included", True)
                else f'({r["predicted"]*100:.1f}%)')
        out.append(
            f'<tr{mark}><td>{name}</td><td>{bed.get(r["bed"], r["bed"])}</td>'
            f'<td class="num">{r["observed"]*100:.1f}%</td>'
            f'<td class="num">{pred}</td>'
            f'<td class="num">{r["gamma0"]:.3f}</td>'
            f'<td>{html.escape(r.get("construct", ""))}</td>'
            f'<td>{html.escape(r.get("trigger", ""))}</td>'
            f'<td>{html.escape(r.get("unit", ""))}</td>'
            f'<td class="num">{r.get("window_days", "")} d</td>'
            f'<td class="num">{r["weight"]:.2f}</td></tr>'
            f'<tr{mark}><td class="s" colspan="10">'
            f'{html.escape(r.get("citation", ""))}<br>{html.escape(r["source"])}'
            f'</td></tr>')
    out.append("</tbody></table></div>")
    out.append(
        '<p class="hint" style="margin-top:8px">Every anchor carries the endpoint it '
        'actually reports, because an earlier version of this table did not, and got '
        'thirteen of sixteen values wrong. The preferred construct is 12-month '
        '<b>clinically driven target lesion revascularisation</b>; anchors reporting '
        'all-cause or symptom-driven TLR are labelled and down-weighted, and four '
        'anchors are excluded from the fit but kept in the table so that what was '
        'dropped stays visible. Trust weight encodes audited evidence quality, not '
        'author confidence.</p>')
    return "\n".join(out)


def main() -> None:
    src = open(SRC, encoding="utf-8").read()
    tpl = open(TPL, encoding="utf-8").read()

    # the exported model carries Chinese display labels for the private workbench;
    # swap them for English so the public page has no stray CJK in its source
    m = json.load(open(os.path.join(HERE, "out", "model.json"), encoding="utf-8"))
    bed_en = {"coronary": "Coronary", "sfa": "Femoropopliteal", "btk": "Below the knee",
              "carotid": "Carotid", "renal": "Renal", "iliac": "Iliac"}
    prep_en = {"none": "None", "noncomp": "Non-compliant balloon", "scoring": "Scoring balloon",
               "atherec": "Atherectomy", "ivl": "Lithotripsy (IVL)"}
    for k, v in m["beds"].items():
        v["name_cn"] = bed_en[k]
    for k, v in m["prep"].items():
        v["label"] = prep_en[k]
    model = json.dumps(m, ensure_ascii=False, separators=(",", ":"))

    style, operator = extract(src)
    page = (tpl.replace("__STYLE__", style)
               .replace("__OPERATOR__", operator)
               .replace("__ANCHORS_TABLE__", anchors_table())
               .replace("__MODEL__", model))

    leftover = [c for c in page if "一" <= c <= "鿿"]
    if leftover:
        raise SystemExit(f"the public page still contains {len(leftover)} CJK characters; "
                         "translate them before publishing")
    for token in ("__STYLE__", "__OPERATOR__", "__MODEL__", "__ANCHORS_TABLE__"):
        assert token not in page, token

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    # the site's files use CRLF
    with open(OUT, "w", encoding="utf-8", newline="\r\n") as fh:
        fh.write(page)
    print("written", OUT, len(page), "chars")


if __name__ == "__main__":
    main()
