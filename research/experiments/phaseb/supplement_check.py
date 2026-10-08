"""
Phase B supplementary checks (each closes a gap the other scripts leave):
  X1 severity of every OBSERVED_ISSUE finding equals the rule's defined severity
  X2 server-refusal streams (genC reject_upgrade) produce SEC-STLS-001 OBSERVED_ISSUE
  X3 report CONTENT consistency across html / pdf / mr / both vs the assessment
  X4 how a truncated / header-only / garbage upload is surfaced through the API

    PYTHONPATH=src python3 research/experiments/phaseb/supplement_check.py
"""
import html as htmllib, io, json, os, re, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _corpus import load_captures  # noqa: E402
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
import pypdf
from fastapi.testclient import TestClient
from nyaysaakshya.backend.api import create_app
from nyaysaakshya.backend.pipeline import run_pipeline
from nyaysaakshya.backend.service import AnalysisService
from nyaysaakshya.reporting.service import render_bytes

cap = load_captures()
out = {}

# X1 -- expected severities are read from the rule source (analysis/rules/*.py, crosssession/rules.py)
EXPECT = {"SEC-PLAIN-001": {"HIGH"}, "SEC-PLAIN-002": {"MEDIUM"}, "SEC-STLS-001": {"MEDIUM"},
          "SEC-TLS-001": {"HIGH", "CRITICAL"}, "SEC-CERT-002": {"HIGH"}, "SEC-CERT-003": {"HIGH"},
          "SEC-CERT-004": {"HIGH"}, "SEC-CERT-005": {"MEDIUM"}, "SEC-FS-001": {"MEDIUM"}, "CS-STARTTLS-001": {"MEDIUM"}}
n = bad = 0
unk = set()
for c in cap:
    for f in c["findings"]:
        if f["status"] == "OBSERVED_ISSUE":
            n += 1
            if f["rule_id"] not in EXPECT:
                unk.add(f["rule_id"])
            elif f["severity"] not in EXPECT[f["rule_id"]]:
                bad += 1
out["X1_severity_vs_rule"] = {"observed_issue_findings": n, "severity_mismatches": bad, "rules_without_expectation": sorted(unk)}

# X2 -- reject_upgrade streams
gt = {x["pcap"]: x for x in json.load(open(os.path.join(ROOT, "research/experiments/oq36/corpus/genC/ground_truth.json")))["captures"]}
tot = hit = 0
for name, g in gt.items():
    c = next(x for x in cap if x["name"] == name)
    for st in g["streams"]:
        if st["behaviour"] != "reject_upgrade":
            continue
        s = next(x for x in c["sessions"] if x["client_ip"] == st["client"] and x["client_port"] == st["client_port"])
        tot += 1
        hit += any(f["rule_id"] == "SEC-STLS-001" and f["status"] == "OBSERVED_ISSUE" and f["stream"] == s["stream"] for f in c["findings"])
out["X2_reject_upgrade"] = {"streams": tot, "with_SEC-STLS-001_OBSERVED_ISSUE": hit}

# X3 -- report content
def pdf_text(b): return re.sub(r"\s+", " ", " ".join((p.extract_text() or "") for p in pypdf.PdfReader(io.BytesIO(b)).pages))
def vis(h):
    h = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", h)
    return re.sub(r"\s+", " ", htmllib.unescape(re.sub(r"<[^>]+>", " ", h)))
