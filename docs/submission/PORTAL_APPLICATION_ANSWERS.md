# Portal application answers: Seva First Innovation Challenge 2026 (final paste-ready version)

Final audit 15 October 2026. For **manual entry by the applicant**. Nothing here was entered into, or checked against, the live portal.

**Limits of the evidence**

- The portal screenshots were not available to this session as images. The field list is the transcription in the Phase F brief. It is not claimed to be the whole form. Character limits, option wording and mandatory flags are **unknown**: read them on the form and shorten if needed.
- Public rules were re-read on 14 Oct 2026 (`sevainnovationchallenge.in` home, FAQ, `/guidelines.html`).
- Product facts come from `VALIDATION.md`, `DEPLOYMENT.md`, the code, and a local run on 14 Oct 2026.

Labels: **Verified** (checked in the repo, run or public source) · **Proposal** (our judgement) · **Confirm** (only you can decide or declare).

Portal facts (transcribed): sector **Law and Order**; sub-theme **Cyber-fraud, digital extortion and financial-crime intelligence**; team size 1; team lead **Siddhant Hiralal Patil**; deadline 17 Oct 2026, 11:59 PM IST. Use these strings exactly. **Confirm** the spelling of the team name on the dashboard: it shows `NYAYSAakshya` / `NYAYSAKSHYA`, the product is NyaySaakshya.

Related files: `PROFILE_FINAL_COPY.md` (project profile text), `FINAL_RELEASE_AUDIT.md` (release gate), `USER_INPUT_REQUIRED.md` (what only you can supply).

---

## 1. Your understanding of the problem

> Cyber-fraud investigators often hold a network capture of email traffic that is cut short or encrypted. Packet tools show the packets, but the analyst must decide what is safe to conclude, which is manual and hard to repeat. A conclusion the evidence cannot support can weaken a case. The Government's PIB backgrounder (7 Oct 2025) cites over 17.82 lakh complaints under the national CFCFRMS cyber-fraud system; the period is not stated. That is a general cyber-fraud figure, not an email-specific one. How many cases involve email is not published, so we make no claim about that.

- **Source check (15 Oct 2026):** the PIB PDF `Curbing Cyber Frauds in Digital India` (7 October 2025) was re-opened. Its sentence reads: through CFCFRMS "financial institutions have been able to save more than ₹5,489 crore in over 17.82 lakh complaints". The reporting period is not given. So "cites over 17.82 lakh complaints" is accurate; "handled" or "reported this year" would not be. The figure is national and financial-fraud wide.
- **Do not use:** Maharashtra 5.16 lakh / ₹7,592 crore (press only), any email share.
- **Qualification:** "often" is our reasoning. No investigator was interviewed. Say "can" if you prefer.
- **Confidence:** Verified (statistic wording, product facts); Proposal ("often").

## 2. Estimated number of people/units affected in your target area

> No verified estimate. We have not found a defensible count of people or units for the target area, so we are not guessing. The first target is one supervised pilot unit, a Maharashtra cyber cell or forensic lab, with no partner yet agreed.

- **Why:** the earlier "about 50 district cyber police stations" figure came from one broadcaster report that could not be checked against the official directory (the site returned an error). It is removed. No replacement estimate is offered.
- **If the field accepts only a number:** enter `1` (the pilot-unit target) and keep the sentence above wherever text is allowed. Or ask the helpdesk what to enter when no verified estimate exists. Do **not** enter 17.82 lakh: it is a complaint count, not users or units.
- **Confidence:** Proposal. **Confirm** the entry.

## 3. Proposed solution

> NyaySaakshya is a working prototype for forensic triage of saved email-traffic captures (SMTP, IMAP, POP3). It reads a capture and produces evidence-linked findings and a report. Every fact carries one of six states: observed, inferred, unknown, ambiguous, incomplete or not observable. Each finding cites the packets it rests on. If the capture cannot support a score, it gives none and says why. The same capture and software give the same result and ID. It does not detect fraud, identify suspects, name an attacker or decrypt TLS.

