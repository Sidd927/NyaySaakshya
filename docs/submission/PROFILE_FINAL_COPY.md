# Project profile: final replacement copy

Prepared 15 October 2026 for the Seva portal team/project profile. The exact current profile text was not available to this session; the unsupported statements below are those reported in the Phase F and G briefs (forensic triage platform, district cyber cells, network captures and device data, suspect activity, Marathi/English reports, tamper-evident case files). Compare against what is on the portal and replace as shown.

Every sentence below was checked against the repository on 15 October 2026 (README, `DEPLOYMENT.md`, `VALIDATION.md`, `src/nyaysaakshya`). Nothing here was tested on real case data.

## Replacement copy

**One line (about 150 characters)**

> NyaySaakshya is a working prototype that turns saved email-traffic captures into evidence-linked findings and says what the capture cannot prove.

**Short profile (about 480 characters)**

> NyaySaakshya is a working prototype for forensic triage of saved email-traffic captures (SMTP, IMAP, POP3). It rebuilds the sessions and reports what the capture shows, with every finding linked to the packets it rests on. Each fact is labelled as observed, inferred, unknown, ambiguous, incomplete or not observable. When the capture cannot support a score, it withholds one and says why. The same capture and software give the same assessment ID. It does not detect fraud or identify suspects.

**Fuller profile (about 900 characters)**

> NyaySaakshya is a working prototype for the evidence-handling step of cyber-fraud investigations. An investigator uploads a saved capture of email traffic. The tool fingerprints it with SHA-256, rebuilds the SMTP, IMAP or POP3 sessions with TShark, and applies standards-based rules to what is visible. Findings cite the exact packets they rest on and carry an evidence state, so a cut-off handshake is reported as incomplete, never as "no encryption". If the capture cannot support a score, the tool says "not scored" and gives the reason. Reports (JSON, HTML, PDF) carry the capture's SHA-256 and a reproducible assessment ID. The prototype has been tested internally on 98 controlled lab captures and 1,521 automated tests. It has no external pilot, no real-world accuracy benchmark and no government approval. It is not production-ready: login, audit log, encrypted storage and backups are not built.

## Replace or remove

| Unsupported statement | Why | Replace with |
|---|---|---|
| "Platform" | Single-analyst prototype. No authentication, no multi-user operation. | "Working prototype" |
| Analyses "device data" | **Not implemented.** The tool reads only email-traffic captures. No phone, disk or device-data analysis exists. | Delete. Say "saved email-traffic captures". |
| Detects or flags "suspect activity" | **Not implemented, and contrary to design.** It does not detect suspects, intent, attackers or fraud, and says so in every report. | "States what a capture does and does not establish." |
| Used by or ready for "district cyber cells" | No cell uses it and none has agreed to a pilot. | "Proposed first users: a Maharashtra cyber cell or forensic lab." |
| "Marathi/English reports" as ready | English is the full report. A Marathi rendering exists for HTML only, is a machine draft and is marked unreviewed. It has **not** been tested with a Marathi reader or in this validation. | Omit Marathi from the profile. If you mention it: "A Marathi draft of the HTML report exists; it is unreviewed." |
| "Tamper-evident" or "case-file" readiness | A SHA-256 recorded at upload gives traceability only. There is no signing, no audit log, no access control and no protection against alteration of stored files. Not a case-management system. | "Reports carry the capture's SHA-256 and a reproducible assessment ID." |
| Legal chain of custody or court admissibility | Not claimed anywhere in the product and not established. | Do not state either. |
| "AI" or ML detection | The optional anomaly lane is off by default and cannot change a finding, band, score or coverage. | Do not state it as a capability. |
| Speed, accuracy or cost claims | Never measured. | Omit. |

## Real differentiators (supported)

1. **Evidence-linked findings.** Each finding cites frames and standards; 13,822 cited frames cross-checked against TShark with 0 stream mismatches (`VALIDATION.md`, internal validation).
2. **Explicit uncertainty.** Six evidence states; the tool abstains and withholds a score when evidence is too thin (`scored: false`, `value: null`).
3. **Reproducible assessments.** The same capture and software give the same assessment ID; 98 of 98 controlled captures were deterministic.
4. **Traceability to packet evidence.** Capture SHA-256 plus frame citations in JSON, HTML and PDF reports.

## Limits to keep stated

No real-world accuracy benchmark; internal validation on controlled captures only; no external pilot; no government approval; not production-ready; Marathi report untested and unreviewed; not a chain-of-custody system; no claim of admissibility.
