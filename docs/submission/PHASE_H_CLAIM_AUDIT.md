# Phase H claim audit

Audited 15 October 2026 against `f798d8d` plus the Phase H deck. Evidence was re-checked in source and by running the system locally (backend on 127.0.0.1, synthetic captures only, scratch data directory). "Deck" slide numbers refer to `NyaySaakshya_Seva_Innovation_Challenge_2026.pptx`; "App" means a field in `PORTAL_APPLICATION_ANSWERS.md`.

Status: **V** verified, **P** partially verified (qualified wording used), **U** unsupported (removed or labelled as proposal).

## A. Product capabilities (re-checked)

| Item | Finding | Evidence and location | Status |
|---|---|---|---|
| Supported protocols | SMTP, IMAP, POP3, including implicit-TLS SMTPS/IMAPS/POP3S. Other traffic is reported as unsupported and not graded | `README.md` "What it examines today"; `VALIDATION.md` AB-6 (7 of 7 non-mail cases withheld) | V |
| Capture formats | PCAP and PCAPNG (pcapng gives the same score and band; the capture ID differs) | `VALIDATION.md` ED-2; `DEPLOYMENT.md` upload validation | V |
| Six evidence states and when assigned | OBSERVED (directly in bytes), INFERRED (basis required), UNKNOWN, AMBIGUOUS (more than one reading), INCOMPLETE (capture truncated at that point), NOT_OBSERVABLE (impossible to see passively) | `src/nyaysaakshya/evidence/states.py`; all six demonstrated by reproducible captures (`VALIDATION.md` ES-1 to ES-6) | V |
| Score withheld when | no session assessed; fewer than 50% of sessions yield any conclusion (`MIN_ASSESSED_FRACTION = 0.5`); no coverage and no established issue | `src/nyaysaakshya/posture/scoring.py` lines 168-215; run 15 Oct: `E_cut_during_handshake.pcap` gave INSUFFICIENT_EVIDENCE, `scored:false`, `value:null` | V |
| Finding-to-packet provenance | Every finding has at least one evidence reference; every OBSERVED_ISSUE cites a standard and at least one frame; 13,822 cited frames, 0 stream mismatches against TShark (8,920 single-session findings) | `VALIDATION.md` PF-8, line 381 | V for OBSERVED_ISSUE; informational or abstaining findings cite evidence but not always a frame, so the deck says "each issue it reports" |
| Reproducibility | Same capture and software give the same assessment ID: 98 of 98 controlled captures. Re-run 15 Oct: flagship `afa30ff290742813`, withheld `870e1edcae99f7da`, identical to 14 Oct on a fresh data directory | `VALIDATION.md` 14.9-14.10; local run | V |
| SHA-256 | Identifies the capture bytes (and each report); gives traceability, not legal custody, tamper-evidence or authorship: no signing, no audit log, no access control | `README.md` ("not a legal chain-of-custody claim"); `DEPLOYMENT.md` | V (scope stated) |
| Reports | JSON, HTML, PDF export works: flagship 73,654 / 42,236 / 28,709 bytes; withheld 10,114 / 19,896 / 14,288 bytes, all valid file starts (15 Oct). Marathi report **not exercised** and not human-reviewed | local run; `README.md` | V (English); Marathi U |
| Optional anomaly (ML) analysis | Off by default (`ai_enabled: false` in API responses); with it on or off, findings, band, score, coverage and abstentions are identical on all 98 captures; it adds no detection the deterministic lane did not already make | `VALIDATION.md` ML-1 to ML-5, line 742; API response | V. Therefore **not** claimed as a capability |
| Test evidence | 1,521 tests collected. A clean run on `f798d8d` gives **1,520 passed, 1 failed** (95 s). The failure is a code-freeze guard (`test_backend_architecture.py::test_phase_seven_source_changes_only_where_declared`) that diffs against the old tag `v1.0.0-nyaysaakshya`; it passed in Phase B.4 only because the fixes were then uncommitted. All behaviour and validation tests pass | local `pytest` run, see `PHASE_H_BASELINE.md` | P. Not "1,521 passing". Not fixed (a test edit is out of scope; the guard needs a declared allow-list justified by an ADR) |
| Controlled-capture composition | 98 captures: 10 real Postfix/Dovecot sessions, 6 real OpenSSL handshakes, 82 crafted by in-project generators. No third-party or real-world traffic. No false-positive or false-negative rates | `VALIDATION.md` lines 617-622 | V. The deck states the composition and "lab validation only" |
| Known failure cases | Validation found and fixed: "no TLS" asserted on truncated streams (D1), non-mail traffic graded STRONG 100 (D2), INCOMPLETE not produced (D3), cut-handshake abstention (D7). One arguable case remains (`F_missing_setup`). Mail on a non-standard port is withheld, not detected | `VALIDATION.md` headline, lines 520, 299 | V |
| Security, storage, concurrency | No authentication or case isolation; shared SQLite connection (`db.py:105`); `AnalysisTimeout` defined but never raised; no delete or audit route; no encryption at rest; container runs as root; TShark not sandboxed; Docker image not built or validated | re-checked in source 14 Oct; unchanged in Phase H | V |
| Version labels | Console workbench shows "Engine Live · 0.8.0"; report generator "NyaySaakshya 0.9.0"; `/health` backend 0.1.0; posture engine 0.10.0, schema 1.1, rules 1.4. Inconsistent | UI source, report meta, `/health` | V. Not in the deck; screenshots are crops that exclude the label. Do not show the label in a demo |
| Duplicate upload quirk | Re-uploading an identical capture returns the original run but adds a `CANCELLED` run row | observed 14 Oct | V. Not fixed; avoid in demos |
| Licensing | NyaySaakshya has **no licence file** ("No license has been selected"). Components: TShark/Wireshark GPL-2.0-or-later (separate program), FastAPI, pydantic, React MIT; Uvicorn BSD-3; python-multipart Apache-2.0; ReportLab BSD; lucide-react ISC; IBM Plex and Tiro Devanagari Marathi fonts OFL-1.1 | `README.md`; installed package metadata and `node_modules` read 15 Oct | V |
| Local-first | The core analysis makes no outbound network call (code inspection of `src/`); this is a design property, not a validated deployment | `README.md`, `DEPLOYMENT.md` | P |

