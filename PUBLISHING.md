# Publishing checklist

Everything here needs **your** account and **your** signature. None of it can be done
for you: creating accounts, entering credentials and agreeing to a server's terms on
someone else's behalf are yours alone, and a preprint cannot be un-posted once it is up
(bioRxiv marks a withdrawal; the record stays).

Work down the list in order. Step 3 depends on step 2, and step 2 depends on step 1.

---

## 0. Status, 19 September 2026

Settled:

- [x] **Author list.** You, Shen, Ge — the order of *Eur Heart J* 2025;46(35):3400–3403,
      with that paper's five affiliations carried across verbatim.
- [x] **Competing interests.** No financial interests, confirmed by the first author.
      The statement is **not** "none", though: the EHJ paper that is reference 1 here
      already discloses that L.Y. and L.S. are Executive Secretaries of the National
      Basic Science Center and J.G. its Director. That sentence is carried across, and
      still ends in "no other competing interests".
- [x] **Funding.** The four grants indexed against the EHJ paper: NSFC T2288101 and
      82170342, FudanX24AI003, yg2023-01. Confirm each applies to *this* work.
- [x] Li Shen: shen_li@fudan.edu.cn

Still open, and each of these needs a person, not a script:

- [ ] **Prof. Shen and Prof. Ge have read this version.** bioRxiv makes the submitting
      author affirm it, and the paper reports that thirteen of our own sixteen first
      anchors did not hold up, that the cross-bed transfer claim is refuted, and that
      the fit switches off the mechanical axis. Those are three sentences they should
      read themselves.
- [x] **ORCIDs.** L.Y. 0000-0003-0794-5907, J.G. 0000-0002-9360-7332, taken from the Europe PMC record of the EHJ
      paper and each verified against its public ORCID record. Prof. Shen has none.
- [x] **Prof. Ge's email:** jbge@zs-hospital.sh.cn
- [x] **Corresponding authors.** Prof. Ge and Prof. Shen, both, as on the EHJ paper.
- [x] **Emails.** L.Y. lingsenyou@fudan.edu.cn; L.S. shen_li@fudan.edu.cn; J.G. jbge@zs-hospital.sh.cn
- [ ] **Institutional policy.** Check whether Zhongshan Hospital / Fudan requires
      internal clearance before a preprint is posted. Some Chinese institutions do.

## 1. Publish the code (GitHub)

Full instructions with every Zenodo field pre-filled are in `ZENODO.md`; the short
version follows. `gh` is not installed on this machine, so the repository has to be
created in the browser.

1. Go to <https://github.com/new>. Owner `lingsenyou`, name `panvas-buddy`,
   **Public**, and do **not** initialise with a README, licence or .gitignore —
   the local repository already has them.
2. Then, from `Documents\claude_tmp\panvas_buddy`:

```bash
git remote add origin https://github.com/lingsenyou/panvas-buddy.git && git push -u origin main
```

   Credential Manager should already hold your token from the website pushes. If the
   push fails with a TLS `unexpected eof`, just retry — that happens on this connection.

3. Check the rendered README and that `LICENSE`, `CITATION.cff` and `.zenodo.json` are
   present at the repository root.

## 2. Mint a DOI (Zenodo)

1. Sign in at <https://zenodo.org> with GitHub.
2. Open **Account → GitHub**, find `lingsenyou/panvas-buddy`, and flip the switch **on**.
   Zenodo only archives releases created *after* the switch is on.
3. Back on GitHub: **Releases → Draft a new release**, tag `v0.1.0`, title
   `PanVas-Buddy v0.1.0`, publish it.
4. Zenodo picks the release up within a few minutes and mints two DOIs: a **concept
   DOI** that always points at the newest version, and a version DOI. **Cite the concept
   DOI in the paper.**
5. On the Zenodo record, before you publish it: add every co-author in the agreed order,
   add ORCIDs, and set the licence to MIT. `.zenodo.json` pre-fills most of this but the
   author list is deliberately left for you.

## 3. Post the preprint

**Server.** bioRxiv's *Bioengineering* category fits **only because there is no
patient data in this version**. The moment the XINSORB five-year cohort or the
multicentre 3D reconstruction cohort goes in, this becomes a study of human subjects and
must go to **medRxiv** instead, with an ethics statement and a data-availability
statement to match. Do not post a patient-data version to bioRxiv.

Before uploading:

- [ ] Replace the code-availability paragraph with the Zenodo **concept DOI**.
- [ ] Finish the reference list. Every anchor that names a trial needs its own primary
      citation; every anchor that is an expert estimate must be labelled as one in the
      text rather than given a citation that does not support it.
- [ ] Delete every red TODO block from the manuscript.
- [ ] Fill in funding, competing interests and author contributions.
- [ ] Re-read §7 Limitations and make sure nothing earlier in the paper contradicts it.

At upload: **Bioengineering**; choose a licence (CC-BY 4.0 is the usual choice and is
what most journals accept downstream); declare no conflict only if that is true; answer
"no" to the clinical-trial and patient-data questions for this version.

## 4. After posting

- [ ] Add the preprint DOI to the Zenodo record as a related identifier
      (`isSupplementTo`).
- [ ] Add the preprint to <https://lingsenyou.com/> — News and Publications, and link it
      from <https://lingsenyou.com/suitcordance/>.
- [ ] Put the preprint DOI in `CITATION.cff` under `preferred-citation`.

---

## What not to claim

The paper reports a calibration, a simulation, and a **null result on cross-bed
transfer**. It does not report a validated model. If you find yourself describing it as
"the pan-vascular AI model for device selection" in a talk, a grant or a tweet, that is
further than the evidence goes. What it does establish — and what a preprint is
genuinely good for — is priority on the operator form, on τ_sc as a quantity, and on the
preregistered falsification plan in §6.
