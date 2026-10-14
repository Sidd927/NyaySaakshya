# Portal application answers (final, paste-ready)

Final rebuild 15 October 2026 (Phase H). For **manual entry by the applicant**. Nothing here was entered into the portal, and the logged-in portal was never accessed.

**What is and is not known about the form**

- The Phase F brief's transcription of the portal screenshots lists the 15 fields below. The screenshots themselves were not available to this session as images. The list is not claimed to be the whole form.
- **Character limits and mandatory flags: UNKNOWN.** Every long answer therefore has a short version. Read the limit on the form and use the shortest version that fits.
- Public pages read on 15 Oct 2026 (`sevainnovationchallenge.in` home page with FAQ, `guidelines.html`, and the public profile-wizard code) add: a profile-stage "Solution maturity" list, and a **140-character** "In one line, what are you working on?" field. See `PHASE_H_RESEARCH_AND_EVALUATION.md`.

Labels: **Verified** (checked in the repo, by running it, or at a public source) | **Proposal** (our judgement) | **Confirm** (only you can decide or declare).

**Fixed facts (use exactly):** sector **Law and Order**; sub-theme **Cyber-Fraud, Digital Extortion and Financial-Crime Intelligence** (verified on the official page as Law and Order sub-theme 2; the portal showed it in sentence case); team size 1; applicant **Siddhant Hiralal Patil**; deadline 17 Oct 2026, 11:59 PM IST. Check the team-name spelling on the dashboard (the transcription shows `NYAYSAakshya` / `NYAYSAKSHYA`; the product is NyaySaakshya).

**Fit warning.** The sub-theme says "intelligence". NyaySaakshya does not produce intelligence, detect fraud, identify suspects, attribute an attacker, decrypt TLS or read message content. It supports the evidence-handling step. Never write otherwise.

---

## P. Profile-stage fields (if you are still asked)

| Field | Answer | Notes |
|---|---|---|
| Primary sector | Law and Order | Do not change. |
| Sub-theme | Cyber-Fraud, Digital Extortion and Financial-Crime Intelligence | As on the portal. |
| Solution maturity | See field 5 below | The public wizard lists: Idea stage (TRL 1-2); Concept validated (TRL 3-4); Working prototype (TRL 5-6); Pilot / field-tested (TRL 7); Market-ready / deployed (TRL 8-9). |
| In one line, what are you working on? (max 140) | Forensic triage of email-traffic captures: cites its packets and withholds a score when the evidence is too thin. | 113 characters. Alternative (108): Email-capture forensic triage: findings cite their packets, and no score is given when evidence is too thin. |

---

## 1. Your understanding of the problem

**Recommended answer** (799 characters):

> Investigators examining cyber-fraud cases can hold a network capture of email traffic. A capture can show less than it seems to: it may stop before a TLS handshake finishes; a server that never offers STARTTLS looks identical whether it does not support it or something removed the offer; and TLS 1.3 encrypts the server certificate, so a passive capture cannot show it. Reading too much into such evidence can undermine the finding built on it. Packet tools show the packets, but deciding what is safe to conclude is manual and hard to repeat. Context only: a Government of India PIB backgrounder (7 Oct 2025) cites over 17.82 lakh complaints in the national CFCFRMS cyber-fraud system (period not stated). That figure is not email-specific, and we make no claim about how many cases involve email.

**Short version** (335 characters):

> Investigators can hold a network capture of email traffic that is cut short, ambiguous or encrypted. Reading too much into it can undermine the finding built on it. Packet tools show packets; deciding what is safe to conclude is manual and hard to repeat. PIB cites over 17.82 lakh national cyber-fraud complaints (not email-specific).

- **Evidence:** failure modes from RFC 3207 (STARTTLS), RFC 8446 section 1.2 (TLS 1.3 encrypts handshake messages after ServerHello) and the prototype's validation record; the statistic is from the PIB PDF *Curbing Cyber Frauds in Digital India* (7 Oct 2025), re-read 15 Oct 2026: "financial institutions have been able to save more than ₹5,489 crore in over 17.82 lakh complaints". The period is not stated.
- **Dependency:** none, apart from your own comfort with "can hold" (no investigator was interviewed).
- **Warning:** do not say "email fraud" or imply the 17.82 lakh figure counts email cases. It is a national, financial-fraud-wide complaint count. Do not add the unverified Maharashtra 5.16 lakh / ₹7,592 crore figures.
- **Confidence:** Verified (sources, product facts); Proposal (framing).

## 2. Estimated number of people/units affected in your target area

**Recommended answer** (305 characters):

> No verified estimate. We have not found a defensible count of people or units in the target area, so we are not guessing. The first target is one supervised pilot unit (a Maharashtra cyber cell or forensic lab); no partner has agreed. The 17.82 lakh national complaint figure is context, not a user count.

