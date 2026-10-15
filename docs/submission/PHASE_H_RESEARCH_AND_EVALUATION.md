# Phase H research and evaluation

Researched 15 October 2026 (all "accessed" dates below are 15 Oct 2026 unless stated). Method: pages were opened and read directly (browser or `curl` plus text extraction); two search-engine summaries were used only to find sources and every claim below was re-checked at the source unless marked otherwise. The applicant's logged-in portal was **not** accessed.

**Labels.** VERIFIED = read at the source. SECONDARY = press or third party. HYPOTHESIS = our reasoning. UNKNOWN = could not be established.

---

## 1. Official Maharashtra-zone requirements

Sources: **S1** home page https://www.sevainnovationchallenge.in/ (includes the FAQ, sector data and timeline graphic); **S2** guidelines https://www.sevainnovationchallenge.in/guidelines.html. `faq.html` returns HTTP 404; the FAQ is on S1. Neither page carries a publication date.

| Requirement | What the source says | Source | Status |
|---|---|---|---|
| Deadline | "Last date to apply: 17 October 2026." Timeline graphic: application closure "17 Oct, 11:59 PM" | S1 | VERIFIED |
| Who may apply | Individuals, students, teams, startups, companies, institutions. "Individuals, students and informal teams may apply without a registered company" | S1, S2 | VERIFIED |
| Domicile | "An individual or any one of the founders of an entity should possess a Domicile certificate of either one of the States of Maharashtra, Chhattisgarh, Dadra and Nagar Haveli and Daman and Diu and Goa." FAQ: "Applicants must refer to the eligibility guidelines" | S2, S1 | VERIFIED (what, not whether the applicant has one) |
| Individual vs team | FAQ: apply individually or as a team; "up to five core team members, including the team lead"; team lead cannot be changed later | S1 | VERIFIED |
| Sector fit | "The solution should align with one of the 10 sectors and demonstrate a credible problem-solution fit." One innovation, one primary sector; duplicates "will be disqualified after verification" | S2 | VERIFIED |
| Sector list | Agriculture; **Law and Order**; Women and Child; Urban Development; Health and Medical; Defence; Sustainability; Infrastructure and Mobility; Emerging Technologies (AI, Blockchain and Others); Education and Employability; Other | S1 | VERIFIED |
| Law and Order sub-themes | 1 Missing persons, trafficking and inter-district case matching; **2 Cyber-Fraud, Digital Extortion and Financial-Crime Intelligence**; 3 Drug-network tracking and youth protection; 4 Predictive public-safety, emergency response and beat intelligence; 5 Organised crime and cross-agency intelligence integration. All "Open for all" | S1 page source (`SECTOR_DETAILS`) | VERIFIED. Caution: the same page's profile-wizard data (`SECTORS`) is misaligned (it lists health sub-themes under Law and Order), so the wizard is indicative only |
| Disclosures | "Applicants should disclose the current stage of development, prototype status, pilots, users/beneficiaries/customers, validation evidence, IP status and regulatory dependencies." | S2 | VERIFIED |
| Consent | "Applicants should consent to verification of submitted information and permit the organizers to seek supporting evidence during due diligence." Finalists must be available for the final stage | S2 | VERIFIED |
| Submission format | "Every application is submitted as a single PowerPoint (.pptx) presentation, prepared using the official Seva First template" | S2 | VERIFIED |
| Slide structure | Six slides: title and applicant snapshot; problem; solution and innovation; feasibility and implementation; impact and scalability; team/individual and support required | S1 FAQ | VERIFIED |
| Format and size limit | FAQ: "Please follow the file format and size limit displayed on the application portal at the time of upload." The applicant reports PDF, PPT, PPTX up to 15 MB | S1; applicant | Portal limit UNKNOWN (applicant-reported; not independently seen) |
| Presentation mandatory | "Is uploading a pitch presentation mandatory? Yes. The applicant manual lists the pitch presentation as a required document." | S1 | VERIFIED |
| Prototype/demo and website links | "You can provide a prototype/demo link or website/product link, where available. These links are listed as optional in the applicant manual." | S1 | VERIFIED: **optional** |
| Live deployment | No source requires a live deployment | S1, S2 | VERIFIED (absence) |
| Applicant manual | Referred to by the FAQ; no public copy found | S1 | UNKNOWN |
| Required documents | Identity document (Aadhaar, PAN, passport or driving licence; PDF/JPG/JPEG/PNG; max 5 MB); Aadhaar verification before final submission; name comes from Aadhaar and cannot be edited | S1 | VERIFIED |
| Application form fields | Not published. FAQ says to prepare: applicant details, innovation and sector information, problem statement ("who is affected, and the estimated number of people or organisations impacted"), proposed solution ("what makes it innovative, the technology or approach used, its key advantages, the intended beneficiaries, and its expected impact"), pilot/testing/user details, team details, pitch presentation. The applicant's transcription lists 15 fields | S1; applicant | Field list partly VERIFIED; limits and mandatory flags UNKNOWN |
| Profile-stage fields | Public wizard code: "Solution maturity" (options below), "In one line, what are you working on?" (**max 140 characters**), sector, sub-theme, division/district | S1 page source | VERIFIED in the public code; the live portal may differ |
| Stage options | Idea stage (TRL 1-2); Concept validated (TRL 3-4); **Working prototype (TRL 5-6)**; Pilot / field-tested (TRL 7); Market-ready / deployed (TRL 8-9) | S1 page source | VERIFIED (wizard); live form UNKNOWN |
| Edits | Draft can be saved; edits allowed until the deadline, after which applications are locked | S1 | VERIFIED |
| Conflicts of interest | Evaluators declare theirs. Whether applicants must declare one is UNKNOWN from public pages; the applicant reports a conflict-of-interest declaration on the form | S1; applicant | Applicant-reported |
| Evaluation stages | "Administrative scrutiny, then two independent online evaluations, technical and impact assessment, finalist validation, and a final Grand Jury." No scoring rubric, criteria or weights | S1 | VERIFIED stages; rubric UNKNOWN |
| Timeline | Eligibility screening 18 Oct; assessment 19-29 Oct; consolidation 30 Oct-5 Nov; selected-applicant communication and due diligence 6-10 Nov; orientation 11-13 Nov; jury onboarding 14-15 Nov; **online presentations 16-25 Nov**; score consolidation 26-27 Nov; semifinalist shortlisting 28 Nov; **final presentations 9 Dec at Nagpur** | S1 timeline graphic (`assets/timeline.png`) | VERIFIED. Conflict: press says Nagpur on 7 Dec (see section 6) |
| Awards | About 200 exhibition finalists, 50 awardees; each winner eligible for a work order of up to ₹10 lakh "subject to technical and financial evaluation, successful due diligence, and applicable programme approvals" | S1 | VERIFIED |

