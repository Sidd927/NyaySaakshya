# Portal application answers: final reviewed candidate

15 October 2026. **Candidate for applicant approval.** It does not replace `PORTAL_FIELD_BY_FIELD_FINAL.md` until you approve it. Once approved, **this file becomes the manual-entry reference** (see `FINAL_PORTAL_CHANGELOG.md`). Nothing was entered into the portal.

Limits: you report no visible word or character limits on the substantive fields. I could not inspect the logged-in portal, so this is applicant-reported, not verified. The one known limit is the 140-character profile one-liner (public profile-wizard code). Character counts are given so you can spot any counter that does appear.

Labels used below: **ACHIEVED** (done and evidenced), **PROPOSED** (plan, not agreed or started), **APPLICANT MUST CONFIRM** (a personal fact or declaration).

Fixed facts: sector Law and Order; sub-theme Cyber-Fraud, Digital Extortion and Financial-Crime Intelligence; individual applicant, team size 1; Siddhant Hiralal Patil.

---

## Profile one-liner (limit 140; this is 113)

> Forensic triage of email-traffic captures: cites its packets and withholds a score when the evidence is too thin.

Retained unchanged: it fits, and it says what the tool does and the one thing that makes it different.

## 1. Your understanding of the problem (free text; 1194 characters)

> When a cyber-fraud case involves email, an investigator may be handed a saved recording of network traffic (a "capture") and asked what it proves. A capture can show less than it appears to. If the recording stops before the encryption handshake finishes, it is tempting to report "no encryption was used", but the capture simply does not contain the answer. If a mail server never offers encryption, that can mean it never supported it or that someone removed the offer in transit; the recorded bytes look the same. With modern encryption (TLS 1.3) the server's certificate is hidden, so a capture cannot show whether it was valid. Packet-analysis tools display the traffic but leave these judgements to the analyst, which is manual, hard to repeat and hard for a supervisor to check. A conclusion the evidence cannot support is a weak foundation for a case. How often investigators in Maharashtra face such captures has not yet been measured; a first pilot would establish it. (Context only: a Government of India PIB backgrounder of 7 October 2025 cites over 17.82 lakh complaints in the national CFCFRMS cyber-fraud system. The period is not stated and the figure is not specific to email.)

Short alternative (386 characters), only if a limit appears:

> Investigators can be handed an email-traffic capture that is cut off, ambiguous or encrypted, and must say what it proves. Reading more into it than it shows ("no encryption was used" when the recording simply stops) weakens the finding. Packet tools leave that judgement to the analyst, which is manual and hard to check. How often this occurs in Maharashtra has not yet been measured.

## 2. Estimated number of people / units affected in your target area (free text; 313 characters)

> No verified estimate is available. We have not measured how many cases or investigators in Maharashtra handle email-traffic captures, and we will not guess. Intended first users: investigators and supervisors in one Maharashtra cyber cell or forensic lab, if one agrees to a supervised pilot. None has agreed yet.

If the field turns out to accept **numbers only**: APPLICANT MUST CONFIRM. Do not invent a number. Ask the helpdesk (support@sevainnovationchallenge.in, +91 91377 78135) what to enter when no verified estimate exists. If you must proceed without an answer, `1` is the only defensible entry, and only if you also state elsewhere that it is the proposed first pilot unit, not an affected-population estimate.

## 3. Proposed solution (free text; 980 characters)

> NyaySaakshya is a working prototype that reads a saved email-traffic capture and reports what it does, and does not, establish about how the email connections were protected. An analyst uploads the file in a web console. The software rebuilds each mail session and labels every fact with one of six evidence states: observed, inferred, unknown, ambiguous, incomplete or not observable. Fixed rules based on published standards then produce findings. Each reported issue names the rule, the standard it relies on and the packet numbers that show it, so a supervisor can check it. If too little of the capture can be assessed, the tool gives no score and says why, instead of a reassuring grade. Reports are exported as JSON, HTML and PDF, and the same capture and software version always produce the same assessment ID. It works only on saved captures of supported mail traffic (SMTP, IMAP, POP3). It does not detect fraud, identify suspects, decrypt traffic or read email content.

## 4. Who will use or benefit from the solution? (checkboxes)

- **Government officials: tick.** Direct intended users: cyber-cell and forensic-lab investigators and their supervisors. None uses it yet.
- Citizens: optional, indirect only (sounder findings in cases that affect them). Unticked is equally defensible. APPLICANT MUST CONFIRM if ticked.
- All other categories: do not tick (no supported link).

## 5. Current stage of solution (single choice)

**Working prototype.** ACHIEVED: runs end to end locally; validated on lab captures. Never "pilot" or "deployed". If a TRL label is shown beside it, be ready to say "lab-validated, no external pilot".

## 6. What makes your solution innovative? (free text; 883 characters)

> The innovation is a discipline for evidence, not a new packet decoder: every statement must say how strongly the capture supports it, and the tool must stay silent when it cannot. Three design choices follow. (1) Six evidence states keep "seen", "deduced" and "cannot know" apart, so a cut-off recording is reported as incomplete, never as "no encryption". (2) Each reported issue is traced from packet to rule to published standard (RFC or NIST), so it can be checked rather than trusted. (3) The tool withholds a score when evidence is too thin, and repeated runs give the same assessment ID. Packet tools such as Wireshark, Zeek and NetworkMiner show packets and fields; in their documentation we did not find per-fact evidence states or deliberate abstention. We present this as a design strength, not a claim of uniqueness. Verdicts come from 19 fixed rules; no AI decides them.

## 7. Technology / approach used (checkboxes)

