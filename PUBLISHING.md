# Publishing checklist

Everything here needs **your** account and **your** signature. None of it can be done
for you: creating accounts, entering credentials and agreeing to a server's terms on
someone else's behalf are yours alone, and a preprint cannot be un-posted once it is up
(bioRxiv marks a withdrawal; the record stays).

Work down the list in order. Step 3 depends on step 2, and step 2 depends on step 1.

---

## 0. Blockers — resolve before anything else

- [ ] **Author list.** The manuscript currently carries one author. Decide who else
      belongs on it, in what order, and get each person's **written agreement to this
      specific version being posted as a preprint**. bioRxiv makes the corresponding
      author affirm that all authors agree. Do not add a senior author without their
      explicit sign-off — the framing of this paper (a calibration with a reported null
      result) is exactly the kind of thing a co-author may have views about.
- [ ] **Competing interests.** Declare any relationship — consulting, speaking,
      research funding, equity, family — with manufacturers of the device classes
      modelled here: drug-eluting stents, bioresorbable scaffolds, drug-coated balloons,
      nitinol and covered peripheral stents. A device-selection model with an
      undeclared industry relationship is the single fastest way to lose the paper.
- [ ] **Funding statement.**
- [ ] **Institutional policy.** Check whether Zhongshan Hospital / Fudan requires
      internal clearance before a preprint is posted. Some Chinese institutions do.

## 1. Publish the code (GitHub)

`gh` is not installed on this machine, so create the repository in the browser.

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