- **Evidence:** README; `VALIDATION.md` (13,822 cited frames, 0 stream mismatches; 98/98 deterministic).
- **Do not add:** device-data analysis, suspect detection, live capture, financial-crime intelligence, any AI claim.
- **Confidence:** Verified.

## 4. Who will use or benefit from the solution?

| Option | Recommend | Reason |
|---|---|---|
| Government officials | **Tick** (direct users) | Intended users are cyber-cell and forensic-lab investigators and supervisors. None uses it yet. |
| Citizens | Optional, **indirect** only | Possible indirect benefit through sounder cyber-fraud cases. No citizen uses it. **Confirm.** |
| All others (Businesses/MSMEs, Women, Children, Students, Farmers, Rural, Urban, Healthcare, Educational) | **Do not tick** | No supported link. |

- **Confidence:** Proposal. **Confirm** the Citizens choice.

## 5. Current stage of solution

**Working Prototype** (nearest option on the form). Not Field Pilot or Ready to Deploy.

- **Evidence:** runs end to end locally on synthetic captures (re-run 14 Oct 2026); `DEPLOYMENT.md` classification B; no pilot, no authentication, no audit trail.
- **Confidence:** Verified (self-assessed against the evidence).

## 6. What makes the solution innovative?

> Packet tools show packets and fields. NyaySaakshya adds a rule: every statement must say how strongly the capture supports it, and the tool must abstain when it cannot. Six evidence states separate what was seen from what was inferred or cannot be known. A cut-off handshake is "incomplete", never "no encryption". A score is withheld when there is too little evidence. Reports carry the capture's SHA-256 and a reproducible assessment ID. It complements packet tools; it does not replace them.

- **Qualification:** we have not verified that no other tool does this. Do not write "first", "only" or "unique".
- **Confidence:** Verified (behaviour); Proposal (framing).

## 7. Technology/approach used

| Option | Recommend | Reason |
|---|---|---|
| **Mobile/web platform** | **Tick** | React web console and FastAPI service. |
| **Data analytics** | **Tick** | Rule-based analysis of parsed capture data and cross-session comparison. |
| Process innovation | Optional | The innovation is the evidence-bounded workflow. |
| **AI/ML** | **Do not tick** | An optional anomaly lane exists but is off by default and cannot change a finding, band, score or coverage (98 captures verified, VALIDATION 14.11). It gives no independent detection value we can claim. If a text box exists: "Optional anomaly signal, off by default, cannot change any finding." |
| All others | **Do not tick** | Not used. |
| Other (optional text) | "Network forensics: TShark protocol dissection and rule-based evidence reasoning" | Accurate. |

- **Confidence:** Verified (what is used). **Confirm** the AI/ML decision.

## 8. Key advantages

| Option | Recommend | Reason |
|---|---|---|
| New process/service model | **Tick** | Evidence-state workflow with abstention. |
| Other | **Tick**, type: "Evidence traceability, explicit uncertainty, reproducible reports" | Directly supported. |
| Lower cost, Faster, More accurate | **Do not tick** | Never measured. |
| Easier to use, Better government efficiency, Better citizen experience | **Do not tick** | Hypotheses for a pilot. |
| Scalable | **Do not tick** | Single-analyst prototype; SQLite concurrency defect open; no authentication. |
| More accessible, More inclusive | **Do not tick** | The Marathi report is an unreviewed machine draft and has not been tested. |
| Uses new technology, Environmentally sustainable | **Do not tick** | Not supported or not relevant. |

- **Confidence:** Proposal. **Confirm.**

## 9. Has the solution been tested or piloted?

Select **tested internally, not piloted** (or the nearest option). If the form is only Yes/No and asks about "tested", answer Yes and state "internal validation only" in field 10. Do not select anything that implies an external pilot.

- **Evidence:** 1,521 automated tests; 98 controlled captures. Both are **internal validation**, not an external pilot.
- **Confidence:** Verified.

## 10. Pilot/deployment details

