#!/usr/bin/env python3
"""
Refresh the derived artefacts that embed pipeline results and are NOT written by
generate_bundle.py:

  demo/evidence/real_pcap_evidence_pack.json
  frontend/src/fixtures/real_fixtures.json                 (landing hero record, evidence
                                                            example, workbench demo fallback)
  demo/i18n-samples/*.both.html
  frontend/public/samples/deepdive_cross_session_control_endpoint.both.html

Every value is read back from the real pipeline through the real HTTP API (an in-process
TestClient on a fresh, throw-away data directory); nothing is typed by hand. The flagship
capture is analysed in TWO separate databases a couple of seconds apart, because the landing
page presents "one capture, two runs, one assessment ID" as the determinism result: the
hero record comes from the first run and the shipped sample report from the second.

Run after any change that alters an assessment (rules, fusion, coverage), then regenerate
the demo bundle with demo/commands/generate_bundle.py.

    PYTHONPATH=src python3 demo/commands/refresh_derived_artifacts.py
"""
from __future__ import annotations

import json
import os
import re
import shutil
import sys
import tempfile
import time

sys.path.insert(0, "src")

from fastapi.testclient import TestClient                          # noqa: E402

from nyaysaakshya.backend.api import create_app                    # noqa: E402
from nyaysaakshya.backend.service import AnalysisService           # noqa: E402
from nyaysaakshya.reporting.service import render_bytes            # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEMO = os.path.join(ROOT, "demo")
EXP = os.path.join(ROOT, "research", "experiments")

FIXTURE_CAPTURES = {
    "backup_weak_certificate": os.path.join(DEMO, "captures", "backup_weak_certificate.pcap"),
    "scene_b_certificate_honesty": os.path.join(DEMO, "captures", "scene_b_certificate_honesty.pcap"),
    "deepdive_cross_session_control_endpoint":
        os.path.join(DEMO, "captures", "deepdive_cross_session_control_endpoint.pcap"),
}
EVIDENCE_PACK = [  # (capture, real_world, path)
    *[(n, True, os.path.join(EXP, "oq33r", "out", n)) for n in (
        "dovecot_imap_imaps_implicit_tls.pcap", "dovecot_imap_plaintext_login.pcap",
        "dovecot_imap_starttls_upgrade.pcap", "dovecot_pop3_plaintext_login.pcap",
        "dovecot_pop3_pop3s_implicit_tls.pcap", "dovecot_pop3_stls_upgrade.pcap",
        "postfix_smtp_client_declines.pcap", "postfix_smtp_no_starttls_offered.pcap",
        "postfix_smtp_plaintext_session.pcap", "postfix_smtp_starttls_upgrade.pcap")],
    *[(n, False, os.path.join(EXP, "p11cert", "out", n)) for n in (
        "smtps_tls12_weak_sha1_rsa1024.pcap", "smtps_tls12_selfsigned_rsa2048.pcap",
        "smtps_tls12_chain_rsa2048.pcap")],
]
#: Stable identities of the three demo runs. The workbench's demo-fallback mode, its deep links
#: (`?run_id=...`) and the frontend capture scripts all key on these. A run id is an opaque
#: uuid that carries no evidence, so it is pinned across regenerations; every evidential value
#: (assessment id, score, findings, timestamps) still comes from the fresh run.
PINNED_RUN_IDS = {
    "backup_weak_certificate": "58d5f74ba5024c83ad6e62dae6dd06b6",
    "scene_b_certificate_honesty": "9aaefe1d93f046faac255dfe67c86c18",
    "deepdive_cross_session_control_endpoint": "871ea0c739b246098ff481c887afcc0f",
}
SAMPLE_REPORTS = {  # i18n sample name -> capture path
    "deepdive_cross_session_control_endpoint": FIXTURE_CAPTURES["deepdive_cross_session_control_endpoint"],
    "backup_weak_certificate": FIXTURE_CAPTURES["backup_weak_certificate"],
}


class Fresh:
    """One throw-away backend: its own data directory and its own database."""

    def __init__(self) -> None:
        self.dir = tempfile.mkdtemp(prefix="sms-derived-")
        self.client = TestClient(create_app(service=AnalysisService(os.path.join(self.dir, "data"))),
                                 raise_server_exceptions=True)

    def analyse(self, path: str) -> dict:
        with open(path, "rb") as fh:
            created = self.client.post("/api/v1/analyses",
                                       files={"file": (os.path.basename(path), fh.read(),
                                                       "application/octet-stream")})
        created.raise_for_status()
        run_id = created.json()["run_id"]
        get = lambda suffix: self.client.get(f"/api/v1/analyses/{run_id}{suffix}")  # noqa: E731
        listing = {r["run_id"]: r for r in self.client.get("/api/v1/analyses?limit=50").json()["items"]}
        item = listing[run_id]
        return {
            "run": {k: item[k] for k in ("run_id", "state", "source_filename", "overall_posture",
                                         "score_value", "created_at", "duration_ms")},
            "assessment": get("/assessment").json()["assessment"],
            "dashboard": get("/dashboard").json(),
            "sessions": get("/sessions?limit=100").json(),
        }

    def close(self) -> None:
        shutil.rmtree(self.dir, ignore_errors=True)


