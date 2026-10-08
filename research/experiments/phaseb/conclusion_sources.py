"""
Phase B.3: which rules supply the conclusions that make a session "assessed"?

A session counts as assessed when at least one OBSERVED_ISSUE or COMPLIANT finding names it.
This script lists, over the 98-capture corpus, the *sets of rules* that are the only source
of that status for a session. A session whose every conclusion comes from a coverage-style
or consistency-style rule (SEC-CFG-001, CS-*) is the pattern behind defect D7.

    PYTHONPATH=src python3 research/experiments/phaseb/conclusion_sources.py
"""
from __future__ import annotations

import collections
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, HERE)

from nyaysaakshya.analysis.model import FindingStatus                 # noqa: E402
from nyaysaakshya.backend.pipeline import run_pipeline                # noqa: E402
from run_corpus import CORPORA                                        # noqa: E402

CONCLUSION = (FindingStatus.OBSERVED_ISSUE, FindingStatus.COMPLIANT)


def main() -> None:
    label = sys.argv[1] if len(sys.argv) > 1 else "final"
    by_set = collections.Counter()
    examples = {}
    only_weak = []
    for corpus, d in CORPORA:
        for name in sorted(os.listdir(d)):
            if not name.endswith((".pcap", ".pcapng", ".cap")):
                continue
            r = run_pipeline(os.path.join(d, name))
            per = collections.defaultdict(set)
            for f in r.findings:
                if f.status in CONCLUSION:
                    per[f.tcp_stream_id].add(f.rule_id)
            for f in r.cross_findings:
                if f.status in CONCLUSION:
                    per[f.tcp_stream_id].add(f.rule_id)
            for s in r.sessions:
                rules = frozenset(per.get(s.tcp_stream_id, ()))
                if not rules:
                    continue
                key = tuple(sorted(rules))
                by_set[key] += 1
                examples.setdefault(key, f"{name}#{s.tcp_stream_id}")
                if all(x == "SEC-CFG-001" or x.startswith("CS-") for x in rules):
                    only_weak.append({"capture": name, "stream": s.tcp_stream_id, "rules": list(key),
                                      "completeness": s.completeness.value,
                                      "tls_state": s.tls_state.value})
    rows = [{"rules": list(k), "sessions": v, "example": examples[k]} for k, v in sorted(by_set.items())]
    os.makedirs(os.path.join(HERE, "results", "phase_b3"), exist_ok=True)
    with open(os.path.join(HERE, "results", "phase_b3", f"conclusion_sources_{label}.json"), "w") as fh:
        json.dump({"rule_sets": rows, "sessions_assessed_only_by_checklist_or_consistency_rules": only_weak},
                  fh, indent=1)
    print(f"{sum(by_set.values())} assessed sessions; "
          f"{len(only_weak)} rest only on SEC-CFG-001 / CS-* conclusions")
    for r in rows:
        print(f"{r['sessions']:5d}  {', '.join(r['rules'])}   e.g. {r['example']}")
    by_cap = collections.Counter(w["capture"] for w in only_weak)
    print(dict(by_cap))


if __name__ == "__main__":
    main()