> No external pilot and no real-world deployment. Internal validation only, on synthetic or lab-generated captures: 1,521 automated tests; 98 controlled captures, all giving the same result on repeat; 13,822 cited packets cross-checked against TShark with no mismatches. There is no real-world accuracy benchmark, no government approval, and no use on real case data. No partner has agreed. Proposed, not agreed: one supervised pilot in a Maharashtra cyber cell, after login, an audit log, encrypted storage and backups are built.

- **Evidence:** `VALIDATION.md`, `DEPLOYMENT.md`; blockers re-verified in `DEPLOYMENT_GO_NO_GO.md`.
- **Do not add:** users, interviews, customers, letters of support, funding, a live URL.
- **Confidence:** Verified.

## 11. Expected impact

> Expected, not yet measured: investigators spend less effort deciding what a capture can support, and cyber-fraud cases are less likely to rest on conclusions the evidence cannot bear. A supervised pilot would measure time to a first assessment, time to a finished report, share of findings with usable packet citations, correct handling of unresolved evidence, repeatability and supervisor confidence. No savings, speed, beneficiary or job figures are claimed. Supports SDG 16 (target 16.a, strengthening institutions that combat crime).

- **Evidence:** pilot measures from `SUBMISSION_EVIDENCE.md` section 9; SDG 16.a wording read at sdgs.un.org on 14 Oct 2026.
- **Confidence:** Proposal.

## 12. Standard six-slide presentation upload

Upload `submission/seva-innovation-challenge-2026/NyaySaakshya_Seva_Innovation_Challenge_2026.pptx` (about 0.12 MB; the portal accepts PDF, PPT, PPTX up to 15 MB; public guidelines say a single PPTX). Do not upload the `_PREVIEW.pdf`: it is a LibreOffice render with a substitute font.

- **Confidence:** Verified (size, six slides). The deck was inspected only in LibreOffice, **not in PowerPoint**: open it in PowerPoint and check each slide before uploading.

## 13. Prototype/demo link

**Leave blank** (optional per the FAQ), unless you record the synthetic demo and choose to share it as an unlisted video. Do not enter `secure-mail-scope-psi.vercel.app`: it serves a stale "SecureMailScope" build and its `/api/v1/health` returns 404, so no backend sits behind it.

## 14. Website/product link

**Leave blank.** The GitHub repository is private (confirmed with the GitHub CLI), so evaluators could not open it. Making it public is a separate decision and is not recommended before the deadline.

## 15. Consent and conflict-of-interest declaration

**Not answered here.** See below.

---

## Declarations that need you personally

Nothing below was answered on your behalf. Read each one on the portal and decide yourself.

| Declaration | What it means | What to verify first |
|---|---|---|
| Consent to verification | The organisers may verify your information and request supporting evidence during due diligence. | Every statement you enter can be backed. `SLIDE_CLAIM_AUDIT.md` lists the evidence. |
| Conflict of interest | Whether you have any relationship with organisers, evaluators or the bodies running the challenge that could influence evaluation. | Only you know. |
| Domicile | The individual (or one founder) must hold a domicile certificate of Maharashtra, Chhattisgarh, Dadra and Nagar Haveli and Daman and Diu, or Goa. With team size 1, that is you. | You hold a valid certificate, and from which state. Have the file ready if the portal asks. |
| IP status | Who owns the code. The repo has no licence file (README: "No license has been selected"). **Git history also shows another contributor: see the contributor flag in `FINAL_RELEASE_AUDIT.md`.** | No employer, college or funder has a claim. Confirm dependency licences before any procurement. |
| Regulatory dependencies | Approvals needed to use it. | Real captures can hold personal data. Use on real evidence would need the unit's own legal approval and controls that do not exist yet. State this plainly. Not legal advice. |
| Originality and single submission | One innovation, one primary sector. | You submit it nowhere else under another sector. |
| Identity / Aadhaar | Already verified on the portal. Name is from Aadhaar and cannot be edited. | The deck's name matches the portal spelling. |
| Final accuracy declaration | Whatever the form's text says. | Read the exact words before ticking. |

## Team profile

Replace the portal's project profile with the text in `PROFILE_FINAL_COPY.md`, and delete claims about device data, suspect activity, district cyber-cell adoption, Marathi/English readiness and tamper-evident case files.
