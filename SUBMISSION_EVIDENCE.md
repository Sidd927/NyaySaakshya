# NyaySaakshya — Submission Evidence Package

Seva First Innovation Challenge, Maharashtra Zone. Application deadline **17 October 2026**; finals in Nagpur on 7 December 2026 (organiser's site and press, see section 14). Prepared 14 October 2026 against branch `design/landing-redesign`, commit `c7accff`; forensic baseline tag `v1.1.0-validation-baseline` (`c0f77b9`).

This is an evidence package, not the slide deck. The official template has six slides: (1) title and applicant snapshot, (2) problem, (3) solution and innovation, (4) feasibility and implementation, (5) impact and scalability, (6) team and support required. Each section below says which slide it feeds. Facts are tagged **[verified]** (read in the repository or by running it), **[sourced]** (public source, section 14), **[hypothesis]** (our reasoning, to be tested) or **[proposed]** (not built). Nothing proposed is presented as implemented.

---

## 1. Executive product description  *(slides 1, 3)*

NyaySaakshya is an **evidence-first triage tool for captured email traffic** in cyber-fraud investigations. An investigator uploads a packet capture (PCAP) of SMTP, IMAP or POP3 traffic. The system reconstructs the sessions and reports, per session, what the capture **does and does not establish** about transport security (was TLS used, did a STARTTLS upgrade complete, what version and certificate were visible), as findings that cite the exact frames they rest on. When the capture cannot support a conclusion, it says so and withholds a score instead of guessing.

The pipeline is Capture → Analysis → Evidence → Finding → Posture → Report. Output is a JSON, HTML (English, Marathi draft, or both) and PDF report that carries the capture's SHA-256 and a reproducible assessment ID **[verified: README, VALIDATION.md]**.

It is not an AI fraud detector, does not attribute an attacker, does not decide that fraud occurred, and is not a legal chain-of-custody system.

---

## 2. Problem statement  *(slide 2)*

**The scale of the wider problem [sourced].** The National Cybercrime Reporting Portal recorded 24,02,579 financial-fraud complaints and ₹22,495 crore of reported losses in calendar 2025 (MHA reply to the Rajya Sabha, 11 Feb 2026; complainant-reported, not verified police cases). For Maharashtra, the Chief Minister told the Legislative Council on 4 March 2026 that 2024–25 saw 5.16 lakh cases of suspicious online transactions with ₹7,592 crore lost, and that about 1,000 police officers had been trained by 26 cyber experts in forensic tools for investigating online fraud. (The same reply gives ₹941 crore across 1.99 lakh cases for a different 2024–26 scope; the article does not reconcile the figures, so we quote them separately and do not add them.)

**What we could not source.** We found **no published figure** for how many of these cases involve email, phishing or business-email-compromise. CERT-In's 2025 totals (29.44 lakh incidents) were not broken down by category in the sources we found. We therefore do **not** claim email is a major vector in Maharashtra; the problem we address is the narrower one below.

**The narrower, defensible problem [hypothesis, partly sourced].** When an investigator holds a capture of mail traffic, the practical questions are: was this session protected, did a TLS upgrade actually happen, was a downgrade possible, and which of those facts can I stand behind and cite? Two sourced facts make this question real rather than academic: STARTTLS is optional and SMTP "fails open", and a 2015 measurement study found network devices that corrupt STARTTLS so mail travels in cleartext (41,405 servers in 193 countries on the study's data; Durumeric et al., IMC 2015). That study is about mail in general, not India or fraud cases.

**Who experiences it [hypothesis].** Cyber-cell and forensic-lab investigators and the supervisors who must defend a conclusion; whether this is a frequent task for them is exactly what a pilot would measure (section 9). We have not interviewed any investigator and make no claim about their workflow beyond what the public sources state.

---

## 3. Target beneficiaries  *(slide 2, 5)*

Intended (not partnered, not deployed anywhere): investigators and forensic analysts in Maharashtra cyber-cell and forensic-lab settings; supervising officers who review findings; the courts and defence only indirectly, if a pilot unit chose to use a report as supporting material (we make no admissibility claim). Secondary: students and researchers learning evidence-bounded analysis.

No pilot unit, user count or letter of support exists. The submission should say "intended beneficiaries" and "proposed pilot".

---

## 4. Solution and originality  *(slide 3)*

**What a packet tool already gives, from its own documentation [sourced].** Wireshark offers packet dissection, "Expert Information", stream following, and TLS decryption **if** the analyst supplies keys. Zeek's `smtp.log` records a `tls` field as true/false (documentation example reviewed). These give investigators raw facts or a boolean.

**What NyaySaakshya adds [verified in the product; the comparison is a hypothesis].** The workflow, not the stack, is the contribution:

1. **Every fact carries a state.** Six evidence states: OBSERVED, INFERRED, UNKNOWN, AMBIGUOUS, INCOMPLETE, NOT_OBSERVABLE. An absent STARTTLS advertisement stays AMBIGUOUS, never "stripped"; a cut-off handshake is INCOMPLETE, never "no TLS"; a TLS 1.3 certificate is NOT_OBSERVABLE, never "invalid". All six are produced by reproducible captures (VALIDATION §14.7).
2. **Findings cite frames and standards**, and the cited frames were checked against TShark: 13,822 cited frames, 0 stream mismatches, 0 issues without a frame (VALIDATION §15.5).
3. **The tool abstains.** A capture with nothing assessable, or too little, gets no score (`scored: false`, `value: null` in the JSON), with the reason stated. A partial checklist or a cut-off session cannot become a "compliant" result (VALIDATION §14).
4. **Reproducible and traceable.** Same capture, same software: same assessment ID and content; a different engine or rule version gives a different ID (VALIDATION §14.9–14.10).
5. **Marathi report as a reviewable draft**, marked unreviewed.

**Caution on novelty.** We have not verified that no other tool offers evidence-state-labelled findings, and we do not claim it. The safe statement is: *we did not find the tools above documenting per-fact evidence states or deliberate withholding of a grade; NyaySaakshya makes that the product's organising rule.*

---

## 5. Demonstrated capabilities  *(slide 3, 4)*

Verified by running the system on 14 October 2026, locally, with lab/synthetic captures only:

| Check | Result |
|---|---|
| Health | `status ok`, posture engine 0.10.0, schema 1.1 |
| Upload and analysis, flagship capture | HTTP 201; CRITICAL, score 22.15, 10 issue groups; HTML (42 KB) and PDF (29 KB) reports generated |
| Capture cut inside the TLS handshake | HTTP 201; INSUFFICIENT_EVIDENCE, `scored: false`, `value: null`; reports generated |
| Raw TLS on a non-mail port (unsupported) | HTTP 201; INSUFFICIENT_EVIDENCE, `value: null` |
| Error behaviour | garbage bytes → 500 (structured error; a known P2 defect, VALIDATION D4); empty file → 422; wrong content type → 415; unknown run → 404; `DELETE` → 405 |
| Timing | each small capture analysed in about 0.15 s on a development laptop; **single observation on tiny captures, not a benchmark, not for use as a performance claim** |

Product surface [verified]: React analyst console (upload, evidence, findings, cross-session, provenance, report tabs); FastAPI backend; SQLite catalogue; 1,521 automated tests passing at the baseline.

---

## 6. Validation evidence  *(slide 4)*

From `VALIDATION.md` (controlled corpus: 98 captures, 1,426 TCP streams; 10 captures are real Postfix/Dovecot traffic, 6 real OpenSSL handshakes, the rest crafted by in-project generators):

- Extracted facts agree with an independent raw-byte read of the same packets on 1,426/1,426 streams (three of four facts; the fourth differs only on the 3 raw-TLS streams the engine deliberately does not analyse).
- Score recomputed independently for 98/98 captures; determinism 98/98 over two runs; the ML lane (off by default) leaves findings, band, score, coverage and abstentions identical on all 98.
- Defects found during validation were fixed or recorded, and the history is preserved (D1–D3, D7 closed; remaining limitations listed in §14.14 and §15).
- **No false-positive rate, false-negative rate or real-world accuracy has been measured.** A synthetic-corpus count is not a rate and must not be presented as one.

---

## 7. Deployment feasibility  *(slide 4)*

From `DEPLOYMENT.md` (classification **B: validated prototype with a credible pilot path**; not pilot-ready, not production-ready).

- **Runs locally [verified]:** no outbound network call found in `src/`; fonts bundled; no GPU dependency. The strongest safe wording: *the core analysis is designed to run locally without sending captures to a third-party analysis service.* An air-gapped run has not been tested.
- **Correction to an earlier overbroad statement.** "A capture never leaves the cyber cell" is true **only of the proposed on-premise deployment**, not of the current hosted application. The hosted design (frontend on one provider, backend container on another) means an uploaded capture **does** leave the user's machine and sits on a third party's filesystem. There is also **no live URL configured today** (README placeholders say "URL to be added"). The demo and any pitch statement must say which deployment is meant: *local/on-premise (design)* versus *hosted demo (test captures only)*.
- **Not suitable for real evidence today [verified]:** no authentication, roles, audit log, TLS in-app, encryption at rest, or retention/deletion; a known SQLite concurrency defect (TECH-DEBT #10); the configured analysis wall-clock limit is not enforced; the UI contains demo-fixture fallback.
- **Smallest credible pilot [proposed]:** one hardened unit-owned server, TLS reverse proxy, local accounts and three roles, encrypted volume, audit log, tested backup, unprivileged no-network worker; each control has a named acceptance test (DEPLOYMENT §9, §17).
- **Reusable as is [verified]:** the engine, evidence model, report renderer, hash-at-write artifact store, atomic finalisation, resource limits. **To build [proposed]:** identity and roles, case isolation, audit, retention, backup, worker isolation, concurrency fix.

---

## 8. Preliminary cost assumptions  *(slide 4, 6)*

**All figures are estimates, not quotations, tenders or approved budgets.** External prices were read on 14 October 2026; they change. Exchange-rate assumption: **₹96 per US$** (RBI reference rate reported as ₹95.749 on 12 October 2026 and about ₹96 in early October; source in section 14). Costs exclude taxes unless a source says otherwise.

### A. Current demonstration

| Item | Cost | Source / assumption |
|---|---|---|
| Local run on an existing laptop (recommended for the 7 December jury demo) | ₹0 incremental | no network needed to analyse |
| Hosted backend, Render **Free** | $0 | **Spins down after 15 min idle, takes about a minute to wake, wipes local files (uploads, SQLite) on spin-down, no persistent disk** (Render docs). A judge's analysis can vanish |
| Hosted backend, Render Standard (1 CPU, 2 GB) | $25/month ≈ ₹2,400 | Render pricing as reported; paid services can attach disks |
| Persistent disk | from $0.25/GB/month (10 GB ≈ $2.50 ≈ ₹240) | same |
| Frontend, Vercel Hobby | $0, **personal non-commercial use only** (Pro $20/month) | Vercel pricing page |

Whether the 512 MB / 0.5 CPU or the 2 GB instance is enough for TShark plus analysis has **not been measured**. Reported repricing by Render in September 2026 means the numbers must be re-checked before relying on them.

### B. Single-unit controlled pilot (proposed)

Cost = one-time + recurring, from this formula; no price below is a quotation.

| Component | One-time | Recurring | How to estimate (no figure invented) |
|---|---|---|---|
| Server or forensic workstation | hardware purchase | power, rack/space, warranty | obtain ≥3 vendor quotations for a multi-core machine; sizing from a measured pilot run (we have none) |
| Encrypted storage | SSD capacity | replacement | capacity = captures per month × average size × retention months × (1 + backup copies) |
| Backup target | media or appliance | media rotation | same formula; restore drill each quarter |
| Software licences | none expected, **licences to be confirmed** | none | stack is open source (Wireshark, Python, FastAPI, SQLite, React); confirm each licence before procurement |
| P0 engineering (identity, roles, case isolation, audit, retention, concurrency fix, worker isolation, TLS proxy, fixtures off, TShark check) | engineer time | maintenance | **our judgement: on the order of one to three engineer-months, to be re-estimated after a short spike**; not a measurement |
| Security review and policy work | external or internal review | annual | per organisation's rates |
| Operations and support | training, runbook | staff time for patching, release re-validation, incidents | person-days per quarter × local rate |

### C. Multi-unit deployment (proposed)

Total ≈ N × (per-unit cost from B, with engineering amortised) + a central administration tier (identity, signed releases, aggregate counts) + central support. Because raw captures stay local in the hybrid model, no central evidence storage or bandwidth for captures is budgeted. Detailed numbers need pilot measurements and local quotations.

### GPU

**Not required.** No dependency uses a GPU: the core is pure Python plus TShark, and the optional ML lane is a stdlib robust-z model (scikit-learn is used only for research candidates).

---

## 9. Potential impact and measurable indicators  *(slide 5)*

Impact below is **potential**. **Demonstrated** today is limited to the technical properties in section 6. No baseline or improvement percentage is stated, because none has been measured.

| Indicator | Why it matters | How a controlled pilot would measure it | Baseline | Demonstrated today? |
|---|---|---|---|---|
| Time to a first assessment from an uploaded capture | investigator time | timestamp upload → first assessment, per capture, on pilot hardware and a size ladder | collect from the unit's current method on the same captures | No (single tiny-capture observation only) |
| Share of findings with usable provenance | whether claims can be defended | investigator checks each cited frame against the capture; score proportion usable | n/a | Partly: 0 mismatches over 13,822 frames on the controlled corpus |
| Effort to interpret a capture | cognitive load | timed task, same captures, with and without the tool, several investigators, order randomised | measured in the study | No |
| Time to prepare a report | admin burden | time from assessment to a report the supervisor accepts | measured | No |
| Correct identification of unresolved or unobservable evidence | the product's main safeguard | seeded captures with known-unobservable facts; count how often the tool abstains correctly and how often an analyst without it over-concludes | measured | Partly: abstention behaviour is tested on the controlled corpus |
| Reproducibility on re-analysis | trust | re-run by a second person; same assessment ID | n/a | Yes on 98 captures (single software version) |
| Supervisor confidence | adoption | structured questionnaire after each review | measured | No |

A pilot would use synthetic or consented captures first, a fixed protocol and pre-registered metrics, and would record negative results.

---

## 10. Scalability pathway  *(slide 5)*

From DEPLOYMENT §9–§18: Stage 0 validated prototype (now) → Stage 1 controlled technical pilot on synthetic data (all P0 controls pass their acceptance tests) → Stage 2 single-unit operational pilot under the unit's own policy → Stage 3 several units on one signed release line (hybrid: local evidence, central administration) → Stage 4 state-scale operations after capacity is **measured**. No dates; no authority is assumed to adopt it.

Main bottlenecks **[hypothesis, unmeasured]**: CPU in session reconstruction and rules, memory per analysis, the single SQLite writer, and in-request analysis with one slot. **Scaling has not been benchmarked**; workers are not claimed stateless or horizontally scalable.

---

## 11. Current limitations  *(slide 4, 6: honesty)*

- Scope is SMTP, IMAP, POP3 (and implicit TLS). Mail on an unrecognised port and non-mail traffic are withheld, not detected.
- Validated on a controlled corpus, mostly synthetic or lab-generated; no real-world accuracy, no false-positive or false-negative rate.
- Passive and offline: cannot decrypt, cannot see TLS 1.3 certificates (NOT_OBSERVABLE), no trust or revocation checking, cannot tell stripping from non-support in one session.
- No authentication, authorization, audit trail, retention control, TLS or encryption at rest in the app; SQLite concurrency defect; analysis wall-clock limit not enforced.
- Hosted demo: no live URL configured; free tier is ephemeral, spins down and wipes data; no authentication means runs are listable by anyone who can reach the API (observed: `GET /analyses` lists all runs unauthenticated).
- TShark version sensitivity: golden results were produced on 4.6.8; the Docker image installs 4.6.x from a PPA and was never built or run in validation.
- Marathi output is an unreviewed machine draft.
- Not a legal chain-of-custody or admissibility solution.

**Demo-safety observations (reported, not changed):**

1. *Fixture fallback.* The UI starts with three bundled demo analyses, labelled "Demo Fixture" in the header. With the backend down, an upload fails with "The analysis service is unavailable"; it does **not** produce a fake result. The residual risk is a viewer opening a bundled demo run and taking it for their own. Safest demo practice: run the backend locally and say so.
2. *Stale label.* The workbench sidebar shows a hard-coded "Engine Live · 0.8.0" while the engine is 0.10.0. One-line frontend fix; left untouched because the frontend is frozen.
3. *Cold start and data loss.* On Render Free the first request after idle takes about a minute and earlier uploads are gone. Warm the instance beforehand or demo locally.
4. *Public exposure.* On any public instance every uploaded capture is visible to anyone who calls the list endpoint. Use only synthetic captures.

---

## 12. Competition-safe claims  *(all slides)*

| Proposed claim | Supporting evidence | Limitation | Safe wording |
|---|---|---|---|
| What the prototype does today | Ran it 14 Oct 2026: upload → analysis → findings → assessment → HTML/PDF/JSON report | Test captures only; no live URL configured | "A working prototype that turns an email-traffic capture into evidence-linked findings and a report." |
| Validated evidence model | VALIDATION.md: 98-capture controlled corpus; 1,521 tests; baseline tag | Mostly synthetic/lab data; no real-world accuracy or error rates | "Validated for behaviour on a controlled corpus; real-world accuracy is not yet measured." |
| Six evidence states | All six produced by reproducible captures (VALIDATION §14.7) | INCOMPLETE is produced on three fields only | "Every fact carries one of six evidence states, including 'not observable' and 'incomplete'." |
| Reproducibility and SHA-256 | Hash computed while the file is written; same software + capture gives same assessment ID and content (98/98) | Report bytes differ across re-analyses by the timestamp; hash is traceability, not legal custody; TShark version not in the ID | "Every capture is identified by its SHA-256 and the analysis is reproducible with the same software." |
| Provenance and reports | 13,822 cited frames, 0 mismatches; JSON/HTML/PDF generated | Marathi is an unreviewed draft | "Each finding points to the frames it rests on." |
| ML lane's bounded role | Off by default; findings, band, score unchanged with it on across 98 captures | Research-grade; adds no detection the deterministic lane lacked | "An optional anomaly signal that cannot change a finding or a score. The product is not AI fraud detection." |
| Local / offline potential | No outbound calls in `src/`; fonts bundled; no GPU | Air-gap not tested; installation needs packages; Docker image never built in validation | "Designed to run locally without sending captures to a third-party analysis service." |
| "Capture never leaves the cyber cell" | **Only true of the proposed on-premise deployment** | The hosted demo sends captures to a third party | **Do not use as written.** Say: "In the proposed on-premise design, captures stay inside the unit; the online demo is for test captures only." |
| Hosting and storage | Render Free is ephemeral and spins down | No live URL; no persistence | "The hosted demo is for synthetic data and is not retained." |
| Unresolved issues | SQLite concurrency (TECH-DEBT #10), unenforced time limit, no auth, fixture fallback | Listed in DEPLOYMENT §6 | "Before real evidence: accounts, roles, audit, encryption and a concurrency fix are required and not yet built." |
| Pilot-readiness | DEPLOYMENT.md classification B | | "A validated prototype with a defined pilot path." |

**Do not say:** production-ready, pilot-ready, government-approved or adopted, integrated with any state system, court-admissible, legal chain of custody, tamper-proof, secure for real evidence, any accuracy or false-positive figure, any throughput or user count, "detects fraud", "AI-powered", "email is a leading fraud vector" (unsourced).

---

## 13. Likely judge questions and evidence-based answers

1. **How is this different from Wireshark?** Wireshark shows packets and, with keys, decrypted content; it leaves the conclusion to the analyst. We add per-fact evidence states, frame-cited findings and a grade that is withheld when the capture cannot support one. We have not claimed other tools cannot do this; we did not find it documented.
2. **How accurate is it?** We have not measured real-world accuracy. We can show extraction agreeing with an independent raw-byte read on 1,426/1,426 controlled streams and independently recomputed scores; those are consistency checks, not accuracy rates.
3. **Is this AI?** The conclusions are deterministic rules tied to RFCs and NIST guidance. An optional ML signal exists, is off by default and cannot change a finding or score.
4. **Why email?** Mail transport security (STARTTLS downgrade, cleartext sessions) is a concrete, checkable question with published research behind it. We have no source quantifying email's share of Indian cyber-fraud cases and do not claim one.
5. **Who would use it?** Intended: cyber-cell and forensic-lab investigators and supervisors. No unit has used it; a pilot would test that.
6. **Does evidence leave the cell?** In the proposed on-premise design, no. The online demo is hosted and for test captures only.
7. **Is it legally usable?** We make no admissibility claim. A hash gives traceability; custody needs procedure, access control and audit that the prototype does not have.
8. **What would a pilot cost?** Not quoted. Components and formula are in section 8; hardware needs vendor quotations and capacity needs measuring.
9. **Does it scale across Maharashtra?** As a design, unit by unit with central administration only. Scaling has not been benchmarked and no adoption exists.
10. **What happens with encrypted traffic?** We report what is visible and mark the rest NOT_OBSERVABLE. We do not decrypt.
11. **Is the hosted demo safe for real data?** No; it has no authentication and is ephemeral.
12. **What about Marathi?** A machine-drafted report exists and is labelled unreviewed; native review is a listed pilot step.

---

## 14. Source links and assumptions

Read 14 October 2026.

- Challenge details: [Seva First Innovation Challenge, Maharashtra Zone](https://sevainnovationchallenge.in/) (six-slide template, last date 17 October 2026, evaluation stages, no scoring weights published, eligibility); [Free Press Journal on the challenge](https://www.freepressjournal.in/mumbai/seva-first-innovation-challenge-opens-applications-with-5-crore-prize-pool-for-technology-solutions-across-states) (cyber fraud prevention among themes, prize pool, 7 Dec 2026 final in Nagpur, as reported).
- NCRP 2025 totals (24,02,579 complaints; ₹22,495 crore): reported in search results citing an MHA reply in the Rajya Sabha on 11 Feb 2026; we did not open the parliamentary record itself, so treat as secondary. See also [IndiaSpend data visualisation](https://www.indiaspend.com/data-viz/dataviz-how-indias-cyber-crime-incidence-is-rising-972933).
- Maharashtra figures and ~1,000 officers trained: [Free Press Journal, 5 Mar 2026](https://www.freepressjournal.in/mumbai/maharashtra-govt-informs-council-941-crore-lost-in-199-lakh-cyber-fraud-cases-through-nccrp-portal) (written reply of 4 Mar 2026; figures not reconciled in the article).
- CERT-In 2025 totals, no category split found: [PIB backgrounder, CERT-In](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2217537&lang=1&reg=3).
- STARTTLS stripping: [Durumeric et al., "Neither Snow Nor Rain Nor MITM…", IMC 2015](https://zakird.com/papers/mail.pdf).
- Wireshark capabilities and TLS decryption needing keys: [Wireshark User's Guide](https://www.wireshark.org/docs/wsug_html/), [Wireshark TLS wiki](https://wiki.wireshark.org/TLS). Zeek SMTP log `tls` field: [Zeek SMTP log documentation](https://docs.zeek.org/en/master/logs/smtp.html).
- Hosting: [Render free-instance limits](https://render.com/docs/free), [Render disks](https://render.com/docs/disks), [Render compute plans](https://render.com/docs/compute-plans); Render prices ($7 Starter, $25 Standard, disks from $0.25/GB) as reported on [Render's pricing page mirror](https://render-web.onrender.com/pricing), with third-party reports of repricing in September 2026, so verify; [Vercel pricing](https://vercel.com/pricing) (Hobby $0 non-commercial, Pro $20).
- Exchange rate: RBI reference rate ₹95.749/US$ on 12 October 2026, as reported in a web search summary; official source [FBIL](https://www.fbil.org.in/).
- Internal evidence: `VALIDATION.md`, `DEPLOYMENT.md`, `README.md`, tag `v1.1.0-validation-baseline`.

**Assumptions:** ₹96/US$; all costs are estimates; engineering effort is judgement; no benchmark was run; the 14 October observations used tiny synthetic captures on a development laptop; no real investigative evidence was used anywhere.