- **Mobile / web platform: tick.** Web console and service.
- **Data analytics: tick.** Rule-based analysis of parsed capture data, including comparison across sessions.
- **AI / ML: do not tick.** Verdicts come from fixed rules. An optional anomaly lane exists but is off by default, cannot change any finding, band, score or coverage, and added no detection the rules had not already made on 98 captures. Ticking it would misdescribe the product.
- Process innovation: optional.
- Other (optional text): "Network protocol analysis (TShark) and rule-based evidence reasoning"
- All other options: do not tick.

## 8. Key advantages of your solution (checkboxes)

- **New process / service model: tick.**
- **Other: tick**, text: "Evidence traceability, explicit uncertainty, reproducible reports"
- Lower cost, Faster, More accurate, Easier to use, Better government efficiency, Better citizen experience, Scalable, More accessible, More inclusive, Uses new technology, Environmentally sustainable: **do not tick**. None has been measured or demonstrated.

## 9. Has the solution been tested or piloted? (single choice)

**Testing in progress.** It is the only true option: "No" would deny the internal testing; "Yes - One Pilot", "Yes - multiple pilots" and "Currently deployed" would claim something that has not happened. Field 10 opens by saying there is no external pilot, so the choice cannot be misread.

## 10. Pilot / deployment details (free text; 1801 characters)

> Not yet done: no external pilot, no deployment, no government approval, no use on real case data, and no measured real-world accuracy.
>
> Done internally, on lab captures only: 1,521 automated tests pass. 98 controlled captures were analysed: 10 sessions from real Postfix and Dovecot mail servers run in a lab, 6 real OpenSSL handshakes, and 82 crafted by generators written in this project; none is real-world traffic. All 13,822 packet citations in the single-session findings were checked against the TShark packet tool and found in the cited connection (this shows traceability, not accuracy). Every capture gave an identical assessment when analysed twice. Testing also exposed a failure: on 44 cut-off connections the software reported "no encryption" in 41. After the fix it does so in 1, where the recording starts mid-session but the unencrypted exchange is visible; we still count it as a failure.
>
> Proposed first pilot (no partner has agreed): one cyber cell or forensic lab, run by its own analyst with the applicant's support, on synthetic captures first and consented captures later. Before any real case data: login and roles, an audit log, encrypted storage, backups, a fix for a known database-concurrency defect, an enforced analysis time limit, isolated parsing of untrusted files, a written threat model, and the unit's own legal approval. Measured against the unit's current practice: time to a first assessment and to a finished report, share of findings whose packet references a reviewer can verify, correct handling of incomplete and unknown evidence, repeatability, reviewer usability and supervisor confidence. Stop or redesign if reviewers cannot verify findings, if the tool states a conclusion the evidence does not support, or if the security prerequisites cannot be met.

Short alternative (318 characters), only if a limit appears:

> No external pilot, deployment, approval or real case data yet. Internally: 1,521 automated tests pass; 98 lab captures analysed (82 crafted in-project); 13,822 packet citations checked against TShark; identical results on repeat runs. Proposed: one supervised cyber-cell pilot after security hardening; no partner yet.

## 11. Expected impact (free text; 806 characters)

> Intended outcome, not yet measured: cyber-fraud findings drawn from email-traffic evidence that state only what the evidence supports, can be checked by a supervisor and can be reproduced. If the pilot works, investigators should spend less effort deciding what a capture can support, supervisors should be able to verify each finding against its packets, and fewer conclusions should rest on incomplete or ambiguous evidence. Each of these will be measured against current practice in the pilot; today we claim no savings, speed-up, accuracy or beneficiary numbers. If the pilot shows value, further units could follow, each running the tool locally so that captures stay within the unit (a proposed design, not yet built). This supports SDG 16, target 16.a (strengthening institutions that combat crime).

Short alternative (303 characters):

> Intended, not yet measured: findings from email-traffic evidence that claim only what the evidence supports and that a supervisor can verify. A supervised pilot would measure time, verifiability and handling of incomplete evidence against current practice. No savings or beneficiary numbers are claimed.

## Cost and feasibility (only if the portal asks; no such field is in the known list)

> Current prototype: runs on existing hardware using open-source components; the local demonstration needs no cloud service or GPU. Security hardening and a pilot: not yet quoted. Our own engineering judgement is about one to three engineer-months for the prerequisites listed above, to be re-estimated after a short technical spike; this is an estimate, not a quotation. Recurring costs for a pilot unit (a workstation or server, encrypted storage, backups, security review, staff time) require vendor quotations and the unit's own rates. No cost saving is claimed.

## 12. Standard six-slide presentation upload

Upload `submission/seva-innovation-challenge-2026/NyaySaakshya_Seva_Innovation_Challenge_2026.pptx`, not the preview PDF. Open it in PowerPoint first (never checked in PowerPoint). The deck and these answers were cross-checked; no contradiction found (see `FINAL_PORTAL_CHANGELOG.md`).

## 13. Prototype / demo link

**Leave blank** (optional per the official FAQ). There is no safe public link: public deployment is NO-GO, and the old SecureMailScope site is stale. A local demo exists and can be shown on request; no recording exists.

## 14. Website / product link

**Leave blank.** The repository is private.

## 15. Compliance consent

**APPLICANT MUST CONFIRM.** You report that you agree with it. Read the exact wording and tick it yourself only if every part is true for you. **Unresolved:** whether Dishita, who helped with some frontend work and is not a team member, has agreed that her contribution can be included and submitted, and whether she keeps any rights. Nothing in the repository resolves this. If the consent text covers the right to submit all code and assets, settle this first (one message to her is enough as a record).

## 16. Relationship with organisers or jury

**APPLICANT MUST CONFIRM.** You report "No". Select No only on that basis; it was not independently verified.
