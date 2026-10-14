# Final submission checklist: Seva First Innovation Challenge 2026

Prepared 14 October 2026 (Wednesday). **Deadline: Saturday 17 October 2026, 11:59 PM IST.** Target: submitted and verified by **Friday 16 October**. After the deadline applications are locked (FAQ).

Related: `PORTAL_APPLICATION_ANSWERS.md` (paste-ready answers), `DEPLOYMENT_GO_NO_GO.md` (decision: NO-GO for public deployment; local demo and video), `submission/seva-innovation-challenge-2026/SLIDE_CLAIM_AUDIT.md`.

**Source limits.** Portal screenshots were not available to this session; the form fields come from the Phase F brief's transcription. The portal was not logged into or touched. The public pages read on 14 Oct 2026 were `sevainnovationchallenge.in` (home, FAQ) and `/guidelines.html`. The "applicant manual" the FAQ cites is **not public**; its content is known only through the FAQ.

## 1. Requirements, classified

### A. Mandatory (stated on the official public pages)

| Requirement | Source | Status |
|---|---|---|
| Apply by 17 Oct 2026 | Home page, guidelines | Open |
| Aadhaar verification before final submission | FAQ | **Done** (transcription) |
| Pitch presentation upload | FAQ: "Is uploading a pitch presentation mandatory? Yes." | **Not done**: deck has placeholders |
| Six slides: title and applicant snapshot; problem; solution and innovation; feasibility and implementation; impact and scalability; team/individual and support required | FAQ, template | Deck has six slides in this order |
| Official Seva template | Guidelines section 3: "single PowerPoint (.pptx)… prepared using the official Seva First template" | Deck built from the official template |
| One innovation, **one primary sector** | Guidelines, FAQ | Law and Order (transcription) |
| Domicile certificate of Maharashtra, Chhattisgarh, DNH and DD, or Goa for the individual (or one founder) | Guidelines | **Applicant must confirm** (team of 1) |
| Disclose stage, prototype status, pilots, users, validation evidence, IP status, regulatory dependencies | Guidelines | Answers drafted; IP and regulatory need the applicant |
| Consent to verification and due diligence | Guidelines | **Applicant declaration** |
| Identity document upload (Aadhaar, PAN, passport or driving licence; PDF/JPG/JPEG/PNG; max 5 MB) | FAQ | Unclear whether still needed after Aadhaar verification: check the dashboard |
| Problem statement to include who is affected and the estimated number of people or organisations | FAQ | Answer drafted (units, not people) |

### B. Visible portal fields (transcription; not claimed exhaustive)

Problem understanding; estimated number affected; proposed solution; who benefits (checkboxes); current stage; innovation; technology (checkboxes); key advantages (checkboxes); tested or piloted; pilot/deployment details; expected impact; six-slide upload (PDF, PPT, PPTX, **15 MB**); prototype/demo link; website/product link; consent and conflict-of-interest declaration. Mandatory flags and character limits: **unknown**, read them on the form.

### C. Optional but useful

- Prototype/demo link: **optional** (FAQ). Only an unlisted video of the synthetic demo, if you make one.
- Website/product link: **optional** (FAQ). Leave blank; repository is private and the old Vercel site is stale.
- A recorded demo (see `DEPLOYMENT_GO_NO_GO.md` section 7). Not created yet.

### D. Needs helpdesk confirmation

Helpdesk: **support@sevainnovationchallenge.in**, **+91 91377 78135**. One short email covers all of these:

1. Exact stored team-name spelling (portal shows `NYAYSAakshya` / `NYAYSAKSHYA`) and whether it can be corrected.
2. Whether "financial-crime intelligence" sub-theme fits a forensic evidence tool, or the sector choice is final once saved. (Do not change the sector unless they advise it.)
3. What the "estimated number of people/units" field accepts (number only, or text with units).
4. Format discrepancy: public guidelines say a single PPTX; the portal accepts PDF, PPT and PPTX. Confirm PPTX is fine.
5. Whether a separate domicile certificate or identity upload is needed beyond Aadhaar, and for a team of 1.
6. Whether the applicant manual can be shared.

Do not wait for replies to proceed: draft everything, then adjust.

## 2. Findings that need the user

**Declarations only the applicant can make:** consent to verification; conflict of interest; domicile; IP status and any employer or institution claim; regulatory dependencies; single submission; accuracy of the whole application. See `PORTAL_APPLICATION_ANSWERS.md`, last section.

**Unsettled facts:** contact email and mobile (the Aadhaar-linked details are on the portal); team name spelling; whether you hold the domicile certificate and for which state; whether to tick "Citizens"; whether AI/ML stays unticked; whether to add a mentor.

## 3. Inconsistencies found (prioritised)

Deck = `NyaySaakshya_Seva_Innovation_Challenge_2026_DRAFT.pptx`. Not edited yet, by instruction. Edit after you approve the answers.