x3 = {}
for label, path in (("deepdive(G)", "demo/captures/deepdive_cross_session_control_endpoint.pcap"),
                    ("weak_cert", "demo/captures/backup_weak_certificate.pcap"),
                    ("scene_b", "demo/captures/scene_b_certificate_honesty.pcap")):
    r = run_pipeline(os.path.join(ROOT, path))
    a = r.assessment.to_dict()
    titles = sorted({f.title for f in r.findings if f.status.value == "OBSERVED_ISSUE"} | {f.title for f in r.cross_findings if f.status.value == "OBSERVED_ISSUE"})
    rules = sorted({f.rule_id for f in r.findings if f.status.value == "OBSERVED_ISSUE"} | {f.rule_id for f in r.cross_findings if f.status.value == "OBSERVED_ISSUE"})
    frames = sorted({fr for f in r.findings if f.status.value == "OBSERVED_ISSUE" for fr in f.all_frames})
    lim = a["limitations"][0] if a["limitations"] else None
    texts = {"html_en": vis(render_bytes(a, "html", "en")[0].decode()), "pdf": pdf_text(render_bytes(a, "pdf", "en")[0]),
             "html_mr": vis(render_bytes(a, "html", "mr")[0].decode()), "html_both": vis(render_bytes(a, "html", "both")[0].decode()),
             "json": json.dumps(a)}
    row = {}
    for k, t in texts.items():
        tn = re.sub(r"\s+", "", t)
        row[k] = {
            "assessment_id": a["assessment_id"] in tn, "capture_sha256": a["capture_id"] in tn,
            "score": any(x in tn for x in {f"{a['score']['value']:.2f}", f"{a['score']['value']:.1f}", f"{a['score']['value']:g}"}), "generated_date": a["generated_at"][:10] in tn,
            "band_word_or_marathi_present": (a["score"]["band"] in t) if k in ("html_en", "pdf", "json", "html_both") else None,
            "rule_ids": all(x in tn for x in rules),
            "finding_titles_english": all(re.sub(r"\s+", "", t0) in tn for t0 in titles),
            "first_limitation_text": (re.sub(r"\s+", "", lim) in tn) if lim else None,
        }
    x3[label] = {"expected_titles": titles, "expected_rules": rules, "frames": frames, "contains": row}
out["X3_report_content"] = x3

