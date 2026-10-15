# Final release audit

Phase H gate, 15 October 2026, on branch `design/landing-redesign` (starting commit `f798d8d`). Validation tag `v1.1.0-validation-baseline` still points at `c0f77b9`. I did not touch the portal: no login, no edit, no upload, no submission. No public deployment. No change to the frontend, backend, scoring, rules, evidence semantics or tests.

## Verdict

**READY WITH EXPLICIT APPLICANT INPUTS.**

All safe work is finished and verified. What remains is yours: factual answers about the IP/contributor position, the personal declarations, a PowerPoint check of the deck, and a few choices. None of these is a release defect. The earlier failing code-freeze test is fixed (section 5).

## 1. Deliverables

| File | Size | Note |
|---|---|---|
| `submission/seva-innovation-challenge-2026/NyaySaakshya_Seva_Innovation_Challenge_2026.pptx` | 227,561 bytes (0.23 MB) | **Submission file.** Six slides, official template, built from source by `build_deck.py` |
| `submission/seva-innovation-challenge-2026/NyaySaakshya_Seva_Innovation_Challenge_2026_PREVIEW.pdf` | 413,538 bytes (0.39 MB) | LibreOffice render, review only |
| `submission/seva-innovation-challenge-2026/build_deck.py`, `assets/screen_scored.png`, `assets/screen_withheld.png`, `reference/` (official template, unmodified) | | Reproducible build; screenshots are 2x crops of the real console |
| `docs/submission/PORTAL_FIELD_BY_FIELD_FINAL.md` | | **Definitive manual-entry guide**, 16 portal fields in order, character counts, fallbacks, selections, caveats |
| `docs/submission/PORTAL_APPLICATION_ANSWERS.md` | | Same answer text plus reasoning and the declarations table |
| `docs/submission/PROFILE_FINAL_COPY.md` | | One-liner 113 characters (limit 140) |
| `docs/submission/FINAL_DECK_RED_TEAM_REVIEW.md`, `FINAL_DECK_CLAIM_AUDIT.md`, `FINAL_DECK_CHANGELOG.md` | | Final deck pass: official applicant guide read, slide 3 architecture strip, concrete failure-and-fix, before/after framing, demo line; the deck-claim audit here supersedes the deck section of `PHASE_H_CLAIM_AUDIT.md` |
| `docs/submission/PHASE_H_RESEARCH_AND_EVALUATION.md`, `PHASE_H_CLAIM_AUDIT.md`, `PHASE_H_RED_TEAM_REVIEW.md`, `PHASE_H_BASELINE.md` | | Research, 36 deck claims audited, three-reviewer critique, baseline |
| `docs/submission/FINAL_SUBMISSION_CHECKLIST.md`, `USER_INPUT_REQUIRED.md`, `DEPLOYMENT_GO_NO_GO.md` | | Ordered checklist; applicant-only items; NO-GO re-confirmed |

Both files are far below the 15 MB limit reported for the portal.

## 2. Deck verification

- **Six slides**, in the official order, confirmed with `python-pptx` and the 6-page PDF; 16:9, 10 x 5.625 in.
- **No placeholders, DRAFT marks, template guidance, repo file names or internal notes**: a text scan of every shape and speaker note found 0 hits. Speaker notes now cite public sources only.
- **Text size:** body 9 to 12.5 pt, captions 8.5 pt, the template's footer 8 pt, headings 13.5 to 28 pt.
- **Rendering:** all six slides were rendered to PNG at 130 dpi in LibreOffice and viewed, in the default fallback font and in a wider-font stress render (Arial in place of Nirmala UI). Final-pass change: slide 4 now says "98 controlled lab captures: 10 from Postfix and Dovecot software in a lab" and "no real-world traffic", so "real" cannot be read as real-world data. Layout problems found (overlapping caption on slide 3, a wrapped ask on slide 6, tight boxes on slides 4 and 5, the kicker overlapped by the panel on slide 1) were fixed and re-rendered. A second renderer, macOS Quick Look, rendered slide 1 only. Keynote could not be driven by script, so there is no Keynote check.
- **Not done:** the deck was **never opened in Microsoft PowerPoint**. Nirmala UI is not installed on the build Mac. A PowerPoint check by you is required (checklist step 2).
- **Design:** official template header, footer, colours and font kept. Each slide has one message line, one visual structure, real product evidence (two enlarged real screen crops, a worked provenance example in native text), and limitations in labelled boxes.

