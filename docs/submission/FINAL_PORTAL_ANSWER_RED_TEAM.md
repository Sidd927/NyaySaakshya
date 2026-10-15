# Final portal answers: red-team review

15 October 2026. Reviews the answers in `PORTAL_FIELD_BY_FIELD_FINAL.md` (identical text in `PORTAL_APPLICATION_ANSWERS.md`) and records the revisions made in `PORTAL_APPLICATION_ANSWERS_FINAL_REVIEWED.md`.

## Sources re-checked

- **Present and read:** all files named in the brief. `PORTAL_FIELD_BY_FIELD_FINAL.md`, `PORTAL_APPLICATION_ANSWERS.md`, the three `FINAL_DECK_*` files and the deck exist. None is missing.
- **Official pages:** home page with FAQ, guidelines, template, the "Be a Problem Solver" guide and its workbook (all read 15 Oct 2026; the pages were unchanged during the day).
  - **Explicitly required:** six-slide official-template presentation; eligibility and domicile; disclosure of stage, prototype status, pilots, users, validation evidence, IP status and regulatory dependencies; consent to verification. The FAQ asks the problem statement to say who is affected and the estimated number affected.
  - **Recommended guidance (the guide and workbook, not binding):** a one-sentence problem with "how often" and its cost; stakeholder evidence; a working demo; one failure and the fix; before/after impact, or "baseline, expected result and trial date" if untested ("an honest 'not yet tested' beats an invented number"); the related Maharashtra department; a stagewise scale-up; cost, who pays and sustainability, with estimates marked; say what it is NOT; name any AI and say what it did.
  - **No Maharashtra scoring rubric or weights are published.** Other zones' criteria are not used as Maharashtra criteria.
- **Evidence:** every number was traced to its original record (see `FINAL_PORTAL_CLAIM_EVIDENCE_MATRIX.md`).

## Overall verdict on the old answers

The old answers were **accurate and safe but not optimally persuasive**. They led with mechanism rather than the investigator's situation, used protocol jargon (STARTTLS, implicit TLS) without explanation, hid the most credible evidence (the measured failure and fix) and gave field 10 no pilot plan an owner could act on (who runs it, what data, prerequisites, stop conditions). There was no cost answer. Nothing in them was false; three phrases were imprecise ("each finding cites", "13,822 cited packets cross-checked" without saying what that proves, and "all giving the same result" without saying how it was measured).

## Field by field

