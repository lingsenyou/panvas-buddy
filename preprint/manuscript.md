# Suitcordance: a calibrated, time-resolved operator for device–vessel matching across the arterial tree, and an audit of the literature values it was calibrated against

**Lingsen You**<sup>1,2,3,4,5</sup>, **Li Shen**<sup>1,2,3,4,5</sup>‡,
**Junbo Ge**<sup>1,2,3,4,5</sup>‡

<sup>1</sup> Department of Cardiology, Zhongshan Hospital, Fudan University, Shanghai
Institute of Cardiovascular Diseases, No. 180 Fenglin Road, Xuhui District, Shanghai
200032, China

<sup>2</sup> National Clinical Research Center for Interventional Medicine, No. 180
Fenglin Road, Xuhui District, Shanghai 200032, China

<sup>3</sup> Oriental Pan-Vascular Devices Innovation College, University of Shanghai
for Science and Technology (USST), No. 516 Jungong Road, Yangpu District, Shanghai
200093, China

<sup>4</sup> State Key Laboratory of Cardiovascular Diseases, Zhongshan Hospital, Fudan
University, No. 1609 Xietu Road, Xuhui District, Shanghai 200032, China

<sup>5</sup> NHC Key Laboratory of Ischemic Heart Diseases, No. 1609 Xietu Road, Xuhui
District, Shanghai 200032, China

‡ Corresponding authors. Email: shen_li@fudan.edu.cn (L.S.);
&lt;GE_EMAIL&gt; (J.G.).



---

## Abstract

Device selection in endovascular intervention is governed by bed-specific rules of
thumb that are not commensurable across arterial beds and carry no explicit time
course. We formalise device–vessel failure as a property of the *agreement*
between device and vessel rather than of either alone, and define a suitcordance
operator Γ_sc on four axes: geometric, mechanical, hemodynamic and biological. The
axes combine as a bed-weighted geometric mean, so that a collapse on any one axis
cannot be compensated by the other three. Every axis is a function of time, which
yields two scalars the static formulation lacked: a time constant τ_sc, the time by
which the trajectory has accumulated 63.2% of its total variation, and a
time-averaged mismatch dose. Risk is linked through λ(t) = λ₀·exp(β·(Γ*−Γ_sc(t))),
anchored per bed at the match level that bed's own reference device attains.

Calibrating such an operator requires published event rates, and assembling them
turned out to be the hardest and most instructive part of the work. Our first
anchor set of sixteen literature values was subjected to an adversarial citation
audit in which every value was independently hunted and then attacked by two
skeptics. **Only three of the sixteen were values the primary source actually
reports at a commensurable 12-month endpoint; two of those three were the two arms of a
single trial, and fixing our own stated endpoint preference then moved the third, so two
values survived into the final set — one trial, two numbers.** Fourteen values changed,
every one of them downward, by factors of 1.02 to 5.83, and five could be
reverse-engineered exactly from a *different* endpoint reported in the correctly cited
paper — endpoint substitution rather than transcription error. Within a single trial, target lesion failure and clinically driven target
lesion revascularisation differ by two- to threefold, so a claim that the endpoint
is "held constant" while either may be used holds nothing constant.

We therefore report the corrected calibration: 12 anchors, all
revascularisation constructs, each carrying seven declared provenance fields, with
four further anchors excluded and listed. Eleven free constants fit these with a
mean absolute error of 1.4 percentage points — which we report as a consistency check
and not as performance, because eleven constants against roughly seven informative
comparisons is under-determined. Seven of the eleven land on their bounds, and two of
those are the compliance-mismatch and overstretch kernels: once the anchors are
corrected, the fit no longer needs the mechanical axis. We read that as a 12-month
revascularisation endpoint having no power over slow-acting mechanics rather than as
the axis being empty, and §7 states the test that would decide it. In a 9,000-procedure simulation
with an unobserved frailty term and realistic measurement error, the operator's
four-number summary reached AUC 0.790 at n = 100, a level 44 raw
features had not reached by n = 800. The pan-vascular transfer claim did not survive
its own test: against a linear model given the same continuous bed physiology, the
operator's cross-bed advantage was -0.024 AUC (95% bootstrap -0.041 to -0.010),
an interval that excludes zero: it is worse.
No patient-level data were used. This is a modelling, calibration and
evidence-audit report, not a validation.

