"""
Phase B validation: run every capture the repository holds through the production
pipeline (`nyaysaakshya.backend.pipeline.run_pipeline`, the same function the API uses)
and record what came out. This script ASSERTS NOTHING and reads no expected values; the
judgement against independent expectations is done in `check_expectations.py`, so the raw
observations here cannot be shaped by what we hoped to see.

    PYTHONPATH=src python3 research/experiments/phaseb/run_corpus.py

Writes research/experiments/phaseb/results/corpus_run.json. Needs tshark.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from typing import Any, Dict, List

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))

from nyaysaakshya.analysis.model import FindingStatus  # noqa: E402
from nyaysaakshya.backend.pipeline import run_pipeline  # noqa: E402

EXP = os.path.join(ROOT, "research", "experiments")
CORPORA = [
    ("oq33r", os.path.join(EXP, "oq33r", "out")),
    ("oq28", os.path.join(EXP, "oq28", "pcaps")),
    ("oq46", os.path.join(EXP, "oq46_47", "oq46")),
    ("oq47", os.path.join(EXP, "oq46_47", "oq47")),
    ("p11cert", os.path.join(EXP, "p11cert", "out")),
    ("oq36-genB", os.path.join(EXP, "oq36", "corpus", "genB")),
    ("oq36-genC", os.path.join(EXP, "oq36", "corpus", "genC")),
]

#: Evidence fields on a session (session/model.py). Census is taken over exactly these.
FIELDS = [
    "starttls_advertised", "starttls_requested", "starttls_accepted", "tls_transition",
    "tls_negotiated_version", "tls_cipher_suite_name", "tls_key_exchange",
    "tls_named_group", "tls_forward_secrecy", "tls_certificate_chain",
    "plaintext_continuation", "auth_activity",
]


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def session_record(s: Any) -> Dict[str, Any]:
    return {
        "stream": s.tcp_stream_id, "protocol": s.protocol,
        "client_ip": s.client_ip, "client_port": s.client_port,
        "server_ip": s.server_ip, "server_port": s.server_port,
        "client": f"{s.client_ip}:{s.client_port}", "server": f"{s.server_ip}:{s.server_port}",
        "frames": [s.first_frame, s.last_frame], "packets": s.packet_count,
        "tls_state": s.tls_state.value, "completeness": s.completeness.value,
        "implicit_tls": s.implicit_tls,
        "fields": {name: {"state": getattr(s, name).state.value,
                          "value": getattr(s, name).value,
                          "frames": list(getattr(s, name).frames)}
                   for name in FIELDS},
    }


def finding_record(f: Any, kind: str) -> Dict[str, Any]:
    d = f.to_dict()
    return {
        "kind": kind, "rule_id": d["rule_id"], "status": d["status"], "severity": d["severity"],
        "title": d["title"], "conclusion": d.get("conclusion"), "explanation": d.get("explanation"),
        "stream": d["session"]["tcp_stream_id"] if "session" in d else None,
        "frames": d.get("frames", []), "n_evidence_refs": len(d.get("evidence_refs", [])),
        "has_standards": bool(d.get("standards")),
        "evidence_ref_states": sorted({r["evidence_state"] for r in d.get("evidence_refs", [])}),
    }


def analyse_one(corpus: str, path: str) -> Dict[str, Any]:
    rec: Dict[str, Any] = {"corpus": corpus, "file": os.path.relpath(path, ROOT),
                           "name": os.path.basename(path), "sha256": sha256_file(path)}
    try:
        r = run_pipeline(path)
    except Exception as exc:  # recorded, never hidden
        rec["error"] = f"{type(exc).__name__}: {exc}"
        return rec
    a = r.assessment.to_dict()
    rec.update({
        "packets": r.run.packet_count, "run_status": r.run.status.value,
        "sessions": [session_record(s) for s in r.sessions],
        "findings": ([finding_record(f, "single") for f in r.findings]
                     + [finding_record(f, "cross") for f in r.cross_findings]),
        "assessment_id": a["assessment_id"], "overall_posture": a["overall_posture"],
        "score": a["score"], "coverage": a["coverage"],
        "abstentions": a["risk_summary"].get("abstentions"),
        "issue_groups": [{k: g.get(k) for k in ("issue_class", "severity", "recurrence", "penalising", "fact_kind", "dimension")}
                         for g in a["issue_groups"]],
    })
    return rec


def main() -> None:
    out: List[Dict[str, Any]] = []
    for corpus, d in CORPORA:
        for name in sorted(os.listdir(d)):
            if name.endswith((".pcap", ".pcapng", ".cap")):
                out.append(analyse_one(corpus, os.path.join(d, name)))
                tag = out[-1].get("overall_posture") or out[-1].get("error", "?")[:40]
                print(f"{corpus:10s} {name:48s} {tag}", flush=True)
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    # Finding text repeats thousands of times; intern it (see _corpus.load_captures to expand).
    table, index = [], {}
    for r in out:
        for f in r.get("findings", []):
            for k in ("title", "conclusion", "explanation"):
                t = f.get(k)
                if isinstance(t, str):
                    f[k] = index.setdefault(t, len(index))
                    if f[k] == len(table):
                        table.append(t)
    with open(os.path.join(HERE, "results", "corpus_run.json"), "w") as fh:
        json.dump({"texts": table, "captures": out}, fh, separators=(",", ":"), sort_keys=True, default=str)
    print(f"\n{len(out)} captures, {sum(1 for r in out if 'error' in r)} errors")


if __name__ == "__main__":
    main()
