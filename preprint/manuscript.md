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

‡ Corresponding authors. Email: jbge@zs-hospital.sh.cn (J.G.); shen_li@fudan.edu.cn (L.S.).

ORCID: L.Y. 0000-0003-0794-5907; J.G. 0000-0002-9360-7332.



---

## Abstract

Device selection in endovascular intervention is governed by bed-specific rules of
thumb that are not commensurable across arterial beds and carry no explicit time
course. We formalise device–vessel failure as a property of the *agreement*
between device and vessel rather than of either alone, and define a suitcordance
operator Γ_sc on four axes: geometric, mechanical, hemodynamic and biological. The
axes combine as a bed-weighted geometric mean, so that a collapse on any one axis drags
the composite down instead of being averaged away by the other three. Every axis is a function of time, which
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
and not as performance, because eleven constants against six informative
comparisons is under-determined, and because six of the twelve anchors are their own
bed's reference case and reproduce its baseline rate by construction: on the six
genuinely informative anchors the error is 2.3 points. Seven of the eleven constants land
on their bounds, and **removing the mechanical axis entirely improves the fit** (1.37 to
1.32 points), so that axis is not merely unused but currently harmful. Whether it is
empty, wrongly specified, or simply invisible to a 12-month revascularisation endpoint is
not decidable here; §7 states the test. In a 9,000-procedure simulation
with an unobserved frailty term and realistic measurement error, the operator's
four-number summary reached AUC 0.790 at n = 100, a level 44 raw
features had not reached by n = 800. The pan-vascular transfer claim did not survive
its own test either way: against a linear model given the same continuous bed
physiology, the operator's cross-bed difference was −0.024 AUC at the first seed we
ran, but the sign flips across simulation seeds (−0.024 to +0.037), and a bootstrap over
the four held-out beds — the actual unit of the claim — covers zero at every seed. With
four beds the design has no power to decide, which is itself the finding.
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

The framework this paper operationalises is our group's own. Device–vessel suitcordance
was named as the object of study of China's National Basic Science Center for
panvascular interventional complex systems [1], developed as a tri-ecological balance
[2], extended to full-watershed organs [3], given an experimental platform in a
panvascular-on-a-chip system [4], and connected to intravascular imaging and digital
twins [5]. What none of those papers does — and what we had not done — is **compute** it:
Γ_sc has been specified verbally, without a numerical value, a time course, fitted
constants, or anything that could be checked against an outcome. This paper is the first
executable implementation, and it reports what happened when we tried.

Related mechanistic work exists and is in some respects ahead of this one. Multiscale
models of in-stent restenosis couple haemodynamics to agent-based tissue growth and
predict at this same 12-month horizon, and the femoropopliteal ones have been calibrated
against per-patient lumen area at one month and one year — patient-level validation this
operator does not have. What is different here is scope rather than depth: one operator
applied across six arterial beds from a single parameter set, with a device-selection
layer on top, and with its calibration evidence published field by field.

This paper does four things. It defines an operator that computes the agreement
between a device and a vessel on four axes, as a function of time, in any of six
arterial beds from one parameter set (§2). It reports an adversarial audit of the
literature values such an operator has to be calibrated against, which found most of
our own first attempt to be wrong (§3) — a result we believe generalises well beyond
this model. It fits the operator to the corrected values (§4) and tests, in
simulation, the claim that motivated the construction, reporting that the design turns
out to have no power to decide it (§5). And it states what would falsify the operator on real data before
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
[1] and subsequently developed [2, 3]. The mapping is not one to one, and the difference is deliberate: the geometric
and hemodynamic axes separate two things the mechanical balance conflated, namely
whether the device fits the vessel and whether the lumen it leaves carries flow. §4
reports that the corrected calibration does not currently need the mechanical axis,
which is a result about this operator and this endpoint, not about the balances.

### 2.2 Composition

    Γ_sc(x, a, t) = Π_i Γ_i(x, a, t)^{w_i(bed)},   Σ_i w_i = 1