### National portal

https://sevafirst.mic.gov.in/ (and `/timeline`) is the **South Zone** edition (Andhra Pradesh, Karnataka, Kerala, Tamil Nadu, Telangana and others), run through NITs and IISc, for student ideation. It is a different programme from the Maharashtra zone. Its stated common framework is "relevance, originality, feasibility, cost, impact, scalability and quality of solution" (`/timeline`). **It is not a Maharashtra-zone rule** and is used here only as a hypothesis about what the same programme family values.

---

## 2. What evaluators reward

| Evidence | Kind | Content |
|---|---|---|
| Maharashtra FAQ | **Explicit, official** | Stages only (above). Evaluators declare conflicts. Applicants should disclose stage, prototype status, pilots, users, validation evidence, IP, regulatory dependencies. The six-slide structure |
| Maharashtra guidelines | **Explicit, official** | "credible problem-solution fit" within one sector; consent to due diligence |
| sevafirst.mic.gov.in `/timeline`, `/` | Official, **different edition** | Relevance, originality, feasibility, cost, impact, scalability, quality of solution (timeline); problem clarity, originality, feasibility, cost, impact, scalability (home FAQ) |
| Free Press Journal, updated 24 Sep 2026, "'Seva First Innovation Challenge' Opens Applications With ₹5-Crore Prize Pool…" | SECONDARY (press) | Assessors weigh "problem relevance, innovation, and technological maturity, along with impact, scalability, implementation capability, and deployment potential"; 1,500 to 2,000 applications expected; about 20 finalists per sector. Not an official rubric |
| Previous editions, finalist or winner decks | none found | A search found none; this appears to be the first edition (launch late Sep 2026) |

**Reasoned hypotheses (not official criteria):**

1. A concrete, checkable failure mode beats a broad statistic. (Slide 2 now leads with three failure modes.)
2. Honest maturity helps at due diligence (6-10 Nov), where claims are verified; overstatement is a rejection risk. The stage options carry TRL labels, so "working prototype" must be backed by evidence.
3. The jury stage involves presenting and demonstrating (press: "present and demonstrate"; official timeline: online presentations 16-25 Nov), so a reliable local synthetic demo matters more than a public link.
4. A specific, small ask (mentorship, one supervised pilot, IP/testing guidance) reads as feasible.
5. Fit risk: the sub-theme says "financial-crime intelligence". NyaySaakshya is an evidence-handling tool, not an intelligence system. Stating this plainly is safer than stretching it.
6. Competition is broad: roughly 200 finalists from 1,500-2,000 applications (press estimate) across 10 sectors.

---

## 3. Problem research (primary sources preferred)

