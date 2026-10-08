"""
Phase B.4: the final, small semantic acceptance matrix. Nine canonical cases through the real
pipeline, then the machine-readable contract check on the three the brief names.

    PYTHONPATH=src python3 research/experiments/phaseb/final_matrix.py

Writes research/experiments/phaseb/results/phase_b4/matrix.json. Asserts nothing; the judgement is
in VALIDATION.md §15 and in tests/test_semantic_contract.py.
"""
from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "tests"))

from fastapi.testclient import TestClient                          # noqa: E402

from nyaysaakshya.analysis.model import FindingStatus              # noqa: E402
from nyaysaakshya.backend.api import create_app                    # noqa: E402
from nyaysaakshya.backend.pipeline import run_pipeline             # noqa: E402
from nyaysaakshya.backend.service import AnalysisService           # noqa: E402

import b3_snapshot                                                 # noqa: E402

EXP = os.path.join(ROOT, "research", "experiments")
CONCLUSION = (FindingStatus.OBSERVED_ISSUE, FindingStatus.COMPLIANT)


def cases(tmp):
    from test_evidence_integrity import _scapy_capture
    http = _scapy_capture(tmp, "http.pcap", 80, [b"POST /login HTTP/1.1\r\n\r\nuser=a&pass=b"],
                          [b"HTTP/1.1 200 OK\r\n\r\n"])
    return {
        "A complete cleartext": f"{EXP}/oq33r/out/postfix_smtp_plaintext_session.pcap",
        "B complete TLS (TLS 1.3, implicit)": f"{ROOT}/demo/captures/scene_b_certificate_honesty.pcap",
        "C STARTTLS accepted, capture ends": f"{EXP}/oq36/corpus/genC/C19_truncated.pcap",
        "D ClientHello incomplete": f"{EXP}/oq46_47/oq46/E_cut_during_handshake.pcap",
        "E ServerHello, then capture ends": f"{EXP}/oq28/pcaps/K_network_cond.pcap",
        "F tiny fragment (+ one real session)": f"{EXP}/oq33r/out/postfix_smtp_starttls_upgrade.pcap",
        "G unsupported HTTP": http,
        "H unsupported raw TLS": f"{EXP}/p11cert/out/tls12_weak_sha1_rsa1024.pcap",
        "I flagship deep-dive": f"{ROOT}/demo/captures/deepdive_cross_session_control_endpoint.pcap",
    }


def describe(path):
    r = run_pipeline(path)
    a = r.assessment.to_dict()
    first = r.sessions[0]
    by_stream = {}
    for f in r.findings:
        by_stream.setdefault(f.tcp_stream_id, []).append(f)
    concl = sorted({f"{f.rule_id}:{f.status.value}" for f in r.findings if f.status in CONCLUSION})
    ev = lambda s, n: f"{getattr(s, n).state.value}" + (f"={getattr(s, n).value}" if getattr(s, n).value is not None else "")  # noqa: E731
    lim = sorted({l for f in r.findings if f.status in CONCLUSION for l in f.limitations
                  if "complete session" in l})
    return {
        "scope": sorted({s.protocol or "unsupported" for s in r.sessions}),
        "sessions": len(r.sessions), "tls_state": sorted({s.tls_state.value for s in r.sessions}),
        "completeness": sorted({s.completeness.value for s in r.sessions}),
        "evidence_session0": {n: ev(first, n) for n in ("starttls_accepted", "tls_transition",
                                                         "tls_negotiated_version", "tls_forward_secrecy",
                                                         "tls_certificate_chain")},
        "conclusive_findings": concl,
        "findings_without_conclusion": sorted({f"{f.rule_id}:{f.status.value}" for f in r.findings
                                               if f.status not in CONCLUSION})[:12],
        "assessed": f"{a['coverage']['sessions_assessed']}/{a['coverage']['sessions_total']}"
                    + (f" (+{a['coverage']['sessions_unsupported']} unsupported)" if a["coverage"].get("sessions_unsupported") else ""),
        "posture": a["overall_posture"], "scored": a["score"]["scored"], "score_value": a["score"]["value"],
        "scope_note_on_conclusions": lim,
    }


def main() -> None:
    tmp = tempfile.mkdtemp(prefix="sms-b4-")
    try:
        c = cases(tmp)
        out = {"matrix": {k: describe(p) for k, p in c.items()}}
        client = TestClient(create_app(service=AnalysisService(os.path.join(tmp, "data"))))
        contract = {}
        for name in ("H unsupported raw TLS", "D ClientHello incomplete", "I flagship deep-dive"):
            snap = b3_snapshot.snapshot_one(client, c[name])
            numeric = any(snap["numeric_score_strings"].values())
            contract[name] = {
                "posture": snap["overall_posture"], "scored": snap["assessment_score"]["scored"],
                "value": snap["assessment_score"]["value"], "run_list_value": snap["api_list"]["score_value"],
                "dashboard_text": snap["dashboard_posture"]["score_text"],
                "report_json_equals_assessment": snap["report_json_equals_assessment"],
                "numeric_score_in_downloads": snap["numeric_score_strings"],
                "id_in_html": snap["html_contains_id"], "assessment_id": snap["assessment_id"],
                "coherent": (snap["assessment_score"]["scored"] == (snap["overall_posture"] != "INSUFFICIENT_EVIDENCE")
                             and (snap["assessment_score"]["value"] is not None) == snap["assessment_score"]["scored"]
                             and (numeric == snap["assessment_score"]["scored"])
                             and snap["report_json_equals_assessment"] and snap["html_contains_id"]),
            }
        out["contract"] = contract
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    os.makedirs(os.path.join(HERE, "results", "phase_b4"), exist_ok=True)
    with open(os.path.join(HERE, "results", "phase_b4", "matrix.json"), "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
    for k, v in out["matrix"].items():
        print(f"{k:42s} {v['scope']} {v['posture']:22s} scored={v['scored']!s:5s} value={v['score_value']!s:6s} assessed={v['assessed']}")
        print(f"    evidence: {v['evidence_session0']}")
        print(f"    conclusions: {v['conclusive_findings']}  scope-note: {bool(v['scope_note_on_conclusions'])}")
    for k, v in out["contract"].items():
        print("CONTRACT", k, {x: v[x] for x in ("posture", "scored", "value", "run_list_value", "dashboard_text", "coherent")})


if __name__ == "__main__":
    main()
