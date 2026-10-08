"""
Phase B: executed counterfactual for defect D1. The oq33r captures begin with a 2-frame fragment of the
capture harness's own readiness probe (stream 0: a server banner + RST, or a bare FIN/ACK; no dialogue).
Delete exactly those two frames with editcap and re-run the production pipeline.

    PYTHONPATH=src python3 research/experiments/phaseb/probe_counterfactual.py     (needs editcap, from Wireshark)
"""
import json, os, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
from nyaysaakshya.backend.pipeline import run_pipeline

OUT = os.path.join(ROOT, "research", "experiments", "oq33r", "out")
rows = []
with tempfile.TemporaryDirectory() as d:
    for name in ("postfix_smtp_starttls_upgrade", "dovecot_imap_starttls_upgrade", "postfix_smtp_no_starttls_offered"):
        cut = os.path.join(d, name + ".nofrag.pcap")
        subprocess.run(["editcap", os.path.join(OUT, name + ".pcap"), cut, "1", "2"], check=True, capture_output=True)
        o = run_pipeline(os.path.join(OUT, name + ".pcap")).assessment
        c = run_pipeline(cut).assessment
        rows.append({"capture": name, "original": [o.band.value, round(o.score.value, 2), o.coverage.sessions_total],
                     "with_probe_frames_1_2_removed": [c.band.value, round(c.score.value, 2), c.coverage.sessions_total]})
        print(rows[-1])
json.dump(rows, open(os.path.join(HERE, "results", "probe_fragment_counterfactual.json"), "w"), indent=1)
