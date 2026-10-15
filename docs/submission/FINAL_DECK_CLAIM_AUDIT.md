# Final deck claim audit

15 October 2026, final deck `NyaySaakshya_Seva_Innovation_Challenge_2026.pptx` (six slides). Evidence re-checked today in source and by running the system (backend on 127.0.0.1 with synthetic captures only); official pages re-read. "VAL" = `VALIDATION.md`. Status: **V** verified, **P** partially verified (qualified in the wording), **H** hypothesis or proposal (labelled as such on the slide).

## Quantitative and technical claims

| Claim (slide) | Evidence | Risk | Status | Disposition |
|---|---|---|---|---|
| **1,521 automated tests** (4) | Full suite on the final branch: 1,521 passed, 0 failed, 0 skipped (95 to 99 s, run twice on 15 Oct). Meaning: automated checks of the prototype's own behaviour, mostly written in-project; it is not a field test | Read as real-world validation | V | Kept; slide labels it "Built and tested (internal)" and "lab validation only" |
| **98 controlled lab captures: 10 from Postfix and Dovecot software in a lab, 6 OpenSSL handshakes, 82 crafted in-project** (4) | VAL lines 617-622: 10 captures are real Postfix/Dovecot sessions run in a lab, 6 real openssl handshakes, 82 crafted by in-project generators; no third-party or real-world traffic | "Real" read as real-world | V | Wording fixed in the previous pass; "no real-world traffic" stated |
| **13,822 cited frames, 0 stream mismatches** (not on the slides; used in the portal answers) | `research/experiments/phaseb/provenance_check.py` re-run today against TShark 4.6.8: 8,920 single-session findings, 13,822 frames, 0 frame-to-stream mismatches, 0 P2 violations; output identical to the committed `provenance_check.json` | Over-reading: it shows cited frames exist in the cited stream, not that findings are correct | V | Kept out of the deck; answers say "cross-checked against TShark" |
| **Same capture and software give the same result (98 of 98)** (4) | VAL 14.9 to 14.10 (98 of 98); re-confirmed today on two captures: flagship `afa30ff290742813`, cut-handshake `870e1edcae99f7da`, identical IDs to 14 Oct on a fresh data directory (`repro_check.py` also run: identical across layers; a changed analyser version gives a different assessment) | pcapng conversion keeps the score but changes the capture ID | V (98/98 from the recorded run; 2 re-run today) | Kept; wording is "same capture and software" |
| **On 44 cut-off streams the engine said "no TLS" 41 times; now once (an arguable case)** (4) | VAL NG-5: "1/44 carries SEC-PLAIN-002 (Phase B: 41/44)"; the remaining case is `F_missing_setup`, flagged "arguable" | Reads as unreliability | V | New in this pass (the official guide asks for one failure and its fix) |
| **19 versioned rules cited to RFC or NIST** (3) | Rule registry: 16 single-session + 3 cross-session; every rule has a non-empty `standards` tuple containing an RFC or NIST reference (checked in code today) | "Standards-bound" read as certified | V | Kept |
| **No AI in verdicts** (3) | Verdicts come from the deterministic rule and posture engines. The optional ML lane is off by default (`ai_enabled: false`) and with it on or off findings, band, score, coverage and abstentions are identical on all 98 captures; it adds no detection the deterministic lane did not make (VAL ML-1 to ML-5) | None | V | Kept; AI is not claimed anywhere |
| **Architecture strip (3)**: web upload of PCAP or PCAPNG with SHA-256; read-only TShark parse; sessions rebuilt, every fact gets an evidence state; rules; posture (score or Not scored); JSON/HTML/PDF with packet citations | `backend/pipeline.py` composes `analyze_capture` (hash, validate, `tshark -r`), `reconstruct_sessions`, `SecurityAnalysisEngine`, `CrossSessionEngine`, optional ML, `PostureEngine`; reports rendered from the stored assessment; pcapng accepted (VAL ED-2); README: passive, never connects to a mail server, no decryption | Diagram implying services, live capture or custody | V | No microservices, live capture, content reading, decryption, attribution, custody or integration is shown or implied |
| **Not scored if no session assessed or fewer than half yield a conclusion** (3) | `posture/scoring.py`: `sessions_assessed == 0`; `assessed_fraction < MIN_ASSESSED_FRACTION (0.5)`; also no coverage and no established issue | None | V | Kept |
| **Worked example values** (3): SHA-256 `97b2b61a…`, stream #0 10.0.0.6 to 10.0.0.80:587, frame #7, authentication activity True (OBSERVED), TLS transition False (OBSERVED), SEC-PLAIN-001, NIST SP 800-52 Rev. 2 section 3.1, CONFIRMED | Provenance view of the real run on `deepdive_cross_session_control_endpoint.pcap` (hash matches `demo/hashes/SHA256SUMS.txt`) | Synthetic capture shown as case evidence | V | Labelled "from a real run on a synthetic lab capture" |
| **22.15 scored; "Not scored" example** (1) | Reproduced 15 Oct: CRITICAL 22.15 (12 of 12 sessions assessed); `E_cut_during_handshake.pcap` INSUFFICIENT_EVIDENCE, `scored:false`, `value:null` | Crops hide stale version labels | V | "Cropped from the working console; not edited" |
| **17.82 lakh** (2) | PIB backgrounder *Curbing Cyber Frauds in Digital India*, 7 Oct 2025, re-read: "financial institutions have been able to save more than ₹5,489 crore in over 17.82 lakh complaints" through CFCFRMS. Period not stated | Read as users, email cases or target-area units | V (as context) | Secondary strip, "period not stated", "not email-specific", "no claim about how many cases involve email" |

