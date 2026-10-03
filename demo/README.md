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
| A.2 — genuine STARTTLS non-support | `scene_a_2_genuine_nonsupport.pcap` | ADEQUATE | 85.0 |
| B — certificate/evidence honesty (TLS 1.3) | `scene_b_certificate_honesty.pcap` | STRONG | 100.0 |
| C — `--no-ai` equivalence | `scene_c_no_ai_equivalence.pcap` | ADEQUATE (identical with AI on/off) | 88.0 |
| Backup — weak certificate (generated fixture) | `backup_weak_certificate.pcap` | CRITICAL | 44.0 |
| Backup — self-signed certificate (generated fixture) | `backup_selfsigned_certificate.pcap` | ADEQUATE | 88.0 |
| Backup — healthy chain, negative control (generated fixture) | `backup_healthy_chain.pcap` | STRONG | 100.0 |
| Deep-dive — cross-session, control endpoint present | `deepdive_cross_session_control_endpoint.pcap` | CRITICAL | 22.15 |
| Deep-dive — cross-session, no control endpoint (the honest negative case) | `deepdive_cross_session_no_control.pcap` | CRITICAL | 34.15 |

Presenter-facing steps and fresh-machine setup are in [`RUNBOOK.md`](RUNBOOK.md).

**Regenerating this bundle:** run `PYTHONPATH=src python3 demo/commands/generate_bundle.py` from
the repository root. It is read-only with respect to `src/` and only writes into `demo/`.