**Keywords:** pan-vascular intervention, device–vessel matching, endpoint
definition, calibration, evidence audit, bioresorbable scaffold, drug-coated balloon

---

## 1. Introduction

An interventionalist choosing a device is solving a matching problem, but the tools
of the trade do not describe it as one. Sizing rules are bed-specific and mutually
untranslatable: 1:1 to the distal reference in a coronary artery, 10–20% oversizing
for a self-expanding femoropopliteal stent, 15–50% in the carotid. Each rule is
defensible in its own bed, and none of them says what the rules have in common —
that a device and a vessel can agree or disagree along several axes at once, and
that the disagreement evolves.

Every clinically consequential mismatch has a time course. A scaffold's compliance
converges on the wall's as it resorbs; a drug washes out while the proliferative
stimulus it opposes decays on its own schedule; a nitinol stent accumulates fatigue
over the first year in the flexion zone. Yet device–vessel matching is almost always
discussed as a property of the moment of implantation, and two devices that look
identical on the table can diverge over the following two years for reasons that are
predictable from their materials.

The framework this paper operationalises was set out by our group as the research
programme of China's National Basic Science Center for panvascular interventional
complex systems [1]. That statement names device–vessel suitcordance as the object of
study; what it does not do — what no statement of the idea has done — is compute it.
Γ_sc has been a concept with no numerical value, no time course, and therefore nothing
that could be checked against an outcome. This paper is an attempt to close that gap
and to report honestly what happens when one does.

This paper does four things. It defines an operator that computes the agreement
between a device and a vessel on four axes, as a function of time, in any of six
arterial beds from one parameter set (§2). It reports an adversarial audit of the
literature values such an operator has to be calibrated against, which found most of
our own first attempt to be wrong (§3) — a result we believe generalises well beyond
this model. It fits the operator to the corrected values (§4) and tests, in
simulation, the claim that motivated the construction, reporting that the claim
failed (§5). And it states what would falsify the operator on real data before
anyone runs it (§7).

## 2. The operator

### 2.1 Four axes

For a lesion *x* (bed, proximal and distal reference diameter, length, calcium,
tortuosity, bifurcation, side branch, runoff, diabetes, inflammatory burden) and a
plan *a* (device class, nominal diameter, length, number of devices, lesion
preparation, post-dilatation), four agreement functions are defined on [0, 1]:

**Γ_G, geometric.** Device-to-vessel diameter ratio against the bed's own band, with
asymmetric penalties above and below it (undersizing bites harder than oversizing);
edge coverage margin, penalised steeply for geographic miss and gently for needless
edge injury; conformability against tortuosity; and the residual mismatch a straight
device leaves in a tapering vessel. For a device that leaves nothing behind, the
geometric question is whether the balloon was sized correctly at inflation — what
recoil then costs is charged to Γ_H as residual lumen, not twice.

**Γ_M, mechanical.** Compliance mismatch between device and wall, where wall
compliance falls with calcium and device compliance for a resorbable scaffold relaxes
toward the wall's with its degradation time constant; overstretch wall stress against
a calcium-dependent tolerable strain; and cyclic fatigue, which accrues over the
first year in proportion to the bed's deformation burden, the device's fatigue
resistance and the implanted length. A device that leaves nothing behind is, by
construction, a perfect compliance match — which is why the classic drug-coated
balloon trade-off falls out of the model rather than being written into it: perfect
on Γ_M, unhelped against recoil on Γ_G and Γ_H.

**Γ_H, hemodynamic.** Flow lumen restored, computed from the deployed diameter less
struts and the neointima that grows on them, against the reference; strut flow
disturbance, scaled by strut thickness over calibre and by the bed's baseline shear,
decaying as struts are covered; and branch cost, for a covered device across a branch
that matters, a stented bifurcation, or a peripheral lesion with poor runoff.

**Γ_B, biological.** Antiproliferative supply against neointimal drive. Drive is the
bed's proliferative propensity scaled by diabetes, inflammatory burden and the
barotrauma the plan delivers; supply is the device's drug concentration decaying with
its retention constant. What is penalised is the *fraction* of drive left unopposed,
not its absolute size, so a drug outliving its stimulus earns nothing. A second term
charges the healing window: the period struts stay uncovered, lengthened by the drug
and by strut thickness, and for a resorbable device the agreement between resorption
and healing timescales.