**Short version** (89 characters):

> No verified estimate. First target: one supervised pilot unit; no partner has agreed yet.

**Decision path (no defensible number exists, so you choose):**

1. **Text accepted:** use the answer above. It is the honest entry.
2. **Number only:** enter `1` (the pilot-unit target) and put the sentence above in any text field. A bare `1` can be misread as "one affected unit", so prefer asking the helpdesk first (support@sevainnovationchallenge.in, +91 91377 78135): "What should I enter when no verified estimate exists?"
3. **Never enter:** 17.82 lakh (a complaint count, not users), a number of police stations (the earlier "about 50" rested on one broadcaster report that could not be checked against the official directory), or any beneficiary figure.

- **Confidence:** Proposal. **Confirm** the choice. Expect this field to cost some points; an invented figure could fail due diligence, which verifies claims.

## 3. Proposed solution

**Recommended answer** (672 characters):

> NyaySaakshya is a working prototype for forensic triage of saved email-traffic captures (SMTP, IMAP, POP3; PCAP or PCAPNG). It rebuilds the sessions with TShark and labels every fact as observed, inferred, unknown, ambiguous, incomplete or not observable. Each issue it reports cites the rule, the standard and the packets it rests on. If the capture cannot support a score (no session can be assessed, or fewer than half yield a conclusion), it says "Not scored" and gives the reason. The same capture and software give the same assessment ID. Reports are available as JSON, HTML and PDF. It does not detect fraud, identify suspects, attribute an attacker or decrypt TLS.

**Short version** (241 characters):

> A working prototype that reads saved email-traffic captures and reports what they do and do not establish. Each issue cites its packets; when evidence is too thin it gives no score and says why. It does not detect fraud or identify suspects.

- **Evidence:** README; `VALIDATION.md` (13,822 cited frames, 0 stream mismatches; 98 of 98 deterministic; pcapng check); `scoring.py` thresholds; reports exported 15 Oct.
- **Warning:** do not add device-data analysis, suspect detection, live capture, financial-crime intelligence, or any AI claim. None exists.
- **Confidence:** Verified.

## 4. Who will use or benefit from the solution?

| Option | Select? | Reason |
|---|---|---|
| Government officials | **Yes** (direct users) | Intended users are cyber-cell and forensic-lab investigators and supervisors. None uses it yet. |
| Citizens | Optional, indirect only | Possible indirect benefit through sounder cyber-fraud findings. No citizen uses it. **Confirm**; leaving it unticked is also defensible. |
| Other | Optional | Type "Forensic-lab analysts" only if the form does not count them as government officials. |
| Businesses/MSMEs, Women, Children, Students, Farmers, Rural communities, Urban residents, Healthcare professionals, Educational institutions | No | No supported link. |

- **Warning:** distinguish direct users (officials) from indirect beneficiaries. Do not tick groups to look broader.
- **Confidence:** Proposal. **Confirm.**

## 5. Current stage of solution

**Recommended: "Working prototype (TRL 5-6)"** if the form uses the public wizard's list, or "Working Prototype" if it uses plain names. Never "Pilot / field-tested" or "Market-ready / deployed".

- **Honest reading of the scale:** the system runs end to end, and it was validated on real mail-server software (Postfix, Dovecot, OpenSSL) in a lab and on synthetic captures. Strictly, validation in a *relevant operational environment* (TRL 5-6) has not happened, so a conservative reader could place it at TRL 4 ("Concept validated (TRL 3-4)").
- **Decision (Confirm):** choose "Working prototype" only if you are comfortable explaining "lab-validated, no external pilot" at due diligence. The text fields and the deck state exactly that. If you prefer the conservative option, "Concept validated (TRL 3-4)" is also true, and costs nothing in credibility.
- **Evidence:** runs end to end locally (re-run 15 Oct); `DEPLOYMENT.md` classification B.
- **Confidence:** Verified (state of the prototype); Confirm (which label).

## 6. What makes the solution innovative?

**Recommended answer** (596 characters):

> Packet tools show packets and fields. NyaySaakshya adds a rule: every statement must say how strongly the capture supports it, and the tool must abstain when it cannot. Six evidence states separate what was seen from what was inferred or cannot be known. An incomplete handshake is "incomplete", never "no encryption". A score is withheld when evidence is too thin. Reports carry the capture's SHA-256 and a reproducible assessment ID. In the documentation we reviewed (Wireshark, Zeek, NetworkMiner) we did not find per-fact evidence states; this is a design strength, not a claim of uniqueness.

**Short version** (247 characters):

> Every statement carries an evidence state, and the tool abstains (no score) when the capture cannot support one. Findings cite rule, standard and packets; the same capture gives the same assessment ID. A design strength, not a claim of uniqueness.

