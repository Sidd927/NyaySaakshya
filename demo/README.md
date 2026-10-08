# NyaySaakshya demo bundle

Everything needed to reproduce the NyaySaakshya demonstration from a clean checkout.
Nothing here is invented — every expected value in `expected/` was written
by `commands/generate_bundle.py` running the *actual, released* analysis pipeline, not typed by
hand.

## Contents

| Directory | Contents |
|---|---|
| `captures/` | symlinks to the canonical captures already in `research/experiments/` — **not copies**, so there is exactly one source of truth for each PCAP |
| `expected/` | one JSON manifest per scene, machine-generated, with the real posture, score, issue classes, abstentions, and coverage the system actually produced |
| `reports/` | pre-rendered JSON/HTML/PDF for the four scenes that need a rendered artifact on hand (Scene A, B, C, and the weak-certificate backup) |
| `hashes/SHA256SUMS.txt` | SHA-256 of every capture, computed directly against the real files |
| `environment/environment.json` | the Python/tshark/platform versions the bundle was generated against |
| `commands/` | `generate_bundle.py` (regenerates everything above), `run_scene.sh` (re-run one scene live), `start_demo.sh` (launch the backend + dashboard) |
| `evidence/` | `real_pcap_evidence_pack.json` — the capture-by-capture evidence inventory across the real corpus |

## Quick start

```bash
cd demo
bash commands/start_demo.sh        # backend + dashboard on http://127.0.0.1:8000/dashboard/
```

Then upload any file in `captures/` through the dashboard, or:

```bash
bash commands/run_scene.sh scene_a_1_benign_decline
```

## Scene index

| Scene | Capture | Expected posture | Expected score |
|---|---|---|---|
| A.1 — benign STARTTLS decline | `scene_a_1_benign_decline.pcap` | ADEQUATE | 88.0 |
| A.2 — genuine STARTTLS non-support | `scene_a_2_genuine_nonsupport.pcap` | ADEQUATE | 88.0 |
| B — certificate/evidence honesty (TLS 1.3) | `scene_b_certificate_honesty.pcap` | STRONG | 100.0 |
| C — `--no-ai` equivalence | `scene_c_no_ai_equivalence.pcap` | STRONG (identical with AI on/off) | 100.0 |
| Backup — weak certificate (generated fixture) | `backup_weak_certificate.pcap` | CRITICAL | 44.0 |
| Backup — self-signed certificate (generated fixture) | `backup_selfsigned_certificate.pcap` | ADEQUATE | 88.0 |
| Backup — healthy chain, negative control (generated fixture) | `backup_healthy_chain.pcap` | STRONG | 100.0 |
| Deep-dive — cross-session, control endpoint present | `deepdive_cross_session_control_endpoint.pcap` | CRITICAL | 22.15 |
| Deep-dive — cross-session, no control endpoint (the honest negative case) | `deepdive_cross_session_no_control.pcap` | CRITICAL | 34.15 |

Presenter-facing steps and fresh-machine setup are in [`RUNBOOK.md`](RUNBOOK.md).

**Regenerating this bundle:** run `PYTHONPATH=src python3 demo/commands/generate_bundle.py` from
the repository root. It is read-only with respect to `src/` and only writes into `demo/`.

The landing page, the evidence pack and the shipped sample reports embed pipeline results that this
script does not write. After any change that alters an assessment, also run
`PYTHONPATH=src python3 demo/commands/refresh_derived_artifacts.py` (it rebuilds
`frontend/src/fixtures/real_fixtures.json`, `demo/evidence/real_pcap_evidence_pack.json`, the i18n
sample reports and the bundled deep-dive sample from the real pipeline), then copy the printed
assessment ID and analysis time into `frontend/src/components/landing/reportSample.ts` and the fallback
runs in `frontend/src/context/InvestigationContext.tsx`.

**Scores changed in Phase B.2.** Scene A.2 moved 85.0 → 88.0 and Scene C moved 88.0 → 100.0 (STRONG).
Both captures begin with a two-frame fragment from the capture harness's own port-readiness probe; it
was being reported as a cleartext mail session and is no longer. The reason and the arithmetic are in
`VALIDATION.md` §6 (D1) and `tests/test_phase11_real_pcap.py`.