The geometric mean is the modelling commitment, not a convenience — but it has to be
stated precisely, because the strong version of the claim is false. A weighted geometric
mean is still compensatory: with exponents between 0.16 and 0.36, a collapse on one axis
is attenuated by a root rather than preserved. BTK-POBA has Γ_H = 5.1 × 10⁻⁴ and
Γ_sc = 0.056, so a two-thousand-fold collapse on one axis becomes an eighteen-fold
reduction in the composite. What can honestly be claimed is that the product is *less*
compensatory than a weighted sum — a bad axis drags the composite down instead of being
averaged away — and that is the property we want. Genuine non-compensation would need a
minimum, or a CES aggregator with ρ → −∞. Weights are bed-specific and declared: the mechanical
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
**The audit was run by large language model agents, not by people**, and that has to be
stated plainly because it changes how much weight the result can carry. Forty-nine agents
(Claude Opus 5, with web search and page-fetch tools) performed 696 source lookups; each
was instructed to open the primary source, forbidden from inventing an identifier, and
required to quote the sentence or name the table carrying the number. The original
sixteen anchors were themselves assembled with the same class of assistance. So the
honest statement of what happened is that an LLM-assisted workflow produced sixteen
values, a second, adversarial LLM-assisted workflow found fourteen of them wrong, and
**the corrected values have not yet been confirmed by a human opening the papers.** Until
that human pass exists, the corrected set is better documented than the first one but
not, on its own authority, better grounded. Doing that pass — twelve papers, an hour —
is the single highest-value thing anyone could do to this manuscript, and it is listed in
§7 as such.

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

**Mean absolute error 1.4 percentage points** over the twelve retained anchors, worst
residual 4.3 points on BTK-POBA (Figure 2). **Half of that figure is an identity.** Six
of the twelve anchors — COR-DES-modern, SFA-DCB, BTK-DCB, CAR-stent, ILIAC-stent and
RENAL-stent — *are* their bed's reference case, the case used to compute Γ*(bed), so for
them λ(t) = λ₀·exp(β(Γ*−Γ_sc(t))) returns λ₀ up to a small Jensen gap whatever the eleven
constants are. Their mean residual is 0.4 points. On the six anchors that are genuinely
informative — COR-BRS-plla, COR-BMS, COR-POBA, SFA-POBA, SFA-nitinol, BTK-POBA — the mean
absolute error is **2.3 percentage points**, and that is the number a reader should hold
us to.

What that number is not. Six of the twelve anchors are their bed's reference case, as
above. Carotid, iliac and renal contribute exactly one anchor each, which is also that
bed's λ₀, so those three beds are fitted trivially and constrain nothing about the
operator's shape. Four of the retained anchors are two arms each of
two trials (IN.PACT SFA, IN.PACT DEEP), both Medtronic paclitaxel DCB randomised
trials sharing sites, adjudication committee and CD-TLR trigger definition, so their
errors are correlated and they are not four independent residuals. The fit is really
driven by six informative comparisons — against eleven free constants. **An MAE
of 1.4 points is therefore not evidence that the operator is right.** With more free
parameters than informative constraints, a low residual is what one should expect, and
we report it as a consistency check rather than as performance.

**Seven of the eleven fitted constants sit on their bounds**, which is the clearest
signal in the fit and points at the model rather than at the data. Γ_M is built from
three kernels and all three are degenerate: the compliance-mismatch and overstretch
kernels collapse to their floors, and the cyclic-fatigue kernel is pinned at its
*ceiling* (11.999 against a bound of 12.0). We report the ceiling as well as the floors,
because omitting it would be exactly the selective reading of a bounds table that this
paper otherwise argues against.

We then did the obvious test and it went against us. **Setting Γ_M ≡ 1 for every anchor
improves the fit**: mean absolute error falls from 1.37 to 1.32 points, and the residual
on SFA-nitinol — the one anchor the fatigue term exists to explain — falls from 1.39 to
0.54 points. The saturated fatigue term is pushing its own anchor the wrong way. The
mechanical axis is therefore not merely never binding; on this endpoint it is actively
harmful.

Three readings are available and these data cannot separate them. The axis may be empty.
Its functional forms may be wrong, which the pinned bounds independently suggest. Or — the
reading we find most likely, and which §7 is designed to test — a 12-month
revascularisation endpoint simply cannot see it: compliance convergence, fatigue accrual
and resorption are slow, a poly-L-lactide scaffold's compliance approaches the wall's
only over two to three years, and an axis whose predictions live in years 2 to 5 cannot
be identified from year-one revascularisation. What is not available is presenting the
four-axis structure as established by this calibration. It is not.

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

**Cross-bed transfer: the experiment cannot answer the question (Figure 3b).** Training on coronary and carotid and testing on femoropopliteal, below-the-knee, renal
and iliac, the operator reached AUC 0.610 against 0.635 for raw features plus continuous
bed physiology under a linear model — a difference of −0.024, with a case-level bootstrap
interval of (−0.041, −0.010) that excludes zero.