## B. Deck claims

| # | Claim (slide) | Evidence | Status | Action |
|---|---|---|---|---|
| 1 | Working prototype for forensic triage of saved email-traffic captures (1) | README; local run | V | none |
| 2 | "Each issue it reports cites the packets behind it" (1) | PF-8 above | V | reworded from "every finding" in Phase H |
| 3 | "When a capture cannot support a score, NyaySaakshya says so" (1, 3) | scoring.py; `E_cut` run | V | none |
| 4 | "Does not detect fraud or identify suspects" (1) | README non-goals; every report's limitations list | V | none |
| 5 | Applicant, individual, team size 1, sector, sub-theme (1, 6) | applicant and portal transcription; sub-theme on the official page source | V (sector/sub-theme); applicant-supplied (name, team) | applicant to check spelling |
| 6 | "Working Prototype: lab-validated, no external pilot" (1, 4) | VAL; DEPLOYMENT classification B | V | TRL label: see App 5 |
| 7 | Two screenshots are real, unedited crops (1) | Captured 15 Oct from the local console; scores reproduce | V | none |
| 8 | Incomplete capture is "Incomplete", not "no encryption" (2) | `states.py`; `E_cut` run; D1 history | V | none |
| 9 | Missing STARTTLS offer is ambiguous: non-support and stripping look identical (2) | README line 75; VAL ES-4; RFC 3207 | V | none |
| 10 | TLS 1.3 encrypts the server certificate, so it is not observable passively (2) | RFC 8446 section 1.2 | V | none |
| 11 | "A conclusion the evidence cannot support can weaken a cyber-fraud case" (2) | reasoning; no legal source cited | P | stated as consequence, not a statistic; the red-team review flags it |
| 12 | Packet tools show packets; deciding what is safe to conclude is manual and hard to repeat (2) | Wireshark, Zeek, NetworkMiner documentation | P | "hard to repeat" is reasoning |
| 13 | Who is affected; proposed first users; no partner has agreed (2, 6) | no partner exists | V (as proposal) | none |
| 14 | PIB cites over 17.82 lakh complaints in CFCFRMS; period not stated; not email-specific (2) | PIB PDF read 15 Oct | V | none |
| 15 | Pipeline Capture, Analysis, Evidence, Finding, Posture, Report; PCAP/PCAPNG; SHA-256 (3) | README; VAL ED-2 | V | none |
| 16 | Six states and their one-line meanings (3) | `states.py` | V | none |
| 17 | Worked example values (3): SHA-256 `97b2b61a…`, stream #0 10.0.0.6 to 10.0.0.80:587, frame #7, auth activity True OBSERVED, TLS transition False OBSERVED, SEC-PLAIN-001, NIST SP 800-52 Rev. 2 section 3.1, CONFIRMED | Provenance view of the real run, 15 Oct; hash matches `demo/hashes/SHA256SUMS.txt` | V | none |
| 18 | "Fewer than half yield a conclusion, the result is Not scored" (3) | `MIN_ASSESSED_FRACTION = 0.5` | V | none |
| 19 | "Blindness is never reported as safety" (3) | design comment and AB-6 (7 of 7) | P | rhetorical summary of a verified behaviour |
| 20 | Documentation of Wireshark, Zeek, NetworkMiner "has no per-fact evidence states"; "not a claim of uniqueness" (3) | docs read 15 Oct | P | qualified: "as we read it" |
| 21 | Stack: Python, TShark, React, FastAPI, SQLite (4) | repo | V | none |
| 22 | 1,521 automated tests (4, 6) | collected count | P | wording says "tests", not "passing"; one freeze guard currently fails (section A) |
| 23 | 98 controlled captures: 10 Postfix/Dovecot, 6 OpenSSL, 82 in-project (4) | VAL 617 | V | none |
| 24 | Same result on repeat, 98 of 98 (4) | VAL 14.9 | V | none |
| 25 | Validation found and fixed over-reading cases (4) | VAL headline | V | none |
| 26 | "Not built yet" list; "not production-ready"; demo local and synthetic only (4) | DEPLOYMENT; `DEPLOYMENT_GO_NO_GO.md` | V | none |
| 27 | 0-3, 3-6, 6-12 month path; dependencies; costs not estimated (4) | proposal | V (as proposal; labelled "not committed") | none |
| 28 | Public value expected, not measured; re-checkable findings (5) | hypothesis; reproducibility V | P | labelled "expected" |
| 29 | SDG 16, target 16.a (5) | sdgs.un.org/goals/goal16, read 14 Oct | V (mapping is judgement) | none |
| 30 | Adoption path and local-run intention "not built or validated" (5) | proposal | V (as proposal) | none |
| 31 | Pilot measures; "no targets claimed" (5) | proposal | V | none |
| 32 | "Not claimed: beneficiaries, savings, jobs" (5) | none measured | V | none |
| 33 | "Builds on open-source components; NyaySaakshya's own licence is not yet chosen" (5) | section A licensing | V | resolves the earlier "open source / licences unconfirmed" contradiction |
| 34 | Next milestone and "core analysis is built; what blocks a pilot is security engineering and access to a supervised unit" (6) | DEPLOYMENT P0 list | V | reworded in Phase H (earlier text implied no engineering) |
| 35 | Support requested (6) | applicant's request | applicant's choice | applicant to confirm each tick |
| 36 | "No other team member, mentor, partner or funder is named" (6) | statement of what is named, not of who contributed | V | see IP note in `USER_INPUT_REQUIRED.md` |

## C. Application-answer claims (summary; full text in `PORTAL_APPLICATION_ANSWERS.md`)

| Claim | Status | Note |
|---|---|---|
| Stage: working prototype | P | Portal option reads "Working prototype (TRL 5-6)". Evidence is lab validation; the answers file explains the choice and the more conservative alternative |
| Technology: Mobile/web platform and Data analytics; not AI/ML | V | ML lane off by default, no independent detection value |
| Advantages: New process/service model; evidence traceability, uncertainty, reproducibility | V | no speed, accuracy, cost, scale claims |
| Estimated number affected | none given | no defensible figure; decision path in the answers file |
| Tested/piloted: internal testing only | V | no external pilot |
| Expected impact | proposal | labelled expected and unmeasured |
| Demo and website links | blank | no live URL; repository private; stale Vercel site excluded |

## D. Removed or never used

Maharashtra 5.16 lakh cases and ₹7,592 crore; national 24,02,579 complaints; CERT-In 29.44 lakh; "41,405 servers in 193 countries"; "about 50 district cyber police stations"; hosting prices and cost totals; "no GPU needed" and "no outbound calls" (true but not needed); any AI/ML capability claim; any Marathi readiness claim; "built by one developer"; "developer of the prototype"; any claim of being first, only or unique.
