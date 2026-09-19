"""
Render the preprint manuscript to .docx, with figures and the anchor table.

bioRxiv accepts Word as well as PDF, and Word is the more useful of the two here
because the author list, funding and competing-interest statements still have to
be filled in by a human before anything is posted.
"""

import json
import os
import re
import sys

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt, RGBColor

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "preprint", "manuscript.md")
OUT = os.path.join(HERE, "preprint", "Suitcordance_preprint.docx")
FIGS = [("Figure 1", "out/figures/fig1_trajectories.png", 6.4),
        ("Figure 2", "out/figures/fig2_calibration.png", 3.9),
        ("Figure 3", "out/figures/fig3_experiments.png", 6.4)]

INLINE = re.compile(r"(\*\*.+?\*\*|\*[^*]+?\*|`[^`]+?`)")


def add_runs(par, text):
    """Bold, italic and code spans; everything else plain."""
    for piece in INLINE.split(text):
        if not piece:
            continue
        if piece.startswith("**") and piece.endswith("**"):
            par.add_run(piece[2:-2]).bold = True
        elif piece.startswith("`") and piece.endswith("`"):
            r = par.add_run(piece[1:-1])
            r.font.name = "Consolas"
            r.font.size = Pt(9.5)
        elif piece.startswith("*") and piece.endswith("*"):
            par.add_run(piece[1:-1]).italic = True
        else:
            par.add_run(piece)


def anchor_table(doc):
    rows = json.load(open(os.path.join(HERE, "out", "anchors.json"), encoding="utf-8"))
    bed = {"coronary": "Coronary", "sfa": "Femoropopliteal", "btk": "Below the knee",
           "carotid": "Carotid", "renal": "Renal", "iliac": "Iliac"}
    p = doc.add_paragraph()
    add_runs(p, "**Table 1. The sixteen calibration anchors.** Endpoint throughout: "
                "12-month clinically driven target lesion revascularisation or target "
                "lesion failure. Trust: 1.0 a randomised trial figure quoted directly, "
                "0.7 a consistent range across trials, 0.4 an expert estimate.")
    t = doc.add_table(rows=1, cols=6)
    t.style = "Light Grid Accent 1"
    hdr = ["Anchor", "Bed", "Observed", "Predicted", "Gamma_sc(0)", "Trust"]
    for c, h in enumerate(hdr):
        cell = t.rows[0].cells[c]
        cell.text = ""
        r = cell.paragraphs[0].add_run(h)
        r.bold = True
        r.font.size = Pt(9)
    for r0 in rows:
        cells = t.add_row().cells
        vals = [r0["name"], bed.get(r0["bed"], r0["bed"]),
                f'{r0["observed"]*100:.1f}%', f'{r0["predicted"]*100:.1f}%',
                f'{r0["gamma0"]:.3f}', f'{r0["weight"]:.1f}']
        for c, v in enumerate(vals):
            cells[c].text = ""
            run = cells[c].paragraphs[0].add_run(v)
            run.font.size = Pt(8.5)
    doc.add_paragraph()
    p = doc.add_paragraph()
    r = p.add_run("Source notes for each anchor are carried in the released code "
                  "(panvas/anchors.py) and must be replaced by primary citations "
                  "before posting.")
    r.italic = True
    r.font.size = Pt(9)


def main():
    md = open(SRC, encoding="utf-8").read().splitlines()
    doc = Document()

    st = doc.styles["Normal"]
    st.font.name = "Calibri"
    st.font.size = Pt(10.5)
    st.paragraph_format.space_after = Pt(7)
    st.paragraph_format.line_spacing = 1.25

    in_code = False
    for raw in md:
        line = raw.rstrip()

        if line.startswith("    ") and line.strip():
            p = doc.add_paragraph()
            r = p.add_run(line.strip())
            r.font.name = "Consolas"
            r.font.size = Pt(9.5)
            p.paragraph_format.space_after = Pt(2)
            in_code = True
            continue
        in_code = False

        if not line.strip() or line.strip() == "---":
            continue

        if line.startswith("# "):
            h = doc.add_heading(line[2:].strip(), level=0)
            h.alignment = WD_ALIGN_PARAGRAPH.LEFT
        elif line.startswith("## "):
            doc.add_heading(line[3:].strip(), level=1)
        elif line.startswith("### "):
            doc.add_heading(line[4:].strip(), level=2)
        elif line.startswith("> "):
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.3)
            add_runs(p, line[2:].strip())
            for r in p.runs:
                r.font.color.rgb = RGBColor(0xA8, 0x33, 0x2A)
                r.font.size = Pt(9.5)
        elif re.match(r"^\d+\.\s", line):
            p = doc.add_paragraph(style="List Number")
            add_runs(p, re.sub(r"^\d+\.\s", "", line))
        elif line.startswith("- "):
            p = doc.add_paragraph(style="List Bullet")
            add_runs(p, line[2:])
        else:
            p = doc.add_paragraph()
            add_runs(p, line)

    doc.add_page_break()
    doc.add_heading("Figures", level=1)
    for name, path, width in FIGS:
        full = os.path.join(HERE, path.replace("/", os.sep))
        if not os.path.exists(full):
            raise SystemExit(f"missing figure: {full}")
        doc.add_picture(full, width=Inches(width))
        doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
        cap = doc.add_paragraph()
        r = cap.add_run(f"{name}. See legend in the text.")
        r.font.size = Pt(9)
        r.italic = True
        cap.alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_page_break()
    doc.add_heading("Table 1", level=1)
    anchor_table(doc)

    doc.save(OUT)
    print("written", OUT, os.path.getsize(OUT), "bytes")


if __name__ == "__main__":
    main()