## Failure modes, differentiation, scope

| Claim (slide) | Evidence | Status | Disposition |
|---|---|---|---|
| Cut-off capture is "incomplete", not "no encryption" (2) | `states.py` (INCOMPLETE); VAL D1 history; `E_cut` run | V | Kept |
| Missing STARTTLS offer is ambiguous: non-support and stripping look identical (2) | README; VAL ES-4; RFC 3207 notes stripping by deleting the "250 STARTTLS" response | V | Kept |
| TLS 1.3 encrypts the server certificate, so it is not observable passively (2) | RFC 8446 section 1.2: "All handshake messages after the ServerHello are now encrypted" | V | Kept |
| Packet tools "show packets"; deciding what is safe is manual and hard to repeat (2) | Wireshark, Zeek, NetworkMiner documentation | P ("hard to repeat" is reasoning) | Kept |
| Wireshark, Zeek and NetworkMiner "expose packets and fields"; documentation "as we read it" has no per-fact evidence states; "not a claim of uniqueness" (3) | Documentation read 15 Oct (Wireshark Expert Information and TLS wiki, Zeek `SMTP::Info`, NetworkMiner product page). Other tools not reviewed | P | Qualified; no comparative superiority claimed |
| Does not detect fraud or identify suspects (1) | README non-goals; every report's limitations list | V | Kept |
| "A conclusion the evidence cannot support is a weak foundation for a case" (2) | Reasoning, no legal source | H | Softened from "weaken a cyber-fraud case" |
| "Not yet known: how often investigators meet such captures; none consulted" (2) | No investigator interviewed | V (statement of ignorance) | New |

## Feasibility, cost, scale, impact

| Claim (slide) | Evidence | Status | Disposition |
|---|---|---|---|
| Not built: login and roles, audit log, encrypted storage and backups, concurrency fix, enforced time limit, sandboxed parsing (4, 6) | `DEPLOYMENT.md`; source re-checked: no auth, `db.py:105` shared connection, `AnalysisTimeout` never raised, no delete or audit route, TShark not sandboxed, container root | V | Kept; "Not production-ready" |
| "Cost not priced; a technical pilot needs no cloud service or GPU" (4) | No cost verified; the local demo runs on a laptop with no cloud and no GPU dependency (`SUBMISSION_EVIDENCE.md` section 8, README) | V (no figure given) | New; hosting prices removed since the earlier redesign and not reinstated |
| 0 to 3, 3 to 6, 6 to 12 month path (4) | Proposal | H | "Proposed path (not committed)" |
| "Demonstrable now: a local demo on synthetic captures: a supported finding, a withheld score and a report export" (6) | Run 14 and 15 Oct (JSON, HTML, PDF exported for both) | V | New; no recording exists and none is claimed |
| Public value, measures, before/after, "existing cost it targets is analyst time, to be measured" (5) | Proposal | H | All labelled expected, to be measured, no targets |
| "Likely owner: Home Department (police cyber cells); no office approached yet" (5) | The official applicant guide's department table lists the Home Department for defence and security; mapping police cyber cells to it is our reasoning | H | Labelled "likely"; no contact claimed |
| "Each unit would run it locally... a design intention, not built or validated" (5) | Proposal | H | Never a present guarantee |
| SDG 16, target 16.a (5) | sdgs.un.org/goals/goal16 | V (mapping is judgement) | One line |
| Open-source components; own licence not chosen (5) | README "No license has been selected"; component licences read 14 and 15 Oct | V | Resolves the earlier contradiction |
| Individual applicant, team size 1, name, sector, sub-theme (1, 6) | Applicant statement and portal transcription; sub-theme on the official page source | applicant-provided | Not independently verifiable |
| Support requested (6) | Applicant's request | applicant's choice | The applicant must confirm each tick |

## Not claimed anywhere

Fraud detection, suspect or attacker identification, TLS decryption, email-content reading, device analysis, government users or approval, pilot, production readiness, AI or ML capability, Marathi readiness, speed, accuracy, savings, hosting prices, a live link, qualifications, mentors, partners, endorsements, "first", "only" or "unique".
