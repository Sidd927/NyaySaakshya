# Phase H red-team review

Three independent readings of the revised deck and answers, 15 October 2026. Each criticism ends in one of three dispositions: **FIX** (changed, with evidence), **REFRAME** (said more truthfully), or **DISCLOSE** (a genuine limitation that stays visible). Nothing was inflated to answer a criticism.

## Reviewer A: official evaluator

Does it answer what the Challenge asks, and what would cause rejection, a low score or a clarification request?

| # | Criticism | Disposition | What was done |
|---|---|---|---|
| A1 | **Sub-theme fit.** "Financial-crime intelligence" implies analytics that surface criminals or money flows. This tool assesses how mail transport was protected in a capture. An evaluator may see weak relevance. | **DISCLOSE** + REFRAME | Slide 1 says "It does not detect fraud or identify suspects"; slide 2 frames the use as avoiding over-reading evidence in cyber-fraud cases. The answers file warns the applicant not to claim intelligence. If the applicant wants certainty, ask the helpdesk whether the sub-theme fits (it is in the checklist). Fit remains the weakest part of the submission |
| A2 | No published rubric, but the programme family lists relevance, originality, feasibility, impact, scalability, cost. Is each visible? | **FIX** | Slide 2 relevance (concrete failure modes), 3 originality (stated as design strength), 4 feasibility, 5 impact and scalability. Cost is left as "not yet estimated" because no verified figure exists |
| A3 | **"Estimated number of people or units affected" is blank.** The FAQ asks for it. | **DISCLOSE** | No defensible, scoped estimate exists (the only candidate, about 50 district cyber police stations, rests on one broadcaster report). The answers file gives the exact wording and a decision path. An honest "no verified estimate" may cost points; an invented figure could fail due diligence |
| A4 | Stage claim: the portal option is "Working prototype (TRL 5-6)". Lab validation on synthetic captures is arguably TRL 4. | **REFRAME** | Slides say "Working Prototype, lab-validated, no external pilot". The answers file lays out both options and the risk; the applicant chooses |
| A5 | **Implementation capability.** One applicant, no qualification, mentor or institution shown. | **DISCLOSE** | Qualification, mentor and contact are left out rather than guessed. If the applicant has real credentials, adding them is the single biggest credibility gain (listed in `USER_INPUT_REQUIRED.md`) |
| A6 | Due diligence (6 to 10 Nov) will test IP and domicile. | **DISCLOSE** | Contributor and licence questions are listed for the applicant to answer factually (section on IP in `USER_INPUT_REQUIRED.md`) |
| A7 | Stale or inconsistent information would invite clarification requests. | **FIX** | Removed hosting prices, the "about 50" figure and open-source wording that contradicted the licence status; finals date corrected to the official 9 Dec |

## Reviewer B: technical reviewer

Are claims credible, specific, reproducible and qualified? Does the pilot plan face the real security gaps?

