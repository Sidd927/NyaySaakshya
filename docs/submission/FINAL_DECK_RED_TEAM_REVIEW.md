# Final deck red-team review

15 October 2026. Reviewed as an official evaluator, a cybersecurity architect and a sceptic, against the deck as built before this pass (`d07463a`) and the deck after it. Findings are ranked by selection relevance, then severity. Disposition: **FIXED**, **REFRAMED**, or **DISCLOSED** (genuine limitation, kept visible).

## Official criteria and sources checked (Maharashtra zone only)

All read on 15 Oct 2026; the two pages and the timeline image were byte-identical to the 15 Oct morning copies.

| Source | URL | What it establishes |
|---|---|---|
| Home page and FAQ | https://www.sevainnovationchallenge.in/ | Six-slide structure; presentation mandatory; demo and website links optional; evaluation **stages** (administrative scrutiny, two independent online evaluations, technical and impact assessment, finalist validation, Grand Jury); timeline (assessment 19 to 29 Oct; due diligence 6 to 10 Nov; online presentations 16 to 25 Nov; final 9 Dec, Nagpur); Law and Order sub-theme 2 wording |
| Guidelines | https://www.sevainnovationchallenge.in/guidelines.html | Single .pptx on the official template; eligibility and domicile; "credible problem-solution fit"; disclosures (stage, prototype, pilots, users, validation evidence, IP, regulatory dependencies); consent to due diligence |
| Official template | https://www.sevainnovationchallenge.in/assets/Seva-First-Innovation-Challenge-PPT-Template.pptx | SHA-256 matches the repository copy used by the build (`reference/`) |
| **Applicant guide "Be a Problem Solver"** (Government of Maharashtra, SEEID) | https://www.sevainnovationchallenge.in/assets/The%20First-Time%20Problem%20Solvers%20Guide.pdf (and the linked Workbook `.docx`) | **Official applicant guidance, newly read this pass.** Its "Judges' lens" page: (1) a real problem with evidence, (2) **a working demo** ("Judges trust what they can see over what they are told"), (3) fits money the government already spends, (4) a deliverable pilot plan (what, where, by when, who runs it). It also asks for: a one-sentence problem ("[Who] loses [what] because [what goes wrong], [how often]"), a one-line solution, **one failure and the fix**, before/after impact in numbers or, if untested, "the baseline, your expected result, and your trial date. An honest 'not yet tested' beats an invented number", the related Maharashtra department, a stagewise scale-up plan, and cost / who pays / sustainability with "estimates marked as estimates"; "say what it is NOT"; "used a tool, an AI? Name it and say exactly what it did" |

**Not published:** a Maharashtra scoring rubric, criteria list or weights. The guide's four-point "Judges' lens" is the closest official statement and is **guidance, not a published rubric**. The national site (sevafirst.mic.gov.in, South Zone edition) lists "relevance, originality, feasibility, cost, impact, scalability, quality of solution"; it belongs to another zone's programme, so it is used only as a hypothesis. The six dimensions below are assessed against the Maharashtra guide where it speaks and flagged as hypothesis otherwise.

## The six dimensions

| Dimension | Basis | Before this pass | After | Remaining gap |
|---|---|---|---|---|
| Problem clarity | Guide step 1: who, what goes wrong, how often, cost | Strong failure modes; no statement of what is unknown | Failure modes kept; "Not yet known: how often investigators meet such captures; none consulted yet" added | **How often and what it costs are unknown.** No stakeholder evidence. Disclosed |
| Originality | Guide: say what it is, name any AI | Evidence states and abstention clear; AI use unstated | Architecture strip now says "No AI in verdicts"; differentiation still "a design strength, not a claim of uniqueness" | Novelty not independently verified; competitor research partial |
| Demonstrated feasibility | Guide: working demo; one failure and the fix | Test counts and composition; failure story generic | Concrete failure and fix (41 of 44 cut-off streams wrongly asserted "no TLS"; now 1, arguable); "Demonstrable now: local demo on synthetic captures" | No real-world data, no pilot, no accuracy benchmark |
| Cost | Guide step 7: cost, payer, sustainability, estimates marked | "Costs not yet estimated" | "Cost not priced; a technical pilot needs no cloud service or GPU"; sustainability line unchanged; hosting prices stay removed | **No cost figure.** Not invented; a small honest line only |
| Beneficiary impact | Guide step 4: before/after; or baseline, expected result, trial date | Measures listed | Before/after framing, "existing cost it targets is analyst time, to be measured", expected result and trial path stated | No measured impact; no estimated affected population |
| Scalability | Guide step 6: one site, repeat, pilot, state | One unit then more | Adds likely owner (Home Department, police cyber cells; hypothesis) and "no office approached yet" | Single-analyst prototype, no authentication; scaling is intent only |