**That result does not survive its own robustness check, and we report the check rather
than the result.** Repeating the whole experiment at five simulation seeds gives
differences of −0.024, +0.024, +0.037, +0.003 and −0.005: the sign flips, the mean is
+0.007, and the case-level interval excludes zero in three of the five seeds — in both
directions. The case-level bootstrap is also resampling the wrong unit. The claim is
about four arterial beds; resampling 6,041 individual procedures treats them as 6,041
independent observations of bed-to-bed transfer, which they are not. Resampling the four
**beds** instead gives intervals that cover zero at every seed, including the seed that
produced the headline number: (−0.036, +0.035).

Within the seed we first ran, three of the four held-out beds in fact favour the operator
(below-the-knee 0.576 against 0.549, renal 0.676 against 0.644, femoropopliteal 0.692
against 0.646); only the iliac bed goes the other way (0.704 against 0.730), and the
pooled figure reverses because pooling across beds with different event rates is not the
same as averaging discrimination within them.

The honest conclusion is therefore neither that the operator transfers nor that it fails
to: **with four held-out beds this design has no power to decide**, and a study that
wanted to decide it would need many more beds, or many centres within beds, and would
have to treat the bed as the unit of analysis. The apparent advantage over tree models
(0.571) is a separate and more robust point: a linear model extrapolates along a
continuous bed parameter and a tree, which can only interpolate between values it has
seen, cannot. Representations (A) and (A′) were numerically identical, for that reason.

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

## 6. A harness that recovers the operator's own preferences

Device selection needs a policy deciding how the operator is used — the sizing rule,
when to prepare calcium, when to demand an antiproliferative device. Following the
separation used in recent interactive scientific agents [6], we hold that policy as
data rather than code, score candidate plans against a fixed rubric composer, and
improve the policy with the operator's constants frozen. Across 60 development tasks with
120 held out, the held-out rubric score rose from 0.749 to 0.948 with no change to the
operator.

**This is an internal-consistency result and must not be read as evidence that the policy
got clinically better.** The rubric's heaviest criterion is the operator's own optimum,
its second-heaviest is Γ_G at deployment, and the single edit producing almost the whole
gain is "consult the operator before choosing". A policy instructed to optimise the
operator scores better against a rubric the operator computes. What the loop demonstrates
is that harness search recovers the operator's preference ordering without touching its
constants, and that the machinery works. Demonstrating that it *helps* requires at least
one criterion the operator does not compute — guideline concordance, or an
interventionalist's judgement on a sample of plans — scored separately. One negative finding is
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
6. **The model's intermediate quantities must match published imaging.** Late lumen loss
   and percent diameter stenosis at follow-up are reported by the anchor trials and are
   free to check. The current fit implies neointimal thicknesses up to 2.4 mm and fails
   this immediately; any version that is to be taken seriously must pass it before its
   endpoint agreement means anything.
7. **A human must open the twelve retained primary sources** and record, for each, the
   page or table and the verbatim sentence carrying the number. Until then the corrected
   anchor set is better documented than the first one, not better grounded.
8. **The endpoint must be fixed in advance** — one construct, one trigger, one
   adjudication standard, one analysis unit, one window — and any anchor that cannot
   supply it must be excluded rather than converted.

## 8. Limitations

- **No patient-level data.** Nothing here has seen a patient.
- **The calibration rests on six informative comparisons**, three beds are
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
- **Seven of eleven constants are on their bounds, and removing the mechanical axis
  improves the fit.** The four-axis structure is not established by this calibration.
- **Half the headline calibration error is an identity.** Six of the twelve anchors are
  their own bed's reference case; on the six informative ones the error is 2.3 points.
- **The model's intermediate quantities are not physiological.** The fitted neointimal
  asymptote implies per-side thicknesses of 0.4 to 2.4 mm — up to 2,358 µm in a 2.75 mm
  below-the-knee vessel, against published in-stent late lumen loss of order 0.1 mm — and
  Γ_H spends much of year one at its numerical floor in the balloon anchors. The operator
  reproduces the endpoint while getting the path to it wrong, which is the failure a
  12-month endpoint cannot detect and an imaging endpoint would.
- **The audit was performed by language-model agents and has not been checked by a human
  opening the papers.**
- **Correlated penalties compound.** A badly oversized device is charged on both the
  geometric and mechanical axes; intentional, but the axes are not independent.
