# Deployment go / no-go: Seva submission

Assessed 14 October 2026 on branch `design/landing-redesign` at `ed1718a`. Validation tag `v1.1.0-validation-baseline` still points at `c0f77b9`. Working tree was clean at the start.

## Decision: **NO-GO** for a public live deployment

Use a local demonstration, the two verified screenshots and a short recorded demo (synthetic captures only). A live URL is optional on the portal, so skipping it costs no mandatory requirement.

Reasons, in short:

1. The portal does not require a live URL (section 1).
2. Every blocker found in Phase C is still present in the source today (section 3).
3. The application that would be exposed accepts arbitrary file uploads, has no authentication and lists every run to anyone who can reach it. No small change makes that safe in the 2.5 days left, and the brief rules out exposing an unauthenticated analysis API.
4. A public instance adds risk (a defaced or crashed demo, a stray real capture uploaded by someone) and no marked benefit: the evaluators' stated criteria and the FAQ treat links as optional.

## Phase H re-confirmation (15 Oct 2026)

**Still NO-GO.** `src/` is unchanged since the 14 Oct check (`git log` shows no source commits after `c0f77b9`), so every blocker below stands. Re-run today on the local console and backend (127.0.0.1, scratch data directory, synthetic captures): flagship CRITICAL 22.15 (assessment ID `afa30ff290742813`) and the cut-handshake capture INSUFFICIENT_EVIDENCE (`870e1edcae99f7da`), identical IDs to 14 Oct; JSON, HTML and PDF reports exported for both. No live URL is required by any official page (FAQ: demo and website links are optional). The official timeline shows online presentations of selected applications on 16 to 25 Nov 2026 and final presentations at Nagpur on 9 Dec 2026 (press says 7 Dec): a reliable **local** synthetic demo is the right preparation for those stages. The repository is private and the old Vercel site is stale. No video exists. Test suite (final pass): 1,521 passed, 0 failed after the stale code-freeze guard was re-baselined; see `FINAL_RELEASE_AUDIT.md`.

## 1. Answers to the ten questions

| # | Question | Answer | Evidence |
|---|---|---|---|
| 1 | Is a live URL required by the portal? | **No, optional.** | Public FAQ: "You can provide a prototype/demo link or website/product link, where available. These links are listed as optional in the applicant manual." The Phase F brief's screenshot transcription lists both fields without a mandatory marker; **the portal's own required-field markers were not seen**, so confirm on the form. |
| 2 | Is a demo video or local demo enough? | **Yes for submission.** The pitch deck is the mandatory item (FAQ: "Is uploading a pitch presentation mandatory? Yes"). A local demo is enough for the later stages: the official timeline graphic shows online presentations of selected applications on 16 to 25 Nov 2026 and final presentations at Nagpur on 9 Dec 2026 (the earlier "7 Dec" came from press and is superseded). | FAQ, guidelines. |
| 3 | Risks of public deployment now? | See section 3. | Source inspection, below. |
| 4 | Smallest safe demo configuration? | **Local only**: backend bound to `127.0.0.1`, local frontend, synthetic captures only. This is what was run today. | Section 6. |
| 5 | Can it be limited to synthetic captures and fixed test cases? | **Locally, yes, by procedure** (bundled `demo/captures/*`). **Publicly, no**: nothing in the service restricts uploads to those files. The API accepts any file up to 256 MB (default `max_upload_bytes` 268,435,456 in `/health` today). | Health output, `limits.py`. |
| 6 | Can fixture fallback be eliminated or disclosed? | **Disclosed, not eliminated.** The UI shows "Demo Fixture" (amber) versus "Engine Live" (green) in the header (`Header.tsx:123`). The fallback is compiled into the frontend (`InvestigationContext.tsx`: `isUsingFixtures`). Removing it needs a frontend change, out of scope for this phase. For the demo, start with the backend up and confirm the pill says "Engine Live". | Source. |
| 7 | Are API uploads and outputs protected appropriately? | **No.** No authentication or authorization anywhere in `backend/` (grep for auth, bearer, API key, `Depends(` auth: no match). `GET /api/v1/analyses` lists all runs with no credentials (verified: 3 runs returned to an unauthenticated request). CORS is opt-in and is not access control. | `api.py`, run today. |
| 8 | Does it store captures, and where? | **Yes.** Each upload is written, hashed and kept in a content-addressed artifact store under `SMS_DATA_DIR` (Docker: `/data`; locally `./nyaysaakshya-data`, which is git-ignored). Reports are cached there. There is **no delete API**: nothing removes evidence. No encryption at rest. On Render's free plan `/data` is ephemeral and lost on restart. Observed today: `/tmp/f_data/artifacts/` and `securemailscope.db` created by two uploads. | `artifacts.py`, `render.yaml`, run today. |
| 9 | Does the current public demo run the latest code? | **No.** `secure-mail-scope-psi.vercel.app` serves a page titled "SecureMailScope: Cryptographic Security Posture Assessment", with a cached response about 12 days old, and `/api/v1/health` returns **404**: no backend is behind it. No Render service URL is recorded in the repo, and README says "Live demo: URL to be added after redeployment". | `curl` today, `README.md:9`. |
| 10 | Can it be demonstrated reliably without a new production claim? | **Yes, locally.** Verified in section 6. Say "prototype, synthetic captures, local run". | Section 6. |

