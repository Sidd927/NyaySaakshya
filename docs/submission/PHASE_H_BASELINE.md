# Phase H baseline

Recorded 15 October 2026, 00:53 IST, before any Phase H change.

## Repository state

| Item | Value |
|---|---|
| Directory | `/Users/siddhant_patil/Projects/NyaySaakshya` (NyaySaakshya; not another project) |
| Branch | `design/landing-redesign`, tracking `origin/design/landing-redesign` |
| Latest commit | `f798d8d` "docs: finalize Seva submission deck, profile copy and release audit" (after `e24cae7`, `ed1718a`, `e62cb21`) |
| Working tree | **Clean** (`git status --short` empty). No pre-existing user changes to preserve |
| Validation tag | `v1.1.0-validation-baseline` -> `c0f77b9` (unchanged) |
| `main` | `22bcd7d`, an **ancestor** of the branch: 0 commits on `main` not on the branch, 13 on the branch not on `main` |
| Diff vs `main` | 183 files, +65,436 / -1,200 (validation fixes and evidence, landing redesign, docs, research experiments, submission files) |
| Authors on this branch | 19 commits, all Siddhant Patil. Other authors (Dishita's GitHub account, `Sidd_927`) exist only in the older `pre-rebrand-main` history |

## Artifacts inspected

| Artifact | Path | State at baseline |
|---|---|---|
| Final deck | `submission/seva-innovation-challenge-2026/NyaySaakshya_Seva_Innovation_Challenge_2026.pptx` | 6 slides, 125,082 bytes; built by `build_deck.py` from the official template |
| Preview PDF | `..._PREVIEW.pdf` | 6 pages, 347,111 bytes; LibreOffice render |
| Official template copy | `submission/seva-innovation-challenge-2026/reference/Seva_Innovation_Challenge_2026_Presentation_Template.pptx` | Unmodified |
| Screenshots | `submission/seva-innovation-challenge-2026/assets/` | Two 774 px crops from 14 Oct (replaced in Phase H with 2x crops) |
| Demo captures | `demo/captures/*.pcap` (9 files, hashes in `demo/hashes/SHA256SUMS.txt`); insufficient-evidence case at `research/experiments/oq46_47/oq46/E_cut_during_handshake.pcap` | Present |
| Phase F and G docs | `docs/submission/*.md`, `SLIDE_CLAIM_AUDIT.md`, `SUBMISSION_EVIDENCE.md`, `VALIDATION.md`, `DEPLOYMENT.md`, `README.md` | Read |

## Findings at baseline that change the plan

1. **Test suite is not "1,521 passed".** Running the full suite on a clean `f798d8d` gives **1,520 passed, 1 failed** (95 s). The failure is `tests/test_backend_architecture.py::test_phase_seven_source_changes_only_where_declared`, a code-freeze guard that diffs against the old tag `v1.0.0-nyaysaakshya`. It passed during Phase B.4 only because the Phase B fixes were still uncommitted (`git diff <tag> HEAD` ignores the working tree); once committed as `c0f77b9`, 16 protected files differ from that tag and the guard fails. It is not a behaviour test. `VALIDATION.md` and `README.md` still say "1521 passed, 0 failed". Not fixed here (see `PHASE_H_CLAIM_AUDIT.md`). A scratch copy of the test file with the baseline tag re-pointed to `v1.1.0-validation-baseline` passed all 22 architecture tests; the repository's test file was not touched.
2. **Official finals date.** The official timeline graphic says final presentations at Nagpur on **9 Dec 2026**. Earlier documents said 7 Dec (from press; the Free Press Journal article still says 7 Dec). Corrected in `SUBMISSION_EVIDENCE.md` and `DEPLOYMENT_GO_NO_GO.md`.
3. **Official sub-theme exists.** The organiser's page source lists Law and Order sub-theme 2 as "Cyber-Fraud, Digital Extortion and Financial-Crime Intelligence" (previously UNKNOWN).
4. **Stage options carry TRL labels** in the public profile wizard: "Working prototype (TRL 5-6)". See the answers file.
5. **One-line profile field is limited to 140 characters** (public wizard code). The Phase G one-liner was about 150.
6. `faq.html` on the organiser's site returns HTTP 404; the FAQ is on the home page.
7. The `v1.0.0` freeze guard, the stale "Engine Live 0.8.0" label, and report generator "0.9.0" versus engine 0.10.0 are known version-label inconsistencies.

**Resolved in the final execution pass (15 Oct 2026):** the guard's baseline tag was re-pointed to `v1.1.0-validation-baseline` (comment added in the test file), a probe edit in a scratch worktree still failed the guard, and the full suite then passed: 1,521 passed, 0 failed. See `FINAL_RELEASE_AUDIT.md` section 5.

## Scope for Phase H

Research, deck redesign inside the official template, answers, claim audit, red-team review, release audit, commit and push. No change to the frontend, backend, scoring, rules, tests or validation baseline. No deployment.
