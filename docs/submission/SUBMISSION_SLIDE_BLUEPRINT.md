# NyaySaakshya — Seva Innovation Challenge 2026: Slide Blueprint

Prepared 14 October 2026 on branch `design/landing-redesign` (base commit `ec689ee`, validation tag `v1.1.0-validation-baseline` = `c0f77b9`). This is a plan and copy bank, not the deck. The final PowerPoint is built in Phase E2.

**Evidence classes used on every claim:** **Demonstrated** (reproducible test or inspected behaviour), **Sourced** (external source I opened), **Estimate** (explicit assumptions), **Target** (a future pilot objective, never an achieved result), **Unknown** (no numerical claim made). Unfilled applicant facts are `[USER INPUT REQUIRED: …]`.

---

## 0. What was inspected, and what the official template requires

| Item | Result |
|---|---|
| Official template `Seva_Innovation_Challenge_2026_Presentation_Template.pptx` | **Opened** (from Downloads; unzipped and read slide XML and speaker notes). 6 slides, 16:9, 9,144,000 × 5,143,500 EMU (10 in × 5.625 in), so text boxes are small. Not rendered to images in this phase |
| Reference `SIH 2026 PS 2.pdf` | **Opened** (6 pages, text extracted). Reference only: SecureMailScope, Team "AyurX", Team ID 131458 |
| `docs/submission/reference/…` copies | Not present; not required, as instructed |
| Repository state | Clean tree; `design/landing-redesign` tracks `origin`; `ec689ee` and `SUBMISSION_EVIDENCE.md` present; tag still on `c0f77b9` |

**Slide order and required content (authoritative):** 1 Title and applicant snapshot · 2 The Problem · 3 Our Solution & Innovation · 4 Feasibility & Implementation · 5 Impact & Scalability · 6 Team/Individual & Support Required. No seventh slide.

**Template instructions to obey:** replace every grey `[bracketed]` text; delete guidance boxes (slide 1 has a "How to use this template" box); simple language; facts and numbers with sources; add prototype or field photos where available; submit as PDF, maximum 10 MB.

**Reviewer guidance printed in the speaker notes (use as the scoring lens):** slide 1 fill every field exactly as in the online form; slide 2 one strong statistic beats many weak ones, cite every number; slide 3 compare against what exists, originality and relevance are scored here; slide 4 be realistic, a costed plan with an identified adopting department scores better than a vague one, mention validation already done; slide 5 quantify where possible, state assumptions, link to a Government scheme, mission or the SDGs; slide 6 list only active members, be specific about support.