The four axes are a refinement of the three ecological balances — mechanical,
cellular, and physicochemical–immune — in which the framework was originally stated
[1] and subsequently developed [2]. The mapping is not one to one, and the difference is deliberate: the geometric
and hemodynamic axes separate two things the mechanical balance conflated, namely
whether the device fits the vessel and whether the lumen it leaves carries flow. §4
reports that the corrected calibration does not currently need the mechanical axis,
which is a result about this operator and this endpoint, not about the balances.

### 2.2 Composition

    Γ_sc(x, a, t) = Π_i Γ_i(x, a, t)^{w_i(bed)},   Σ_i w_i = 1

The geometric mean is the modelling commitment, not a convenience. A device fails
along its worst-matched axis, and a product cannot be rescued by a high score
elsewhere the way a sum can. Weights are bed-specific and declared: the mechanical
axis carries the largest weight in the femoropopliteal artery, where stent fracture
is a real failure mode; the geometric axis carries it in the carotid, where large
deliberate oversizing is the technique.

### 2.3 Time, and τ_sc

Γ_sc is evaluated on a day grid to two years. Two scalars are read off it:

    τ_sc : the time t at which ∫₀^t |dΓ_sc/ds| ds = 0.632 · ∫₀^T |dΓ_sc/ds| ds
    D_T  : (1/T) ∫₀^T (1 − Γ_sc(t)) dt

τ_sc is defined on total variation rather than on a monotone approach to an
asymptote, so it stays well defined when the trajectory is non-monotone, which it
routinely is. It separates devices that are indistinguishable at implantation
(Figure 1b): in the same coronary lesion a paclitaxel-coated balloon has τ_sc = 124
days while an ultrathin-strut drug-eluting stent has τ_sc = 261 days — the balloon's
fate is largely settled in the first four months, the stent's is not. The two are not
indistinguishable at implantation (Γ_sc(0) 0.801 against 0.857), but the gap at
implantation is small next to the difference in how fast each one gets there.

### 2.4 Hazard link

    λ(t) = λ₀(bed) · exp(β · (Γ*_bed − Γ_sc(t)))

λ₀ is the bed's published best-practice 12-month clinically driven TLR. Γ*_bed is
**not** a global constant: it is the year-one mean match that the bed's own reference
device attains under the current parameters. Anchoring per bed was necessary rather
than cosmetic — best practice does not reach the same absolute Γ_sc in every bed, and
a global Γ* forced the fit to over-predict systematically where the achievable match
is lowest.

## 3. An audit of the literature values

### 3.1 Why this section exists

A mechanistic model of device–vessel matching is only as good as the outcome rates it
is tied to, and those rates are the part of such a paper that is least often checked.
We built a first anchor set of sixteen 12-month event rates across six beds in the
ordinary way: from the interventional literature as the author remembered and
re-read it, each with a note on its justification and a subjective trust weight.

We then audited it adversarially. Each anchor was given to an independent literature
agent tasked with finding and *opening* the primary source, forbidden from inventing
any identifier, and required to report the number and the endpoint exactly as the
source words them. Every citation that came back was then attacked by two further
independent checkers with different briefs — one asked only whether the citation
exists and says this, the other only whether the endpoint, timepoint and population
are the ones claimed — each instructed to default to refutation when unsure.
Forty-nine agents, 696 source lookups.

### 3.2 What the audit found

**Three of the sixteen survived, and then one of those three moved too.** Two criteria
have to be kept apart here, because conflating them is the very failure this section is
about. On *citation integrity* — the paper exists, the identifier resolves, the value is
transcribed correctly — the per-bed flags were coronary 1 of 7, femoropopliteal 3 of 4,
carotid 1 of 1, below-the-knee 1 of 2, iliac 0 of 1, renal 0 of 1: six of sixteen. On
*value support* — the source reports this number at a commensurable 12-month endpoint —
three survived: COR-BRS-plla, SFA-DCB and SFA-POBA, two of them the two arms of one
trial.

Then applying our own stated preference for clinically driven TLR moved COR-BRS-plla as
well, because its asserted 7.8% is ABSORB III's TLF composite and that trial's
ischaemia-driven TLR is 3.0%. **Two values survived into the final anchor set unchanged:
SFA-DCB and SFA-POBA. One trial, two numbers.** That is what the original calibration
actually rested on.

