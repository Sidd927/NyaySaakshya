# Portal field by field: final manual-entry guide

Definitive guide, 15 October 2026 (final execution pass). Enter these by hand, in portal order. **I never opened, edited or submitted the portal.**

**How to use**

- The field list and option labels come from the applicant's description of the portal screenshots (16 fields; testing options "No / Testing in progress / Yes - One Pilot / Yes - multiple pilots / Currently deployed"). The screenshot images themselves were not available to this session, so **mandatory markers and character limits are UNKNOWN to me**: read the asterisks and any counters on your screen. The only mandatory/optional facts I can cite come from the official FAQ: the presentation upload is mandatory; the demo and website links are optional.
- Where a limit is not visible, use the **short fallback**. Never exceed a counter you can see.
- Same wording as `PORTAL_APPLICATION_ANSWERS.md` (rationale) and `PROFILE_FINAL_COPY.md` (profile). If they ever differ, this file wins.
- Fixed facts: sector **Law and Order**; sub-theme **Cyber-Fraud, Digital Extortion and Financial-Crime Intelligence**; individual applicant, team size 1; Siddhant Hiralal Patil; deadline 17 Oct 2026, 11:59 PM IST.
- Statements by the applicant (consent agreement, no relationship with organisers or jury, individual submission, Dishita's role) are **applicant-provided, not independently verified**.

**What NyaySaakshya is not** (never write otherwise): a fraud detector, a suspect or attacker identifier, a TLS decryptor, a reader of email content, a device-data analyser; it has no government users, no completed pilot, no approval, and is not production-ready.

---

## 1. Your understanding of the problem
Mandatory: UNKNOWN. Type: text.

**Final text** (799 characters, portal limit UNKNOWN):

> Investigators examining cyber-fraud cases can hold a network capture of email traffic. A capture can show less than it seems to: it may stop before a TLS handshake finishes; a server that never offers STARTTLS looks identical whether it does not support it or something removed the offer; and TLS 1.3 encrypts the server certificate, so a passive capture cannot show it. Reading too much into such evidence can undermine the finding built on it. Packet tools show the packets, but deciding what is safe to conclude is manual and hard to repeat. Context only: a Government of India PIB backgrounder (7 Oct 2025) cites over 17.82 lakh complaints in the national CFCFRMS cyber-fraud system (period not stated). That figure is not email-specific, and we make no claim about how many cases involve email.

**Short fallback** (335 characters, portal limit UNKNOWN):

> Investigators can hold a network capture of email traffic that is cut short, ambiguous or encrypted. Reading too much into it can undermine the finding built on it. Packet tools show packets; deciding what is safe to conclude is manual and hard to repeat. PIB cites over 17.82 lakh national cyber-fraud complaints (not email-specific).

- **Evidence:** RFC 3207 (STARTTLS stripping), RFC 8446 section 1.2 (TLS 1.3 encrypts post-ServerHello handshake messages), `VALIDATION.md` (incomplete and ambiguous states). 17.82 lakh: PIB backgrounder *Curbing Cyber Frauds in Digital India*, 7 Oct 2025, re-read: "financial institutions have been able to save more than ₹5,489 crore in over 17.82 lakh complaints" through CFCFRMS.
- **Caveats:** the figure is a national CFCFRMS cyber-fraud context number; **period not stated; not email-specific; not a count of affected users, email cases or target-area units.** "can hold" is deliberate: no investigator was interviewed.

## 2. Estimated number of people / units affected in your target area
Mandatory: UNKNOWN. Type: text or number (UNKNOWN).

**Final text** (305 characters, portal limit UNKNOWN):

> No verified estimate. We have not found a defensible count of people or units in the target area, so we are not guessing. The first target is one supervised pilot unit (a Maharashtra cyber cell or forensic lab); no partner has agreed. The 17.82 lakh national complaint figure is context, not a user count.

**Short fallback** (89 characters, portal limit UNKNOWN):

> No verified estimate. First target: one supervised pilot unit; no partner has agreed yet.

- **If only a number is accepted (unresolved portal ambiguity):** do not invent one. Ask the helpdesk first (support@sevainnovationchallenge.in, +91 91377 78135): "What do I enter when no verified estimate exists?" Only if forced to proceed without a reply, enter `1` and state in fields 3, 10 and 11 that 1 is the proposed first pilot unit, **not** an affected-population estimate. Never enter 17.82 lakh, a police-station count or a beneficiary figure.
- **Evidence:** no defensible, scoped estimate exists; the earlier "about 50 district cyber police stations" rested on one broadcaster report and could not be checked against the official directory.

## 3. Proposed solution
Mandatory: UNKNOWN. Type: text.

**Final text** (672 characters, portal limit UNKNOWN):

> NyaySaakshya is a working prototype for forensic triage of saved email-traffic captures (SMTP, IMAP, POP3; PCAP or PCAPNG). It rebuilds the sessions with TShark and labels every fact as observed, inferred, unknown, ambiguous, incomplete or not observable. Each issue it reports cites the rule, the standard and the packets it rests on. If the capture cannot support a score (no session can be assessed, or fewer than half yield a conclusion), it says "Not scored" and gives the reason. The same capture and software give the same assessment ID. Reports are available as JSON, HTML and PDF. It does not detect fraud, identify suspects, attribute an attacker or decrypt TLS.

**Short fallback** (241 characters, portal limit UNKNOWN):

> A working prototype that reads saved email-traffic captures and reports what they do and do not establish. Each issue cites its packets; when evidence is too thin it gives no score and says why. It does not detect fraud or identify suspects.

- **Evidence:** README; `VALIDATION.md` (13,822 cited frames, 0 stream mismatches; 98/98 deterministic; pcapng check); `scoring.py` (withhold rules); JSON/HTML/PDF reports exported on 14 and 15 Oct.
- **Caveats:** "each issue" (not "every finding") because only OBSERVED_ISSUE findings are verified to cite a frame; no claim of fraud detection, suspect identification, attribution, decryption, content reading or device analysis.

## 4. Who will use or benefit from the solution?
Mandatory: UNKNOWN. Type: checkboxes.

| Option | Tick? | Why |
|---|---|---|
| **Government officials** | **Yes** | Intended direct users: cyber-cell and forensic-lab investigators and supervisors. None uses it yet. |
| Citizens | **Optional (indirect only)** | Possible indirect benefit via sounder cyber-fraud findings; no citizen uses it. Leaving it unticked is equally defensible. |
| Farmers, Women, Children, Students, Rural communities, Urban residents, Businesses/MSMEs, Healthcare professionals, Educational institutions | **No** | No supported link. |
| Other | **No** (or type "Forensic-lab analysts" only if they are not covered by Government officials) | |

## 5. Current stage of solution
Mandatory: UNKNOWN. Type: dropdown or radio.

**Select: Working prototype.** (Never "Pilot", "Field pilot" or "Ready to deploy".)
- **Evidence:** runs end to end locally (re-run 15 Oct); `DEPLOYMENT.md` classification B; validated on lab-generated captures only.
- **Caveat:** if the portal shows a TRL label beside it (the public wizard listed "Working prototype (TRL 5-6)"), be ready to explain "lab-validated, no external pilot"; the conservative alternative "Concept validated (TRL 3-4)" is also true.

## 6. What makes your solution innovative?
Mandatory: UNKNOWN. Type: text.

**Final text** (596 characters, portal limit UNKNOWN):

> Packet tools show packets and fields. NyaySaakshya adds a rule: every statement must say how strongly the capture supports it, and the tool must abstain when it cannot. Six evidence states separate what was seen from what was inferred or cannot be known. An incomplete handshake is "incomplete", never "no encryption". A score is withheld when evidence is too thin. Reports carry the capture's SHA-256 and a reproducible assessment ID. In the documentation we reviewed (Wireshark, Zeek, NetworkMiner) we did not find per-fact evidence states; this is a design strength, not a claim of uniqueness.

**Short fallback** (247 characters, portal limit UNKNOWN):

> Every statement carries an evidence state, and the tool abstains (no score) when the capture cannot support one. Findings cite rule, standard and packets; the same capture gives the same assessment ID. A design strength, not a claim of uniqueness.

- **Evidence:** `evidence/states.py` (six states); the Wireshark, Zeek and NetworkMiner documentation read on 15 Oct 2026.
- **Caveats:** never "first", "only" or "unique"; no speed, cost or accuracy comparison (none measured).

## 7. Technology / approach used
Mandatory: UNKNOWN. Type: checkboxes.

| Option | Tick? | Why |
|---|---|---|
| **Mobile / web platform** | **Yes** | React web console and FastAPI service. |
| **Data analytics** | **Yes** | Rule-based analysis of parsed capture data and cross-session comparison. |
| AI / ML | **No (leave unticked)** | The optional anomaly lane is off by default, cannot change a finding, band, score or coverage, and adds no detection the deterministic lane did not already make (98 captures; `VALIDATION.md` ML-1 to ML-5). |
| IoT, Robotics, Drones, Blockchain, Hardware, Biotechnology, Advanced materials, Clean technology, No specific technology | No | Not used. |
| Process innovation | Optional | The novelty is the evidence-bounded workflow. |
| Service innovation, Business/delivery model innovation | No | Not demonstrated. |
| Other (text, optional) | "Network protocol analysis (TShark) and rule-based evidence reasoning" (68 characters) | Accurate. |

## 8. Key advantages of your solution
Mandatory: UNKNOWN. Type: checkboxes.

| Option | Tick? | Why |
|---|---|---|
| **New process / service model** | **Yes** | Evidence-state workflow with deliberate abstention. |
| **Other** | **Yes**, type: "Evidence traceability, explicit uncertainty, reproducible reports" (65 characters) | Directly supported. |
| Lower cost, Faster, More accurate | No | Never measured. |
| Easier to use, Better citizen experience, Better government efficiency | No | Hypotheses for a pilot. |
| Scalable | No | Single-analyst prototype; no authentication; open SQLite concurrency defect. |
| More accessible, More inclusive | No | The Marathi report is an unreviewed machine draft, untested. |
| Uses new technology, Environmentally sustainable | No | Not supported or not relevant. |

## 9. Has the solution been tested or piloted?
Mandatory: UNKNOWN. Type: dropdown or radio. Options: No / Testing in progress / Yes - One Pilot / Yes - multiple pilots / Currently deployed.

**Select: Testing in progress.**
- **Why not the others:** "No" would deny 1,521 automated tests and 98 controlled captures; "Yes - One Pilot", "Yes - multiple pilots" and "Currently deployed" would claim a pilot or deployment that does not exist.
- **Internal validation vs pilot:** internal validation is the author running tests on lab-generated captures. A pilot is a supervised trial by real users on real cases. There has been none. "Testing in progress" can be misread as an external trial, so field 10 starts by saying there is no external pilot.
- **Evidence:** 1,521 automated tests (a clean run on the final branch passes all 1,521; one stale code-freeze guard was re-baselined, see `FINAL_RELEASE_AUDIT.md`); 98 controlled captures.

## 10. Pilot / deployment details
Mandatory: UNKNOWN. Type: text.

**Final text** (646 characters, portal limit UNKNOWN):

> No external pilot and no real-world deployment. Internal validation only, on lab-generated or synthetic captures: 1,521 automated tests; 98 controlled lab captures (10 sessions on real Postfix/Dovecot software, 6 OpenSSL handshakes, 82 crafted in-project; no real-world traffic), all giving the same result on repeat; 13,822 cited packets cross-checked against TShark with no mismatches. There is no real-world accuracy benchmark, no government approval and no use on real case data. No partner has agreed. Proposed, not agreed: one supervised pilot in a Maharashtra cyber cell, after login, an audit log, encrypted storage and backups are built.

**Short fallback** (182 characters, portal limit UNKNOWN):

> No external pilot or deployment. Internal validation only (1,521 automated tests; 98 lab-generated captures). Proposed: one supervised pilot after security hardening; no partner yet.

- **Evidence:** `VALIDATION.md` lines 617-622 (composition: 10 sessions on real Postfix/Dovecot software in a lab, 6 OpenSSL handshakes, 82 crafted by in-project generators; no real-world traffic); `DEPLOYMENT.md`; `DEPLOYMENT_GO_NO_GO.md`.
- **Caveats:** no users, interviews, customers, letters of support, funding or live URL; local-only processing is a proposed design, not a validated deployment.

## 11. Expected impact
Mandatory: UNKNOWN. Type: text.

**Final text** (528 characters, portal limit UNKNOWN):

> Expected, not yet measured: investigators spend less effort deciding what a capture can support, and cyber-fraud findings are less likely to rest on conclusions the evidence cannot bear. A supervised pilot would measure time to a first assessment, time to a finished report, share of findings with usable packet citations, handling of unresolved evidence, repeat-run agreement and supervisor confidence. No savings, speed, beneficiary or job figures are claimed. Aligns with SDG 16 (target 16.a, institutions that combat crime).

**Short fallback** (262 characters, portal limit UNKNOWN):

> Expected, not yet measured: fewer cyber-fraud findings resting on conclusions the evidence cannot support. A supervised pilot would measure time to assess, time to report, citation quality and supervisor confidence. No savings or beneficiary figures are claimed.

- **Evidence:** pilot measures are proposals (`SUBMISSION_EVIDENCE.md` section 9); SDG 16.a wording read at sdgs.un.org.
- **Caveats:** "expected" and "not yet measured" must stay; no savings, speed, beneficiary, adoption or job figures.

## 12. Standard six-slide presentation upload
**Mandatory: YES** (official FAQ: the pitch presentation is a required document). Accepted types reportedly PDF, PPT, PPTX, up to 15 MB (applicant's description).

**Upload:** `submission/seva-innovation-challenge-2026/NyaySaakshya_Seva_Innovation_Challenge_2026.pptx` (six slides, about 0.23 MB). Do **not** upload `..._PREVIEW.pdf` (a LibreOffice render with a substitute font).
- **Caveat:** the deck was checked in LibreOffice (all six slides, plus a wider-font stress render) and, for slide 1, macOS Quick Look. It has **never been opened in PowerPoint**: do that before uploading.

## 13. Prototype / Demo Link
**Optional** (official FAQ). **Leave blank.** No safe, working, representative link exists: public deployment is NO-GO; the old `secure-mail-scope-psi.vercel.app` is a stale "SecureMailScope" build with no backend (not acceptable). A demo video would be acceptable only if it is recorded and inspected first; none exists.

## 14. Website / product link
**Optional** (official FAQ). **Leave blank.** The repository is private, so evaluators could not open it; do not make it public before the deadline.

## 15. Compliance consent
Applicant-confirmed (he agrees with the statement shown). **You tick it yourself**, after reading its exact wording. Make sure every part that applies is true for you: accuracy, eligibility, originality, documents, and the right to submit the code and assets.
- **Unresolved fact that could make the IP/right-to-submit part unsafe:** see "IP and permission" below.

## 16. Relationship with the organisers or jury
Applicant states: **No** (not related to, employed by, or professionally linked with the organisers or jury). **Select No**, on that applicant statement only (not independently verified). You tick it yourself.

---

## IP and permission (resolve before ticking field 15)

Team size 1 and commit authorship do not establish ownership. Dishita is a friend who helped with some frontend work and is **not** a team member; she is not added to the team. Permission to submit contributed code and legal ownership are separate from team membership. The repository does not show any assignment or licence, and I have invented none.

Facts only you can supply:
1. Did she agree her frontend contributions may be included in this project and submitted by you? A message or email from her is enough as a record; if you have not asked, one message resolves it.
2. Did she assign or license the work to you, or does she keep rights? Is any of it copied from elsewhere?
3. Should she be acknowledged (for example one line in the IP answer)?
4. Does any employer, college or funder have a claim on the code?

If you can truthfully say yes to 1 and no to 4, you may tick the consent as applicant-confirmed. If you are unsure, do not tick it yet: ask her first.

## Applicant-only checklist

1. Domicile certificate (Maharashtra, Chhattisgarh, DNH and DD, or Goa) and identity document ready; upload if the form asks.
2. Name and team-name spelling match the portal (the portal shows the team name in capitals; the product is NyaySaakshya).
3. IP permission question above answered truthfully.
4. Open the PPTX in PowerPoint and check all six slides.
5. Read each field's limit and mandatory marker; use the short fallbacks where needed.
6. Paste fields 1 to 11, make selections as above, upload the PPTX, leave 13 and 14 blank.
7. Tick fields 15 and 16 yourself after reading the exact wording.
8. Save as draft, re-read once, then click Submit yourself. Save the dashboard confirmation.

## Unresolved items

- **Portal ambiguity:** whether field 2 accepts text; helpdesk question above.
- **Applicant fact:** IP permission (above).
- **Not verified:** mandatory markers and character limits (screenshots unavailable to me); the exact consent wording.
