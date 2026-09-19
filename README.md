# PanVas-Buddy

A pan-vascular interventional counterpart to ScienceBuddy (PhAI Labs, arXiv 2609.17523):
a domain **operator** that can be calibrated and refitted, and an editable **harness**
that decides how the operator gets used, with the two improved in separate loops.

The mapping to the paper is deliberate:

| ScienceBuddy | here |
|---|---|
| model θ (an LLM, trained with GRPO) | the suitcordance operator Γ_sc and its 13 constants (`panvas/suitcordance.py`) |
| harness H (instructions, skills, context) | `panvas/agent.py` `HARNESS_V0` — skills and numeric knobs, as data |
| inner recursion: fix θ, improve H | `inner_loop.py` |
| outer recursion: fix H, train θ | `calibrate.py` on published anchors, `fit_real.py` on a real cohort |
| tasks + rubrics from researcher interaction | `panvas/rubric.py`, and the disagreement form in the workbench |
| auxiliary model that diagnoses and writes edits | a lookup table from failing criterion to bounded edit (weaker, and transparent) |

Workbench: <https://lingsenyou.com/suitcordance/> — runs the calibrated operator entirely
in the browser. (A private Chinese-language build of the same page lives at
<https://claude.ai/artifact/D6CZMFWYJnPAX4fNR85L2X>.)

**Not a medical device.** Research prototype, not validated in patients, not to be used
to guide the care of any patient.

---

## 1. The operator

Device–vessel failure is treated as a property of the **agreement** between device and
vessel, not of either alone, and the same operator is applied in six arterial beds with
only the bed's own parameters changed.

Four axes, each in [0, 1]:

| axis | what it measures |
|---|---|
| Γ_G geometric | sizing against the bed's band, edge coverage, conformability, taper |
| Γ_M mechanical | device/wall compliance mismatch, overstretch wall stress, cyclic fatigue |
| Γ_H hemodynamic | flow lumen restored, strut flow disturbance, side branches, runoff |
| Γ_B biological | antiproliferative supply against neointimal drive, healing window |

    Γ_sc(t) = Π Γ_i(t)^{w_i},   Σw_i = 1, weights bed-specific

The geometric mean is the modelling commitment: a device fails along its worst-matched
axis, and a product cannot be rescued by a high score elsewhere the way a sum can.

Two scalars come off the trajectory, and one link turns it into risk:

    τ_sc    the time by which Γ_sc(t) has accumulated 63.2% of its total variation
    D_T     the time-averaged mismatch dose, (1/T)∫(1 − Γ_sc)dt
    λ(t)    = λ0(bed) · exp(β·(Γ*_bed − Γ_sc(t)))

λ0 is that bed's published best-practice 12-month event rate, and **Γ\*_bed is the match
level the bed's own reference device achieves** — not a global constant. Anchoring per
bed was necessary: best practice does not reach the same absolute Γ in every bed, and a
global Γ\* forced the fit to over-predict in the beds where it is lowest.

### What this fixes in the standing framework

- **three/four axes were used inconsistently** — there are exactly four here, each with
  named sub-terms and within-axis weights declared in one place (`W_G, W_M, W_H, W_B`).
- **Γ_sc had never actually been computed** — it now is, numerically, for any lesion and
  plan, and it is calibrated against published outcomes rather than asserted.
- **there was no time constant** — τ_sc is defined, computed, and reported; it separates
  devices that look identical at implantation. A PLLA BRS and a thin-strut DES in the same
  lesion differ in τ_sc by hundreds of days, because the scaffold's compliance converges
  on the wall's while the stent's never does.

## 2. Calibration, and the audit behind it

The first anchor set was sixteen literature values assembled the ordinary way, from
the interventional literature as remembered and re-read, each with a note and a
subjective trust weight. It was then audited adversarially: every value was hunted by
an independent agent required to *open* the primary source and forbidden to invent an
identifier, then attacked by two further checkers with different briefs - one asking
only whether the citation exists and says this, the other only whether the endpoint,
timepoint and population match - each told to default to refutation. 49 agents, 696
source lookups.

**Three of sixteen survived on value support, two of them the two arms of one trial —
and then applying our own CD-TLR preference moved the third, so two values survived
into the final set. One trial, two numbers.** Fourteen values changed, every one of them
downward, by factors of 1.02 to 5.83.
Five were endpoint substitutions, recoverable exactly from a different endpoint in the
correctly cited paper:

| anchor | asserted | what it actually was | correct |
|---|---|---|---|
| SFA-long-bare | 0.350 | 100 - 64.8, primary *patency* loss | TLR 0.318 |
| RENAL-stent | 0.140 | one-sided 95% upper bound of 9-month restenosis | CD-TLR 0.059 |
| CAR-stent | 0.035 | the trial's primary composite *safety* endpoint | CD-TLR 0.006 |
| COR-POBA | 0.320 | 6-month *angiographic* restenosis in the *stent* arm | 0.170 |
| ILIAC-stent | 0.045 | midpoint of CD-TLR and duplex restenosis | 0.028 |

and a sixth, BTK-DCB, was the midpoint of two *arms* of one trial. Coronary anchors
survived 1 of 7; femoropopliteal 3 of 4 on citation integrity, 0 of 7 against 2 of 4 on value support - the opposite of what was expected. About 74
percent of the original calibration weight rested on values the sources do not report.

The old claim that "the endpoint is held constant throughout" was false and has been
deleted rather than patched: within ABSORB III, TLF is 7.8 percent and ischaemia-driven
TLR is 3.0; within BIOFLOW V, 6.2 and 2.0. An endpoint stated as "CD-TLR or TLF"
permits a 2-3x choice at every row.

Every anchor now declares seven provenance fields - construct, trigger, adjudication,
estimator, analysis unit, actual window in days, design. One construct is preferred
(12-month clinically driven TLR); all-cause and symptom-driven TLR are labelled and
down-weighted; four anchors are excluded from the fit and kept in the table so that
what was dropped stays visible. Five of the six bed baseline rates were revised downward; the femoropopliteal
baseline was unchanged, because its reference arm is the one that survived the audit.

**Refit: MAE 1.4 percentage points over 12 anchors** (it was 3.5 over the
sixteen uncorrected ones).

Three things to hold against that number:

- **It is not performance.** Eleven free constants against roughly seven informative
  comparisons is under-determined; a low residual is what one should expect. Carotid,
  iliac and renal contribute one anchor each, which is also that bed's lambda0, so
  those beds are fitted trivially; four anchors are two arms each of two trials that
  share sites, adjudication and endpoint trigger.
- **Seven of eleven constants sit on their bounds**, including the compliance-mismatch
  and overstretch kernels, which both collapse to their floors. Once the anchors are
  corrected, **the fit no longer needs the mechanical axis**: the retained anchors are
  explained by Gamma_H and Gamma_B, and Gamma_M is never the binding axis. Either that
  axis is not doing real work, or a 12-month revascularisation endpoint cannot identify
  something whose predictions live in years 2-5. The falsification plan tests exactly
  that; the four-axis structure is not established by this calibration.
- **Three revascularisation constructs remain mixed** (CD-TLR, all-cause TLR,
  symptom-driven TLR), labelled and weighted rather than unified. Symptom-driven TLR
  without routine angiography biases low, surveillance-triggered TLR biases high; the
  biases run in opposite directions.

Anchors, provenance and the audit record are in `panvas/anchors.py`; fitted values in
`panvas/theta.json`. Disagree with an anchor, change it, re-run - the whole operator
moves with it.

## 3. Inner recursion: the harness

`inner_loop.py` holds the operator's constants fixed and edits only the harness:
which skills are on, and the thresholds they read. Parent and candidates are scored on
the same 60 development tasks; an edit is kept only if it is valid and strictly better.
120 test tasks are scored at the start and the end and never used to choose an edit.

**Held-out rubric score 0.749 → 0.948 (+0.199), with zero change to the operator.**

Two edits did all the work: *consult the operator before choosing a device* (+0.224) and
*modify moderate calcium before implanting* (+0.016). Nine further candidates were
proposed and rejected because they did not improve the development score.

One thing this taught that is worth keeping: the first version of the diagnoser proposed
**atomic** edits — enable a skill, or move a threshold — and the loop stalled on step 1,
because enabling a skill whose threshold still excludes every case is a no-op and so is
moving a threshold for a skill that is off. Edits have to be compound to be testable.

## 4. Experiments, including the one that failed

`experiments.py`, n = 9000 simulated procedures, outcomes drawn with an unobserved
frailty term and features seen through realistic measurement error. Re-run after the
anchor audit and refit; both headline findings sharpened.

**E1 — cross-bed transfer. Train on coronary + carotid, test on SFA, BTK, renal, iliac.**

| representation | in-bed AUC | cross-bed AUC | cross Brier | intercept-only | slope + intercept |
|---|---|---|---|---|---|
| A   raw + bed one-hot (tree) | 0.765 | 0.571 | 0.151 | 0.163 | 0.133 |
| A'  raw + bed physiology (tree) | 0.765 | 0.571 | 0.151 | 0.163 | 0.133 |
| A'' raw + bed physiology (linear) | 0.792 | 0.635 | 0.164 | 0.149 | 0.131 |
| B   suitcordance, 4 numbers (linear) | 0.820 | 0.610 | 0.249 | 0.151 | 0.132 |

Base-rate-only Brier on the test beds is 0.135. Both recalibration columns use the
test labels, so both are ceilings.

**The pan-vascular transfer claim did not survive its own test, and after the refit it
fails clearly.** Against a linear model given the same bed physiology, the operator's
cross-bed AUC advantage is **-0.024 (95% bootstrap -0.041 to -0.010)** — on the
uncorrected anchors this was −0.014 with an interval spanning zero; on the corrected
ones the interval excludes zero and the operator is worse. What looked like an
advantage over trees was only that a linear model extrapolates along a continuous bed
parameter and a tree cannot. Do not write the transfer claim into a paper.

Two further findings:

- **The risk scale does not transfer, and an offset does not fix it.** B's raw cross-bed
  Brier (0.249) is far worse than the base rate (0.135). An
  intercept-only shift leaves every arm worse than the base rate
  (0.151 for the operator); only refitting the slope repairs
  them, and the slope the operator needs is 0.26 — its
  log-odds are about four times too steep across beds. Ordering carries; the scale is
  over-dispersed, not merely offset.
- A and A' are identical by construction. With a handful of training beds, continuous
  bed parameters carry exactly the information of a one-hot, and a tree can only
  interpolate between values it has seen. Reported rather than engineered away.

**E2 — sample efficiency, coronary only, held out n = 400.**

| representation | n=100 | 200 | 400 | 800 |
|---|---|---|---|---|
| A   raw + bed one-hot (tree) | 0.600 | 0.744 | 0.664 | 0.699 |
| A'' raw + bed physiology (linear) | 0.596 | 0.670 | 0.755 | 0.778 |
| B   suitcordance, 4 numbers | 0.790 | 0.797 | 0.794 | 0.797 |

This is the result worth building on, and the refit strengthened it: four
physics-derived numbers sit at 0.790 from n = 100, a level 44 raw
features have not reached by n = 800. For single-centre cohorts, where n is always the
binding constraint, that is the whole argument for the operator.

**E3 — decision utility, 300 fresh cases, mean predicted 12-month event rate.**

    fixed protocol      0.0913
    harness v0          0.1097      (worse than the protocol: v0 never consults the operator)
    harness evolved     0.0431
    catalogue oracle    0.0412

## 5. What this cannot claim

- **Nothing here has seen a patient.** Outcomes in E1–E3 are generated by the same operator
  that model B consumes. They are statements about the representation under the model's own
  assumptions, not evidence about people.
- **The operator has no cost, complication, procedure-time or contrast term.** It will
  therefore recommend maximal lesion preparation almost every time. That column of the
  shortlist is a model gap, not advice.
- **Device entries are representative class parameters**, not specific commercial
  specifications, and several (radial force, device compliance, fatigue resistance) are
  order-of-magnitude estimates.
- **Bed parameters are priors, not measurements.** Every one is a single number in
  `panvas/beds.py`, declared so it can be challenged individually.
- **It is not a clinical decision tool** and the workbench says so on its face.

## 6. Attaching a real cohort

`fit_real.py` takes a CSV of real procedures with 12-month outcomes, refits the operator's
constants by maximum likelihood, and reports cross-validated AUC and Brier against a
logistic model on the same raw features as a floor. If the refitted operator does not beat
that floor out of sample, that is the finding.

Two cohorts this was built around:

- **XINSORB 5-year follow-up.** The only arm that can test the resorption term in Γ_M,
  because it is the only device whose compliance is supposed to converge on the vessel's.
  The model makes a falsifiable prediction: the BRS advantage on Γ_M appears only after
  roughly twice the degradation time constant, i.e. in years 2–5, not year 1.
- **The multicentre 3D reconstruction cohort.** It carries per-lesion geometry, which is
  exactly what Γ_G and Γ_H need and what registry data never has. Curvature and taper
  measured from the reconstruction should replace the `tortuosity` and `taper` proxies.

## 7. Reproducing it

```bash
pip install -r requirements.txt
python tests/test_operator.py      # 38 property checks on the operator
python calibrate.py                # refit the constants on the published anchors
python inner_loop.py               # evolve the harness with the operator frozen
python experiments.py              # E1-E3
python export_model.py             # dump the operator for the web workbench
python make_figures.py             # the three preprint figures
python build_site.py               # build the public page
python make_docx.py                # render the manuscript
```

`calibrate.py` runs a 12-start bounded least-squares fit and takes several minutes.
Everything else is fast. `tests/test_operator.py` needs no test runner and checks the
properties the operator is supposed to have -- axis bounds, that Gamma_sc really is the
weighted geometric mean of its axes, that tau_sc is finite, that a resorbable scaffold
has a longer time constant than a balloon, that preparing calcium lowers predicted risk,
that the per-bed reference cases reproduce their own lambda0, and that anchor MAE stays
under five percentage points. A refit that breaks one of those has broken the model, not
the test.

The browser workbench is a second implementation of the operator, so it can drift.
`tests/js_parity.md` records a numerical check of the published page against Python
(agreement to 5e-7 on Gamma and risk, 4e-4 days on tau_sc, across five lesions in four
beds) and says how to repeat it. Re-run it whenever the operator, the fitted constants
or the workbench source changes.

## 8. Publishing

`PUBLISHING.md` is the checklist for releasing the code, minting a DOI and posting the
preprint -- including the blockers that need a human: the author list and everyone's
written agreement, the competing-interest declaration, and the choice of preprint
server. bioRxiv fits this version only because it contains no patient data; a version
with the XINSORB or 3D reconstruction cohorts in it belongs on medRxiv.

## 9. Files

    panvas/beds.py          six arterial beds, one declared prior per field
    panvas/devices.py       15 device classes + lesion preparation
    panvas/suitcordance.py  the operator: four axes, τ_sc, the hazard link
    panvas/anchors.py       the audited anchor set: 12 in the fit, 4 excluded and kept
                            visible, each with seven provenance fields and its citation
    export_anchors.py       dump the anchor set with provenance and predictions
    panvas/agent.py         the harness (data) and the device-selection agent
    panvas/rubric.py        the fixed rubric composer and scorer
    panvas/tasks.py         task sampling; `from_case_log` for real recorded cases
    calibrate.py            outer loop on published anchors  -> panvas/theta.json
    inner_loop.py           inner loop on the harness        -> harness/harness_final.json
    experiments.py          E1-E3                            -> out/experiments.json
    fit_real.py             attach a real cohort             -> panvas/theta_real.json
    export_model.py         dump the operator for the web workbench
    app/workbench.src.html  the workbench source (`__MODEL__` is substituted at build)
    app/site.tpl.html       the public page template for lingsenyou.com/suitcordance/
    build_site.py           assemble the public page from the two above
    make_figures.py         the three preprint figures
    make_docx.py            render preprint/manuscript.md to .docx
    tests/test_operator.py  property checks, no test runner needed
    tests/js_parity.md      the JavaScript/Python numerical parity check
    PUBLISHING.md           release checklist, and what needs a human

**Not a medical device.** A research prototype, not validated in patients, not reviewed
by any regulatory authority, and not to be used to guide the care of any patient.
