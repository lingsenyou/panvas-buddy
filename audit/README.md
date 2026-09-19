# Citation audit, 19 September 2026

The raw record of the audit described in §3 of the preprint and §2 of the repository
README. It is kept verbatim so that anyone can check the conclusions against what the
agents actually returned, including where they disagreed with each other.

## What was run

Sixteen anchors, each through a three-stage pipeline:

1. **Find.** One independent agent per anchor, told to locate and *open* the primary
   source, forbidden from inventing any DOI, PMID, volume or page, and required to
   report the value and the endpoint in the source's own words, with a short verbatim
   quote or a precise table locator. Permitted to answer "not found" or
   "this is an expert estimate" rather than produce something.
2. **Refute.** Two further independent agents per surviving citation, with different
   briefs and each told to default to refutation when unsure:
   - *Lens 1 — does the citation exist and say this?* Resolve the identifier, confirm
     authors, journal, year, and that the number appears for the stated arm and
     timepoint.
   - *Lens 2 — is it the same endpoint and the same population?* Check the number is
     12-month CD-TLR or TLF and not binary restenosis, primary patency loss, TVR, MACE
     or a different timepoint, and that bed, device class and lesion characteristics
     match.
3. **Audit.** One agent over the whole set, asked whether the endpoint really was held
   constant, which anchors should be dropped, which values should change, and whether
   the survivors were biased in a way that would distort a shared-parameter fit.

49 agents, 696 source lookups, no agent errors.

## Files

    citation_audit_2026-09-19.txt   human-readable summary: per anchor, the citation
                                    found, the value and endpoint as the source words
                                    them, both refutation verdicts, and the full
                                    cross-set audit
    citation_audit_journal.jsonl    the raw per-agent return values

## The finding, in one line

Of sixteen anchors, three were values the primary source actually reports at a
commensurable endpoint, and two of those three were the two arms of a single trial;
the other thirteen were stated high by factors of 1.0 to 5.8, with five traceable to a
different endpoint reported in the same paper.

## One methodological caveat the audit raised about itself

The `survived` flag in the raw record measures the reviewers' *policy*, not the
evidence. Six anchors drew split verdicts in which both reviewers agreed on every fact
and differed only on whether a value mismatch counts as a refutation — one logging it
as refuted, the other as a caveat. Two anchors are marked as surviving while both
reviewers explicitly flagged their values as wrong by 5.8x and 1.3x. Citation integrity
(is the paper real and correctly transcribed) and value support (does the paper report
this number) are separate questions and were separated by hand afterwards. On value
support the pass rate is 3 of 16.