**Fourteen of the sixteen values changed, every one of them downward**, by factors of
1.02 to 5.83 — thirteen because the source reports something else, and COR-BRS-plla
because we fixed the endpoint. The direction is uniform and the magnitudes are not, so
this is not a scale factor a shared intercept can absorb: it distorts the ordering of
the anchors relative to one another, which is exactly what a cross-bed shared-parameter
fit depends on.

**Five were endpoint substitutions**, recoverable exactly from a different endpoint in
the correctly cited paper (Table 1):

| anchor | asserted | is actually | correct value |
|---|---|---|---|
| SFA-long-bare | 0.350 | 100 − 64.8, primary *patency* loss | TLR 0.318 |
| RENAL-stent | 0.140 | one-sided 95% upper bound of 9-month binary restenosis (point estimate 10.5%) | CD-TLR 0.059 |
| CAR-stent | 0.035 | the trial's primary composite *safety* endpoint | CD-TLR 0.006 |
| COR-POBA | 0.320 | 6-month *angiographic* restenosis in the *stent* arm | 1-y symptom-driven TLR 0.170 |
| ILIAC-stent | 0.045 | midpoint of CD-TLR (2.8%) and duplex restenosis (6.1%) | CD-TLR 0.028 |

and a sixth, BTK-DCB at 0.120, was the midpoint of the two *arms* of one trial (9.2%
and 13.1%). None of these is a typing mistake. Each is a plausible number from the
right paper, and each was reachable by someone reading that paper without holding the
endpoint definition fixed.

**The endpoint was not held constant, and could not have been.** Within ABSORB III,
TLF is 7.8% and ischaemia-driven TLR is 3.0%; within BIOFLOW V, TLF is 6.2% and
CD-TLR is 2.0%. A stated endpoint of "CD-TLR or TLF" permits a 2–3× choice at every
row. The original set in fact spanned five constructs — CD-TLR, TLF composites,
all-cause TLR, symptom-driven TLR and vessel-level TVF — and three time windows (312,
365 and 390 days). That sentence has been deleted from this paper rather than
repaired.

**The survival pattern was the opposite of what we expected.** On either criterion the
direction is the same: coronary was the worst-sourced bed in the set and femoropopliteal
the best — 1 of 7 against 3 of 4 on citation integrity, 0 of 7 against 2 of 4 on value
support. Roughly 74% of the original calibration weight rested on values the sources do
not report, concentrated in the bed the author knows best.

### 3.3 What we did about it

Every anchor now declares seven provenance fields — endpoint construct, trigger
(clinical vs protocol surveillance vs routine angiography), adjudication (independent
committee, core laboratory, or none stated), estimator, analysis unit (patient,
lesion or vessel), actual time window in days, and design. One construct is
preferred, 12-month clinically driven TLR; anchors reporting all-cause or
symptom-driven TLR are labelled and down-weighted rather than silently pooled. Four
anchors were excluded from the fit and are kept in the table so that what was dropped
stays visible: COR-undersized (vessel-level TVF, and stent under-*expansion* against
an absolute area cut-off is not under-*sizing*), SFA-long-bare (surveillance-triggered
all-cause TLR, single-arm), COR-DES-complex and COR-DCB-small (TLF composites,
secondary or post hoc). Trust weight now encodes audited evidence quality rather than
author confidence. **Five of the six beds' λ₀ values were revised downward; the
femoropopliteal baseline was unchanged**, because its reference arm is the one that
survived the audit — the asymmetry matters, and averaging it away would hide it.

### 3.4 What we take from it

The audit is, we think, the most transferable part of this paper. Device-outcome
numbers are quoted across the interventional literature without their endpoint
construct attached, and once detached they are freely substitutable for each other by
a reader acting in good faith. The five substitutions above were each internally
reasonable. The defence is not more care; it is carrying the construct, trigger,
adjudication, unit and window next to every number, so that a mismatch is visible
rather than invisible. Any comparative model built on pooled device outcomes — not
only this one — should be expected to show the provenance fields, and should be
assumed to have this problem until it does.

## 4. Calibration

Eleven of the thirteen free constants were fitted to the 12 retained anchors
by least squares on log-odds, weighted by audited evidence quality. One shared
parameter set; no per-bed tuning.