## Findings, ranked

### Selection-critical

| # | Finding | Severity | Disposition |
|---|---|---|---|
| R1 | **Sub-theme fit.** "Financial-crime intelligence" implies analytics that surface criminals or flows. The tool assesses how mail transport was protected in a capture. | High | DISCLOSED + REFRAMED. Slide 1 says it does not detect fraud or identify suspects; slide 2 frames the use as avoiding over-reading evidence. Cannot be fixed by wording; ask the helpdesk if worried |
| R2 | **Problem frequency and cost unknown; no stakeholder evidence.** The guide's first and strongest criterion is a real problem with field evidence. | High | DISCLOSED. Slide 2 now states "not yet known" and "none consulted". The single best improvement outside this repo is one real conversation with an investigator, truthfully reported |
| R3 | **No working link, but a working demo exists.** The guide says judges trust what they see. The deck did not say a demo exists. | Medium | FIXED. Slide 6 "Demonstrable now": local demo on synthetic captures (supported finding, withheld score, report export). A public link stays NO-GO |
| R4 | **Failure story was generic.** The guide calls an honest failure "your strongest credibility line". | Medium | FIXED. Slide 4 gives the measured one: before the fix the engine asserted "no TLS" on 41 of 44 cut-off streams; after, 1 (arguable) |
| R5 | **No before/after impact framing; no named government owner.** | Medium | REFRAMED. Slide 5 states before/after, the existing cost targeted (analyst time, to be measured) and "likely owner: Home Department (police cyber cells); no office approached yet". The owner is a hypothesis taken from the guide's department table (Home Department is listed for defence and security) |

### Technical and architectural

| # | Finding | Severity | Disposition |
|---|---|---|---|
| T1 | **Slide 3's pipeline labels (Analysis, Evidence, Finding) were vaguer than the code.** | Medium | FIXED. Replaced with the implemented flow: web upload of PCAP/PCAPNG with SHA-256, read-only TShark parse, session reconstruction with evidence states, 19 versioned rules (16 single-session, 3 cross-session, each citing an RFC or NIST publication), posture (score or Not scored), JSON/HTML/PDF reports. No microservices, live capture, decryption, AI, content reading, custody or integration implied |
| T2 | "No AI in verdicts" may look like a missing feature. | Low | REFRAMED. It is the accurate answer to the guide's "name the tool and what it did"; the optional anomaly lane is off by default and adds no independent detection |
| T3 | Internal validation is circular (82 of 98 captures crafted in-project). | Medium | DISCLOSED on slide 4 ("98 controlled lab captures: 10 from Postfix and Dovecot software in a lab, 6 OpenSSL handshakes, 82 crafted in-project"; "no real-world traffic") |
| T4 | Security prerequisites for a supervised pilot must be visible. | High | Already visible and kept: login and roles, audit log, encrypted storage, backups, concurrency fix, enforced time limit, sandboxed parsing; "Not production-ready" |
| T5 | Local-first claim could be read as a present security guarantee. | Medium | Kept labelled "a design intention, not built or validated" |

### Sceptic's view

| # | Finding | Disposition |
|---|---|---|
| S1 | Strongest reason not to select: solo applicant, lab-only validation, no user, no pilot, frequency of the use case unknown, narrow fit. | DISCLOSED. True and visible; nothing inflates it |
| S2 | Slide 3 is dense. | REFRAMED. One hierarchy (flow strip, states beside a worked example, two callouts); minimum 8.5 pt except the template footer. Accepted trade-off; nothing added in this pass beyond relabelling the strip |
| S3 | "Home Department" could imply contact with a department. | REFRAMED. Slide says "likely owner" and "no office approached yet" |
| S4 | Hosting prices and Render behaviour. | Already removed in the earlier redesign; not reinstated: a verified price list is not what the evaluator needs |
| S5 | Screenshot legibility: dark UI crops. | Kept at 3.84 in, 2x resolution; the large score and "Not scored" headline are legible; fine text is reproduced as native text on slide 3 |

## Verdict

**Improve and submit.** The deck was already honest and well structured; the official applicant guide, read this pass, exposed four gaps that could be closed truthfully (working demo, a concrete failure and fix, before/after framing with a likely owner, the AI question) and a clearer architecture strip. Nothing was added that the evidence does not support. The weaknesses that remain (fit, no stakeholder evidence, no real-world data) cannot be fixed in the deck.