| # | What the evaluator wants | Old answer: strengths / problems | Change |
|---|---|---|---|
| One-liner | What is it, in one breath | Clear, fits 140, distinctive | **Retained** |
| 1 Problem | Who loses what, why, how often | Accurate; opened with "Investigators examining cyber-fraud cases can hold a network capture", then three technical failure modes in protocol terms; frequency not addressed; statistic well qualified | Rewritten to open with the investigator's situation in plain words, explain "capture", keep the three failure modes with jargon removed, add "how often has not yet been measured; a pilot would establish it" (the guide asks for frequency), keep 17.82 lakh as a final, bracketed context line |
| 2 Units affected | A scale estimate | Honest "no verified estimate"; slightly defensive | Kept the substance; names the intended first users; numeric-only decision path kept as APPLICANT MUST CONFIRM |
| 3 Solution | What it is and how it works | Good, but "SMTP, IMAP, POP3; PCAP or PCAPNG" up front; "each issue cites the rule…" fine | Leads with what it does for the investigator, then mechanism, then scope and "what it is not" (the guide's "say what it is NOT"); "published rules" corrected to "rules based on published standards" (the rule code is not public) |
| 4 Beneficiaries | Who gains | Correct | **Retained** |
| 5 Stage | Maturity | Correct | **Retained** |
| 6 Innovation | Why it is new | Correct, qualified; repeated much of field 3 | Reframed as "a discipline for evidence" with three numbered design choices; removed overlap with field 3; added "Verdicts come from 19 fixed rules; no AI decides them" (the guide asks applicants to name AI use) |
| 7 Technology | Selections | Correct; AI/ML unticked with evidence | **Retained** (implementation re-checked: verdicts are rule-based; ML lane off by default, cannot change findings) |
| 8 Advantages | Selections | Correct | **Retained** |
| 9 Tested | Single choice | "Testing in progress" correct | **Retained** |
| 10 Pilot details | What was tested; what a pilot would look like | Honest list of numbers; no failure story; no pilot owner, data plan, prerequisites in one place, or stop conditions | Restructured into **Not yet done / Done internally / Proposed first pilot**; added the measured failure and fix (the guide calls this the strongest credibility line); says what each number does and does not show; full pilot plan with who runs it, data sequence, prerequisites, measures and stop conditions |
| 11 Impact | Change expected and how measured | Honest; measures listed | Rewritten as intended outcomes, each to be measured against current practice; scale path labelled as a proposed design |
| Cost (if asked) | Cost, who pays, sustainability | Absent | Added a separated answer: current prototype, hardening and pilot (labelled engineering estimate, not quotation), recurring costs needing quotes, no saving claimed |
| 12 to 14 | Upload, links | Correct | **Retained** |
| 15 to 16 | Declarations | Correctly left to the applicant | **Retained**; the Dishita permission question stays unresolved |

## Independent reviewer pass (on the first draft)

**A. Government evaluator.** Strengths: concrete failure modes; an honest, specific pilot ask; a working demo. Problems found in the draft: field 1 was long and still technical in its second half; field 11 promised "less effort" without saying how it would be measured. *Revision:* kept the example-led opening but ended field 1 with the frequency gap and the context figure; field 11 now says each outcome is measured against current practice.

**B. Sceptical cybersecurity reviewer.** Problems found:
- "Fixed, published rules" implied the rules are public. *Revised* to "rules based on published standards".
- "All 13,822 packet citations in the findings" over-reached: the check covers single-session findings only. *Revised.*
- "Same capture always gives the same assessment ID" is true for the same software version and the same bytes only. Kept, with "and software version".
- Repeatability is not correctness, and traceability is not accuracy. Both are now stated in field 10.
- The 1-of-44 remaining case: the record calls it arguable but the pre-registered check still counts it as a failure. The answer says "we still count it as a failure", which is the stricter truthful wording.

**C. Pilot owner.** Problems found: no owner of daily operation; no data sequence; no stop rule; cost absent. *Revised:* "run by its own analyst with the applicant's support", "synthetic captures first and consented captures later", explicit prerequisites before real data, stop or redesign conditions, separated cost answer.

## Three strongest elements

1. A concrete, checkable failure mode (a cut-off recording read as "no encryption"), plus the tool's own measured history of making and fixing that mistake.
2. Traceability that a supervisor can check: packet to rule to published standard, with a withheld score when evidence is thin.
3. A pilot plan that names its own security prerequisites and stop conditions.

## Five most material weaknesses

1. **No stakeholder evidence and no frequency data** (intrinsic now; improvable before the deadline only by a real conversation with an investigator, truthfully reported).
2. **Lab-only validation, 82 of 98 captures generated in-project** (intrinsic).
3. **Partial fit with "financial-crime intelligence"** (intrinsic; disclosed).
4. **No affected-population estimate and no cost quotation** (intrinsic; honest answers given).
5. **Prototype lacks login, audit, encryption and backups** (intrinsic; listed as prerequisites).

## Claims that could undermine trust at due diligence

- Any reading of 13,822 citations or 98/98 determinism as accuracy: guarded in the text.
- The 1-of-44 case: stated strictly.
- AI: not ticked; stated that no AI decides verdicts.
- The compliance consent if the contributor permission is not settled: flagged.
- The engineering-time estimate: labelled as the applicant's judgement, not a quotation.
