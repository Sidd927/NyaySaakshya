# Final release audit: Seva First Innovation Challenge 2026

Audited 15 October 2026 on branch `design/landing-redesign`, from `e24cae7`. Validation tag `v1.1.0-validation-baseline` still points at `c0f77b9`. No frontend, scoring, rules, test or validation file was changed. No portal action was taken: the portal was not opened, logged into or modified, and nothing was uploaded or submitted.

## Decision

**BLOCKED** for submission readiness, **only on items that need you** (section 5). Everything that can be finished without you is finished and verified. Once you clear the MUST items in section 5, the PPTX is ready to upload.

## 1. Deliverables

| File | Size | Notes |
|---|---|---|
| `submission/seva-innovation-challenge-2026/NyaySaakshya_Seva_Innovation_Challenge_2026.pptx` | 125,082 bytes (0.12 MB) | **Primary submission file.** Built from the official template by `build_deck.py` |
| `submission/seva-innovation-challenge-2026/NyaySaakshya_Seva_Innovation_Challenge_2026_PREVIEW.pdf` | 347,111 bytes (0.33 MB) | LibreOffice render. Preview only, do not upload |
| `submission/seva-innovation-challenge-2026/build_deck.py` | | Reproducible build; optional `APPLICANT` block |
| `submission/seva-innovation-challenge-2026/SLIDE_CLAIM_AUDIT.md` | | Claim-by-claim evidence map for the final deck |
| `docs/submission/PORTAL_APPLICATION_ANSWERS.md` | | Final paste-ready answers and declaration table |
| `docs/submission/PROFILE_FINAL_COPY.md` | | Replacement project profile text |
| `docs/submission/USER_INPUT_REQUIRED.md` (copy in the submission folder) | | What only you can supply |
| `docs/submission/DEPLOYMENT_GO_NO_GO.md`, `FINAL_SUBMISSION_CHECKLIST.md` | | Phase F, still valid |

Limit: the portal accepts up to 15 MB. Both files are far below it. The earlier `_DRAFT.pptx` was removed from the tree (still in git history).

## 2. Six-slide verification

- `python-pptx` reports **6 slides**; the PDF has **6 pages**, 16:9 (720 x 405 pt). Order: title and snapshot; problem; solution and innovation; feasibility; impact and scalability; team and support.
- A text scan of every slide, table and speaker note found **0 placeholders**: no `[…]` markers, DRAFT, TODO, REQUIRED, template guidance, "SecureMailScope", Marathi, AI, device-data or suspect-activity wording, and no "about 50 district cyber police stations".
- Orange text remaining on the slides is template design colour (kicker, big numbers, labels), not placeholders.
- **Visual inspection:** all six slides were rendered to PNG at 110 dpi and viewed, including a wider-font stress render (Arial in place of Nirmala UI) of slides 1 to 6. Slide 4's Technology box and slide 2's Evidence box were tight in the stress render and were shortened. Final renders of slides 1 to 5 are byte-identical to the viewed renders; slide 6 was re-rendered and viewed after its last text edit.
- **Not verified:** the deck has **not** been opened in PowerPoint. Nirmala UI is not installed on this Mac, so the renders use fallback fonts. Open it in PowerPoint and check each slide.

## 3. Claim audit results

`SLIDE_CLAIM_AUDIT.md` maps every statement to evidence or labels it target, estimate, portal or no-claim.

- **17.82 lakh (slide 2):** re-verified at the primary source today. The PIB PDF *Curbing Cyber Frauds in Digital India* (7 Oct 2025) says financial institutions "have been able to save more than ₹5,489 crore in over 17.82 lakh complaints" through CFCFRMS. The period is not stated. The deck says "PIB cites", "period not stated" and "not email-specific", and states that the email share is unpublished.
- **Removed:** Maharashtra 5.16 lakh / ₹7,592 crore, 24,02,579, CERT-In 29.44 lakh, "41,405 servers", "about 50 district cyber police stations". Nothing replaced them.
- **Retained limitations on slides:** internal validation only; no external pilot; no real-world accuracy benchmark; no government approval; not production-ready; missing login, audit log, encrypted storage, backups, concurrency fix.
- **Absent from the deck:** AI or ML claims, speed or cost claims, measured impact, Marathi, a live URL, contact details, mentor, qualification, partners, pilots, revenue.
- **Internal validation wording:** 1,521 tests and 98 controlled captures are labelled "internal validation" on slides 4 and 6.

### Cross-document consistency

