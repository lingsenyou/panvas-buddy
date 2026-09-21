"""
Regenerate preprint/abstract_plaintext.txt from the manuscript's Abstract section.

It used to be a hand-maintained copy, and on 2026-09-21 -- while it was being pasted
into the bioRxiv form -- it turned out to predate the Route B repairs. It still said the
mechanical axis was "not merely unused but currently harmful" because removing it
improved the fit, which is the opposite of what the repaired model does, and carried MAE
1.4 (now 1.51), informative-subset 2.3 (2.63), AUC 0.790 (0.817) and a cross-bed
difference of -0.024 (+0.012).

Deriving it from the manuscript means it cannot drift again.
"""

import io
import os
import re

BS = chr(92)   # a literal backslash, for the regex below

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "preprint", "manuscript.md")
OUT = os.path.join(HERE, "preprint", "abstract_plaintext.txt")


def main():
    text = io.open(SRC, encoding="utf-8").read()
    m = re.search(r"^## Abstract\s*$(.*?)^## ", text, re.S | re.M)
    if not m:
        raise SystemExit("no Abstract section in " + SRC)
    body = m.group(1)

    body = re.sub(r"\*\*(.+?)\*\*", r"\1", body, flags=re.S)   # bold
    body = re.sub(r"(?<!\w)\*(.+?)\*(?!\w)", r"\1", body, flags=re.S)  # italics
    body = re.sub(r"`(.+?)`", r"\1", body)
    body = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", body)       # links

    # Split on blank lines, whatever the line ending. This used os.linesep, which is
    # CRLF on Windows while the file stores LF, so every paragraph came back as one.
    blank = BS + "r?" + BS + "n" + BS + "s*" + BS + "r?" + BS + "n"
    paras = [" ".join(x.split()) for x in re.split(blank, body)]
    paras = [p for p in paras if p]

    # The Abstract section also carries the keyword line and a horizontal rule;
    # neither belongs in the journal form's abstract box.
    cut = [p for p in paras if not p.startswith("Keywords:") and set(p) != {"-"}]
    paras = cut

    out = ("\n\n".join(paras)) + "\n"
    io.open(OUT, "w", encoding="utf-8", newline="\n").write(out)
    words = len(out.split())
    print("preprint/abstract_plaintext.txt written: %d paragraphs, %d words, %d characters"
          % (len(paras), words, len(out.rstrip())))
    if len(out.rstrip()) > 5000:
        print("  WARNING: bioRxiv's abstract box is limited; check the length")


if __name__ == "__main__":
    main()