| Claim supported | Source, publisher, date | URL | Notes |
|---|---|---|---|
| Over 17.82 lakh complaints in the national CFCFRMS cyber-fraud system; period not stated | *Curbing Cyber Frauds in Digital India*, PIB (Government of India), 7 Oct 2025 | https://static.pib.gov.in/WriteReadData/specificdocs/documents/2025/oct/doc2025107659501.pdf | Re-read 15 Oct: "financial institutions have been able to save more than ₹5,489 crore in over 17.82 lakh complaints". National, financial-fraud wide, **not email-specific**. The PIB release page itself returned HTTP 403 on 14 Oct |
| STARTTLS can be defeated by an active attacker deleting the "250 STARTTLS" response; opportunistic TLS | RFC 3207, IETF, Feb 2002 | https://datatracker.ietf.org/doc/html/rfc3207 | Primary technical standard |
| Cleartext mail access and submission should be discouraged; prefer Implicit TLS; TLS 1.2+ required | RFC 8314, IETF, Jan 2018 | https://datatracker.ietf.org/doc/html/rfc8314 | Primary |
| In TLS 1.3 "all handshake messages after the ServerHello are now encrypted" (so a passive capture cannot show the certificate) | RFC 8446, IETF, Aug 2018 | https://datatracker.ietf.org/doc/html/rfc8446 | Primary; supports slide 2 row 3 |
| Wireshark can decrypt TLS only "when appropriate secrets are provided" (key log file; RSA key does not work with TLS 1.3 or (EC)DHE) | Wireshark Wiki, "TLS" | https://wiki.wireshark.org/TLS | Primary documentation. The page does not state "cannot decrypt without keys" in so many words; the deck no longer says "only if" |
| Guidance on TLS configuration and use | NIST SP 800-52 Rev. 2, Aug 2019 | https://csrc.nist.gov/pubs/sp/800/52/r2/final | The standard cited by rule `SEC-PLAIN-001`. Section 3.1 text itself not re-read in Phase H |
| Email transmission security should use TLS | NIST SP 800-177 Rev. 1 "Trustworthy Email", Feb 2019 | https://csrc.nist.gov/pubs/sp/800/177/r1/final | Abstract read |
| Forensic process (collection, examination, analysis, reporting); record a message digest of original data before copying and verify afterwards | NIST SP 800-86, Aug 2006 | https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-86.pdf | Text extracted and read (digest passage near "message digest"). Old (2006) |
| The Schedule certificate under section 63(4) of the Bharatiya Sakshya Adhiniyam, 2023 asks for the hash value of the electronic record and the algorithm (SHA1, SHA256, MD5, other) | Bharatiya Sakshya Adhiniyam, 2023 (No. 47 of 2023), Gazette of India via MHA | https://www.mha.gov.in/sites/default/files/2024-04/250882_english_01042024_0.pdf | Read in the Gazette PDF. **NyaySaakshya does not produce this certificate and makes no admissibility claim.** It records a SHA-256 per capture, which is the kind of value the form asks for |
| SMTP security extensions are unevenly deployed; "favor failing open"; network attackers caused cleartext delivery in some countries | Durumeric et al., "Neither Snow Nor Rain Nor MITM…", ACM IMC 2015 | https://zakird.com/papers/mail.pdf (abstract read 14 Oct 2026) | Abstract only; general mail study, not India or fraud specific. Stale (2015) |
| Cyber forensic-cum-training laboratories exist across 33 States and UTs (CCPWC) | PIB backgrounder above | as above | Context only |
| How Indian cyber cells handle email-traffic captures in practice | **no primary source found** | | **UNKNOWN.** The operational premise (investigators hold cut-off or encrypted captures) is a HYPOTHESIS; no investigator was interviewed |
| Responsible handling of sensitive data | The Digital Personal Data Protection Act, 2023 exists; **not analysed** in Phase H | | UNKNOWN. The deck makes no data-protection claim and states that real captures need the unit's own legal approval |

Statistics are not turned into an email-specific market size anywhere. The unverified figures withdrawn earlier (Maharashtra 5.16 lakh and ₹7,592 crore, 24,02,579, 29.44 lakh, "41,405 servers in 193 countries", "about 50 district cyber police stations") remain excluded.

---

## 4. Competitor and differentiation audit

Basis: product documentation read on 15 Oct 2026. Absence from a page I read is **not** proof of absence from the product. "Evidence states" and "abstention" are NyaySaakshya's terms; a tool may do something similar under other names.

