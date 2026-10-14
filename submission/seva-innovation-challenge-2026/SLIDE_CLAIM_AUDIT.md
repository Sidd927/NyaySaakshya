# Slide claim audit: Seva Innovation Challenge 2026 deck

Deck: `NyaySaakshya_Seva_Innovation_Challenge_2026.pptx` (6 slides), built by `build_deck.py`. Audited 15 October 2026 (supersedes the 14 October draft audit).

Classes: **VERIFIED** (read in the repo or run locally), **SOURCED** (public primary source opened and read), **ESTIMATE**, **TARGET** (proposed, not built or done), **PORTAL** (as entered on the portal, from the applicant), **NO CLAIM** (slide says we do not claim it).

"SE" = `SUBMISSION_EVIDENCE.md`. "VAL" = `VALIDATION.md`. "DEP" = `DEPLOYMENT.md`.

## Slide 1: Title and applicant snapshot

| Claim | Class | Evidence |
|---|---|---|
| Forensic triage for email-traffic captures; tells investigators what a capture does and does not prove | VERIFIED | SE 1, 4; README |
| "It does not detect fraud or identify suspects" | VERIFIED | SE 1 (not an AI fraud detector, no attribution); reports state it |
| Applicant: Siddhant Hiralal Patil; individual, team size 1 | PORTAL | Phase F brief (portal transcription). Spelling to be checked against the portal by the applicant |
| Sector: Law and Order; sub-theme: Cyber-fraud, digital extortion and financial-crime intelligence | PORTAL | Phase F brief. The slide does not claim the tool provides intelligence |
| Stage: Working Prototype | VERIFIED (self-assessed) | Runs end to end locally (14 Oct run); DEP classification B |
| Screenshot "Scored" (22.15, 6 sessions) | VERIFIED | Reproduced on 14 Oct 2026: `deepdive_cross_session_control_endpoint.pcap`, CRITICAL 22.15, 12 of 12 sessions assessed, ID `afa30ff290742813` |
| Screenshot "Not scored" | VERIFIED | `scored:false, value:null`; reproduced with `E_cut_during_handshake.pcap` (14 Oct) |
| Contact details | **Omitted** | Not known to the repository. Add in `build_deck.py` `APPLICANT["contact"]` if wanted |

## Slide 2: The Problem

| Claim | Class | Evidence |
|---|---|---|
| "PIB cites over 17.82 lakh CFCFRMS cyber-fraud complaints (7 Oct 2025; period not stated; not email-specific)" and the big number "17.82 lakh complaints cited for the national CFCFRMS cyber-fraud system" | SOURCED | PIB PDF *Curbing Cyber Frauds in Digital India*, 7 Oct 2025, re-opened 15 Oct 2026: "financial institutions have been able to save more than ₹5,489 crore in over 17.82 lakh complaints". Period not stated. National, financial-fraud wide |
| "How many involve email is not published, so we make no claim" | NO CLAIM | SE 2 |
| Investigators often hold a capture that is cut short or encrypted | Reasoned premise | SE 2. No investigator interviewed. "often" is our reasoning |
| Wireshark decrypts TLS only if keys are supplied | SOURCED | Wireshark TLS documentation (SE 14) |
| SMTP security "favors failing open" | SOURCED | Durumeric et al., ACM IMC 2015 abstract (SE 2). General study, not India-specific |
| Packet tools show packets; the analyst decides what is safe to conclude | SOURCED / reasoned | Wireshark, Zeek documentation (SE 4) |
| Proposed first users: a Maharashtra cyber cell or forensic lab; no partner has agreed | TARGET / NO CLAIM | SE 3 |

**Removed:** Maharashtra 5.16 lakh / ₹7,592 crore (press only), 24,02,579 national count, CERT-In 29.44 lakh, "41,405 servers in 193 countries", and the Phase F "about 50 district cyber police stations" (single broadcaster report, official directory could not be loaded).

## Slide 3: Our Solution & Innovation

| Claim | Class | Evidence |
|---|---|---|
| Reads a saved capture of email traffic; labels every fact with one of six states | VERIFIED | `evidence/states.py`; all six produced by controlled captures (VAL 14.7) |
| Each finding points to its packets | VERIFIED | 13,822 cited frames, 0 stream mismatches (VAL 15.5) |
| If the capture cannot support a score, it gives none | VERIFIED | `scored:false, value:null` (VAL 14) |
| Input / Process / Output steps; SHA-256 fingerprint; sessions rebuilt; standards-based rules | VERIFIED | README pipeline |
| Table: packet tools "Packets, fields, logs", "Analyst decides", "Depends on the analyst", "General analysis" | Hypothesis (qualitative) | SE 4. No benchmark; slide says so |
| Table: marked incomplete or not observable; same capture + software gives same ID | VERIFIED | VAL 14.7, 14.9–14.10 (98/98 deterministic) |
| "Narrow: evidence-bounded triage" | VERIFIED (scope) | SE 1 |
| Novelty | NOT CLAIMED as absolute | SE 4 caution. "Complements packet tools; no speed or cost comparison is made." |

