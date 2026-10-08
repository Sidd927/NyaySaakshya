"""
Phase B.2 / B.3: compare a committed baseline with the current run (results/corpus_run.json).
Prints the headline counts and every capture whose band or score moved. Reads files only.

    python3 research/experiments/phaseb/before_after.py                    # Phase B  -> now
    python3 research/experiments/phaseb/before_after.py phase_b2_final     # Phase B.2 -> now

Baselines: results/phase_b_baseline (engine 0.8.0 / analysis 0.5.0 / rules 1.1) and
results/phase_b2_final (posture 0.9.0 / analysis 0.6.0 / rules 1.2). A withheld posture has
no score (`None`) from schema 1.1; baselines written before that carry the arithmetic value.
"""
from __future__ import annotations

import collections
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def main() -> None:
    baseline = sys.argv[1] if len(sys.argv) > 1 else "phase_b_baseline"
    before = json.load(open(os.path.join(HERE, "results", baseline, "captures.json")))["captures"]
    after = json.load(open(os.path.join(HERE, "results", "corpus_run.json")))["captures"]
    now = {}
    for x in after:
        states = collections.Counter(f["state"] for s in x["sessions"] for f in s["fields"].values())
        rules = collections.Counter(f["rule_id"] for f in x["findings"] if f["status"] == "OBSERVED_ISSUE")
        now[x["name"]] = {"overall_posture": x["overall_posture"], "score_value": x["score"]["value"],
                          "assessment_id": x["assessment_id"], "states": states, "rules": rules}
    was = {b["capture"]: b for b in before}
    assert set(was) == set(now), "capture sets differ"

    def tally(rows, key):
        c = collections.Counter()
        for r in rows:
            c.update(key(r))
        return dict(sorted(c.items()))

    print("bands before:", tally(before, lambda r: [r["overall_posture"]]))
    print("bands after :", tally(now.values(), lambda r: [r["overall_posture"]]))
    print("states before:", tally(before, lambda r: r["observation_states"]))
    print("states after :", tally(now.values(), lambda r: r["states"]))
    print("OBSERVED_ISSUE before:", tally(before, lambda r: r["observed_issue_by_rule"]))
    print("OBSERVED_ISSUE after :", tally(now.values(), lambda r: r["rules"]))
    print("sessions assessed before/after:", sum(b["sessions_assessed"] for b in before),
          sum(x["coverage"]["sessions_assessed"] for x in after))
    print("assessment ids changed:", sum(1 for n, b in was.items() if b["assessment_id"] != now[n]["assessment_id"]))
    print("\ncaptures whose band or score moved:")
    for n, b in sorted(was.items()):
        a = now[n]
        if (b["overall_posture"], b["score_value"]) != (a["overall_posture"], a["score_value"]):
            print(f"  {b['corpus']:10s} {n:42s} {b['overall_posture']} {b['score_value']} -> "
                  f"{a['overall_posture']} {a['score_value']}")


if __name__ == "__main__":
    main()