- **The carotid anchor is 0.6%**, indistinguishable from zero on a CD-TLR scale. That
  bed's informative endpoint is duplex restenosis, which is not in the retained
  construct, so the carotid bed may simply not be calibratable here.
- **The below-the-knee baseline is a withdrawn device from a negative trial.** λ₀(btk)
  and that bed's reference case are IN.PACT DEEP's drug-eluting balloon arm: the trial
  missed its primary endpoints (CD-TLR 9.2% against 13.1% for plain angioplasty), carried
  a major-amputation signal (8.8% against 3.6%), and IN.PACT Amphirion was withdrawn
  worldwide in 2013. It is used because it is the best-adjudicated 12-month CD-TLR in
  that bed, not because it is good care, and Γ*(btk) = 0.21 against 0.47–0.74 elsewhere
  is a property of that anchor rather than of the bed. Four of the twelve retained
  anchors are paclitaxel-balloon arms from two trials by one manufacturer.
- **The mechanical axis cannot penalise a balloon.** Γ_M is exactly 1 for every
  balloon anchor at every timepoint, because overstretch strain is computed after recoil
  and recoil always puts the balloon below the reference diameter. There is no
  dissection, bailout-stenting or perforation term. In the femoropopliteal bed this hands
  36% of the weight to a drug-coated balloon at a perfect score before any physiology is
  evaluated, and the device setting Γ*(sfa) is itself a balloon.
- **Stenosis severity is ignored.** `Lesion.stenosis` is never read by the operator: a
  40% and a 95% stenosis give bit-identical output. A 1:1 balloon therefore delivers an
  injury index of exactly zero, which deletes the mechanism of post-angioplasty
  restenosis.
- **The model reproduces the endpoint through a physically wrong path.** See §8.1.
- **Not a clinical decision tool** and must not be used as one.

### 8.1 The neointima is not physiological, and it matters

The fitted neointimal constant implies 12-month per-side thicknesses of 0.5 to 2.2 mm —
528 µm for the contemporary drug-eluting stent anchor whose observed CD-TLR is 2.0%,
2,245 µm in a 2.75 mm below-the-knee vessel — against measured values of order 100 µm by
optical coherence tomography for a contemporary stent. The coronary DES anchor is
modelled as ending year one at 52% diameter stenosis in a population that revascularised
2% of lesions, and three anchors reach the lumen floor and are effectively modelled as
occluded. **Γ_H sits at or near its numerical clip for nine of the twelve anchors at 365
days**, so for most anchors τ_sc and the mismatch dose are reporting where a clip was
hit rather than device–vessel physics.

We report this rather than refitting around it, because it is the clearest available
illustration of the paper's own argument. A model can match an endpoint through a path
that is wrong, and a 12-month revascularisation endpoint cannot detect that; late lumen
loss and follow-up percent diameter stenosis are published by these same trials and
falsify it in one line. That is why it is now falsification item 6, and why nothing in
this paper should be read as evidence that the operator's internals are right. A refit
under a physiological bound is the obvious next step, and if the anchors cannot be
reproduced under one, **that is the result**.

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
**Use of AI.** The operator, the calibration and the in-silico experiments were
implemented with the assistance of a large language model (Claude Opus 5), which also
performed the citation audit of §3 and drafted portions of this manuscript. The authors
directed the work, chose the modelling commitments, and take responsibility for the
content. The audit's raw agent-by-agent record is released with the code so that its
provenance can be inspected rather than taken on trust.
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
   *[DOI to be added before posting.]*

3. You L, Chen Y, Zhang Z, Wang Y, Shen L, Ge J. High suitcordance for panvascular
   full-watershed organs: a new interventional perspective. *Research (Wash D C)*.
   2025. doi:10.34133/research.0974

4. You L, Chen Y, Zhang Z, Wang Y, Gu Z, Shen L, Ge J. The FLOW framework: a
   panvascular-on-a-chip platform to model systemic disease and guide panvascular
   interventional device suitcordance. *Sci Bull*. 2026.
   doi:10.1016/j.scib.2025.12.051

5. You L, Yao J, Qiu Y, Wang Y, Sun Y, Zhang R, Shen L, Ge J. From intravascular
   imaging to adaptive vascular care: intelligent photonics and digital twins in
   panvascular disease. *Light Sci Appl*. 2026. doi:10.1038/s41377-026-02410-6

6. Xue S, Zhong J, Nan Z, et al. ScienceBuddy: recursive-in-recursive self-improvement
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