| P | Where | Discrepancy | Fix |
|---|---|---|---|
| **P0** | Slide 1 | Sector shows `[SECTOR REQUIRED]`. Portal has Law and Order and the cyber-fraud sub-theme. | Enter "Law and Order: Cyber-fraud, digital extortion and financial-crime intelligence". |
| **P0** | Slide 1 | Applicant name, application type, contact are placeholders. | Fill: Siddhant Hiralal Patil; individual (team size 1); contact. Confirm the team name spelling first. |
| **P0** | Slide 6 | Four team cards for a team of 1, all placeholders; mentor line; "Thank you" contact. | Keep one card (name, role, qualification, photo). Delete the other three. Mentor only if real. Contact. |
| **P0** | Slide 1, 4, 5, 6 | Orange `[CAPITAL]` placeholders and the "DRAFT" notice and kicker tag. | Resolve or remove every one. |
| **P1** | Slide 4 and 5 | `[MENTOR / PARTNER…]` and `[SUSTAINABILITY MODEL…]` placeholders. | Delete the lines or fill them with something real. No partner exists. |
| **P1** | Slide 2 vs form field 2 | Deck gives only the national 17.82 lakh; the form will say "about 50 district cyber police stations" as potential units. | Optional: add one line on slide 2, "Potential units: about 50 district cyber police stations in Maharashtra (AIR, 12 Oct 2024)". Keeps deck and form consistent. Claim-audit row to add. |
| **P1** | Slide 1 vs form field 5 | Stage matches (Working Prototype). | None. |
| **P1** | Slide 3 vs form fields 3, 6 | Consistent: six states, abstention, reproducibility, no decryption claim. | None. |
| **P1** | Slide 5 vs form fields 8, 11 | Consistent: nothing quantified; "to be measured". | None. |
| **P2** | Profile vs deck | Team profile (as described) mentions device data, suspect activity and district cyber cells. The deck makes none of these claims. | Fix the **profile**, not the deck. Wording in the answers file. |
| **P2** | Sub-theme fit | "Intelligence" wording in the sub-theme overstates what the tool does. | Deck already says "triage" and "what a capture does, and does not, prove". Keep. |
| **P2** | Screenshots | Slide 1 images: current build (22.15 CRITICAL reproduced today; withheld case reproduced). The stale "Engine Live 0.8.0" label is cropped out. | None. |
| **P2** | Fonts | Nirmala UI missing on the build Mac; preview PDF uses a substitute. | Open the final PPTX in PowerPoint and check each slide for overflow. |
| **P2** | Demo link | Deck has no URL, so no mismatch. | If you add a video link, add it to slide 4 as well. |

## 4. Deck edits (after approval)

1. Fill slide 1 fields, one card on slide 6, remove all placeholders and DRAFT marks (edit `build_deck.py` or edit the PPTX directly in PowerPoint; either works).
2. Update `SLIDE_CLAIM_AUDIT.md` for any new line (for example the units line).
3. Open in PowerPoint, check all six slides at 100%, then save as `.pptx`.
4. File name suggestion: `NyaySaakshya_Seva_2026.pptx`. Size must stay under 15 MB (current draft about 0.13 MB).
5. Upload **PPTX**. The guidelines require a single PPTX; the portal also accepts PDF but there is no reason to prefer it.

## 5. Schedule

| When | Task |
|---|---|
| **Wed 14 Oct night / early Thu 15 Oct** | Read the three Phase F documents. Email the helpdesk (section 1D). Decide: team name check, domicile, Citizens tick, AI/ML tick, contact details. |
| **Thu 15 Oct, morning** | Log in. Read every form field, limit and mandatory flag. Note differences from the transcription. Paste answers into a draft (the portal supports saving drafts, per FAQ). |
| **Thu 15 Oct, midday** | Finalise the deck edits (section 4). Fix the team profile text. |
| **Thu 15 Oct, afternoon** | Optional: record the demo (3 to 4 minutes, `DEPLOYMENT_GO_NO_GO.md` section 7). Inspect it. Decide whether to upload it unlisted and fill the demo link. Skip if time is tight. |
| **Fri 16 Oct, morning** | Upload the PPTX. Re-read every answer against the answers file. Make the personal declarations yourself. |
| **Fri 16 Oct, by midday** | Submit. Confirm status on the dashboard. Save a screenshot or PDF of the confirmation. |
| **Fri 16 Oct, afternoon** | Reserve for helpdesk replies and fixes. |
| **Sat 17 Oct** | Buffer only. Do not leave submission to this day. |

## 6. Pre-submit verification

- [ ] Team name, sector and sub-theme on the portal, the deck and every answer match.
- [ ] Deck: six slides, in order, no placeholders, no "DRAFT" text, no guidance text.
- [ ] Deck file under 15 MB; opens in PowerPoint; slide count is six.
- [ ] Every number in the deck and answers is in the claim audit with a source (17.82 lakh PIB; about 50 units AIR; 1,521 tests; 98 captures; 13,822 frames).
- [ ] No unsupported claims: device data, suspect detection, attacker attribution, fraud proof, TLS decryption, speed, accuracy, savings, users, pilots, partners, deployment, live URL.
- [ ] AI/ML not ticked (unless you decide otherwise knowingly).
- [ ] Stage is Working Prototype, not pilot or ready.
- [ ] Demo and website link fields blank, or hold only an unlisted synthetic-data video.
- [ ] Consent, conflict of interest, domicile, IP and regulatory fields completed by you personally.
- [ ] Dashboard shows "submitted"; confirmation saved.

## 7. What to commit

**Committed with this phase (documentation only):**
`docs/submission/PORTAL_APPLICATION_ANSWERS.md`, `docs/submission/DEPLOYMENT_GO_NO_GO.md`, `docs/submission/FINAL_SUBMISSION_CHECKLIST.md`.

**Not committed:** the scratch demo output (`/tmp`), any edited deck (not yet made), screenshots of the portal. No frontend, scoring, rules, validation or test file was changed.