**Mean absolute error 1.4 percentage points**, worst residual 4.3 points on
BTK-POBA (Figure 2).

What that number is not. Carotid, iliac and renal contribute exactly one anchor each,
which is also that bed's λ₀, so those three beds are fitted trivially and constrain
nothing about the operator's shape. Four of the retained anchors are two arms each of
two trials (IN.PACT SFA, IN.PACT DEEP), both Medtronic paclitaxel DCB randomised
trials sharing sites, adjudication committee and CD-TLR trigger definition, so their
errors are correlated and they are not four independent residuals. The fit is really
driven by about seven informative comparisons — against eleven free constants. **An MAE
of 1.4 points is therefore not evidence that the operator is right.** With more free
parameters than informative constraints, a low residual is what one should expect, and
we report it as a consistency check rather than as performance.

**Seven of the eleven fitted constants sit on their bounds**, which is the clearest
signal in the fit and points at the model rather than at the data. Two of the seven
matter more than the rest: the compliance-mismatch kernel and the overstretch-stress
kernel both collapse to their floors. In plain terms, **once the anchors are corrected,
the fit no longer needs the mechanical axis at all.** The retained anchors are explained
almost entirely by Γ_H (lumen restored, strut burden) and Γ_B (antiproliferative supply
against drive); the weakest axis is Γ_H for ten of the twelve anchors and Γ_B for the
other two, and Γ_M is never binding.

We take that seriously rather than tuning around it. Two readings are available and the
data here cannot separate them. Either the mechanical axis is not doing real work and
the operator should be three axes, or — the reading we find more likely and which the
falsification plan in §7 is designed to test — a 12-month revascularisation endpoint has
no power to identify it. Compliance mismatch, fatigue and resorption are all
slow-acting: fatigue accrues across the first year, a poly-L-lactide scaffold's
compliance converges on the wall's only over two to three years. An axis whose
predictions live in years 2 to 5 cannot be identified from year-one revascularisation,
and a fit that switches it off is behaving correctly given what it was shown. Either way,
the four-axis structure should not be presented as established by this calibration.

Within a bed, the device-versus-balloon contrast is same-trial and self-consistent.
Across beds it is not: coronary POBA is 1991–93, symptom-driven, without routine
surveillance, while femoropopliteal POBA is 2015 with committee-adjudicated CD-TLR.
Any bed gradient the model learns carries 22 years of era effect and a change of
endpoint definition inside it. We report this rather than adjusting for it, because
we do not know how to adjust for it honestly.

## 5. In-silico evaluation

### 5.1 What this section can and cannot show

Outcomes here are generated by the same operator that one of the candidate
representations consumes. No experiment in this section can show that Γ_sc is true of
patients. It can show a property of the *representation*: whether a
physics-parameterised summary behaves differently from raw features when both are
given the same information, seen through realistic measurement error, with an
unobserved patient-level frailty term neither can access.

### 5.2 Design

9,000 procedures were sampled across six beds with deliberately varied plans spanning
good and bad matches. True 12-month risk was computed, scaled by a log-normal frailty
multiplier (σ = 0.55) appearing in no feature set, and an event drawn. Features were
then *re-measured*: diameters with 0.16–0.35 mm of Gaussian error, length with 12%
proportional error, calcium and tortuosity coarsened to the grades actually recorded
in practice. Candidates saw only the re-measured lesion, so the operator arm had to
recompute Γ_sc from noisy inputs.

Four representations of the same information: (A) 44 raw lesion and device features
with bed as a one-hot category, gradient-boosted trees; (A′) the same with bed as six
continuous physiological parameters, trees; (A″) the same continuous features under a
linear model, which can extrapolate along them; and (B) the four numbers the operator
produces — year-one mean Γ_sc, mismatch dose, τ_sc and log λ₀ — under a linear model.

### 5.3 Results

**Sample efficiency (Figure 3a).** Within the coronary bed the operator's four numbers
reached AUC 0.790 at n = 100 and were flat thereafter
(0.797 at n = 800). Raw features under a linear model were at
0.596 at n = 100 and had still not caught up at n = 800
(0.778); under trees they were lower and unstable
(0.600 at n = 100, 0.699 at n = 800).
For single-centre cohorts, where the number of procedures is the binding constraint,
this is the operator's only demonstrated practical advantage — and it is the one that
survived the recalibration, in a sharper form.