| Tool | Verified capabilities (documentation) | What the pages read do not claim | NyaySaakshya's corresponding capability | Source | Confidence / uncertainty |
|---|---|---|---|---|---|
| **Wireshark** | Packet dissection; Expert Information with levels Chat, Note, Warn, Error, framed as hints ("doesn't necessarily indicate a problem"); TLS decryption when secrets are supplied | Per-fact evidence states; a graded verdict with deliberate abstention; reproducible assessment IDs | Per-fact state, cited rule + standard + frame, withheld score, assessment ID | Wireshark User's Guide, Expert Information (https://www.wireshark.org/docs/wsug_html_chunked/ChAdvExpert.html); TLS wiki | Medium. Wireshark is far broader; NyaySaakshya is narrow |
| **Zeek** (SMTP log) | `smtp.log` records a `tls` boolean: "Indicates that the connection has switched to using TLS"; no other TLS/STARTTLS field on that page | Evidence strength; incomplete or ambiguous STARTTLS outcomes; certificates in this field | Distinguishes completed upgrade, cut-off, absent offer (ambiguous), not observable | https://docs.zeek.org/en/master/scripts/base/protocols/smtp/main.zeek.html | Medium. Zeek has a separate `ssl.log` not reviewed |
| **NetworkMiner** | Extracts files, emails, credentials, certificates, hosts from PCAPs; sniffs live; JA3/JA4; "not designed to perform decryption" | Assessing TLS or STARTTLS security posture; evidence states or integrity status | Transport-security posture with provenance; no content extraction | https://www.netresec.com/?page=NetworkMiner | Medium |
| **Arkime** | Large-scale full packet capture, session search, hundreds of fields per session incl. TLS/JA4; PCAP/CSV export | Email transport-security assessment; evidence states; PCAP import not described on the page | Per-capture assessment and report | https://arkime.com/ | Low-medium. Page is marketing-level |
| **testssl.sh** | Actively tests a live server for TLS/SSL support and flaws, "any SSL/TLS enabled and STARTTLS service" incl. SMTP, IMAP, POP3 | Analysing saved captures | Passive, offline, historical evidence in a given capture; never connects to a server | https://testssl.sh/ | High. Different input: it answers "what does this server do now", NyaySaakshya answers "what does this capture show" |
| **Internet.nl** | Not established: the page read did not describe its email test | | | https://internet.nl/about/ | UNKNOWN |
| Commercial digital-forensics suites (for example Magnet AXIOM, Cellebrite) | **Not researched** | | | | UNKNOWN |
| Suricata, Snort | **Not researched** | | | | UNKNOWN |

**Verdict.** In the documentation reviewed, per-fact evidence states, deliberate abstention from a verdict, cited rule-and-standard findings and reproducible assessment IDs are not described together by the tools above. I cannot show that no other tool does this. The deck therefore calls it "a design strength, not a claim of uniqueness", and says only that the documentation "as we read it" has no per-fact evidence states. No speed, cost or accuracy comparison is made, and none was run.

Fairness note: general-purpose packet tools are not designed to be assessment tools; the comparison is "what they give an investigator who must decide", not "what they fail to do".

---

## 5. Evidence-integrity and handling notes used in the deck

- SHA-256 gives **traceability**, not legal custody or tamper-evidence: there is no signing, no audit log and no access control (`DEPLOYMENT.md`). The deck and answers say so.
- NIST SP 800-86 supports recording a digest before analysis; the BSA Schedule asks for a hash and algorithm. Neither is claimed as compliance.

---

## 6. Conflicting or stale evidence

| Item | Conflict | Resolution |
|---|---|---|
| Final event date | Official timeline graphic: **9 Dec @ Nagpur**; Free Press Journal (updated 24 Sep 2026): 7 Dec | Use the official graphic; tell the applicant to re-check. Earlier internal documents said 7 Dec and were corrected |
| Below-18 or below-21 category | Official home page: "Below-18 Category"; FPJ: "below 21" | Not relevant to this applicant |
| Evaluation criteria | Official national (South Zone) lists vs press list for Maharashtra | Neither is an official Maharashtra rubric; kept as hypotheses |
| Sub-theme data | Page `SECTORS` array misaligned vs `SECTOR_DETAILS` | `SECTOR_DETAILS` matches the applicant's portal text |
| Test pass count | `VALIDATION.md` says 1,521 passed; a clean run gives 1,520 passed, 1 failed (freeze guard) | Resolved in the final pass: guard re-baselined, 1,521 passed; see `FINAL_RELEASE_AUDIT.md` |
| Durumeric et al. | 2015 study | Used only for the general point; stale for current deployment rates |
| PIB statistic | Period not stated | Qualified on the slide |

---

## 7. UNKNOWN list (needs the applicant or the helpdesk)

Portal field limits and mandatory flags; whether the live stage options match the public wizard; whether a conflict-of-interest declaration is asked of applicants and its exact wording; applicant manual contents; the Maharashtra scoring rubric; whether identity-document upload is still needed after Aadhaar verification; whether the team lead or team size can change; the live sub-theme fit rules. Helpdesk: support@sevainnovationchallenge.in, +91 91377 78135.