## 3. Claims and research

- 36 deck claims audited in `PHASE_H_CLAIM_AUDIT.md`: 29 verified, 6 partially verified (qualified in the wording), 1 the applicant's own choice (support asks), 0 unsupported remaining.
- Official requirements established from the organiser's pages, the public page source and timeline graphic (`PHASE_H_RESEARCH_AND_EVALUATION.md`). New verified facts: Law and Order sub-theme 2 is exactly "Cyber-Fraud, Digital Extortion and Financial-Crime Intelligence"; demo and website links are optional; no live deployment is required; the final presentations are on **9 Dec at Nagpur** (press said 7 Dec); online presentations are 16 to 25 Nov; the one-line profile field is 140 characters; stage options carry TRL labels.
- Statistic: **17.82 lakh** re-read in the PIB PDF; period not stated; stated as non-email-specific. Removed: Maharashtra 5.16 lakh and ₹7,592 crore, 24,02,579, 29.44 lakh, "41,405 servers", "about 50 district cyber police stations", hosting prices, any AI/ML, Marathi, speed, cost and impact claims.
- "Open source" versus licence: resolved. Components are open source (licences read); NyaySaakshya's own licence is not chosen, and the deck says so.
- Differentiation is stated as a design strength, with the comparison limited to what Wireshark, Zeek and NetworkMiner documentation shows. Competitors not researched (commercial forensic suites, Suricata, Internet.nl) are marked UNKNOWN.

## 4. Cross-document consistency

| Check | Result |
|---|---|
| Name, sector, sub-theme, team size | Same in deck, answers, profile (portal not accessed; spelling to be checked by you) |
| Stage | "Working Prototype, lab-validated, no external pilot" everywhere; TRL option choice left to you |
| 17.82 lakh | Same wording and qualifiers in deck, answers, audit, evidence file |
| Test and capture counts | 1,521 tests (labelled "tests", never "passing"), 98 captures (10 + 6 + 82), 13,822 frames; internal validation everywhere |
| AI/ML | Not selected, not claimed |
| Marathi | Not claimed anywhere |
| Deployment | NO-GO and no live URL everywhere; demo and website links blank |
| Finals date | 9 Dec in `SUBMISSION_EVIDENCE.md` and `DEPLOYMENT_GO_NO_GO.md`; the older blueprint is marked fully superseded |
| Estimated number affected | None in the deck; "no verified estimate" in the answers |
| `build_deck.py`, deck notes, audit | Reference the same files |

## 5. Validation suite and the code-freeze guard

- **The guard:** `tests/test_backend_architecture.py` diffs `HEAD` against `FREEZE_BASELINE_TAG`; protected packages (`posture/`, `analysis/`, `crosssession/`, `ml/`, `session/`, `evidence/`, `dissect/`, `ingest/`) may not change after that tag except where a guard declares it. It pointed at `v1.0.0-nyaysaakshya` (3 Oct 2026, the original import).
- **Why it failed:** Phase B (`VALIDATION.md`) made reviewed fixes to 16 protected files, committed as `c0f77b9` (`v1.1.0-validation-baseline`). During Phase B.4 those fixes were uncommitted, and `git diff <tag> HEAD` ignores the working tree, so the guard passed and the suite was reported as 1,521 passed. Once committed, the guard correctly saw them and failed. Between `690d271` and `c0f77b9` the protected packages changed; between `c0f77b9` and the final branch they did not (0 changed files in `src` and `tests`).
- **Is the reference stale, and does the fix keep the protection?** Yes, stale: the validated baseline is the later tag. The fix changes one constant and adds a comment; the protected-package list and every assertion are unchanged. A probe edit to `posture/scoring.py` committed in a scratch worktree made `test_phase_seven_source_changes_only_where_declared` fail again, so the guard still bites. The probe worktree was removed.
- **Results on the final branch:** the 22 architecture tests: 22 passed. Full suite `PYTHONPATH=src python3 -m pytest -q`: **1,521 passed, 0 failed, 0 skipped** (95 s). Before the fix: 1,520 passed, 1 failed. No assertion was weakened, no test disabled, no behaviour, scoring or rule changed. `README.md` and `VALIDATION.md` ("1521 passed, 0 failed") are now accurate.
- Local demo re-run: flagship capture CRITICAL 22.15 (`afa30ff290742813`), cut-handshake capture INSUFFICIENT_EVIDENCE (`870e1edcae99f7da`), identical IDs to 14 Oct; JSON, HTML and PDF reports exported for both.