**Cross-bed transfer: the claim failed, and after the refit it failed clearly
(Figure 3b).** Training on coronary and carotid and testing on femoropopliteal,
below-the-knee, renal and iliac, the operator reached AUC 0.610
against 0.635 for raw features plus continuous bed physiology
under a linear model — a difference of **-0.024 (95% bootstrap -0.041 to
-0.010)**. On the uncorrected anchor set this difference was −0.014 with a confidence
interval spanning zero; on the corrected one **the interval excludes zero and the
operator is worse.** The apparent advantage over tree models
(0.571) was never the operator: it was that a linear model
extrapolates along a continuous bed parameter and a tree, which can only interpolate
between values it has seen, cannot. Representations (A) and (A′) were numerically
identical, for the same reason.

**The risk scale does not transfer, and an offset does not fix it.** The operator's raw
cross-bed Brier score was 0.249, far worse than predicting the test
beds' base rate (0.135). Two different corrections get called "recalibration" and they
are not interchangeable, so we report both. Shifting the intercept only — keeping the
model's log-odds slope — leaves every arm *worse* than the base rate: 0.151
for the operator, 0.149 for raw features plus bed physiology,
0.163 for trees. What actually repairs them is refitting the
slope as well (0.132, 0.131,
0.133), and the slope the operator needs is
0.26 — its log-odds are roughly four times too steep across
beds. Both of these use the test labels and are therefore ceilings, not out-of-sample
scores.

The distinction matters for anyone who wants to use the operator in a new bed. Its
*ordering* carries (AUC 0.610, poor but above chance); its *risk scale*
does not, and it is over-dispersed rather than merely offset. A new bed needs a slope as
well as a level, which is a two-parameter recalibration on real events, not a constant
anyone can look up.

## 6. A harness that improves without retraining the operator

Device selection needs a policy deciding how the operator is used — the sizing rule,
when to prepare calcium, when to demand an antiproliferative device. Following the
separation used in recent interactive scientific agents [3], we hold that policy as
data rather than code, score candidate plans against a fixed rubric composer, and
improve the policy with the operator's constants frozen. Across 60 development tasks
with 120 held out, the held-out rubric score rose from 0.749 to 0.948 with no
change to the operator; two edits accounted for almost all of it. One negative finding is
worth recording: a diagnoser restricted to *atomic* edits stalls immediately, because
enabling a skill whose threshold still excludes every case and moving a threshold for
a skill that is off are both no-ops. Edits have to be compound to be testable.

## 7. Preregistered falsification plan

Stated before any patient data are analysed:

1. **The operator must beat a raw-feature floor.** Refit by maximum likelihood on a
   real cohort, it must exceed a logistic model on the same raw features in
   out-of-fold AUC. If it does not, it adds nothing and we will say so.
2. **τ_sc must carry information Γ_sc(0) does not.** Adding τ_sc to a model containing
   Γ_sc(0) must improve out-of-fold discrimination.
3. **The resorption term makes a dated prediction.** Γ_M for a poly-L-lactide scaffold
   converges on the wall's compliance with the degradation constant, so any advantage
   attributable to that axis must appear only after roughly twice the degradation time
   constant — years 2 to 5, not year 1. An advantage appearing in year 1, or none by
   year 5, falsifies the term.
4. **Sample efficiency must replicate** in real data at n ≈ 100–200 procedures, or the
   §5.3 result is an artefact of the simulator.
5. **The cross-bed null must be retested, not quietly dropped**, against continuous bed
   physiology under a model class that can extrapolate.
6. **The endpoint must be fixed in advance** — one construct, one trigger, one
   adjudication standard, one analysis unit, one window — and any anchor that cannot
   supply it must be excluded rather than converted.

## 8. Limitations

- **No patient-level data.** Nothing here has seen a patient.
- **The calibration rests on about seven informative comparisons**, three beds are
  fitted trivially, and four anchors are two arms of two trials.
- **Three revascularisation constructs remain mixed** in the retained set (CD-TLR,
  all-cause TLR, symptom-driven TLR). They are labelled and weighted, not unified.
  Symptom-driven TLR without routine angiography biases low; surveillance-triggered
  TLR biases high; these are opposite biases and cannot be interchanged.
