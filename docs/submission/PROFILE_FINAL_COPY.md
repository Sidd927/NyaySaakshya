# Project profile: final replacement copy

Final text 15 October 2026 (Phase H) for the Seva portal team/project profile. The exact current profile text was not available to this session; the unsupported statements listed below are those reported in the Phase F and G briefs (forensic triage platform, district cyber cells, network captures and device data, suspect activity, Marathi/English reports, tamper-evident case files). Compare with what is on the portal and replace.

Every sentence was checked against the repository on 15 October 2026 (`README.md`, `VALIDATION.md`, `DEPLOYMENT.md`, `src/nyaysaakshya`) and by running the prototype locally on synthetic captures. Nothing was tested on real case data.

## Replacement copy

**One line (public profile field, limit 140 characters; this is 113)**

> Forensic triage of email-traffic captures: cites its packets and withholds a score when the evidence is too thin.

**Short profile (about 520 characters)**

> NyaySaakshya is a working prototype for forensic triage of saved email-traffic captures (SMTP, IMAP, POP3). It rebuilds the sessions and reports what the capture shows. Each fact is labelled observed, inferred, unknown, ambiguous, incomplete or not observable, and each issue it reports cites the packets behind it. When a capture cannot support a score, it gives none and says why. The same capture and software give the same assessment ID. It does not detect fraud, identify suspects or decrypt TLS.

**Fuller profile (about 960 characters)**

> NyaySaakshya is a working prototype for the evidence-handling step of cyber-fraud investigations. An investigator uploads a saved capture of email traffic. The tool records its SHA-256, rebuilds the SMTP, IMAP or POP3 sessions with TShark, and applies standards-based rules to what is visible. Each issue cites the rule, the standard and the packets it rests on, and every fact carries an evidence state, so a capture that ends inside a TLS handshake is reported as incomplete, never as "no encryption". If the capture cannot support a score, the tool says "Not scored" and why. Reports (JSON, HTML, PDF) carry the capture's SHA-256 and a reproducible assessment ID. It has been tested internally: 1,521 automated tests and 98 controlled lab captures. It has no external pilot, no real-world accuracy benchmark and no government approval, and it is not production-ready: login, audit log, encrypted storage and backups are not built.

## Replace or remove

| Unsupported statement | Why | Replace with |
|---|---|---|
| "Platform" | Single-analyst prototype. No authentication, no multi-user operation. | "Working prototype" |
| Analyses "device data" | **Not implemented.** The tool reads only saved email-traffic captures. | Delete. Say "saved email-traffic captures". |
| Detects or flags "suspect activity" | **Not implemented, and contrary to design.** It does not detect suspects, intent, attackers or fraud, and says so in every report. | "States what a capture does and does not establish." |
| Used by or ready for "district cyber cells" | No cell uses it and none has agreed to a pilot. | "Proposed first users: a Maharashtra cyber cell or forensic lab." |
| "Marathi/English reports" as ready | English is the full report. A Marathi rendering exists for HTML only; it is a machine draft, marked unreviewed, and has not been tested. | Omit Marathi. If you mention it: "A Marathi draft of the HTML report exists; it is unreviewed and untested." |
| "Tamper-evident" or "case-file" readiness | A SHA-256 recorded at upload gives traceability only. There is no signing, audit log, access control or protection against alteration of stored files. Not a case-management system. | "Reports carry the capture's SHA-256 and a reproducible assessment ID." |
| Legal chain of custody or court admissibility | Not claimed anywhere in the product and not established. | Do not state either. |
| "AI" or ML detection | The optional anomaly lane is off by default and cannot change a finding, band, score or coverage. It adds no independent detection. | Do not state it as a capability. |
| Speed, accuracy or cost claims | Never measured. | Omit. |
| "Open source product" | The components are open source; NyaySaakshya itself has **no licence chosen**. | "Built on open-source components; the project's own licence is not yet chosen." |
| "First", "only" or "unique" | Not verified. | "A design strength, not a claim of uniqueness." |

## Real differentiators (supported)

1. **Evidence-linked findings.** Each OBSERVED_ISSUE cites a standard and at least one frame; 13,822 cited frames cross-checked against TShark with 0 stream mismatches (`VALIDATION.md` PF-8, internal validation).
2. **Explicit uncertainty.** Six evidence states; the tool abstains and withholds a score when evidence is too thin (`scored: false`, `value: null`).
3. **Reproducible assessments.** The same capture and software give the same assessment ID; 98 of 98 controlled captures were deterministic.
4. **Traceability to packet evidence.** Capture SHA-256 plus frame citations in JSON, HTML and PDF reports.

## Limits to keep stated

Internal validation on controlled captures only (82 of 98 crafted in-project); no real-world accuracy benchmark; no external pilot; no government approval; not production-ready; Marathi report untested and unreviewed; not a chain-of-custody system; no claim of admissibility.