- **Evidence:** states in `evidence/states.py`; comparison basis in `PHASE_H_RESEARCH_AND_EVALUATION.md` (Wireshark, Zeek, NetworkMiner documentation read 15 Oct 2026).
- **Warning:** never write "first", "only" or "unique", or add a speed, cost or accuracy comparison. None was measured.
- **Confidence:** Verified (behaviour); Proposal (framing).

## 7. Technology/approach used

| Option | Select? | Reason |
|---|---|---|
| **Mobile/web platform** | **Yes** | React web console and FastAPI service. |
| **Data analytics** | **Yes** | Rule-based analysis of parsed capture data and cross-session comparison. |
| Process innovation | Optional | The novelty is the evidence-bounded workflow. |
| **AI/ML** | **No** | An optional anomaly lane exists but is off by default, cannot change a finding, band, score or coverage, and adds no detection the deterministic lane did not already make (98 captures, `VALIDATION.md` ML-1 to ML-5). Ticking it would mislead. If a text box exists: "Optional anomaly signal, off by default; it cannot change any finding." |
| IoT, Robotics, Drones, Blockchain, Hardware, Biotechnology, Advanced materials, Clean technology, Service innovation, Business/delivery model innovation, No specific technology | No | Not used or not applicable. |
| Other (text, optional) | Network protocol analysis (TShark) and rule-based evidence reasoning | 68 characters. |

- **Confidence:** Verified (what is used). **Confirm** the AI/ML decision: it is yours, but ticking it is not supported by the evidence.

## 8. Key advantages

| Option | Select? | Reason |
|---|---|---|
| New process/service model | **Yes** | Evidence-state workflow with deliberate abstention. |
| Other | **Yes**: Evidence traceability, explicit uncertainty, reproducible reports (65 characters) | Directly supported. |
| Lower cost, Faster, More accurate | No | Never measured. |
| Easier to use, Better citizen experience, Better government efficiency | No | Hypotheses for a pilot. |
| Scalable | No | Single-analyst prototype; SQLite concurrency defect open; no authentication. |
| More accessible, More inclusive | No | The Marathi report is an unreviewed machine draft and has not been tested. |
| Uses new technology, Environmentally sustainable | No | Not supported or not relevant. |

- **Confidence:** Proposal. **Confirm.**

## 9. Has the solution been tested or piloted?

Select **tested internally, not piloted** (or the nearest option). If the form is Yes/No about testing, answer Yes and write "internal validation only" in field 10. Do not select anything that implies an external pilot.

- **Evidence:** 1,521 automated tests; 98 controlled captures. Both are internal validation, not an external pilot. **Note:** a clean run on the committed baseline gives 1,520 passed and 1 failed (a code-freeze guard, not a behaviour test); the answers say "automated tests", never "passing". See `PHASE_H_CLAIM_AUDIT.md`.
- **Confidence:** Verified.

## 10. Pilot/deployment details

**Recommended answer** (607 characters):

> No external pilot and no real-world deployment. Internal validation only, on lab-generated or synthetic captures: 1,521 automated tests; 98 controlled captures (10 real Postfix/Dovecot sessions, 6 OpenSSL handshakes, 82 crafted in-project), all giving the same result on repeat; 13,822 cited packets cross-checked against TShark with no mismatches. There is no real-world accuracy benchmark, no government approval and no use on real case data. No partner has agreed. Proposed, not agreed: one supervised pilot in a Maharashtra cyber cell, after login, an audit log, encrypted storage and backups are built.

**Short version** (182 characters):

> No external pilot or deployment. Internal validation only (1,521 automated tests; 98 lab-generated captures). Proposed: one supervised pilot after security hardening; no partner yet.

- **Evidence:** `VALIDATION.md` lines 617-622 (composition and limits); `DEPLOYMENT.md`; `DEPLOYMENT_GO_NO_GO.md`.
- **Warning:** do not add users, interviews, customers, letters of support, funding, a live URL, or the phrase "evidence stays within the unit" as a present capability (it is a proposed design).
- **Confidence:** Verified.

## 11. Expected impact

**Recommended answer** (528 characters):

> Expected, not yet measured: investigators spend less effort deciding what a capture can support, and cyber-fraud findings are less likely to rest on conclusions the evidence cannot bear. A supervised pilot would measure time to a first assessment, time to a finished report, share of findings with usable packet citations, handling of unresolved evidence, repeat-run agreement and supervisor confidence. No savings, speed, beneficiary or job figures are claimed. Aligns with SDG 16 (target 16.a, institutions that combat crime).

**Short version** (262 characters):

> Expected, not yet measured: fewer cyber-fraud findings resting on conclusions the evidence cannot support. A supervised pilot would measure time to assess, time to report, citation quality and supervisor confidence. No savings or beneficiary figures are claimed.