- **No cost, complication, procedure-time or contrast term.** The operator will
  therefore recommend maximal lesion preparation almost every time. That is a gap in
  the model and must not be read as a procedural recommendation.
- **Device entries are representative class parameters**, not commercial
  specifications; radial force, device compliance and fatigue resistance are
  order-of-magnitude estimates.
- **Bed parameters are declared priors, not measurements.**
- **Seven of eleven constants are on their bounds, and the mechanical axis is switched
  off by the fit.** The four-axis structure is not established by this calibration.
- **Correlated penalties compound.** A badly oversized device is charged on both the
  geometric and mechanical axes; intentional, but the axes are not independent.
- **The carotid anchor is 0.6%**, indistinguishable from zero on a CD-TLR scale. That
  bed's informative endpoint is duplex restenosis, which is not in the retained
  construct, so the carotid bed may simply not be calibratable here.
- **Not a clinical decision tool** and must not be used as one.

## 9. Data and code availability

The implementation, the anchor set with every provenance field and the full audit
record, the fitted constants, and the scripts that reproduce every number and figure
are released with the paper. An interactive workbench running the operator entirely in
the browser is at https://lingsenyou.com/suitcordance/.

> **BEFORE POSTING:** deposit the code and replace this with the Zenodo concept DOI.

## 10. Declarations

**Funding.** This work was supported by the National Natural Science Foundation of China (T2288101, 82170342), the AI for Science Foundation of Fudan University (FudanX24AI003), and the Medical Engineering Joint Fund of Fudan University (yg2023-01).
**Competing interests.** L.Y. and L.S. serve as Executive Secretaries of the National
Basic Science Center for Panvascular Interventional Complex Systems, and J.G. serves as
its Director. The framework this paper operationalises is that centre's research
programme [1], and the work was supported by that centre's award (T2288101). The authors
declare no other competing interests, and no consulting income, speaking fees, equity,
patents or family interests involving any manufacturer of the device classes evaluated
here.
**Ethics.** No human subjects or patient data were involved.
**Author contributions.** L.Y. conceived the operator, wrote the code, performed the
citation audit, the calibration and the in-silico experiments, and wrote the manuscript.
L.S. and J.G. supervised the work and revised the manuscript.

---

## References

> Primary citations for every retained and excluded anchor are carried in Table 1 with
> their DOIs, all verified against the source during the audit in §3. The list below is
> the non-anchor references.

1. You L, Shen L, Ge J. The foundation and development of China's National Basic
   Science Center for panvascular interventional complex systems: pioneering
   device–vessel suitcordance research. *Eur Heart J*. 2025;46(35):3400–3403.
   doi:10.1093/eurheartj/ehaf418

2. You L, et al. Vascular–device suitcordance: a tri-ecological framework for
   eco-rebalancing. *Trends Mol Med*. In press (accepted 14 September 2026).
   *[DOI to be added once assigned — do not post without it.]*

3. Xue S, Zhong J, Nan Z, et al. ScienceBuddy: recursive-in-recursive self-improvement
   for interactive scientific agents. *arXiv*:2609.17523. 2026.

---

## Figure and table legends

**Figure 1. The operator, on one coronary lesion.** A 3.05 mm reference vessel, 22 mm
lesion, moderate calcium, diabetes. **(a)** The four agreement axes and their weighted
geometric mean for an ultrathin drug-eluting stent; the dashed line marks τ_sc.
**(b)** Γ_sc for four strategies in the same lesion, each labelled with its own τ_sc.

**Figure 2. Calibration against the audited anchor set.** One shared parameter set
across six arterial beds. Filled markers are the anchors in the fit, area proportional
to audited trust weight; hollow markers are the four excluded anchors, plotted at the
corrected value. Solid line identity, dashed lines 1.5-fold.

**Figure 3. In-silico evaluation.** **(a)** Sample efficiency within the coronary bed,
held-out n = 400. **(b)** Cross-bed transfer, training on coronary and carotid, testing
on four held-out beds. The operator does not beat raw features plus continuous bed
physiology under a model class that can extrapolate.

**Table 1. The anchor set, with provenance.** Every anchor with its bed, device class,
value, audited trust weight, endpoint construct, trigger, adjudication, estimator,
analysis unit, actual time window and design, the primary citation with DOI, and a note
recording what the first version of the anchor asserted and why it changed. Excluded
anchors are marked.