| Check | Result |
|---|---|
| Name, sector and sub-theme: deck, answers, profile | Consistent: Siddhant Hiralal Patil; Law and Order; "Cyber-fraud, digital extortion and financial-crime intelligence" (deck states it does not itself provide intelligence). Spelling vs the portal not checked by me |
| Stage: deck, answers, profile, DEPLOYMENT.md | Working Prototype everywhere |
| 17.82 lakh wording: deck, answers, audit, SUBMISSION_EVIDENCE.md | Consistent ("cites", national, period not stated, not email-specific) |
| Test and capture counts | 1,521 and 98, labelled internal validation, in all |
| AI/ML | Not selected in answers; not claimed in deck or profile |
| Marathi | Not claimed in the deck. Profile and answers say "unreviewed" and untested |
| Deployment | All say no public deployment, no live URL; `DEPLOYMENT_GO_NO_GO.md` records NO-GO |
| Estimated number affected | Deck gives no count; answers say "no verified estimate" |
| Stale references | `_DRAFT` file name and "about 50" updated or flagged as removed in the checklist, answers and audit. The Phase C/E1 blueprint carries supersession notes |

## 4. Contributor flag (new, needs your decision)

While checking the claim "built by one developer" I found that git history outside this branch has other authors. In the earlier `pre-rebrand-main` history, `Dishita0526` (dishita.5260@gmail.com) authored a 29 Sep 2026 commit "feat: finalize frontend polish and theme updates" touching 48 files (4,330 insertions), and `Sidd_927` authored the very first commit. This branch's root commit (3 Oct 2026, "Initial commit: NyaySaakshya") is under your name, and the current `frontend/src` differs from that commit's tree in only about ten files. I do not know who this person is or what the arrangement is.

Consequences, none of which I have decided for you:

- The IP declaration and team-composition statement must be true. Ownership of that frontend work is for you to confirm.
- The deck says only "Applicant and team lead" and "No other team member, mentor, partner or funder is named". It makes **no** claim of sole authorship. I removed "developer of the prototype" and "built by one developer" for this reason.
- If that person is a collaborator, ask the helpdesk whether team composition can change; the team lead cannot (FAQ).

## 5. Remaining personal inputs (in one place)

**MUST (block submission)**

1. Contributor and IP position (section 4).
2. Conflict-of-interest declaration.
3. Consent to verification and due diligence.
4. Domicile confirmation (state) and certificate upload if the portal asks.
5. IP status and regulatory-dependency statements.
6. Single-submission declaration; final accuracy declaration.
7. Confirm the stored team-name spelling and your name spelling against the portal.
8. Open the PPTX in PowerPoint and check all six slides.
9. Decide: Citizens tick (optional, indirect) and AI/ML (recommended unticked).

**OPTIONAL:** contact line, qualification, mentor, photo, a demo video link. All are left out of the deck; see `USER_INPUT_REQUIRED.md`.

## 6. Portal answers for you to enter and declarations only you can make

- Enter the answers in `PORTAL_APPLICATION_ANSWERS.md` fields 1 to 14 after reading each field's limit. Key choices: stage Working Prototype; technology Mobile/web platform and Data analytics; advantages "New process/service model" plus an "Other" text; tested internally, not piloted; estimated number "no verified estimate" (numeric fallback `1`, your call); demo and website links blank.
- Replace the project profile with `PROFILE_FINAL_COPY.md`.
- **Declarations I did not and will not answer:** consent, conflict of interest, domicile, IP, regulatory dependencies, originality/single submission, accuracy, identity.

## 7. Deployment decision

**NO-GO** for public deployment (`DEPLOYMENT_GO_NO_GO.md`). Re-verified in source on 14 Oct: no authentication, shared SQLite connection, analysis time limit never enforced, no delete or audit route, container runs as root, Docker image unbuilt, fixture fallback and stale version labels present. The old Vercel site is a stale "SecureMailScope" build with no backend. A live URL is optional per the FAQ. Use a local demo and, optionally, a recorded synthetic demo.

## 8. Residual limitations that could affect evaluation

- Prototype only; no authentication, audit trail, encrypted storage or backups. Stated on slide 4.
- Validation is internal on controlled and mostly synthetic captures. No real-world accuracy figure and no external pilot.
- No live demo link, and the repository is private, so evaluators cannot open the code.
- Fit to the sub-theme "financial-crime intelligence" is partial: the tool supports the evidence-handling step and does not detect fraud or provide intelligence.
- Slide 2's premise that investigators "often" hold cut-off or encrypted captures is reasoned, not interviewed.
- The national 17.82 lakh figure is context, not a user count or email-specific.
- Estimated number affected: none, by design.
- Marathi reporting is an unreviewed machine draft and is untested; it is not claimed.
- Rendering checked in LibreOffice only; Nirmala UI absent.
- Speaker notes in the PPTX cite repository file names (for example `VALIDATION.md`); delete the notes in PowerPoint if you prefer.
- Novelty is not claimed as absolute.

## 9. Gate result

| Gate | Result |
|---|---|
| Exactly six slides, official template structure | PASS |
| No placeholders, DRAFT marks or guidance text | PASS |
| File non-empty, under 15 MB | PASS |
| Claims traceable; unverified statistics removed | PASS |
| Documents mutually consistent | PASS |
| Visual inspection (LibreOffice, plus wide-font stress) | PASS, **not in PowerPoint** |
| No frontend, scoring, rules or test changes | PASS |
| Personal declarations and contributor/IP position | **OPEN: needs you** |
| **Overall submission readiness** | **BLOCKED on personal inputs only** |
