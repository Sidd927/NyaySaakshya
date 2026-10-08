"""
Phase B.3: can the ML lane change a security conclusion? Runs every capture in the corpus with
the lane off and on (same code, same capture) and compares everything that is a conclusion.

Expected and asserted nowhere here; the result is written for review and re-checked by
tests/test_semantic_contract.py on a subset:

  identical with AI on and off:  posture band, score object, coverage, abstentions, the
                                 deterministic and cross-session findings, every non-ANOMALY
                                 issue group
  allowed to differ:             assessment_id (anomaly groups join the hash), the ranked
                                 `prioritised` list, ANOMALY_SIGNAL groups, model_summary,
                                 provenance counts, limitations text, risk_summary counts

    PYTHONPATH=src python3 research/experiments/phaseb/ml_isolation.py
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, HERE)

from nyaysaakshya.backend.pipeline import run_pipeline                # noqa: E402
from run_corpus import CORPORA                                        # noqa: E402

ALLOWED = {"assessment_id", "ai_enabled", "risk_summary", "issue_groups", "prioritised",
           "model_summary", "provenance", "limitations", "generated_at", "run_id"}


def main() -> None:
    rows, violations = [], []
    for corpus, d in CORPORA:
        for name in sorted(os.listdir(d)):
            if not name.endswith((".pcap", ".pcapng", ".cap")):
                continue
            path = os.path.join(d, name)
            off = run_pipeline(path, ai_enabled=False)
            on = run_pipeline(path, ai_enabled=True)
            a0, a1 = off.assessment.to_dict(), on.assessment.to_dict()
            changed = sorted(k for k in a1 if a1[k] != a0.get(k))
            non_ml = lambda a: [g for g in a["issue_groups"] if g["fact_kind"] != "ANOMALY_SIGNAL"]  # noqa: E731
            same_findings = ([f.to_dict() for f in off.findings] == [f.to_dict() for f in on.findings]
                             and [f.to_dict() for f in off.cross_findings] == [f.to_dict() for f in on.cross_findings])
            row = {"capture": name, "corpus": corpus, "changed_keys": changed,
                   "same_deterministic_and_cross_findings": same_findings,
                   "same_non_ml_groups": non_ml(a1) == non_ml(a0),
                   "band_equal": a1["overall_posture"] == a0["overall_posture"],
                   "score_equal": a1["score"] == a0["score"],
                   "coverage_equal": a1["coverage"] == a0["coverage"],
                   "abstentions_equal": a1["abstentions"] == a0["abstentions"],
                   "ml_anomalous_sessions": (a1.get("model_summary") or {}).get("by_band", {}).get("ANOMALOUS", 0)}
            rows.append(row)
            if (set(changed) - ALLOWED or not same_findings or not row["same_non_ml_groups"]
                    or not all(row[k] for k in ("band_equal", "score_equal", "coverage_equal", "abstentions_equal"))):
                violations.append(row)
    out = {"captures": len(rows), "violations": violations,
           "captures_with_an_anomalous_session": sum(1 for r in rows if r["ml_anomalous_sessions"]),
           "rows": rows}
    os.makedirs(os.path.join(HERE, "results", "phase_b3"), exist_ok=True)
    with open(os.path.join(HERE, "results", "phase_b3", "ml_isolation.json"), "w") as fh:
        json.dump(out, fh, indent=1)
    print(f"{len(rows)} captures; violations: {len(violations)}; "
          f"captures with >=1 ANOMALOUS session: {out['captures_with_an_anomalous_session']}")
    for v in violations[:10]:
        print("VIOLATION", v)


if __name__ == "__main__":
    main()
