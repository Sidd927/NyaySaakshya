# Final portal answers changelog

15 October 2026. Old reference: `PORTAL_FIELD_BY_FIELD_FINAL.md` (and the same text in `PORTAL_APPLICATION_ANSWERS.md`). New candidate: **`PORTAL_APPLICATION_ANSWERS_FINAL_REVIEWED.md`**. The old files are not overwritten. **After you approve the candidate, use it as the manual-entry reference**; the old guide stays as history.

## Changed

| Field | Change | Why |
|---|---|---|
| 1 Problem | Opens with the investigator's situation; explains "capture"; failure modes in plain words; adds "how often has not been measured"; statistic moved to a closing bracket | Non-specialist evaluators; the official guide asks for frequency |
| 2 Units | Names the intended first users | Clearer, same honesty |
| 3 Solution | Value first, mechanism second, scope and "what it is not" last; "published rules" corrected to "rules based on published standards" | The guide's one-line solution and "say what it is NOT"; accuracy |
| 6 Innovation | Three design choices; less overlap with field 3; "no AI decides verdicts" | Guide: name any AI and what it did |
| 10 Pilot details | Not yet done / done internally / proposed pilot; measured failure and fix; what each number does not prove; pilot owner, data sequence, prerequisites, measures, stop conditions | Guide: one failure and the fix; a deliverable pilot plan |
| 11 Impact | Outcomes stated as intended and each measured against current practice | Guide: before/after, or honest "not yet tested" |
| Cost | New, separated answer, used only if the portal asks | Guide asks cost, who pays and sustainability; no cost field is in the known list |

## Retained

One-liner; selections in fields 4, 5, 7, 8 and 9; links blank; declarations left to the applicant. These were already correct and evidence-backed.

## Deck

The deck was cross-checked against the new answers; no contradiction was found, so it was **not changed**. (Deck: "on 44 cut-off streams the engine said 'no TLS' 41 times; now once (an arguable case)"; answers: "…we still count it as a failure". Both are true of the same record.)

## Unverified or unresolved

- Portal limits and mandatory markers (applicant reports none on substantive fields; not inspected).
- Whether field 2 accepts text.
- Contributor permission from Dishita.
- Frequency of the problem; no stakeholder evidence.
- The hardening estimate (labelled as judgement, not a quotation).

## Minimal corrections (15 October 2026, after applicant review)

Only these six changes were made to `PORTAL_APPLICATION_ANSWERS_FINAL_REVIEWED.md`; all other approved wording is unchanged.

| Field | Correction | Evidence or reason |
|---|---|---|
| 1 | "a first pilot would establish it" became "could begin measuring it in the participating unit, but not across the state" | One unit cannot establish statewide prevalence |
| 2 | Removed the advice to enter `1` if forced. Now: read the exact field wording; enter a number only if it truthfully answers the field; a pilot size is not an affected-population estimate; otherwise ask the helpdesk | A proposed pilot size is not an estimate |
| 3 | "always produce the same assessment ID" became "in repeat tests, re-analysing the same capture with the same software and settings gave the same assessment ID (98 of 98 lab captures)" | `posture/engine.py` `_assessment_id`: the ID is deterministic over its inputs but excludes the TShark version, which `Dockerfile` notes can change results; the ID also depends on the ML setting. So "always" was broader than the evidence; repeatability is what was demonstrated (`score_check.json` S4) |
| 6 | The Wireshark, Zeek and NetworkMiner sentence now says the parts of their documentation we reviewed did not describe the features, and that this does not show the tools lack them | The documentation review was limited |
| 10 | OpenSSL handshakes stated as recorded in a lab, 3 on a mail port and 3 on a non-mail port; "not 98 independent real cases" added | `VALIDATION.md` corpus table: `p11cert`, 3 on port 465, 3 on port 4443 ("not a mail port") |
| 10 | Pilot data: synthetic captures first; real case data only after the unit authorises it and legal, privacy, security and operational prerequisites are met; consent alone is not enough | Consent is not a sufficient basis for handling case evidence |

`FINAL_PORTAL_CLAIM_EVIDENCE_MATRIX.md` was updated to match field 3. The deck, code, portal and declarations are unchanged. The Dishita permission question remains unresolved.

**Final manual-entry reference:** `PORTAL_APPLICATION_ANSWERS_FINAL_REVIEWED.md`, subject to the applicant's confirmation of the personal declarations and of the exact portal field requirements.