| # | Criticism | Disposition | What was done |
|---|---|---|---|
| B1 | "1,521 tests" overstates: one test fails. | **FIX** + DISCLOSE | The slide says "1,521 automated tests", not "passing". The cause (a freeze guard that diffs against an old tag, failing since the validated fixes were committed) is documented in `PHASE_H_BASELINE.md` and the claim audit. The README and `VALIDATION.md` still say "1521 passed, 0 failed"; that statement is inaccurate for the committed baseline and is flagged for the applicant, not edited here |
| B2 | **Circular validation.** 82 of 98 captures are crafted by generators written in the same project as the engine. | **DISCLOSE** | Slide 4 states the composition (10 Postfix/Dovecot, 6 OpenSSL, 82 in-project) and "lab validation only: no real-world accuracy benchmark" |
| B3 | No accuracy, false-positive or false-negative rates. | **DISCLOSE** | Stated on slide 4 and in every answer; none claimed |
| B4 | A tool for sensitive evidence with no authentication, audit log, encryption or sandbox. | **DISCLOSE** | Slide 4 lists each gap; slide 6 makes hardening the next milestone; deployment decision is NO-GO |
| B5 | **Problem-solution fit.** Investigators asking "was this mail session protected?" is a narrow question. Fraud cases more often turn on message content, headers and financial trails, which this tool does not read. | **DISCLOSE** | This is the deepest technical weakness. No source shows how often the question arises in Indian cyber-fraud cases and no investigator was interviewed. The deck therefore calls the premise a failure mode, not a frequency, and the Context line refuses to claim email prevalence. A short conversation with a real investigator would be the most valuable evidence to gather |
| B6 | Comparative claims against Wireshark, Zeek, NetworkMiner. | **FIX** | Checked against their documentation; wording is "their documentation, as we read it, has no per-fact evidence states", "a design strength, not a claim of uniqueness"; no benchmark claimed; the deck no longer says Wireshark decrypts "only if" keys are supplied |
| B7 | "Same capture, same ID" is not true across container formats. | **DISCLOSE** | Verified: pcapng conversion keeps the score but changes the capture ID. The deck's claim is "same capture and software", which is accurate |
| B8 | SHA-256 may be mistaken for chain of custody. | **FIX** | The deck never uses "chain of custody", "tamper-evident" or "admissibility"; the profile copy says traceability only |
| B9 | Inconsistent version labels visible in the UI (0.8.0 / 0.9.0 / 0.10.0). | **DISCLOSE** | Not shown on slides; flagged for any live demo |

## Reviewer C: skeptical reviewer

What feels generic, exaggerated, unsupported or unconvincing? What is the strongest reason not to select this?

| # | Criticism | Disposition | What was done |
|---|---|---|---|
| C1 | **Strongest reason not to select:** a solo applicant with a prototype validated only on lab-built captures, no user, no pilot, no partner, and a use case whose frequency is unknown. | **DISCLOSE** | This is true and is not hidden. The strengths are honesty, a concrete mechanism and a small, specific ask. The submission cannot honestly be made to look like more |
| C2 | "Can weaken a cyber-fraud case" is speculative. | **REFRAME** | Softened to "can undermine the finding built on it" and "a weak foundation for any cyber-fraud case built on it" |
| C3 | The deck is heavy on caveats; it reads as an apology. | **REFRAME** | Slide titles now lead with the point; limitations sit in labelled boxes ("Not built yet", "Not claimed") instead of being sprinkled through the text. Limitations that affect truth stay |
| C4 | Slide 3 is dense. | **REFRAME** | One visual hierarchy: the six-step strip, then states and a worked example side by side; all text 8.5 pt or larger. Accepted trade-off: the template's six-slide limit forces density here |
| C5 | Screenshots are small and mostly dark. | **FIX** | Replaced with 2x crops at 3.84 in wide; the large score and the "Not scored" headline are legible. The finer text is not meant to be read; slide 3 reproduces the key values as native text |
| C6 | Funding is requested with no amount or cost basis. | **DISCLOSE** | The deck says "Funding for a secure pilot build" with no figure and states costs are not estimated. The applicant may untick it |
| C7 | "Aligned with SDG 16" is decorative. | **REFRAME** | One short line, labelled as alignment, not impact |
| C8 | The product name, in Sanskrit-derived branding, and the UI's "Engine Live" language might look like a polished demo hiding an early prototype. | **DISCLOSE** | Slide 4 says what is missing; the screens are labelled "synthetic lab captures" |
| C9 | No video, no live link. | **DISCLOSE** | Optional per the FAQ. No video exists. A local synthetic demo is the plan for the later presentation stages |

## Priorities that remain open

1. Applicant facts that raise credibility (qualification, any real mentor) and the IP/contributor answers.
2. Optionally, one conversation with a real investigator, recorded truthfully if it happens.
3. The failing freeze-guard test and the "1521 passed" statements in `README.md` and `VALIDATION.md`, if the applicant wants the repository to match the facts.