## Slide 4: Feasibility & Implementation

| Claim | Class | Evidence |
|---|---|---|
| Python, TShark, React console, FastAPI, SQLite | VERIFIED | Repository, SE 5 |
| "Internal validation only: 1,521 automated tests; 98 controlled captures" | VERIFIED | Baseline run (SE 5); VAL 14 |
| "No external pilot, real-world accuracy benchmark or approval" | VERIFIED | No pilot, partner or approval exists; VAL states mostly synthetic data |
| "Not production-ready. Missing: login, audit log, encrypted storage, backups, a concurrency fix" | VERIFIED | Re-checked 14 Oct against source: no auth code, no delete/audit route, shared SQLite connection (`db.py:105`); DEP |
| Stage ladder: Working Prototype | VERIFIED (self-assessed) | As slide 1 |
| Cost box: local demo no extra cost; hosted free tiers wipe data; Vercel Hobby $0 personal use only; on-premise not priced | SOURCED / ESTIMATE (no number) | SE 8; Vercel pricing page. Render paid prices and RBI rate unverified, so none are shown |
| 3 / 6 / 12-month milestones | TARGET | "Proposed, not committed" |
| Partners: none yet; no department has agreed | NO CLAIM (accurate) | SE 3 |

**Removed from this slide:** "no GPU needed" and "no outbound calls" (space); both remain true in SE 7 and 8.

## Slide 5: Impact & Scalability

| Claim | Class | Evidence |
|---|---|---|
| "1 pilot (target)"; none reached; no partner | TARGET | SE 9–10 |
| Saving in cost / time: "To be measured"; no baseline | NO CLAIM | SE 9 |
| Jobs or livelihoods: "Not claimed" | NO CLAIM | No evidence |
| Helps investigators avoid unsupported conclusions; "not yet measured" | TARGET / hypothesis | Intended effect, labelled unmeasured |
| SDG 16, target 16.a | SOURCED (mapping is judgement) | sdgs.un.org/goals/goal16, read 14 Oct 2026 |
| No revenue model decided; open-source stack; licences to be confirmed; partner budget or grant is an option, no commitment | VERIFIED / TARGET | SE 8; README ("No license has been selected") |
| Scale-up: demo, close gaps, one supervised pilot, then more units; local per-unit; "Proposed; nothing is deployed" | TARGET | SE 10; DEP |
| Pilot measures listed | TARGET | SE 9 |

## Slide 6: Team/Individual & Support Required

| Claim | Class | Evidence |
|---|---|---|
| Siddhant Hiralal Patil; "Applicant and team lead"; individual application (team size 1) | PORTAL | Portal transcription. The role says nothing about authorship, because git history shows another contributor (see `docs/submission/FINAL_RELEASE_AUDIT.md`, contributor flag) |
| "No other team member, mentor, partner or funder is named" | NO CLAIM | Says only that none is named; does not assert that none contributed |
| "1,521 automated tests and 98 controlled captures (internal validation; see slide 4)" | VERIFIED | As slide 4 |
| Support ticked: mentorship, department pilot, funding for secure deployment, testing/certification/IP; incubation unticked | Applicant's choice (proposed) | Follows the DEP blockers. Applicant must confirm the ticks |
| Qualification, mentor, contact, photo | **Omitted** | Not in the repository. The circle shows initials "SP", not a photo |

## Numbers on the deck

| Number | Where | Basis |
|---|---|---|
| 17.82 lakh | Slide 2 (twice) | PIB, 7 Oct 2025 (SOURCED, national, period not stated, not email-specific) |
| 22.15 / 100, 6 sessions | Slide 1 screenshot | Synthetic capture, current build (VERIFIED, illustrative) |
| 1,521 tests; 98 controlled captures | Slides 4, 6 | VERIFIED, internal validation |
| 3 / 6 / 12 months; 1 pilot | Slides 4, 5 | TARGET |
| $0 (Vercel Hobby) | Slide 4 | Vendor page, personal use only |
| SDG 16 / 16.a | Slide 5 | UN SDG framework |

No beneficiary, savings, jobs, revenue, accuracy or speed figure appears on any slide. No Marathi claim appears. No AI claim appears. No live URL appears.

## Not verifiable in this environment

Rendering was done in LibreOffice only, with a substitute font (Nirmala UI is not installed), plus a wider-font (Arial) stress render. **The deck was not opened in PowerPoint.**
