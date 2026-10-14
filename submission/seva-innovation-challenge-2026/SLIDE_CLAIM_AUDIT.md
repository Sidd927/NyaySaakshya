# Slide claim audit: Seva Innovation Challenge 2026 draft deck

Deck: `NyaySaakshya_Seva_Innovation_Challenge_2026_DRAFT.pptx` (6 slides). Audited 14 October 2026.

Classes: **VERIFIED** (read in repo or run locally), **SOURCED** (public primary source, opened and read), **ESTIMATE** (cost or planning assumption, stated as such on the slide), **TARGET** (proposed, not built or done), **PLACEHOLDER** (applicant must supply), **NO CLAIM** (slide states we do not claim it).

"SE" = `SUBMISSION_EVIDENCE.md` section. "VAL" = `VALIDATION.md`. "DEP" = `DEPLOYMENT.md`.

## Slide 1: Title and applicant snapshot

| Claim on slide | Class | Evidence |
|---|---|---|
| Evidence-first triage for email-traffic captures; says what a capture does and does not prove | VERIFIED | SE 1, 4; README |
| Stage: Working Prototype | VERIFIED (self-assessed) | Runs end to end locally on synthetic captures (SE 5); DEP classification B |
| Screenshot "Scored: every finding cites its evidence" (22.15 / 100, CRITICAL, 6 sessions) | VERIFIED | Screenshot of the running console on a synthetic lab capture, `assets/screen_scored_flagship.png` |
| Screenshot "Not scored" with withheld reason | VERIFIED | `assets/screen_withheld_not_scored.png`; schema 1.1 `scored:false, value:null` (VAL 14) |
| "Maharashtra Zone", "Seva Innovation Challenge 2026" | SOURCED | Organiser site, SE 14 |
| Applicant name, individual/team, sector, contact | PLACEHOLDER | `USER_INPUT_REQUIRED.md` |

## Slide 2: The Problem

| Claim on slide | Class | Evidence |
|---|---|---|
| 17.82 lakh complaints handled through CFCFRMS (PIB, 7 Oct 2025; period not stated) | SOURCED | PIB backgrounder "Curbing Cyber Frauds in Digital India", read in full (SE 2). The release page returned 403; the backgrounder PDF was used. The slide says "over 17.82 lakh" and "period not stated" |
| Investigators often hold a capture that is cut short or encrypted | Reasoned premise (hypothesis) | SE 2 "narrower problem". No investigator was interviewed. The slide says "often"; the applicant should soften or confirm after any interview |
| Reading more into a capture than it shows can produce an unsupported conclusion | Reasoned premise | Basis for the product design; not a measured rate |
| Wireshark decrypts TLS only if keys are supplied | SOURCED | Wireshark documentation (SE 14) |
| SMTP security "favors failing open" | SOURCED | Durumeric et al., ACM IMC 2015, abstract read (SE 2). General mail study, not India or fraud specific |
| Packet tools show packets; the analyst decides what is safe to conclude | SOURCED / reasoned | Wireshark and Zeek documentation (SE 4) |
| Proposed first users: a Maharashtra cyber cell or forensic lab; no partner has agreed | TARGET / NO CLAIM | No partner exists (SE 3) |
| "How many involve email is not published, so we make no claim" | NO CLAIM | SE 2: no published figure found |