## 2. Is deployment likely to materially improve the application?

Unlikely. Evaluation stages (FAQ): administrative scrutiny, two independent online evaluations, technical and impact assessment, finalist validation, Grand Jury. The press-reported criteria include technological maturity and deployability, but the official pages show no weights and **no requirement for a live link**. A recorded demo plus the deck's honest "not yet built" box serves the same purpose. A public link that evaluators open to find "Demo Fixture" or a failing upload would cost more than it adds.

## 3. Risks, re-verified from current source (14 Oct 2026)

| Blocker (Phase C) | Still true? | Evidence today |
|---|---|---|
| No authentication or case isolation | **Yes** | No auth code in `backend/`; unauthenticated `GET /analyses` returned all runs. |
| SQLite shared connection (TECH-DEBT #10) | **Yes** | `backend/db.py:105`: `sqlite3.connect(path, check_same_thread=False, ...)`, one shared connection. |
| Analysis time limit not enforced | **Yes** | `AnalysisTimeout` is defined in `errors.py` and never raised; `max_analysis_seconds` only appears in `limits.py`. Only the TShark timeout (300 s) is enforced. |
| No audit trail, retention, deletion or backup | **Yes** | No delete route in `api.py` (GET and POST only); no audit-log code. |
| TShark not sandboxed; container runs as root | **Yes** | `Dockerfile` has no `USER` line; TShark parses untrusted bytes as the API user. |
| Docker image not built or validated | **Yes** | The `Dockerfile` was last changed in an older commit; no evidence of a build in the validation record. Its comment says TShark 4.6.6 from the PPA; the golden cases were set on 4.6.8 (installed here: 4.6.8). |
| Fixture / demo-mode confusion | **Yes** | `Header.tsx:123`, `WorkbenchView.tsx:196`. |
| Stale version labels | **Yes** (new finding) | The workbench shows "Engine Live · 0.8.0"; reports say generator 0.9.0; the engine is 0.10.0; `/health` reports backend 0.1.0. Visible in any recording. |
| Duplicate upload creates a CANCELLED run row (new finding, observed) | **Yes** | Re-uploading an identical capture returned the original run (`replayed: true`) but the run list then showed an extra run in state `CANCELLED`. Cosmetic, but avoid re-uploading the same file in a recording. Not fixed here, since this phase must not change the system under test. |

Public-exposure risks: anyone can upload any file (including real or hostile captures) for a root-run parser; every upload is stored and listable by anyone; free-tier instance wipes data; a free-tier cold start stalls a live evaluator for tens of seconds. None can be mitigated without code or infrastructure changes.

## 4. Why not CONDITIONAL GO

The shortest safe public configuration would need all of: authentication in front of the API (at least a shared secret enforced at a reverse proxy), an upload allow-list restricted to the bundled captures, a non-root image build and a test run, the pipeline timeout enforced, and removal of the stale Vercel site. That is more than a bounded fix, touches frozen modules (`__main__.py` is test-enforced as frozen) and external infrastructure, and none of it is necessary for submission. **If it is wanted after the deadline for finals,** treat it as the pilot-hardening work in `DEPLOYMENT.md`, not a quick demo deploy. No infrastructure was created, changed or contacted in this phase.

## 5. What not to say

Do not call the system "deployed", "production-ready" or "secure", and do not say captures "stay within a cyber cell" for any hosted instance. The statement that evidence stays local describes a **proposed** on-premise design, not an existing deployment.

## 6. Verified local demo (run 14 Oct 2026)

Everything below was executed on this machine (Python 3.9.6, TShark 4.6.8). Output was not edited.

Start the backend (loopback only, scratch data directory):

```bash
PYTHONPATH=src python3 -m nyaysaakshya.backend --host 127.0.0.1 --port 8016 --data-dir /tmp/f_data
```

Health returned `status: ok`, `tshark: available`, `posture_engine_version: 0.10.0`, `posture_schema_version: 1.1`.

| Step | Capture | Result observed | Notes |
|---|---|---|---|
| 1. Representative analysis | `demo/captures/deepdive_cross_session_control_endpoint.pcap` (SHA-256 `97b2b61a…140e216d`, listed in `demo/hashes/SHA256SUMS.txt`) | **CRITICAL, score 22.15**, 12 of 12 sessions assessed, assessment ID `afa30ff290742813`, run state COMPLETED, 268 ms | Same numbers as the slide 1 screenshot, so that screenshot is from the current build. Re-uploading gave the same assessment ID. |
| 2. Insufficient-evidence case | `research/experiments/oq46_47/oq46/E_cut_during_handshake.pcap` (SHA-256 `7a4a82bb…079d3b9`, tracked in git, not in `demo/captures/`) | **INSUFFICIENT_EVIDENCE**, `scored: false`, `value: null`, 0 of 1 sessions assessed, assessment ID `870e1edcae99f7da` | Basis text: "posture is not graded rather than graded well, because absence of evidence is not evidence of security". A second withheld case, `research/experiments/oq36/corpus/genC/C19_truncated.pcap`, gave the same result via the service. |
| 3. Report export | Both runs | `GET /api/v1/analyses/{run_id}/reports/{json,html,pdf}` returned JSON (73,654 B and 10,114 B), HTML (42,236 B and 19,896 B) and PDF (28,709 B and 14,293 B), all valid file starts | Marathi (`?lang=mr`) was **not** exercised. Do not demo Marathi. |
| 4. Limits of the evidence | Both runs | Every assessment carries the limitations list ("no attacker, intent or attribution is or can be established…"; "absence of a STARTTLS advertisement is ambiguous…") | Point at it in the report. |

Other bundled scenes also ran through `demo/commands/run_scene.sh`: `scene_a_1` ADEQUATE 88.0, `scene_a_2` ADEQUATE 88.0, `scene_b` STRONG 100.0, `scene_c` STRONG 100.0, `backup_weak_certificate` CRITICAL 44.0, `deepdive_cross_session_no_control` CRITICAL 34.15. Per-scene expected values are in `demo/expected/`. Not compared line by line here.

**Gap.** The withheld capture lives under `research/`, not `demo/captures/`. Proposed (not done, since it changes the demo bundle and its hash list): copy it to `demo/captures/` and add its hash to `SHA256SUMS.txt`. Until then, use the repo path above.

The server and the scratch data directory (`/tmp/f_data`, `/tmp/f_*.{json,html,pdf}`) are not part of the repository. The server was stopped after the checks.

## 7. Demo script and recording plan (a video does **not** exist yet)

No video has been created or inspected. Reproduction plan for a 3 to 4 minute screen recording, synthetic data only:

**Before recording**

1. Fresh scratch data directory; start the backend as above on `127.0.0.1`.
2. `cd frontend && npm run dev` (needs a proxy to the backend port; see `frontend/vite.config.ts` and `demo/RUNBOOK.md`, which uses 8001 by default).
3. Confirm the header pill says **Engine Live**, not "Demo Fixture". If it says Demo Fixture, stop: the backend is not connected.
4. Upload each file **once only** (a repeat adds a CANCELLED row). Close other windows and notifications. Browser at 1440 px width.
5. Do not show the "Engine Live · 0.8.0" label close up, or say that version labels in the prototype are not yet consistent.

**Storyboard**

| Time | Screen | Say |
|---|---|---|
| 0:00 | Title slide, then console | "NyaySaakshya is a prototype. It reads a saved capture of email traffic and says what the capture does and does not prove. These are synthetic lab captures." |
| 0:20 | Upload `deepdive_cross_session_control_endpoint.pcap` | "I upload one capture. It gets a SHA-256 fingerprint." |
| 0:45 | Result: CRITICAL 22.15, 12 sessions | "A score appears only because the evidence supports one." |
| 1:15 | Findings, open one finding | "Each finding names its packets and its evidence state: observed, inferred, unknown, ambiguous, incomplete or not observable." |
| 1:50 | Upload `E_cut_during_handshake.pcap` | "Now a capture that ends in the middle of a TLS handshake." |
| 2:15 | Result: Not scored, reason shown | "No score. Absence of evidence is not evidence of security. The tool says why and does not guess." |
| 2:45 | Download the HTML report | "A report carries the capture's SHA-256 and a reproducible assessment ID. The same capture and software give the same ID." |
| 3:15 | Limitations section | "It cannot name an attacker, prove fraud or decrypt TLS." |
| 3:30 | Slide 4 "not yet built" box | "This is a working prototype. It needs login, an audit log, encrypted storage and backups before any pilot. We are seeking one supervised pilot." |

**Rules for the recording:** synthetic captures only; do not show any file path outside this repository; do not narrate numbers that are not on screen; do not claim speed, accuracy or deployment. Record with the macOS screen recorder (Cmd+Shift+5); trim in QuickTime. Inspect the finished file frame by frame before it goes anywhere. Upload it as **unlisted**, and only if you choose to fill the optional demo-link field. Any upload is an outward-facing act and is yours to approve.

## 8. If a live URL is wanted later

Out of scope before 17 October. After submission, the order of work is in `DEPLOYMENT.md` (P0 list): authentication and roles, enforce the pipeline timeout, non-root image build with a test run, a fix for TECH-DEBT #10, audit log, encrypted storage and backups, then a supervised pilot on-premise. Do not skip to a public host.
