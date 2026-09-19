# Getting the DOI

Two routes. Both need you signed in; neither needs you to write anything, because every
field is below. **Route A is the better one** — the DOI then updates itself whenever you
cut a new release, and the code lives somewhere people can read it. Route B is for when
you want the DOI in the next five minutes and will do GitHub later.

---

## Route A — GitHub, then Zenodo (recommended, ~15 minutes)

### A1. You: create an empty repository

<https://github.com/new> → owner `lingsenyou`, name `panvas-buddy`, **Public**.
Do **not** tick "Add a README", a licence, or a .gitignore — the local repository already
has all three and an initialised commit history. Press *Create repository*, then stop.

### A2. Me: push the code

Tell me it exists and I will run the push. Credential Manager already holds the token
from your website pushes, so nothing to type. If you would rather do it yourself:

```bash
cd "C:\Users\25450\Documents\claude_tmp\panvas_buddy" && git remote add origin https://github.com/lingsenyou/panvas-buddy.git && git push -u origin main
```

If it fails with a TLS `unexpected eof`, run it again — that happens on this connection.

### A3. You: switch Zenodo on for the repository

<https://zenodo.org> → *Log in with GitHub* → authorise → **Account → GitHub** → find
`lingsenyou/panvas-buddy` → flip the toggle **On**.

Order matters: Zenodo only archives releases created **after** the toggle is on. A
release made first is invisible to it.

### A4. You: cut the release

On GitHub: **Releases → Create a new release** → tag `v0.1.0` → title
`PanVas-Buddy v0.1.0` → description:

```
The suitcordance operator, the audited anchor set with full provenance, the raw citation-audit record, the editable device-selection harness, the in-silico evaluation, and the browser workbench. Accompanies the preprint of the same name.

Research prototype. Not validated in patients. Not a clinical decision tool.
```

Publish it. Zenodo picks it up within a few minutes.

### A5. You: finish the Zenodo record before publishing it

Zenodo opens a draft pre-filled from `.zenodo.json`. Check and fix:

- **Authors** — You Lingsen, Shen Li, Ge Junbo, in that order, each with the Zhongshan
  affiliation. Add ORCIDs if you have them.
- **Licence** — MIT (matches the LICENSE file).
- **Version** — 0.1.0.
- **Funding** — Zenodo's funder picker does not list the NSFC, so the grants sit in
  *Additional notes* instead: T2288101, 82170342, FudanX24AI003, yg2023-01.

Press *Publish*. You get two DOIs: a **concept DOI** that always resolves to the newest
version, and a version DOI for v0.1.0.

**Cite the concept DOI in the paper.**

---

## Route B — upload the archive directly (~5 minutes, no GitHub)

`out/panvas-buddy-v0.1.0.zip` (1.15 MB, 54 files) is the same content, already packaged.

<https://zenodo.org> → *New upload* → drop the zip in, then fill:

| field | value |
|---|---|
| Resource type | Software |
| Title | PanVas-Buddy: a calibrated, time-resolved operator for device–vessel matching across the arterial tree |
| Authors | You, Lingsen · Shen, Li · Ge, Junbo — all: Department of Cardiology, Zhongshan Hospital, Fudan University, Shanghai Institute of Cardiovascular Diseases, Shanghai, China |
| Licence | MIT |
| Version | 0.1.0 |
| Language | English |

Description — paste as is:

```
A suitcordance operator that treats device-vessel failure as a property of the agreement between device and vessel rather than of either alone. Four axes - geometric, mechanical, hemodynamic and biological - combine as a bed-weighted geometric mean and evolve in time, yielding a time constant and a time-averaged mismatch dose. Eleven free constants are calibrated, as one shared parameter set, against twelve audited 12-month clinically driven target-lesion-revascularisation rates spanning six arterial beds (coronary, femoropopliteal, below-the-knee, carotid, renal, iliac).

The release includes the operator, the anchor set with seven provenance fields per value, the raw record of the adversarial citation audit that rebuilt it, an editable device-selection harness with its rubric scorer, the in-silico evaluation including a reported null result on cross-bed transfer, the scripts that regenerate every figure, and a browser workbench.

Research prototype. Not validated in patients. Not a clinical decision tool. No patient-level data were used.
```

Keywords:

```
interventional cardiology; endovascular therapy; pan-vascular disease; device-vessel matching; suitcordance; drug-eluting stent; drug-coated balloon; bioresorbable scaffold; mechanistic model; model calibration; reproducible research
```

Additional notes:

```
Funding: National Natural Science Foundation of China (T2288101, 82170342); AI for Science Foundation of Fudan University (FudanX24AI003); Medical Engineering Joint Fund of Fudan University (yg2023-01).
```

Press *Publish*.

---

## Then, whichever route

Give me the concept DOI and I will:

1. paste it into §9 of the manuscript in place of the placeholder,
2. put it in the bioRxiv data-availability field,
3. add it to `CITATION.cff`,
4. rebuild the Word file,

and the submission package is closed except for your ORCIDs, Prof. Ge's email, and the
corresponding-author decision.

After the preprint is posted, go back to the Zenodo record once more and add the
preprint DOI as a *related identifier*, relation **is supplement to**. That is what links
the two objects in both directions.