**Removed from this slide:** Maharashtra 5.16 lakh cases / ₹7,592 crore (press-only, unverified), national 24,02,579 complaints (could not be verified), CERT-In 29.44 lakh (snippet only), "41,405 servers in 193 countries" (not in the paper's abstract).

## Slide 3: Our Solution & Innovation

| Claim on slide | Class | Evidence |
|---|---|---|
| Reads a saved capture of email traffic (SMTP/IMAP/POP3) | VERIFIED | README; SE 1 |
| Six evidence states: observed, inferred, unknown, ambiguous, incomplete, not observable | VERIFIED | `src/nyaysaakshya/evidence/states.py`; all six produced by controlled captures (VAL 14.7) |
| Each finding points to its packets | VERIFIED | 13,822 cited frames, 0 stream mismatches (VAL 15.5) |
| If the capture cannot support a score it gives none | VERIFIED | `scored:false, value:null` (VAL 14) |
| Input / Process / Output steps; SHA-256 fingerprint; sessions rebuilt; standards-based rules judge only what is visible | VERIFIED | README pipeline; capture SHA-256 in reports (SE 1) |
| Output: cited findings, score or "not scored", and a report | VERIFIED | JSON, HTML and PDF report (SE 1) |
| Table: packet tools give "Packets, fields, logs", "Analyst decides", "Depends on the analyst", "General analysis" | Hypothesis (qualitative) | SE 4 (Wireshark, Zeek documentation). The deck states no speed, cost or accuracy comparison |
| Table: NyaySaakshya marks cut-off or encrypted traffic as incomplete or not observable | VERIFIED | VAL 14.7 |
| Table: same capture + software gives same ID | VERIFIED | 98/98 controlled captures deterministic (VAL 14.9–14.10) |
| "Narrow: evidence-bounded triage" | VERIFIED (scope) | SE 1: not an AI fraud detector, no attribution |
| Key USP: says how sure the evidence allows us to be | VERIFIED | Evidence states and bands |
| Novelty relative to other tools | NOT CLAIMED as absolute | SE 4 caution: we did not verify that no other tool does this. The slide says "Complements packet tools; no speed or cost comparison is made." |

## Slide 4: Feasibility & Implementation

| Claim on slide | Class | Evidence |
|---|---|---|
| Python and TShark read the capture; React console; FastAPI service; SQLite storage | VERIFIED | Repository; SE 5 |
| 1,521 automated tests | VERIFIED | Baseline run recorded in SE 5 / VAL |
| 98 controlled captures | VERIFIED | VAL 14 |
| No GPU needed | VERIFIED | SE 8 (GPU): no dependency uses a GPU |
| Not yet built: login and roles, audit log, encrypted storage, backups, database-concurrency fix | VERIFIED (known gaps) | DEP blockers; TECH-DEBT #10 |
| Stage ladder with Working Prototype ticked | VERIFIED (self-assessed) | As slide 1 |
| Local synthetic demo: no extra cost | VERIFIED | Runs locally (SE 7) |
| Hosted free tiers wipe stored data when idle | SOURCED / VERIFIED | Vendor free-tier behaviour, SE 8, SE 11 |
| Vercel Hobby is $0 for personal use only | SOURCED | Vercel pricing page (SE 8) |
| On-premise pilot: not priced; needs vendor quotes | ESTIMATE (no number given) | SE 8. Render paid prices and the RBI rate were unverified, so no figure is shown |
| 3 / 6 / 12-month milestones | TARGET | Proposed in SE 10; slide says "Proposed, not committed" |
| Partners: none yet; no department has agreed | NO CLAIM (accurate) | SE 3 |
| [MENTOR / PARTNER] | PLACEHOLDER | `USER_INPUT_REQUIRED.md` |

**Removed from this slide:** the statement "the core makes no outbound calls (code inspection)" was dropped to fit the layout. It remains in SE 7 and DEP and can be restored.

## Slide 5: Impact & Scalability

| Claim on slide | Class | Evidence |
|---|---|---|
| "1 pilot (target)"; none reached yet; no partner yet | TARGET | SE 9–10. Zero beneficiaries today |
| Saving in cost / time: "To be measured" | NO CLAIM | No baseline measured (SE 9) |
| Jobs or livelihoods: "Not claimed" | NO CLAIM | No evidence |
| Helps investigators avoid unsupported conclusions, supporting fairer and stronger cyber-fraud cases | TARGET / hypothesis | Intended effect; slide adds "Social impact is not yet measured" |
| Links to SDG 16, target 16.a (institutions that combat crime) | SOURCED (mapping is our judgement) | UN SDG 16 page (sdgs.un.org/goals/goal16, read 14 Oct 2026): target 16.a concerns strengthening national institutions to prevent violence and combat terrorism and crime. Not recorded in SUBMISSION_EVIDENCE.md. Alignment is an argument, not a measured outcome |
| No revenue model is decided; stack is open source; licences to be confirmed | VERIFIED / PLACEHOLDER | SE 8 (licences row) |
| "Option to discuss with a partner: department budget or grant" | TARGET | Not agreed with anyone |
| [SUSTAINABILITY MODEL] | PLACEHOLDER | `USER_INPUT_REQUIRED.md` |
| Scale-up: demo, close security gaps, one supervised pilot, then further units; each unit runs locally | TARGET | SE 10; DEP. Slide says "Proposed; nothing is deployed" |
| Pilot measures listed (time to first assessment, time to report, provenance share, unresolved-evidence handling, reproducibility, supervisor confidence) | TARGET | SE 9 |

## Slide 6: Team/Individual & Support Required

| Claim on slide | Class | Evidence |
|---|---|---|
| Team member names, roles, qualifications, photos | PLACEHOLDER | `USER_INPUT_REQUIRED.md` |
| Mentor / faculty guide | PLACEHOLDER | As above |
| Support ticked: mentorship (security), pilot with a government department, funding for secure deployment, testing/certification/IP support; incubation unticked | Applicant's choice (proposed) | Driven by the DEP blockers. The applicant must confirm each tick |
| Closing sentence about moving from a tested prototype to a measured trial | TARGET | Does not claim deployment or outcomes |
| Contact email / mobile | PLACEHOLDER | As above |

## Quantitative claims on the deck, in one place

| Number | Where | Basis |
|---|---|---|
| 17.82 lakh | Slide 2 (twice) | PIB backgrounder, 7 Oct 2025 (SOURCED) |
| 22.15 / 100, 6 sessions | Slide 1 screenshot | Synthetic capture on the running console (VERIFIED, illustrative only) |
| 1,521 tests | Slide 4 | Baseline test run (VERIFIED) |
| 98 controlled captures | Slide 4 | VAL 14 (VERIFIED) |
| 3 / 6 / 12 months | Slide 4 | TARGET |
| 1 pilot | Slide 5 | TARGET |
| $0 (Vercel Hobby) | Slide 4 | Vendor page, personal use only (SOURCED) |
| SDG 16 / 16.a | Slide 5 | UN SDG framework (SOURCED; mapping is judgement) |

No beneficiary, savings, jobs, revenue, accuracy or speed figure appears on any slide.
