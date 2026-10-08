"""
Phase B: provenance chain integrity. For every single-session finding in every capture:
  P1 every cited frame number exists in the capture and tshark puts it in the cited TCP stream
  P2 every finding has >=1 evidence reference and every OBSERVED_ISSUE cites a standard
  P3 (informational) OBSERVED_ISSUE findings that cite NO frame (absence-based claims)

    python3 research/experiments/phaseb/provenance_check.py     (after run_corpus.py)
"""
import json, os, sys, subprocess
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _corpus import load_captures  # noqa: E402
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
cap = load_captures()
checked = bad = 0
p2_bad, no_frame = [], Counter()
frames_checked = 0
for c in cap:
    out = subprocess.run(["tshark", "-r", os.path.join(ROOT, c["file"]), "-T", "fields", "-e", "frame.number", "-e", "tcp.stream"],
                         capture_output=True, text=True, timeout=120).stdout
    fmap = {}
    for line in out.splitlines():
        a = line.split("\t")
        if a and a[0].isdigit():
            fmap[int(a[0])] = int(a[1]) if len(a) > 1 and a[1].isdigit() else None
    for f in c["findings"]:
        if f["kind"] != "single":
            continue
        checked += 1
        for fr in f["frames"]:
            frames_checked += 1
            if fmap.get(fr) != f["stream"]:
                bad += 1
                print("BAD", c["name"], f["rule_id"], "frame", fr, "tshark stream", fmap.get(fr), "cited stream", f["stream"])
        if f["n_evidence_refs"] < 1 or (f["status"] == "OBSERVED_ISSUE" and not f["has_standards"]):
            p2_bad.append((c["name"], f["rule_id"]))
        if f["status"] == "OBSERVED_ISSUE" and not f["frames"]:
            no_frame[f["rule_id"]] += 1
res = {"single_session_findings_checked": checked, "frames_checked": frames_checked, "frame_stream_mismatches": bad,
       "p2_violations": p2_bad, "observed_issue_findings_citing_no_frame": dict(no_frame)}
json.dump(res, open(os.path.join(HERE, "results", "provenance_check.json"), "w"), indent=1)
print(json.dumps(res, indent=1))