- **Evidence:** pilot measures are proposals (`SUBMISSION_EVIDENCE.md` section 9); SDG 16.a wording read at sdgs.un.org on 14 Oct 2026.
- **Warning:** "expected" and "unmeasured" must stay in the text.
- **Confidence:** Proposal.

## 12. Standard six-slide presentation upload

Upload `submission/seva-innovation-challenge-2026/NyaySaakshya_Seva_Innovation_Challenge_2026.pptx` (about 0.2 MB; the portal reportedly accepts PDF, PPT, PPTX up to 15 MB; the public guidelines say "a single PowerPoint (.pptx)"). Do **not** upload the `_PREVIEW.pdf` (a LibreOffice render with a substitute font).

- **Dependency:** the deck was inspected only through LibreOffice, **not in PowerPoint**. Open it in PowerPoint, check all six slides, and decide whether to keep the speaker notes (they hold public sources only).
- **Confidence:** Verified (six slides, size); Confirm after the PowerPoint check.

## 13. Prototype/demo link

**Leave blank.** Optional per the FAQ. There is no working, safe, representative link: the old `secure-mail-scope-psi.vercel.app` serves a stale "SecureMailScope" build and its `/api/v1/health` returns 404, so no backend sits behind it; public deployment is NO-GO. Use only an **unlisted** video of the synthetic demo, and only after it has been recorded and inspected (none exists yet).

## 14. Website/product link

**Leave blank.** The GitHub repository is private (confirmed with the GitHub CLI 14 Oct), so evaluators could not open it. Do not make it public before the deadline: it contains research data and no licence.

## 15. Consent and conflict-of-interest declaration

**Not answered here. These are yours.** See the declarations table.

---

## 16. Other fields found in official materials

| Field or document | What to do | Source |
|---|---|---|
| Category (General or Women) | Already chosen at profile stage | FAQ |
| Identity document (Aadhaar, PAN, passport or driving licence; PDF/JPG/JPEG/PNG; max 5 MB) | Upload only if the form still asks after Aadhaar verification. Ask the helpdesk if unclear | FAQ |
| Domicile certificate | The guidelines require one for the individual. Upload if the form asks | Guidelines |
| IP status | **Confirm**: see the IP note below | Guidelines |
| Regulatory dependencies | **Confirm**: suggested facts below | Guidelines |
| Team details | One member, you. No teammate, mentor or qualification is invented | portal |

### IP and contributor note (facts only you can supply)

The repository's older history (`pre-rebrand-main`) shows a 29 Sep 2026 frontend commit by another GitHub account (`Dishita0526`, 48 files) and a first commit by `Sidd_927`. You have explained that Dishita is a friend who helped with some frontend work and is not a member of this team. **She is not added as a team member.** What you still need to answer factually, in your own words:

1. Did she agree that her frontend contributions may be included in this project and submitted by you? In writing is best.
2. Did she assign or license her contribution to you, or does she retain rights? Is any of her code from another source?
3. Should her help be acknowledged (a line in the IP statement or deck)?
4. Does any employer, college or funder have a claim on the code?
5. `Sidd_927`: is that your other account? (If yes, no issue.)

The repository has no licence file, so by default you hold copyright on your own code and no one has a licence to reuse it. Components are open source (TShark GPL-2.0-or-later as a separate program; FastAPI, pydantic, React MIT; others BSD, Apache-2.0, ISC; fonts OFL). This is not legal advice.

### Suggested regulatory-dependency facts

Real captures may contain personal data. Use on real evidence would need the unit's own legal approval and security controls that do not exist yet (no authentication, audit log or encrypted storage). The prototype is passive and offline, uses synthetic captures in all validation, and records a SHA-256 for traceability, not legal custody; no admissibility claim is made.

---

## Declarations that need you personally

Nothing below was answered on your behalf.

| Declaration | What it means | Verify first |
|---|---|---|
| Consent to verification | The organisers may verify your information and ask for supporting evidence during due diligence (6 to 10 Nov). | Each statement can be backed; `PHASE_H_CLAIM_AUDIT.md` lists the evidence. |
| Conflict of interest | Whether you have a relationship with organisers, evaluators or the bodies running the challenge that could influence evaluation. | Only you know. |
| Domicile | Maharashtra, Chhattisgarh, Dadra and Nagar Haveli and Daman and Diu, or Goa certificate for the individual. | You hold a valid certificate; have the file ready. |
| IP status | Who owns the code (see the IP note). | Contributor permission and any third-party claim. |
| Regulatory dependencies | Approvals needed to use it. | See suggested facts. Not legal advice. |
| Originality and single submission | One innovation, one primary sector. | You submit this nowhere else under another sector. |
| Identity / Aadhaar | Already verified. | Name matches the deck. |
| Final accuracy declaration | The form's own text. | Read it first. |