## 6. Personal inputs, declarations and decisions (yours)

Full list: `USER_INPUT_REQUIRED.md`. In short:

1. **IP and contributor facts**: Dishita's frontend help (permission, assignment or licence, acknowledgement, any employer or college claim, whether `Sidd_927` is yours). She is **not** added as a team member.
2. **Declarations, never answered by me:** consent to verification, conflict of interest, domicile, IP status, regulatory dependencies, originality and single submission, final accuracy.
3. Domicile certificate in hand; name and team-name spelling checked against the portal.
4. Choices: stage label, estimated-number entry, Citizens tick, AI/ML unticked, funding ask.
5. Open the PPTX in PowerPoint; read each portal field's limit and mandatory flag.
6. Optional credibility: qualification, real mentor, contact line, photo.

## 7. Deployment decision

**NO-GO** for public deployment. `src/` is unchanged since the 14 Oct check; blockers stand: no authentication or case isolation, shared SQLite connection, analysis time limit never enforced, no delete or audit route, no encryption at rest, container runs as root, TShark not sandboxed, Docker image unbuilt, fixture fallback and stale version labels. A live URL is optional per the official FAQ and no deployment is required. The old Vercel site is stale and has no backend; the repository is private. Use a local synthetic demo for the presentation stages (16 to 25 Nov and 9 Dec). **No demo video exists**; a storyboard and recording plan are in `DEPLOYMENT_GO_NO_GO.md`.

## 8. Git and `main`

- Work is on `design/landing-redesign`; commits are normal and pushed without force; no Claude co-author trailer; `v1.1.0-validation-baseline` is untouched (still `c0f77b9`).
- **Gate for updating `main`:** (a) full suite 1,521 passed, 0 failed on the final branch; (b) `main` (`22bcd7d`) is an ancestor of the branch, so a plain fast-forward is possible; (c) `git diff --name-status main..HEAD` shows 102 added and 84 modified files, **0 deleted or renamed**, from 16 commits: landing-redesign phases 1 to 5, the Phase B validation fixes (`c0f77b9`), deployment and submission documents, research experiments, and the submission deck; (d) a scan of all changed text files for private keys and common token patterns found none; (e) the frontend builds (`npm run build`); (f) the repository is private. **Outcome:** `main` was fast-forwarded from `22bcd7d` to `d07463a` (the branch head at that moment) and pushed normally; no force, no history rewrite. Only this audit file and the final report differ after that point.
- Privacy: the Phase G version of this file (already on the private remote) quoted a third party's email address. It is not repeated in any new file. History is not rewritten. The repository is **private** (checked with the GitHub CLI), which is the least disruptive protection; do not make it public without scrubbing history, or if you do, rewrite history deliberately with her knowledge.

## 9. Residual limitations that could affect evaluation

Weak fit to a sub-theme that names "intelligence"; the premise that investigators face these captures is a hypothesis and no investigator was consulted; validation is internal and mostly in-project synthetic (82 of 98); no real-world accuracy, no pilot, no partner; no estimated number affected; a solo applicant with no stated qualification; no live link and a private repository; the prototype lacks authentication, audit, encryption and backups; inconsistent version labels in the UI and reports; Marathi report unreviewed; rendering not checked in PowerPoint.

## 10. Gate result

| Gate | Result |
|---|---|
| Official template and six slides | PASS |
| Portal answers complete and consistent with the deck | PASS |
| Statistics and technical claims evidenced or qualified | PASS |
| Identity, individual status, sector, sub-theme | PASS against the applicant's transcription (portal not accessed) |
| No placeholder, draft mark or invented claim | PASS |
| Licensing and open-source wording | PASS |
| Deployment recommendation explicit | PASS (NO-GO) |
| Personal declarations and inputs listed | PASS |
| PPTX and PDF generated and inspected | PASS (LibreOffice; slide 1 also Quick Look; **not PowerPoint**) |
| Validation suite | PASS: 1,521 passed, 0 failed (stale freeze guard re-baselined) |
| Git: committed and pushed | See the final report |
| `main` updated | YES: fast-forward `22bcd7d` to `d07463a`, pushed |
| **Overall** | **READY WITH EXPLICIT APPLICANT INPUTS** |
