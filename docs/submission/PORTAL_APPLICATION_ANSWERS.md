# Portal application answers: Seva First Innovation Challenge 2026

Prepared 14 October 2026. For manual entry by the applicant. **Nothing here was entered into, or checked against, the live portal.**

**Evidence base and its limits**

- The portal form screenshots were **not available** to this session as images. The field list below comes from the transcription in the Phase F brief. It is not the exhaustive form, and the character limits, option wording and mandatory-field flags are **unknown**. Where the form shows a limit, shorten the "Short" version further.
- Public rules were re-read on 14 Oct 2026 at `sevainnovationchallenge.in` (home page, FAQ) and `/guidelines.html`.
- Product facts come from `VALIDATION.md`, `DEPLOYMENT.md`, `SUBMISSION_EVIDENCE.md` and the code, and were re-run today (see `DEPLOYMENT_GO_NO_GO.md`, section 6).

Confidence labels: **Verified** (checked in repo, run or public source), **Proposal** (reasonable, our judgement), **Confirm** (only the applicant can decide or declare).

Fixed portal facts (transcribed): sector **Law and Order**; sub-theme **Cyber-fraud, digital extortion and financial-crime intelligence**; team size 1; team lead Siddhant Hiralal Patil; Aadhaar verified; deadline 17 Oct 2026, 11:59 PM IST. Use these strings exactly. Do not change the sector.

**Fit warning.** The sub-theme says "financial-crime intelligence". NyaySaakshya does not produce intelligence, detect fraud or identify suspects. It supports the evidence-handling step of an investigation. Use the wording below, which says that plainly. Do not stretch it.

---

## 1. Your understanding of the problem

**Short (about 450 characters):**

> Cyber-fraud investigators often hold a network capture of email traffic that is cut short or encrypted. Packet tools show the packets, but the analyst must decide what is safe to conclude, which is manual and hard to repeat. A conclusion the evidence cannot support can weaken a case. Over 17.82 lakh cyber-fraud complaints were handled through the national CFCFRMS (PIB, 7 Oct 2025). How many involve email is not published, so we make no claim about that.

**Fuller (about 800 characters):** add after the second sentence: "Examples: a TLS handshake cut off by the end of the capture, certificate details hidden by TLS 1.3, or a missing STARTTLS offer that is byte-identical whether the server never supported it or something removed it." Add at the end: "The problem we address is narrow: stating what a capture does and does not establish, with the packets cited."

- **Evidence:** 17.82 lakh from the PIB backgrounder "Curbing Cyber Frauds in Digital India", 7 Oct 2025 (opened and read; period not stated in the source). The email-share gap is in `SUBMISSION_EVIDENCE.md` section 2. The STARTTLS ambiguity is in VALIDATION (AMBIGUOUS state).
- **Qualification:** "often hold" is our reasoning. No investigator has been interviewed. If you prefer, write "can hold".
- **Do not use:** the Maharashtra 5.16 lakh / ₹7,592 crore figures (press only, unverified).
- **Confidence:** Verified (statistic and product facts); Proposal ("often").

## 2. Estimated number of people/units affected in your target area

**Recommended entry (honest, scoped):**

> Not an estimate of people. The units that could use it are Maharashtra's district cyber police stations: about 50, plus one nodal station (All India Radio, 12 Oct 2024). Units using it today: none. A pilot would start with one. National context only, not a user count: over 17.82 lakh cyber-fraud complaints through CFCFRMS (PIB, 7 Oct 2025).

- **Method:** the figure is a count of potential units quoted from one government-broadcaster report. It is not a forecast of adoption and not a count of beneficiaries. No calculation beyond that quote was made.
- **Source check:** AIR report of 12 Oct 2024 on the state Cyber Command and Control Centre says it supports "50 district cyber police stations across the state" (opened and read). The official directory `mhcyber.gov.in/cyber-police-stations.php` returned HTTP 503 / an overload message today, so the count could **not** be checked against it. Older sources give 43 and 47. Say "about 50".
- **If the field is numeric only:** enter `50` only if the field accepts "units"; otherwise ask the helpdesk, or enter `1` and explain in field 10 that one pilot unit is the target. Do not enter 17.82 lakh, which is a complaint count and not users or units.
- **Confidence:** Proposal. **Confirm** before entering.

## 3. Proposed solution

**Short (about 600 characters):**

> NyaySaakshya is a working prototype that reads a saved capture of email traffic (SMTP, IMAP, POP3) and produces evidence-linked findings and a report. Every fact carries one of six states: observed, inferred, unknown, ambiguous, incomplete or not observable. Each finding cites the packets it rests on. If the capture cannot support a score, it gives none and says why. The same capture and software give the same result and ID. It does not detect fraud, name an attacker or decrypt TLS.

- **Evidence:** README, `VALIDATION.md` (states, 13,822 cited frames checked against TShark with 0 stream mismatches, 98/98 deterministic).
- **Do not add:** device-data analysis, suspect-activity detection, live capture, any AI claim. None exists.
- **Confidence:** Verified.