# X4 -- API surfacing of damaged uploads
raw = open(os.path.join(ROOT, "demo/captures/deepdive_cross_session_control_endpoint.pcap"), "rb").read()
with tempfile.TemporaryDirectory() as td:
    client = TestClient(create_app(service=AnalysisService(os.path.join(td, "data"))), raise_server_exceptions=False)
    x4 = {}
    for name, data in (("header_only_24B", raw[:24]), ("header_truncated_30B", raw[:30]), ("cut_mid_packet", raw[: len(raw) // 2 + 7]), ("garbage", b"x" * 500)):
        r = client.post("/api/v1/analyses", files={"file": (name + ".pcap", data, "application/octet-stream")})
        j = r.json()
        row = {"http": r.status_code}
        if r.status_code == 201:
            a = client.get(f"/api/v1/analyses/{j['run_id']}/assessment").json()
            row.update({"state": j.get("state"), "ingest_status": j.get("ingest_status"),
                        "band": a["assessment"]["score"]["band"], "score": a["assessment"]["score"]["value"],
                        "limitations_mention_truncation": any("trunc" in x.lower() or "incomplete" in x.lower() for x in a["assessment"]["limitations"])})
        else:
            row["error"] = j.get("error", {}).get("code")
        x4[name] = row
out["X4_damaged_uploads_via_api"] = x4

# X5 -- UI fixtures and the shipped sample report
fx = json.load(open(os.path.join(ROOT, "frontend/src/fixtures/real_fixtures.json")))
mp = {"backup_weak_certificate": "demo/captures/backup_weak_certificate.pcap",
      "scene_b_certificate_honesty": "demo/captures/scene_b_certificate_honesty.pcap",
      "deepdive_cross_session_control_endpoint": "demo/captures/deepdive_cross_session_control_endpoint.pcap"}
x5 = {}
for k, v in fx.items():
    fa = v["assessment"]
    fresh = run_pipeline(os.path.join(ROOT, mp[k])).assessment.to_dict()
    x5[k] = {"fixture": [fa["assessment_id"], fa["score"]["value"], fa["score"]["band"], fa["capture_id"][:16]],
             "fresh": [fresh["assessment_id"], fresh["score"]["value"], fresh["score"]["band"], fresh["capture_id"][:16]],
             "equal": [fa["assessment_id"], fa["score"]["value"], fa["score"]["band"], fa["capture_id"]] ==
                      [fresh["assessment_id"], fresh["score"]["value"], fresh["score"]["band"], fresh["capture_id"]]}
sample = open(os.path.join(ROOT, "frontend/public/samples/deepdive_cross_session_control_endpoint.both.html"), encoding="utf-8").read()
_deep = fx["deepdive_cross_session_control_endpoint"]["assessment"]["assessment_id"]
x5["shipped_sample_report"] = {"contains_assessment_id": _deep in sample,
                               "contains_capture_sha256": "97b2b61aa870b74861c606e604f3ecf6f77d8818241817bd22beb814f3dcbe83" in sample,
                               "contains_score_22.15": "22.15" in sample,
                               "generated_at_in_report": sorted(set(re.findall(r"20\d\d-\d\d-\d\dT[\d:]+Z", sample)))}
out["X5_ui_fixtures_and_sample_report"] = x5

# X6 -- demo bundle regression (pipeline-generated expectations; regression only)
by_sha = {c["sha256"]: c for c in cap}
x6 = []
for fn in sorted(os.listdir(os.path.join(ROOT, "demo", "expected"))):
    d = json.load(open(os.path.join(ROOT, "demo", "expected", fn)))
    if "runs" not in d:
        continue
    sm = d["runs"]["ai_false"]["summary"]
    c = by_sha[d["capture_sha256"]]
    x6.append({"file": fn, "expected": [sm["overall_posture"], sm["score_value"], sm["assessment_id"]],
               "now": [c["overall_posture"], c["score"]["value"], c["assessment_id"]],
               "equal": [sm["overall_posture"], sm["score_value"], sm["assessment_id"]] == [c["overall_posture"], c["score"]["value"], c["assessment_id"]]})
out["X6_demo_regression"] = {"files": len(x6), "equal": sum(1 for r in x6 if r["equal"]), "rows": x6}

# X7 -- blind-stripping limitation carried on cross-session findings (re-run, to read the limitation text)
x7 = {}
for name in ("H_no_control", "B_strip_advert", "G_control_endpoint"):
    r = run_pipeline(os.path.join(ROOT, "research/experiments/oq28/pcaps", name + ".pcap"))
    cs = [f for f in r.cross_findings if f.rule_id == "CS-STARTTLS-001"]
    x7[name] = {"cs001_findings": len(cs), "with_blind_stripping_limitation": sum(
        1 for f in cs if any("cannot distinguish a consistently legitimate plaintext configuration" in x for x in f.limitations))}
out["X7_blind_stripping_limitation"] = x7

# X8 -- failed-upgrade streams abstain
def gt_streams(path, key):
    return json.load(open(path))[key] if key else json.load(open(path))
tot8 = abstain8 = issue8 = 0
for g, gtp in (("genB", "oq36/corpus/genB/ground_truth.json"), ("genC", "oq36/corpus/genC/ground_truth.json")):
    for case in json.load(open(os.path.join(ROOT, "research/experiments", gtp)))["captures"]:
        c = next(x for x in cap if x["name"] == case["pcap"])
        for st in case["streams"]:
            if st["behaviour"] != "failed_upgrade":
                continue
            s = next(x for x in c["sessions"] if x["client_ip"] == st["client"] and x["client_port"] == st["client_port"])
            tot8 += 1
            fs = [f for f in c["findings"] if f["kind"] == "single" and f["stream"] == s["stream"]]
            abstain8 += any(f["rule_id"] == "SEC-STLS-001" and f["status"] == "INSUFFICIENT_EVIDENCE" for f in fs)
            issue8 += any(f["status"] == "OBSERVED_ISSUE" for f in fs)
for case in json.load(open(os.path.join(ROOT, "research/experiments/oq28/pcaps/ground_truth.json"))):
    c = next(x for x in cap if x["name"] == case["pcap"])
    for st in case["streams"]:
        if st["kind"] != "failed_upgrade":
            continue
        ip, port = st["stream"].split("->")[0].rsplit(":", 1)
        s = next(x for x in c["sessions"] if x["client_ip"] == ip and x["client_port"] == int(port))
        tot8 += 1
        fs = [f for f in c["findings"] if f["kind"] == "single" and f["stream"] == s["stream"]]
        abstain8 += any(f["rule_id"] == "SEC-STLS-001" and f["status"] == "INSUFFICIENT_EVIDENCE" for f in fs)
        issue8 += any(f["status"] == "OBSERVED_ISSUE" for f in fs)
out["X8_failed_upgrade"] = {"streams": tot8, "with_STLS-001_INSUFFICIENT_EVIDENCE": abstain8, "streams_with_any_OBSERVED_ISSUE": issue8}

json.dump(out, open(os.path.join(HERE, "results", "supplement_check.json"), "w"), indent=1, sort_keys=True, default=str)
print(json.dumps(out, indent=1, sort_keys=True, default=str))
