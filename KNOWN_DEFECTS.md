# Known defects, 19 September 2026

Found by an adversarial pre-submission review (five reviewer lenses over the manuscript
and the code, every finding independently verified, then re-verified here by running the
code). Each entry below was reproduced from the released files before being written down.

**UPDATE 19 September 2026, later the same day.** D1 to D5 have now been fixed and the
operator refitted. Fixing them did not make the model work; it revealed a trade-off, and
that trade-off is now the paper's main result. See §4.2 of the manuscript and
`sweep_bounds.py`:

| bounds on the internals | MAE, pts | worst | neointima | Γ_H on floor | constants at a bound |
|---|---|---|---|---|---|
| unbounded | 1.18 | 5.09 | 1014 µm | 5/12 | 6/11 |
| neointima bounded | 1.51 | 5.87 | 819 µm | 6/12 | 7/11 |
| + lumen kernel bounded | 2.16 | 11.25 | 819 µm | 4/12 | 8/11 |
| both tight | 3.46 | 18.00 | 601 µm | 1/12 | 9/11 |

Accuracy degrades monotonically as the internals are forced toward plausibility. The
shipped constants are the second row — the only setting in which all four axes are
identified. **The operator as specified cannot reproduce these outcomes through a
physiologically defensible path**, and that is the finding, not a nuisance.

What each entry below now says is marked FIXED or OPEN. The citation audit in §3 of the
manuscript is unaffected by all of them.

---

## D1. OPEN (labelling fixed). The below-the-knee baseline is a withdrawn device

`λ₀(btk)` and `REFERENCE_CASE["btk"]` are the drug-eluting balloon arm of IN.PACT DEEP.
That trial **missed its primary efficacy endpoints** (CD-TLR 9.2% against 13.1% for plain
angioplasty, p = 0.291; late lumen loss 0.61 against 0.62 mm, p = 0.950), carried a
**major-amputation signal** (8.8% against 3.6%, p = 0.080), and IN.PACT Amphirion was
**withdrawn from all markets in November 2013**.

The code and the public page called this "best practice" until today. That wording is
now removed everywhere, and the arm is labelled for what it is: the best-adjudicated
12-month CD-TLR available in that bed, which is not the same thing.

Γ*(btk) = 0.21 against 0.47–0.74 for the other five beds. That gap is a property of the
anchor, not of the bed, and every below-the-knee number the operator produces inherits
it.

Four of the twelve retained anchors are paclitaxel-DCB arms from two Medtronic trials.
The paclitaxel mortality meta-analysis and the regulatory response to it are not
discussed anywhere in the paper. They should be.

## D2. FIXED, at a price. The fitted neointima was not physiological

`nih_max_um` = 822 µm at unit drive. Implied 12-month per-side neointimal thickness:

| anchor | implied neointima | vessel | observed CD-TLR |
|---|---|---|---|
| COR-DES-modern | 528 µm | 2.88 mm | 2.0% |
| COR-BMS | 1004 µm | 2.97 mm | 9.8% |
| SFA-POBA | 1400 µm | 5.40 mm | 20.6% |
| SFA-nitinol | 1905 µm | 5.40 mm | 12.7% |
| BTK-POBA | 2245 µm | 2.75 mm | 13.1% |
| RENAL-stent | 1257 µm | 5.40 mm | 5.9% |

Measured 12-month neointimal thickness by OCT or IVUS is of order 100 µm for a
contemporary drug-eluting stent and a few hundred for bare metal. The contemporary DES
anchor is modelled as ending year one with a **1.38 mm lumen in a 2.88 mm vessel — 52%
diameter stenosis — in a population whose observed CD-TLR is 2.0%.** COR-POBA, BTK-DCB
and BTK-POBA reach the 0.25 mm lumen floor, i.e. are modelled as occluded.

**Γ_H is at or near its numerical clip for 9 of the 12 anchors at 365 days.** Γ_H is the
axis the paper says does most of the explaining, so for most anchors τ_sc and the
mismatch dose are reporting when a clip was hit, not device–vessel physics.