def evidence_summary(name: str, real_world: bool, a: dict) -> dict:
    cov = a["coverage"]
    reasons = (a.get("risk_summary", {}).get("abstentions", {}) or {}).get("by_reason", {})
    return {
        "capture": name, "real_world": real_world, "capture_sha256": a["capture_id"],
        "sessions_total": cov["sessions_total"], "sessions_assessed": cov["sessions_assessed"],
        "protocol_counts": cov["protocol_counts"], "observation_counts": cov["observation_counts"],
        "overall_posture": a["overall_posture"], "score_value": a["score"]["value"],
        "issue_classes": sorted({g["issue_class"] for g in a["issue_groups"]}),
        "penalising_classes": sorted({g["issue_class"] for g in a["issue_groups"] if g["penalising"]}),
        "abstention_reasons": sorted(reasons),
        "assessment_id": a["assessment_id"],
    }


def _patch(path: str, edits) -> None:
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    for pattern, repl in edits:
        text, n = re.subn(pattern, repl, text, count=1)
        if n != 1:
            raise SystemExit(f"{path}: pattern not found: {pattern}")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


def sync_frontend_constants(fixtures: dict, flagship: tuple) -> None:
    """Copy the regenerated identities into the few frontend constants that mirror them, so the
    landing page, the demo-fallback runs and the determinism note cannot drift from the fixtures."""
    ctx = os.path.join(ROOT, "frontend", "src", "context", "InvestigationContext.tsx")
    for data in fixtures.values():
        run_id, a, run = data["run"]["run_id"], data["assessment"], data["run"]
        with open(ctx, encoding="utf-8") as fh:
            text = fh.read()
        start = text.index(f"run_id: '{run_id}'")
        end = text.index("score_value:", start)
        block = text[start:end]
        block = re.sub(r"assessment_id: '[^']*'", f"assessment_id: '{a['assessment_id']}'", block)
        for key in ("created_at", "started_at", "completed_at"):
            block = re.sub(rf"{key}: '[^']*'", f"{key}: '{run['created_at']}'", block)
        with open(ctx, "w", encoding="utf-8") as fh:
            fh.write(text[:start] + block + text[end:])
    assessment_id, _generated_at, _size = flagship
    sample = os.path.join(ROOT, "frontend", "src", "components", "landing", "reportSample.ts")
    _patch(sample, [(r"assessmentId: '[0-9a-f]{16}'", f"assessmentId: '{assessment_id}'"),
                    (r"analysedIso: '[^']*'", f"analysedIso: '{flagship[1]}'")])
    copy = os.path.join(ROOT, "frontend", "src", "components", "landing", "copy.ts")
    _patch(copy, [(r"Both runs produced assessment [0-9a-f]{16}\.",
                   f"Both runs produced assessment {assessment_id}."),
                  (r"Marathi draft\. \d+ KB,", f"Marathi draft. {flagship[2] // 1024} KB,")])


def main() -> None:
    # ---- first database: landing fixtures + evidence pack ----------------------------------
    first = Fresh()
    try:
        fixtures = {}
        for key, path in FIXTURE_CAPTURES.items():
            data = first.analyse(path)
            fresh_id = data["run"]["run_id"]
            # Pin the opaque run id everywhere it appears (run, assessment, sessions).
            data = json.loads(json.dumps(data).replace(fresh_id, PINNED_RUN_IDS[key]))
            fixtures[key] = data
        pack = []
        for name, real, path in EVIDENCE_PACK:
            pack.append(evidence_summary(name, real, first.analyse(path)["assessment"]))
    finally:
        first.close()

    with open(os.path.join(ROOT, "frontend", "src", "fixtures", "real_fixtures.json"), "w",
              encoding="utf-8") as fh:
        fh.write(json.dumps(fixtures, indent=2, ensure_ascii=True))
    with open(os.path.join(DEMO, "evidence", "real_pcap_evidence_pack.json"), "w",
              encoding="utf-8") as fh:
        fh.write(json.dumps(pack, indent=2, ensure_ascii=False) + "\n")

    # ---- second, separate database, later: the shipped sample reports ----------------------
    time.sleep(2.2)            # generated_at has one-second resolution; make the two runs distinct
    second = Fresh()
    try:
        for name, path in SAMPLE_REPORTS.items():
            assessment = second.analyse(path)["assessment"]
            html = render_bytes(assessment, "html", "both")[0]
            target = os.path.join(DEMO, "i18n-samples", f"{name}.both.html")
            with open(target, "wb") as fh:
                fh.write(html)
            if name == "deepdive_cross_session_control_endpoint":
                shutil.copyfile(target, os.path.join(ROOT, "frontend", "public", "samples",
                                                     f"{name}.both.html"))
                flagship = (assessment["assessment_id"], assessment["generated_at"], len(html))
    finally:
        second.close()

    hero = fixtures["deepdive_cross_session_control_endpoint"]
    sync_frontend_constants(fixtures, flagship)
    print("hero record   :", hero["assessment"]["assessment_id"], hero["assessment"]["generated_at"])
    print("sample report :", flagship[0], flagship[1], f"{flagship[2] / 1024:.0f} KB")
    print("same assessment ID across the two runs:", hero["assessment"]["assessment_id"] == flagship[0])


if __name__ == "__main__":
    main()
