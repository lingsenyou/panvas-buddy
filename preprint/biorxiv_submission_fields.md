# bioRxiv submission — every field, pre-filled

Open <https://submit.biorxiv.org>, sign in as yourself, and work down this page. Each
heading is a field on the submission form; paste the block under it. Nothing here needs
composing, only checking.

One item is still blank: your own institutional email address. Everything else is
filled in or checked.

---

## 1. Manuscript file

Upload `preprint/Suitcordance_preprint.docx`. bioRxiv accepts Word directly and
converts it; no PDF is needed. Figures are embedded in the file, and Table 1 is the last
page. Do not upload supplementary files for this version.

## 2. Title

```
Suitcordance: a calibrated, time-resolved operator for device–vessel matching across the arterial tree, and an audit of the literature values it was calibrated against
```

## 3. Abstract

Paste the contents of `preprint/abstract_plaintext.txt` (502 words, 3,210 characters,
already stripped of markdown). bioRxiv's box accepts it at this length.

## 4. Authors, in order

| # | Name | Affiliations | ORCID | Email | Role |
|---|---|---|---|---|---|
| 1 | Lingsen You | 1,2,3,4,5 | 0000-0003-0794-5907 | **[YOU]** — use your Fudan address, not a personal one | first author |
| 2 | Li Shen | 1,2,3,4,5 | none | shen_li@fudan.edu.cn | **corresponding** |
| 3 | Junbo Ge | 1,2,3,4,5 | 0000-0002-9360-7332 | jbge@zs-hospital.sh.cn | **corresponding** |

Affiliations, exactly as they appear on *Eur Heart J* 2025;46(35):3400–3403:

```
1  Department of Cardiology, Zhongshan Hospital, Fudan University, Shanghai Institute of Cardiovascular Diseases, No. 180 Fenglin Road, Xuhui District, Shanghai 200032, China
2  National Clinical Research Center for Interventional Medicine, No. 180 Fenglin Road, Xuhui District, Shanghai 200032, China
3  Oriental Pan-Vascular Devices Innovation College, University of Shanghai for Science and Technology (USST), No. 516 Jungong Road, Yangpu District, Shanghai 200093, China
4  State Key Laboratory of Cardiovascular Diseases, Zhongshan Hospital, Fudan University, No. 1609 Xietu Road, Xuhui District, Shanghai 200032, China
5  NHC Key Laboratory of Ischemic Heart Diseases, No. 1609 Xietu Road, Xuhui District, Shanghai 200032, China
```

**A note on the email.** bioRxiv emails every listed author to tell them they have been
named on a preprint. Use institutional addresses, and expect Prof. Shen and Prof. Ge to
receive that message within minutes of you pressing submit — which is a good reason for
them to have read the paper first.

**Corresponding authors: Prof. Ge and Prof. Shen**, both of them, as on the EHJ paper.

The two ORCID iDs are taken from the Europe PMC record of your own EHJ paper — the iDs
the three of you supplied at submission — and each was then checked against its public
ORCID record: 0000-0002-9360-7332 resolves to Junbo Ge, Zhongshan Hospital Fudan University, Director
and Professor of Cardiology and Academician of the Chinese Academy of Sciences;
0000-0003-0794-5907 resolves to Lingsen You and lists the EHJ paper. Prof. Shen has no ORCID, which is
fine — the field is optional.

Worth ten minutes separately: your own ORCID record lists **no employment or affiliation
at all** and only six works, missing Light Science & Applications, Science Bulletin,
Research, Biomarker Research, npj Flexible Electronics and Advanced Fiber Materials.
That record is what a reader lands on from the preprint.

## 5. Category

```
Bioengineering
```

This fits **only because there is no patient data in this version**. When the XINSORB
five-year cohort or the multicentre 3D reconstruction cohort goes in, the paper becomes
a study of human subjects and must go to medRxiv instead, with ethics and
data-availability statements. Do not post a patient-data version here.

## 6. Licence

Recommended: **CC BY 4.0**. It is what most journals accept downstream and what funders
increasingly require. If you would rather restrict commercial reuse — a reasonable
instinct for a device-selection model — CC BY-NC-ND is the conservative alternative.
Note that since January 2026 you can loosen a licence later without posting a new
version, but you cannot tighten one, so starting at CC BY and relaxing is not available
in reverse: choose deliberately.

## 7. Competing interests — not "none"; use your own published wording