## 4. Who will use or benefit from the solution?

| Option | Recommend | Reason |
|---|---|---|
| Government officials | **Tick** (direct users) | Cyber-cell and forensic-lab investigators and supervisors are the intended users. Not yet used by any. |
| Citizens | Optional, **indirect** | Possible indirect benefit through sounder cyber-fraud cases. No citizen uses it. Tick only if you accept "indirect" fits the form's meaning. |
| Other | Optional | Type "Forensic-lab analysts" only if forensic labs are not counted as government officials. |
| Businesses/MSMEs, Women, Children, Students, Farmers, Rural, Urban, Healthcare, Educational | **Do not tick** | No supported link. |

- **Confidence:** Proposal. **Confirm** the Citizens choice.

## 5. Current stage of solution

**Working Prototype** (use the form's nearest option, probably "Prototype" or "Working prototype"). Do not select Field Pilot or Ready to Deploy.

- **Evidence:** runs end to end locally on synthetic captures (re-run 14 Oct 2026); `DEPLOYMENT.md` classification B ("validated prototype with a credible pilot path"); no pilot, no authentication, no audit trail.
- **Confidence:** Verified (self-assessed against the evidence).

## 6. What makes the solution innovative?

**Short (about 500 characters):**

> Packet tools show packets and fields. NyaySaakshya adds a rule: every statement must say how strongly the capture supports it, and the tool must abstain when it cannot. Six evidence states separate what was seen from what was inferred or cannot be known. A cut-off handshake is "incomplete", never "no encryption". A score is withheld when there is too little evidence. Reports carry the capture's SHA-256 and a reproducible ID. This complements packet tools; it does not replace them.

- **Qualification:** we have **not** verified that no other tool does this. The wording says what we built, not that it is unique. Do not write "first", "only" or "unique".
- **Confidence:** Verified (product behaviour); Proposal (framing).

## 7. Technology/approach used

| Option | Recommend | Reason |
|---|---|---|
| Mobile/web platform | **Tick** | React web console and FastAPI service. |
| Data analytics | **Tick** | Rule-based analysis of parsed capture data, cross-session comparison. |
| Process innovation | Optional | The innovation is the evidence-bounded workflow. Tick if the form's meaning fits. |
| **AI/ML** | **Do not tick** | An optional anomaly lane exists but is **off by default** and cannot change a finding, band, score or coverage (98 captures verified, VALIDATION 14.11). Ticking AI/ML would mislead. If a text box exists, write: "Optional anomaly signal, off by default, cannot change any finding." |
| IoT, Robotics, Drones, Blockchain, Hardware, Biotech, Materials, Clean tech | **Do not tick** | Not used. |
| Other | Optional | "Network forensics (TShark protocol dissection) and rule-based evidence reasoning". |

- **Confidence:** Verified (what is used); Proposal (Process innovation); **Confirm** the AI/ML decision, which is the applicant's call.

## 8. Key advantages

| Option | Recommend | Reason |
|---|---|---|
| New process/service model | **Tick** | Evidence-state workflow with abstention. |
| Other | **Tick**, type: "Evidence traceability, explicit uncertainty, reproducible reports" | Directly supported. |
| Lower cost, Faster, More accurate | **Do not tick** | No measurement of any of these. |
| Easier to use, Better citizen experience, Better government efficiency | **Do not tick** | Hypotheses for a pilot to test. Untested. |
| Scalable | **Do not tick** | Single-analyst prototype; SQLite concurrency defect open; no authentication. |
| More accessible, More inclusive | **Do not tick** | The Marathi report is an unreviewed machine draft. |
| Uses new technology | **Do not tick** | Not a supported claim. |
| Environmentally sustainable | **Do not tick** | Not relevant. |

- **Confidence:** Proposal. **Confirm.**

## 9. Has the solution been tested or piloted?

Select the option that means **tested internally / not piloted** (if only Yes/No exists, select **Yes** for "tested" only if the field is about testing, and say "internal testing only" in field 10).

- **Evidence:** 1,521 automated tests; 98 controlled captures; cited frames cross-checked against TShark.
- **Confidence:** Verified.

## 10. Pilot/deployment details

> No pilot and no deployment. Internal testing only, on synthetic or lab-generated captures: 1,521 automated tests; 98 controlled captures, all giving the same result on repeat; 13,822 cited packets cross-checked against TShark with no mismatches. Not tested on real case data. No government partner has agreed. Proposed, not agreed: one supervised pilot in a Maharashtra cyber cell, after adding login, an audit log, encrypted storage and backups.

- **Evidence:** `VALIDATION.md`, `DEPLOYMENT.md` blockers (re-verified, see `DEPLOYMENT_GO_NO_GO.md`).
- **Do not add:** users, interviews, customers, letters of support, funding, a live URL.
- **Confidence:** Verified.

## 11. Expected impact

> Expected, not yet measured: investigators spend less effort deciding what a capture can support, and cyber-fraud cases are less likely to rest on conclusions the evidence cannot bear. A supervised pilot would measure time to first assessment, time to a finished report, share of findings with usable packet citations, correct handling of unresolved evidence, repeatability and supervisor confidence. No savings, beneficiary or job figures are claimed. Supports SDG 16 (target 16.a, strengthening institutions that combat crime).

- **Evidence:** pilot measures from `SUBMISSION_EVIDENCE.md` section 9; SDG 16.a wording read at sdgs.un.org on 14 Oct 2026.
- **Confidence:** Proposal.

## 12. Standard six-slide presentation upload

- Upload the **final official-template PPTX** after the edits in `FINAL_SUBMISSION_CHECKLIST.md` section 4. Current draft is not uploadable: it still has placeholders and a four-person team layout.
- Portal accepts PDF, PPT, PPTX, max 15 MB (transcription). Public guidelines say a single PPTX. Our PPTX is about 0.13 MB.
- Do not upload `..._PREVIEW.pdf`: it is a LibreOffice render with a substitute font.
- **Confidence:** Verified (sizes, formats); Confirm the portal's accepted list when uploading.

## 13. Prototype/demo link

**Leave blank unless you create an unlisted video link of the synthetic demo** (see `DEPLOYMENT_GO_NO_GO.md`, section 7). The FAQ says demo and website links are optional. There is no live deployment. Do not enter the old `secure-mail-scope-psi.vercel.app`: it serves a stale build titled "SecureMailScope", and its `/api/v1/health` returns 404, so no working backend sits behind it.

- **Confidence:** Verified (site state checked 14 Oct 2026).

## 14. Website/product link

**Leave blank.** The GitHub repository (`Sidd927/NyaySaakshya`) is **private**: confirmed by the GitHub CLI today, and an anonymous request returns 404, so evaluators could not open it. Making it public is a separate decision (it holds research data and an unlicensed codebase) and is not recommended before the deadline.

- **Confidence:** Verified.

## 15. Consent and conflict-of-interest declaration

**Not answered here.** See the next section.

---

## Declarations the applicant must make personally

Nothing below was answered on your behalf. Read each one on the portal and decide yourself.

| Declaration | What it means | What to verify first |
|---|---|---|
| Consent to verification | The organisers may verify your information and ask for supporting evidence during due diligence (guidelines, section 1). | Every statement you enter must be backed by something you can show. The claim audit lists the evidence. |
| Conflict of interest | Whether you have a relationship with the organisers, evaluators, the Government of Maharashtra bodies running the challenge, or MSINS/RTMSSU that could influence evaluation. | Only you know. Evaluators declare theirs; applicants are asked too. |
| Domicile | The guidelines require the individual (or one founder) to hold a domicile certificate of Maharashtra, Chhattisgarh, Dadra and Nagar Haveli and Daman and Diu, or Goa. Team size is 1, so it is you. | That you hold a valid certificate, and which state. Have the file ready if the portal asks for upload. |
| IP status | Who owns the code. The repository has no licence file and one committer (Siddhant Patil). README says no licence has been selected. | That no employer, college or funder has a claim on the work. Dependencies are open-source (TShark/Wireshark, Python, FastAPI, ReportLab, React); confirm licence terms before any procurement. |
| Regulatory dependencies | Any approvals needed to use it. | The tool would process investigators' captures, which can contain personal data. Use of real evidence would need the unit's own legal approval and security controls that do not exist yet. Say this plainly. We are not giving legal advice. |
| Originality and single submission | The same innovation may be submitted once, under one primary sector (guidelines). | That you submit it nowhere else under another sector. |
| Identity and Aadhaar | Already verified on the portal. | Name is taken from Aadhaar and cannot be edited. |
| Accuracy of the application | Whatever the final declaration says. | Read the exact text. |

## Team profile audit (statements vs product)

The exact profile text was not available to this session. These are the statements as described in the brief. Compare against what you wrote.

| Profile statement | Product reality | Action |
|---|---|---|
| "Forensic triage platform" | Prototype, not a platform. Single-analyst, no authentication. | Say "prototype". |
| Network captures | Supported: SMTP, IMAP, POP3 captures, including implicit TLS. Other protocols are reported as unsupported and not graded. | Say "email-traffic captures". |
| "Device data" | **Not implemented.** No device, phone or disk analysis exists. | **Remove.** |
| "Suspect activity" | **Not implemented.** The tool does not detect suspects, intent or attackers, and says so. | **Remove.** Say "what the capture does and does not establish". |
| "District cyber cells" | Intended pilot users only. No cell uses it or has agreed. | Say "proposed first users". |
| "Marathi/English reports" | English report is full. Marathi is an unreviewed machine draft (HTML), marked as such. | Say "Marathi draft (unreviewed)". |

## Spelling of the name

The portal shows the team name as `NYAYSAakshya` / `NYAYSAKSHYA` (transcribed), while the product, repository and deck use **NyaySaakshya**. Check the stored spelling on the dashboard. If it is wrong, ask the helpdesk (support@sevainnovationchallenge.in, +91 91377 78135) whether it can be corrected. Use "NyaySaakshya" everywhere you can edit.
