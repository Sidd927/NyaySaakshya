"""
Phase B.3: what "reproducible" means here, measured. For the flagship capture and for a capture
cut inside the TLS handshake, the pipeline is run twice with identical configuration and every
layer is compared; then the same capture is analysed under a changed analyser version and the
two assessments are compared to show that they are NOT presented as the same assessment.

    PYTHONPATH=src python3 research/experiments/phaseb/repro_check.py
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))

from nyaysaakshya.backend.pipeline import run_pipeline                # noqa: E402
from nyaysaakshya.posture import engine as posture_engine            # noqa: E402
from nyaysaakshya.reporting.service import render_bytes              # noqa: E402

CASES = {
    "flagship_deepdive": os.path.join(ROOT, "demo", "captures", "deepdive_cross_session_control_endpoint.pcap"),
    "cut_inside_handshake": os.path.join(ROOT, "research", "experiments", "oq46_47", "oq46", "E_cut_during_handshake.pcap"),
}
FIELDS = ["starttls_advertised", "starttls_requested", "starttls_accepted", "tls_transition",
          "tls_negotiated_version", "tls_cipher_suite_name", "tls_key_exchange", "tls_forward_secrecy",
          "tls_certificate_chain", "plaintext_continuation", "auth_activity"]
TIMES = re.compile(rb"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z")


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def evidence(r):
    return [{f: [getattr(s, f).state.value, getattr(s, f).value, list(getattr(s, f).frames), getattr(s, f).basis]
             for f in FIELDS} | {"stream": s.tcp_stream_id, "completeness": s.completeness.value} for s in r.sessions]


def untime(a):
    return {k: v for k, v in a.items() if k not in ("generated_at", "run_id")}


def one(path):
    r1, r2 = run_pipeline(path), run_pipeline(path)
    a1, a2 = r1.assessment.to_dict(), r2.assessment.to_dict()
    j = lambda x: json.dumps(x, sort_keys=True, default=str)   # noqa: E731
    out = {
        "capture_sha256": [sha(path), sha(path)],
        "evidence_equal": j(evidence(r1)) == j(evidence(r2)),
        "findings_equal": j([f.to_dict() for f in r1.findings + r1.cross_findings]) == j(
            [f.to_dict() for f in r2.findings + r2.cross_findings]),
        "posture_equal": a1["overall_posture"] == a2["overall_posture"],
        "score_equal": a1["score"] == a2["score"],
        "assessment_id_equal": a1["assessment_id"] == a2["assessment_id"],
        "assessment_equal_except_time_and_run": j(untime(a1)) == j(untime(a2)),
        "provenance_equal": j([(f.rule_id, f.tcp_stream_id, [list(e.frames) for e in f.evidence_refs])
                               for f in r1.findings]) == j(
            [(f.rule_id, f.tcp_stream_id, [list(e.frames) for e in f.evidence_refs]) for f in r2.findings]),
        "reports_equal_except_timestamp": {},
    }
    for fmt, lang in (("html", "en"), ("html", "mr"), ("json", "en")):
        b1 = TIMES.sub(b"T", render_bytes(a1, fmt, lang)[0])
        b2 = TIMES.sub(b"T", render_bytes(a2, fmt, lang)[0])
        out["reports_equal_except_timestamp"][f"{fmt}/{lang}"] = b1 == b2
    # same capture, changed analyser version
    original = posture_engine.POSTURE_ENGINE_VERSION
    posture_engine.POSTURE_ENGINE_VERSION = "99.0.0"
    try:
        a3 = run_pipeline(path).assessment.to_dict()
    finally:
        posture_engine.POSTURE_ENGINE_VERSION = original
    out["changed_analyser_version"] = {
        "assessment_id_differs": a3["assessment_id"] != a1["assessment_id"],
        "versions_recorded": [a1["versions"], a3["versions"]],
        "outcome_unchanged": (a3["overall_posture"], a3["score"]) == (a1["overall_posture"], a1["score"]),
    }
    return out


def main() -> None:
    result = {name: one(path) for name, path in CASES.items()}
    os.makedirs(os.path.join(HERE, "results", "phase_b3"), exist_ok=True)
    with open(os.path.join(HERE, "results", "phase_b3", "repro_check.json"), "w") as fh:
        json.dump(result, fh, indent=1)
    print(json.dumps(result, indent=1))


if __name__ == "__main__":
    main()