```
L.Y. and L.S. serve as Executive Secretaries of the National Basic Science Center for Panvascular Interventional Complex Systems, and J.G. serves as its Director. The framework this paper operationalises is that centre's research programme, and the work was supported by that centre's award (T2288101). The authors declare no other competing interests, and no consulting income, speaking fees, equity, patents or family interests involving any manufacturer of the device classes evaluated here.
```

You said there is no competing interest, and financially that is what I have recorded:
no consulting income, speaking fees, equity, patents or family interests involving any
device manufacturer. But **you three already published a disclosure five months ago**, in
what is reference 1 of this very paper. *Eur Heart J* 2025;46(35):3400–3403 states,
verbatim:

> "The authors declare the following relationships: L.Y. and L.S. serve as Executive
> Secretaries of the National Basic Science Center for Panvascular Interventional
> Complex Systems, while Junbo Ge serves as Director of the same center. No other
> competing interests exist."

This paper says in §1 that it operationalises that centre's research programme, lists
that centre's NSFC award (T2288101) as its funding, and ranks commercial device classes.
A reader who clicks reference 1 sees the disclosure in thirty seconds. Institutional
office is a declarable non-financial interest under ICMJE, and the text above is simply
your own EHJ sentence carried across — which is also what "same as EHJ" means. It still
ends in "no other competing interests".

**One thing to ask Prof. Shen and Prof. Ge rather than decide:** the device catalogue
contains an entry named "PLLA BRS, 150 um (XINSORB-class)", and the repository names the
XINSORB five-year cohort as the dataset that would test the resorption term. If either
of them has a role in that scaffold's development or trials, it belongs in this
statement. Ask; do not assume.

## 8. Funding — carried from the EHJ paper, **confirm which apply here**

```
This work was supported by the National Natural Science Foundation of China (T2288101, 82170342), the AI for Science Foundation of Fudan University (FudanX24AI003), and the Medical Engineering Joint Fund of Fudan University (yg2023-01).
```

These are the four grants indexed against *Eur Heart J* 2025;46(35):3400–3403
(T2288101 is the NSFC Basic Science Center award; the others are the group's project
and Fudan medical-engineering funds). I have carried them across because this work sits
in the same programme, but a funding statement should list what funded **this** work,
not everything the group holds. Strike any that do not apply.

## 9. Data and code availability

Paste, once the Zenodo DOI exists:

```
The operator, the full anchor set with provenance, the raw citation-audit record, the fitted constants and the scripts that reproduce every number and figure are openly available at https://doi.org/10.5281/zenodo.XXXXXXX. An interactive workbench running the operator in the browser is at https://lingsenyou.com/suitcordance/.
```

**Do not submit before this DOI exists.** §9 of the manuscript promises availability, and
a preprint that promises code without a resolvable link gets flagged in screening.
`PUBLISHING.md` steps 1 and 2 take about fifteen minutes.

## 10. Subject terms / keywords

```
pan-vascular intervention; device–vessel matching; endpoint definition; calibration; evidence audit; bioresorbable scaffold; drug-coated balloon
```

---

## Before you press submit

- [ ] **All three authors have read this version.** bioRxiv makes you affirm it. The
      paper reports that thirteen of our own sixteen first anchors did not hold up, that
      the cross-bed transfer claim is refuted, and that the fit switches off the
      mechanical axis. Prof. Shen and Prof. Ge should see those three sentences
      themselves rather than a summary of them.
- [ ] Zenodo DOI pasted into §9 of the manuscript and into field 9 above.
- [ ] Every red block deleted from the Word file (the author-block note at the top, the
      one in §9, and the reference-list note).
- [ ] Reference 2 (Trends in Molecular Medicine) has its DOI, or is removed.
- [ ] Competing interests: use the EHJ disclosure above, not "none" — and ask about XINSORB.
- [ ] Funding: four grants carried from the EHJ paper — confirm each applies to this work.
- [x] Corresponding authors, emails and ORCIDs filled in.

## What I could not do

I cannot post this for you. Submission requires signing in to your bioRxiv account, and
I do not enter anyone's credentials. Separately, the form asks the submitting author to
affirm that every listed author has approved this version — that is a statement about
Prof. Shen and Prof. Ge, and it is yours to make once they have actually approved, not
mine to make on your behalf. Posting is also effectively permanent: a withdrawal leaves
a public record rather than removing the preprint.

Everything up to the login is done. If you want, open the submission page and I will
walk the form with you field by field while you type.