**Challenge criteria (organiser's press release and search summary; the official pages I opened state no weights):** relevance of the problem, innovation, technological maturity, potential impact, scalability, implementation capability, possibility of actual deployment. The official site describes administrative scrutiny, two independent online evaluations (technical and impact), finalist validation and a Grand Jury.

### Compliance points the user must resolve (found during inspection)

1. **Format conflict.** The template's slide 1 says "Save as PDF (max 10 MB) before uploading", but the official Guidelines page says each application is "submitted as a single PowerPoint (.pptx) presentation". Confirm on the portal which is required (P0).
2. **Sector.** One idea may be submitted under one primary sector only. The press lists "cyber fraud prevention" among the themes, but I could not open an official page listing the ten sectors. Confirm the sector name in the portal (P0).
3. **Disclosures** the Guidelines page says applicants must make: IP status, pilots, users/beneficiaries/customers. Our truthful answers: no patent; repository has **no licence selected** (README); no pilots; no users. Applicants also consent to verification, so every claim below is checkable.
4. **Domicile** certificate requirement (Maharashtra, Chhattisgarh, DNH & DD, or Goa) applies to the individual or one founder.

---

## 1. Positioning (the one idea behind all six slides)

> **NyaySaakshya tells an investigator what a captured email-traffic file does, and does not, prove, and points to the exact packets behind every statement.**

**Name and tagline:** NyaySaakshya — *Evidence-first triage for email-traffic captures.* (Name continuity with the SIH entry, "SecureMailScope", is a user decision, see P0.)

**Strongest defensible USP:** *explicit uncertainty with traceability.* Each fact carries one of six evidence states; each finding cites its frames; the tool withholds a score when the capture cannot support one; the same capture with the same software gives the same result. **Not** AI, not detection, not speed.

**Why this is the right headline:** it is the only claim that is fully demonstrated by tests, is understandable to non-technical judges ("it knows when it doesn't know"), and cannot be falsified by a judge opening the repository.

---

## 2. Slide 1 — Title and applicant snapshot

| | |
|---|---|
| Judge's question | Who are you, and what is this? (notes: fields must match the online application exactly) |
| Message to remember | A cyber-forensics helper that says what the evidence can and cannot prove |
| Headline | **NyaySaakshya** |
| Slide copy | Title: *NyaySaakshya*. One line: *"An evidence-first triage tool that tells cyber-cell investigators what a captured email-traffic file does, and does not, prove."* Below: Seva Innovation Challenge 2026 · Maharashtra Zone · Sector: `[USER INPUT REQUIRED: sector exactly as in the portal]` · Applicant: `[USER INPUT REQUIRED: name exactly as entered]` · Team/individual: `[USER INPUT REQUIRED]` · Application ID: `[USER INPUT REQUIRED if the portal issues one]` · Contact: `[USER INPUT REQUIRED]` |
| Visual | Template's own title layout. Optionally one small screenshot of a report headline ("Not scored: …"), if approved (P1). **Delete the "How to use this template" box** |
| Evidence | Product description: README, `SUBMISSION_EVIDENCE.md` §1 (**Demonstrated**). No numbers on this slide |
| Qualify | "Triage tool", not "detector"; "email-traffic captures", not "email" in general |
| Omit | "AI-powered", "first", "secure", any score, the old SecureMailScope tagline "AI-Assisted" |
| Criteria addressed | Administrative scrutiny: consistency with the application; relevance of sector |

---

## 3. Slide 2 — The Problem

| | |
|---|---|
| Judge's question | Is this a real, significant problem, and is it backed by evidence? |
| Message | Cyber-fraud losses in Maharashtra are large; investigators handling network evidence can be led into conclusions the evidence cannot support |
| Headline | **Evidence is often incomplete or encrypted, and a wrong conclusion weakens a cyber-fraud case** |

**Slide copy (fits the four template boxes plus the big-number box):**

- **What is the problem?** "Investigators who hold a network capture often cannot tell what it really shows. It may be cut short, or its content may be encrypted. A tool or a person that fills the gap with a guess can produce a conclusion the evidence does not support." *(Hypothesis framed as a problem statement; the sources below support the pieces, not the whole.)*
- **Who is affected?** "Cyber-cell and forensic investigators and the supervisors who must defend a finding. **Proposed first user group:** a Maharashtra cyber cell or forensic laboratory. *No deployment partner exists yet.*"
- **Evidence** (use **one** statistic, the Maharashtra one): "Maharashtra, 2024–25: 5.16 lakh online-fraud cases and ₹7,592 crore lost (Chief Minister's written reply to the Legislative Council, 4 March 2026)."
- **Current gaps:** "Packet tools show what is in the packets. Decrypting TLS needs keys the investigator often does not have. A cut-off or encrypted capture still leaves the reader to judge what can safely be concluded."
- **Big-number box** (`[X (number)]`): **"5.16 lakh"** — *online-fraud cases in Maharashtra, 2024–25.* Why it matters: "Fraud cases are many; each investigation rests on evidence that must be defensible."
- **Honesty line (small print):** "These figures describe cyber fraud overall. How many cases involve email is not published, so we make no claim about it."

**Visual:** a clean big-number card plus a two-line graphic "Capture → What can we safely say?" with three icons (cut-off, encrypted, ambiguous). No stock "hacker" imagery.

**Evidence table**

| Claim | Class | Source (opened) |
|---|---|---|
| Maharashtra 2024–25: 5.16 lakh cases, ₹7,592 crore lost; reply by the CM on 4 Mar 2026 | **Sourced** (press report of a government reply; I did not open the Council record) | Free Press Journal, "Maharashtra Govt Informs Council ₹941 Crore Lost…", updated 5 Mar 2026, accessed 14 Oct 2026. The same article gives other figures for a different scope (₹941 crore, 1.99 lakh cases, 2024–26) and does not reconcile them, so quote only the 2024–25 pair |
| TLS content cannot be read without secrets | **Sourced** | Wireshark wiki, TLS page ("supports TLS decryption when appropriate secrets are provided"; key log file, RSA key, PSK), accessed 14 Oct 2026 |
| SMTP security was added later and "favor[s] failing open", exposing users to downgrade to cleartext | **Sourced** | Durumeric et al., *Neither Snow Nor Rain Nor MITM…*, ACM IMC 2015, abstract read from the PDF, accessed 14 Oct 2026 |
| "Investigators may be led to over-conclude" | **Unknown as a measured rate**; stated as a problem hypothesis, to be tested in a pilot | none |

**Optional second figure (only if space):** national reported loss ₹22,495 crore in 2025 — **Sourced, secondary**: ThePrint, 21 Feb 2026, "sourced from the Ministry of Home Affairs"; it does not name the specific reply. The primary PIB page returned HTTP 403 and was not opened. **User should verify against the Rajya Sabha / PIB record before use.** I recommend dropping it: one strong statistic is better (template note).

**Must qualify:** complaint-reported amounts are not verified police findings. **Omit:** the 24,02,579 national complaint count that appears in the Phase D package: press sources I opened give 28.15 lakh for 2025, the sources disagree, and I could not verify either. Omit "41,405 servers / 193 countries" from the Durumeric paper (appeared in a search summary; not in the abstract I read). Omit any email share of fraud. Omit the SIH deck's problem statistics.

**Criteria:** relevance of the problem (sourced scale; honest about what is and is not known).

---

## 4. Slide 3 — Our Solution & Innovation

| | |
|---|---|
| Judge's question | What have you built, how is it new, and how does it differ from what exists? |
| Message | It separates what the evidence proves from what it does not, and shows the proof |
| Headline | **A capture goes in; findings that cite their evidence, and an honest "cannot tell", come out** |

**Slide copy**

- **Our solution in brief (3–4 lines):** "NyaySaakshya reads a saved network capture of email traffic (SMTP, IMAP, POP3). For each session it says whether the connection was protected, and marks every fact as *observed*, *inferred*, *unknown*, *ambiguous*, *incomplete* or *not observable*. Every finding points to the packets it rests on. If the capture cannot support a score, it gives none."
- **How it works:** **1 Input:** an investigator uploads a capture file. **2 Process:** the file is fingerprinted (SHA-256); sessions are rebuilt; fixed, standards-based rules judge only what the evidence shows. **3 Output:** evidence-linked findings, a posture or a clear "not scored", and a report (PDF/HTML/JSON, Marathi draft).
- **Key USP (one sentence):** "Every finding states how sure the evidence allows us to be, and which packets it rests on; when the capture is not enough, it says so instead of guessing."
- **Compact comparison (small table, qualitative only, from inspected capabilities):**

| | Packet tools (e.g. Wireshark, Zeek) | NyaySaakshya |
|---|---|---|
| What the reader gets | Packets and fields; Zeek's SMTP log shows TLS as true/false in the documentation example | Per-fact evidence state and a cited finding |
| Cut-off or encrypted capture | Reader decides | Marked INCOMPLETE / NOT OBSERVABLE; no score if unsupported |
| Repeat the analysis | Depends on the analyst | Same capture + same software = same assessment ID |
| Role | General network analysis | Narrow: evidence-bounded triage and reporting of mail-traffic captures |

Footnote: *"Complements, does not replace, packet tools."* **No speed, cost or accuracy comparison** appears; those are pilot measurement questions (slide 5).

**Visual:** the template's three-step flow (Input › Process › Output) with a real **screenshot of a withheld result** ("Not scored: no session could be assessed…") beside the flagship finding screen. *Screenshots must be approved by the user (P1) and taken from synthetic captures only.* Optionally a six-chip legend of the evidence states.

**Evidence table**

| Claim | Class | Source |
|---|---|---|
| Six evidence states exist in the code | **Demonstrated** | `src/nyaysaakshya/evidence/states.py`; all six produced by reproducible captures (VALIDATION §14.7) |
| Findings cite frames; cited frames match TShark | **Demonstrated** | `provenance_check`: 13,822 frames, 0 stream mismatches, 0 issues without a frame (VALIDATION §15.5) |
| Score withheld when unsupported (`scored:false`, `value:null`) | **Demonstrated** | VALIDATION §14.8; ran 14 Oct (cut-handshake and raw-TLS captures) |
| Same capture and software → same ID | **Demonstrated** | `score_check` determinism 98/98 over two runs; `repro_check` for two captures |
| Optional ML lane off by default and non-authoritative | **Demonstrated** | API `ai=false` default; `ml_isolation` 98 captures, 0 violations (findings, band, score, coverage, abstentions unchanged) |
| Packet tools' behaviour | **Sourced** | Wireshark TLS wiki; Zeek SMTP log documentation (the `tls` field is shown as true/false in the example), both accessed 14 Oct 2026. I did **not** test Wireshark or Zeek |
| "No other tool does this" | **Unknown, not claimed** | — |

**Must qualify:** "evidence states" and "withholding" are what we found documented in the tools reviewed; say "as far as we found". ML: "an optional ordering aid that cannot create or change a finding". **Omit:** "first", "only", "unlike every tool", "patent", "AI-assisted", cross-session "anomaly detection", the SIH comparison chart (11%/24%/31%/38%/42%/55%/76%/86%/88%/94%), "supports large PCAP datasets", "scale to enterprise", "reduces paper", "cost viability vs proprietary tools". None is supported by current evidence.

**Criteria:** originality and relevance (notes); technological maturity (demonstrated, tested); explicit about what it is not.

---

## 5. Slide 4 — Feasibility & Implementation

| | |
|---|---|
| Judge's question | Is it real, how ready, what will it cost, and who will adopt it? |
| Message | A tested working prototype with an honest, specific path to a supervised pilot |
| Headline | **Working prototype today; a supervised pilot needs defined security work first** |

**Stage: tick "Working Prototype".** Not "Field Pilot" (no field use) and not "Ready to Deploy" (no authentication, audit trail, retention or concurrency fix). "Proof of Concept" understates the validation done. *Evidence:* 1,521 automated tests pass; 98-capture controlled corpus; baseline tag (**Demonstrated**).

**Technology (short):** "Python and TShark (open-source packet reader) analyse the capture; a web console (React) and API (FastAPI) present it; SQLite stores results; no GPU needed; the core makes no outbound network calls (by code inspection)." *(Demonstrated by inspection; air-gapped operation is **not** tested.)*

**What exists vs what is needed (use as a two-column strip, or keep in speaker notes if space is short):**

| Exists today (Demonstrated) | Required before real-evidence use (not built) | Proposed pilot work | Long-term (possibility only) |
|---|---|---|---|
| Analysis, evidence states, reports, reproducibility, hash at upload | Authentication, roles, case isolation; audit log; TLS and encrypted storage; retention/deletion; backups; sandboxed worker; **fix the SQLite concurrency defect (TECH-DEBT #10, open)**; **enforce the analysis time limit (defined, not enforced)**; turn off demo-fixture fallback; check the TShark version in the deployed image (image never built in validation) | One supervised unit, synthetic then consented captures; measure indicators on slide 5 | Several units with local processing and central administration; nothing exists |

**Estimated cost (separate, no invented totals):**

| Scenario | Content | Class |
|---|---|---|
| Local synthetic demonstration | Runs on an existing laptop; ₹0 additional | **Demonstrated** (it ran locally on 14 Oct) |
| Hosting / development prototype | Vercel Hobby $0 (personal, non-commercial only) or Pro $20/month; Render free web services spin down after 15 minutes idle and **wipe files**, no persistent disk, so a paid instance and disk are needed for anything kept. Render paid prices could not be read from the vendor's own pages in my session | **Sourced** for Vercel and Render limits; Render prices **Unknown** (get a quote) |
| Future on-premise pilot | **No total is stated.** Inputs required: vendor quotations for a server and encrypted storage; retained-capture volume (captures/month × size × months × (1 + backup copies)); security-engineering effort for the required items above; support staff time. My judgement, not measured: "one to three engineer-months" of engineering | **Estimate** (judgement) / **Unknown** (cost) |

State: *estimates, not quotations or approved budgets; exchange rate ₹96/US$ assumed where used (RBI reference ₹95.749 on 12 Oct 2026 per a search summary, not opened on FBIL).*

**Proposed milestones (not commitments; each depends on the one before):**

| Horizon | Milestone | Acceptance criterion |
|---|---|---|
| 3 months | Close the security blockers above in a pilot build; identify a supervising mentor/department `[USER INPUT REQUIRED]` | Scripted tests pass: unauthenticated requests refused, parallel requests cause no database error, oversized/slow capture is stopped, restore-from-backup re-verifies every stored file's SHA-256 |
| 6 months | Controlled technical pilot on synthetic and consented captures at one site | Golden captures reproduce the validated results on the pilot machine; baseline measurements collected (slide 5 indicators) |
| 12 months | Supervised single-unit pilot, if the department agrees and policy permits | Pre-agreed metrics reported including negative results; written decision on whether to continue |

**Partners:** **None.** Write: "Seeking a cyber-cell or forensic-laboratory partner for a supervised pilot (no department has agreed)." `[USER INPUT REQUIRED: any real mentor or department conversation, with evidence]`.

**Visual:** stage ladder with Working Prototype ticked; small architecture strip *Capture → TShark → Rules → Evidence → Report*; cost table.

**Must qualify:** every "required" item is **not built**; say so. **Omit:** performance, throughput, "scalable to enterprise", Kubernetes/queue/cloud designs, any hosted-demo URL (none is configured for this product; the old Vercel link in the SIH deck opens a page titled "SecureMailScope" and I could not confirm it runs the current system, so do not present it as a demo).

**Criteria:** technological maturity, implementation capability, possibility of actual deployment (template notes: realistic, costed, adopter identified).

---

## 6. Slide 5 — Impact & Scalability

| | |
|---|---|
| Judge's question | What change will it create and can it grow? |
| Message | Impact is a testable pilot plan, not a claimed result; the path is short and conditional |
| Headline | **Impact will be measured in a supervised pilot; replication follows from safe local deployment** |

The template asks for three numbers (beneficiaries, % saving, jobs). **Do not fabricate them.** Replace the three big-number boxes with labelled targets or measurement statements:

| Template box | Proposed content | Class |
|---|---|---|
| Beneficiaries reached (first year) | **"1 supervised cyber-cell pilot"** — *target, not achieved; no partner yet* | **Target** |
| Saving in cost / time | **"To be measured"** — *time to first assessment and to a finished report, compared with the unit's current method, in the pilot* | **Unknown** (no baseline) |
| Jobs or livelihoods | **"Not claimed"** — *no job-creation evidence* | **Unknown** |

**Social impact (one sentence, qualitative):** "Helps investigators avoid unsupported conclusions, which supports fairer and stronger cyber-fraud cases." Link: **SDG 16** (access to justice; effective, accountable institutions; target 16.a on strengthening national institutions to combat crime), as worded on the UN SDG page I opened. Also the challenge's own cyber-fraud theme (press-reported). *Do not link to a named Government scheme unless the user confirms one; I did not verify any.*

**Pilot indicators (measurement method; no baselines, no percentages):**

| Indicator | How measured in the pilot |
|---|---|
| Time to a first assessment | Timestamp from upload to assessment, on pilot hardware, over a ladder of capture sizes |
| Time to prepare a report | From assessment to a report the supervisor accepts; compare with the unit's current method on the same captures |
| Share of findings with usable provenance | Investigator checks each cited frame; report the proportion usable |
| Correct handling of unresolved evidence | Seeded captures with known-unobservable facts; count correct abstentions and over-conclusions with and without the tool |
| Reproducibility | A second person re-runs; same assessment ID |
| Investigator effort / supervisor confidence | Timed tasks and a short structured questionnaire |

**Demonstrated today vs not yet measured:** *Technical validation (demonstrated):* 98 controlled captures, deterministic 98/98, 13,822 frames with 0 mismatches. *Operational and social impact: not yet measured.* These must not be mixed on the slide.

**Sustainability:** "No revenue model is decided. Options to discuss with a partner: department budget or grant; open-source stack (no licence fee identified, licences to be confirmed)." `[USER INPUT REQUIRED: preferred sustainability model]`.

**Scale-up path (conditional):** controlled demo → security work complete → one supervised cyber-cell pilot → if results and policy allow, further units, each running locally so evidence stays in the unit, with central administration only. *Proposed; nothing deployed.*

**Visual:** three-box row with *Target / To be measured / Not claimed* labels; a four-step path graphic; the six indicators as a small table.

**Evidence table:** SDG 16 wording — **Sourced** (UN, sdgs.un.org/goals/goal16, accessed 14 Oct 2026). Targets and measurement methods — **Target**. Technical figures — **Demonstrated** (VALIDATION, `ml_isolation`, `provenance_check`).

**Omit:** national-scale deployment, fraud reduction %, rupee savings, jobs, "faster", "lower cost", environmental impact (paper), any SIH impact numbers.

**Criteria:** potential impact, scalability, implementation capability; notes ask for stated assumptions and a scheme/SDG link (SDG 16 provided).

---

## 7. Slide 6 — Team/Individual & Support Required

| | |
|---|---|
| Judge's question | Who is behind it, and what exactly do you need? |
| Message | A small team with a validated prototype asking for targeted security and pilot support |
| Headline | **Support that turns a validated prototype into a safe, supervised pilot** |

**Slide copy.** Up to four team cards exactly as the template: Photo · `[USER INPUT REQUIRED: Name]` · `[USER INPUT REQUIRED: Role]` · `[USER INPUT REQUIRED: Qualification/expertise]`. Delete unused cards (notes: only active members). Mentor line: `[USER INPUT REQUIRED: Mentor/faculty guide and designation, or delete]`.

*Repository fact only:* all 16 commits are authored by one identity, Siddhant Patil. That does not establish team membership or roles; do not infer a team from it. The SIH deck's team name and ID are reference facts only; reuse them only if the user confirms.

**Support seeking (tick in this order of fit; the template lists five):**

1. **Mentorship & technical guidance (strongest fit):** security and secure-deployment mentorship for the blockers above.
2. **Pilot with a government department:** a supervised introduction to one cyber cell or forensic laboratory; *no department has agreed.*
3. **Funding / grant support:** secure deployment and testing (authentication, audit, encrypted storage, backups).
4. **Testing, certification or IP support:** independent security testing; licensing/IP guidance (no licence is selected today).
5. *Incubation & workspace:* optional; tick only if the user wants it.

**Closing sentence (template's one line):** *"With security mentorship and one supervised pilot, NyaySaakshya can move from a tested prototype to a measured trial of whether it helps investigators avoid unsupported conclusions."* Footer: `Thank you | [USER INPUT REQUIRED: contact email / mobile]`.

**Evidence:** repository (commit authorship, no licence), user-provided facts only. **Qualify:** no endorsement or partner implied. **Omit:** photos or credentials not supplied; invented roles; the word "incubated".

**Criteria:** implementation capability; clarity of support requested.

---

## 8. Claim audit summary

| Claim proposed for slides | Class | Where used |
|---|---|---|
| Six evidence states; frames cited; score withheld | Demonstrated | 3 |
| Reproducible: 98/98 deterministic; same ID | Demonstrated | 3, 5 |
| 13,822 frames, 0 mismatches | Demonstrated | 3, 5 |
| 1,521 tests pass; 98 controlled captures (synthetic or lab-generated; 10 real Postfix/Dovecot, 6 real OpenSSL handshakes) | Demonstrated | 4 |
| ML off by default; no change to findings, band, score, coverage | Demonstrated | 3 |
| Core makes no outbound calls | Demonstrated (inspection); air-gap Unknown | 4 |
| Maharashtra 5.16 lakh cases, ₹7,592 crore (2024–25) | Sourced (press report of a CM reply) | 2 |
| Wireshark needs secrets to decrypt; Zeek `tls` boolean; SMTP fails open | Sourced | 2, 3 |
| SDG 16 link | Sourced | 5 |
| Pilot targets, milestones, indicators | Target | 4, 5 |
| Pilot cost | Estimate / Unknown | 4 |
| Any speed, accuracy, cost, FP/FN, throughput, savings, jobs, fraud-reduction figure | **Unknown: omitted** | none |

**Corrections to the earlier Phase D package** (found while verifying; not yet edited there): (1) the 24,02,579 complaint count could not be verified and press sources disagree (28.15 lakh), so it is excluded here; (2) "41,405 servers in 193 countries" appeared only in a search summary and is not in the abstract I read; (3) Render's paid prices were not readable from vendor pages; only Vercel's were. `SUBMISSION_EVIDENCE.md` should be updated in a later phase.

---

## 9. Judge-facing messaging

**30 seconds.** "Investigators often hold a network capture that is cut short or encrypted. NyaySaakshya reads a saved capture of email traffic and tells them what it proves and what it doesn't, every finding pointing to the exact packets. When the evidence isn't enough, it gives no score instead of guessing. It's a working prototype; a supervised pilot is the next step."

**60 seconds.** "Cyber-fraud cases are many; in Maharashtra, about 5.16 lakh cases and ₹7,592 crore lost in 2024–25 according to the Chief Minister's reply. Investigators who rely on network captures can face evidence that's incomplete or encrypted, and a confident but unsupported conclusion weakens a case. NyaySaakshya takes a capture, rebuilds the email sessions and labels every fact as observed, inferred, unknown, ambiguous, incomplete or not observable. Findings cite the packets and the standards behind them, the same capture gives the same result, and the report says plainly what it could not determine. It complements packet tools like Wireshark; its difference is the evidence-bounded reasoning and reporting. It's a tested prototype, not yet fit for real evidence; we're seeking security mentorship and one supervised pilot."

**Five strongest evidence-backed differentiators**

1. Per-fact evidence states, all six demonstrated by real captures.
2. Frame-level traceability: 13,822 cited frames, 0 mismatches.
3. Deliberate abstention: no score when the capture can't support one, also in the machine-readable output.
4. Reproducibility: same capture and software, same assessment ID (98/98).
5. Bounded ML: optional, off by default, cannot change a finding or score (checked on all 98).

**Five likely objections**

1. *"Is it accurate?"* We have not measured real-world accuracy or error rates. We show independent agreement checks and reproducibility on a controlled corpus; the pilot is where accuracy-style questions get tested.
2. *"Does it prove fraud?"* No. It describes the transport-security evidence in a capture; it does not attribute or establish fraud.
3. *"Who will use it?"* Intended: cyber-cell and forensic-lab investigators. No unit uses it yet; we are asking for a supervised pilot.
4. *"Can it handle encrypted traffic?"* It does not decrypt. It labels what is visible and marks the rest "not observable".
5. *"Is the data safe?"* Not for real evidence today: no authentication, audit trail or encryption at rest. These are the first pilot tasks; any hosted demo takes synthetic captures only.

**Claims we must never make:** first/only/unique; patented; AI fraud detector; proves fraud or attributes an attacker; decrypts TLS or reads message content; legal chain of custody or court admissibility; government-certified or approved; production-ready or pilot-ready; secure for real evidence; "captures never leave the cyber cell" for the hosted demo; any accuracy, FP/FN, speed, throughput, cost-saving, jobs or fraud-reduction number; any department or user commitment.

**"Why is this not just Wireshark or Zeek?"** "Those tools are excellent and we build on TShark; we're not replacing them. They give an analyst packets, fields and logs, and decrypting TLS needs keys. NyaySaakshya adds a thin layer on top for one narrow task: it states, per fact, whether the capture observed it, inferred it, couldn't see it or was cut off, attaches the frames behind each finding, withholds a grade when the evidence is insufficient, and produces a reproducible report a supervisor can re-check. We have not benchmarked against them and don't claim to be faster or better at packet analysis."

**"If this isn't production-ready, why support it?"** "Because the hard, risky part, getting evidence-bounded reasoning right, is built and validated, and the missing parts are standard, listed and testable: authentication, audit, encryption, backups and a known concurrency fix. Support would fund exactly that, plus a supervised pilot to measure whether it helps. We aren't asking anyone to deploy it on real evidence today."

---

## 10. Unresolved-input checklist (user only)

**P0 — needed before the deck can be finalised**

| Input | Slide |
|---|---|
| Portal submission format: PDF (template) or .pptx (Guidelines page) | all |
| Exact sector name chosen in the portal | 1 |
| Applicant/team name exactly as in the application; individual or team; Application ID if issued | 1, 6 |
| Contact email and mobile for the closing line | 1, 6 |
| Team members (active only), roles, qualifications, photos; mentor/guide and designation, or confirm none | 6 |
| Product name continuity (NyaySaakshya vs SecureMailScope, and whether the SIH team name/ID may be mentioned) | 1, 6 |
| Domicile status and any mandatory portal fields | compliance |
| IP status declaration wording (no patent; no licence selected; do you want one chosen?) | 3, 6 |

**P1 — improves credibility**

| Input | Slide |
|---|---|
| Approved synthetic-data screenshots (a withheld result and a flagship finding screen) | 1, 3 |
| Any genuine conversation with a cyber cell, forensic lab, mentor or department, with evidence (letter, email) | 2, 4, 6 |
| Any verified investigator interview or needs assessment, with sample size and date | 2 |
| Any genuinely measured baseline (e.g. time to assess a capture manually) | 5 |
| Preferred sustainability model | 5 |
| Primary-source check (PIB/Rajya Sabha/Council record) of the Maharashtra figure | 2 |

**P2 — optional:** extra photos or lab visuals, branding preferences, supplementary links, incubation interest.

---

## 11. Sources actually opened (accessed 14 October 2026)

| Source | Publisher / date | Supports |
|---|---|---|
| Seva First Innovation Challenge, Maharashtra Zone, `sevainnovationchallenge.in` and `/guidelines.html` | Organiser (Government of Maharashtra initiative) | Six-slide template, single .pptx, last date 17 Oct 2026, evaluation stages, disclosures (IP, pilots, users), domicile; **no scoring weights or sector list shown** |
| Free Press Journal, Maharashtra Govt Informs Council ₹941 Crore…, updated 5 Mar 2026 | Press | Maharashtra 2024–25 figures and the CM's reply of 4 Mar 2026 |
| ThePrint, 21 Feb 2026 | Press | National 2025 loss ≥ ₹22,495 crore, 28.15 lakh complaints (secondary; unnamed MHA source) |
| Wireshark wiki, TLS | Wireshark project | Decryption requires supplied secrets |
| Zeek documentation, SMTP log | Zeek project | `tls` boolean in the example |
| Durumeric et al., IMC 2015 (PDF, abstract) | ACM IMC | SMTP security patchwork; fail-open; downgrade to cleartext |
| UN SDG 16 page | United Nations | SDG 16 and targets 16.4, 16.6, 16.a wording |
| Vercel pricing page | Vercel | Hobby $0 non-commercial; Pro $20/month |
| Render docs: free instances, disks, compute plans | Render | Free tier spin-down and ephemeral files; plan CPU/RAM; no prices |
| `secure-mail-scope-psi.vercel.app` | Prior deployment | Loads a page titled "SecureMailScope"; not verified as the current product |

**Not opened (primary source unreachable):** PIB release (HTTP 403); the Rajya Sabha and Legislative Council records; FBIL exchange rate; RFC and NIST documents (not cited in this blueprint).