The operator reproduces the endpoint through a path that is wrong. A 12-month
revascularisation endpoint cannot see that; late lumen loss and follow-up percent
diameter stenosis are published by the anchor trials and would have caught it
immediately. That check is now falsification item 6.

Fix: bound `nih_max_um` to a measurable range (≤ 400–500 µm) and refit; report what it
costs. If the anchors cannot be reproduced with physiological neointima, **that is the
result.**

## D3. FIXED. The mechanical axis could not penalise a balloon

Γ_M = 1.0000 exactly, at every timepoint, for all five balloon anchors. A plain balloon
at 1.30:1 in a 2.9 mm below-knee artery still scores exactly 1.0000; it only departs from
1 above about 1.55:1.

The cause is structural: for `expansion == "none"`, `deployed_diameter` returns the
post-recoil diameter, which the recoil model always puts *below* the reference, so
`eps = max(0, (d_dep − d_ref)/d_ref)` is identically zero. The axis that should carry
dissection and wall rupture is inert for exactly the devices that cause them, and there
is no dissection, bailout-stenting or perforation term anywhere in the model.

This is not neutral. In the femoropopliteal bed w_M = 0.36, the largest of the four
weights, so a drug-coated balloon is handed 36% of the weight at a perfect score before
any physiology is evaluated — and the device that sets Γ*(sfa) is itself a DCB.

The manuscript says the DCB trade-off "falls out of the model rather than being written
into it". Half of it is written in, by the `compliance_dev = None` convention.

Fix: compute overstretch strain from the balloon at inflation, not after recoil.

## D4. FIXED. Stenosis severity was ignored

`Lesion.stenosis` is declared and never read by the operator — only by the ML feature
builder and the real-data loader. A 40% stenosis and a 95% stenosis produce bit-identical
output (risk 0.008298 for both in a 3.0 mm coronary with a 3.0 × 20 DES).

Consequences: recoil is applied as a fraction of the balloon diameter rather than of the
acute gain (which is what recoils), and `_injury_index` is driven by
`(nominal_d − d_ref)/d_ref`, so **a 1:1 balloon delivers an injury index of exactly zero**
— plain angioplasty is modelled as causing no barotrauma at all, which deletes the
mechanism of post-PTA restenosis.

## D5. FIXED. Catalogue errors

- `se_interwoven` had `recoil = 2.00` where the field is a fraction and every other
  self-expanding entry is 0.02 — a hundredfold typo. Numerically inert (the
  self-expanding branch never reads recoil) but it shipped to the browser in
  `out/model.json`. **Fixed 2026-09-19.**
- `dcb_siro_cor`: 3.5 µg/mm² with 30-day retention. Marketed sirolimus DCBs are
  ~1.0–1.4 µg/mm², and their design rationale is *longer* tissue retention than
  paclitaxel, not shorter than the 45 days given to the paclitaxel entry. The dose is
  inflated roughly threefold and the retention ordering is reversed. **Not fixed** —
  changing it requires a refit.
- `bms` has `d_range = (2.5, 5.0)`, but the renal reference case uses `nominal_d = 5.5`.
  **The renal bed's entire calibration runs on a device sized outside its own catalogue
  range**, because nothing validates `nominal_d` against `d_range`. **Not fixed** — the
  fix changes λ₀(renal) and requires a refit.

## D6. Reporting

- The audit was performed by language-model agents and **no human has yet opened the
  twelve retained primary sources**. Now stated in §3.2 and §10, and falsification
  item 7.
- Six of the twelve anchors are their own bed's reference case and reproduce λ₀ by
  construction. The informative-subset error is 2.3 points, not 1.4.
- Removing Γ_M entirely improves the fit (1.37 → 1.32 points).
- The cross-bed transfer result does not survive a seed sweep and the bootstrap was
  resampling procedures rather than beds.

All six of these are now stated in the manuscript.
