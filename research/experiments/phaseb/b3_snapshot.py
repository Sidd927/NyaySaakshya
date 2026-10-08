"""
Phase B.3: record, for a fixed set of captures, what every surface says about posture and
score, so that "the API, the dashboard and every report format agree" is a measured
statement rather than an assumption. Reads the real pipeline through an in-process API
client on a throw-away data directory; asserts nothing.

    PYTHONPATH=src python3 research/experiments/phaseb/b3_snapshot.py <label>

Writes research/experiments/phaseb/results/phase_b3/<label>.json. `starting_state` is the
state of the repository at the start of Phase B.3 (after B.2); the label used for the
final state is `final`.
"""
from __future__ import annotations

import io
import json
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, HERE)

from fastapi.testclient import TestClient                          # noqa: E402

from nyaysaakshya.backend.api import create_app                    # noqa: E402
from nyaysaakshya.backend.service import AnalysisService           # noqa: E402

EXP = os.path.join(ROOT, "research", "experiments")
CASES = {
    "D7_E_cut_during_handshake": f"{EXP}/oq46_47/oq46/E_cut_during_handshake.pcap",
    "unsupported_raw_tls": f"{EXP}/p11cert/out/tls12_weak_sha1_rsa1024.pcap",
    "complete_cleartext": f"{EXP}/oq33r/out/postfix_smtp_plaintext_session.pcap",
    "starttls_accepted_then_cut": f"{EXP}/oq36/corpus/genC/C19_truncated.pcap",
    "starttls_requested_then_cut": f"{EXP}/oq46_47/oq46/D_cut_during_starttls.pcap",
    "clienthello_incomplete_E_incomplete": f"{EXP}/oq28/pcaps/E_incomplete.pcap",
    "unanswered_capability_G": f"{EXP}/oq46_47/oq46/G_incomplete_exchange.pcap",
    "cut_mid_dialogue_C": f"{EXP}/oq46_47/oq46/C_cut_mid_dialogue.pcap",
    "quiet_stream_H": f"{EXP}/oq46_47/oq46/H_quiet_stream_then_more_traffic.pcap",
    "missing_setup_F": f"{EXP}/oq46_47/oq46/F_missing_setup.pcap",
    "tiny_probe_scene_C": f"{EXP}/oq33r/out/postfix_smtp_starttls_upgrade.pcap",
    "tls13_implicit_scene_B": f"{ROOT}/demo/captures/scene_b_certificate_honesty.pcap",
    "flagship_deepdive": f"{ROOT}/demo/captures/deepdive_cross_session_control_endpoint.pcap",
}
NUMERIC_SCORE = re.compile(r"\b\d{1,3}(?:\.\d+)?\s*/\s*100\b")


def _text_pdf(data: bytes) -> str:
    import pypdf
    return " ".join((p.extract_text() or "") for p in pypdf.PdfReader(io.BytesIO(data)).pages)


def snapshot_one(client, path: str) -> dict:
    with open(path, "rb") as fh:
        created = client.post("/api/v1/analyses", files={"file": (os.path.basename(path), fh.read(),
                                                                  "application/octet-stream")})
    created.raise_for_status()
    run_id = created.json()["run_id"]
    get = lambda s, **kw: client.get(f"/api/v1/analyses/{run_id}{s}", **kw)       # noqa: E731
    listing = {r["run_id"]: r for r in client.get("/api/v1/analyses?limit=100").json()["items"]}[run_id]
    a = get("/assessment").json()["assessment"]
    dash = get("/dashboard").json()
    html = get("/reports/html").text
    html_mr = get("/reports/html?lang=mr").text
    html_both = get("/reports/html?lang=both").text
    pdf = _text_pdf(get("/reports/pdf").content)
    rep_json = get("/reports/json").json()

    def numeric(t: str) -> list:
        return sorted(set(NUMERIC_SCORE.findall(t)))
    return {
        "capture": os.path.basename(path),
        "assessment_id": a["assessment_id"],
        "overall_posture": a["overall_posture"],
        "api_list": {"overall_posture": listing["overall_posture"], "score_value": listing["score_value"]},
        "assessment_score": {k: a["score"].get(k) for k in ("value", "band", "scored", "basis")},
        "coverage": {k: a["coverage"].get(k) for k in ("sessions_total", "sessions_assessed",
                                                         "sessions_abstained", "sessions_unsupported",
                                                         "assessed_fraction")},
        "issue_groups": [[g["issue_class"], g["fact_kind"], g["severity"], g["recurrence"], g["penalising"]]
                         for g in a["issue_groups"]],
        "dashboard_posture": {k: dash["posture"].get(k) for k in ("value", "withheld", "score_value", "score_text",
                                                                   "scored", "withheld_note")},
        "dashboard_coverage_summary": dash["coverage"].get("summary_text"),
        "report_json_equals_assessment": rep_json == a,
        "numeric_score_strings": {"html": numeric(html), "html_mr": numeric(html_mr),
                                  "html_both": numeric(html_both), "pdf": numeric(pdf)},
        "not_scored_wording": {"html": "Not scored" in html, "pdf": "Not scored" in pdf},
        "html_contains_id": a["assessment_id"] in html,
    }


def main() -> None:
    label = sys.argv[1] if len(sys.argv) > 1 else "final"
    tmp = tempfile.mkdtemp(prefix="sms-b3-")
    try:
        client = TestClient(create_app(service=AnalysisService(os.path.join(tmp, "data"))),
                            raise_server_exceptions=True)
        out = {name: snapshot_one(client, path) for name, path in CASES.items()}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    os.makedirs(os.path.join(HERE, "results", "phase_b3"), exist_ok=True)
    with open(os.path.join(HERE, "results", "phase_b3", f"{label}.json"), "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
    for name, r in out.items():
        print(f"{name:38s} {r['overall_posture']:22s} json={r['assessment_score']['value']!s:6s} "
              f"list={r['api_list']['score_value']!s:6s} dash='{r['dashboard_posture']['score_text']}' "
              f"cov={r['coverage']['sessions_assessed']}/{r['coverage']['sessions_total']} "
              f"numeric={r['numeric_score_strings']['html']}")


if __name__ == "__main__":
    main()
