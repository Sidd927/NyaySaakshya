"""
Phase B: scoring / posture validation. Does NOT claim the score is "right" in any universal
sense; it checks that the implemented score is exactly what its published definition says,
is deterministic, and responds to issue groups (and only to issue groups).

Constants are re-typed here from src/nyaysaakshya/posture/scoring.py (SEVERITY_WEIGHT,
MAX_RECURRENCE_MULTIPLIER, BAND_THRESHOLDS, MIN_ASSESSED_FRACTION) so the arithmetic is
recomputed independently of the engine's own functions.

  S1  recompute penalty/score/band for every capture from its reported score components
  S2  every score component corresponds to a penalising issue group (and vice versa)
  S3  a capture with no OBSERVED_ISSUE finding has zero penalty; penalty>0 implies >=1
  S4  determinism: two full runs per capture give identical assessments (ex generated_at/run_id)
  S5  property tests with the project's own compute_score on real issue groups:
        removing a group raises the score by exactly that group's penalty;
        raising recurrence raises the penalty sub-linearly and never beyond 2.0x;
        changing only observation counts (NOT_OBSERVABLE etc.) leaves the score unchanged
  S6  AI lane on vs off: identical score/band/assessment_id

    PYTHONPATH=src python3 research/experiments/phaseb/score_check.py
"""
from __future__ import annotations

import dataclasses
import json
import math
import os
import sys
from typing import Any, Dict, List

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _corpus import load_captures  # noqa: E402
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))

from nyaysaakshya.backend.pipeline import run_pipeline  # noqa: E402
from nyaysaakshya.posture import scoring  # noqa: E402
from nyaysaakshya.posture.model import EvidenceCoverage  # noqa: E402

W = {"INFO": 0.0, "LOW": 3.0, "MEDIUM": 12.0, "HIGH": 28.0, "CRITICAL": 55.0}
MAXMULT = 2.0
FLOOR = 0.5


def mult(n: int) -> float:
    return 1.0 if n <= 1 else min(MAXMULT, 1.0 + math.log2(n) / 4.0)


def band(v: float) -> str:
    return "STRONG" if v >= 90 else "ADEQUATE" if v >= 75 else "WEAK" if v >= 50 else "CRITICAL"


def canon(a: Dict[str, Any]) -> str:
    b = dict(a)
    b.pop("generated_at", None)
    b.pop("run_id", None)
    return json.dumps(b, sort_keys=True, default=str)


def main() -> None:
    corpus = load_captures()
    out: Dict[str, Any] = {}

    # ---- S1 / S2 / S3 --------------------------------------------------------
    s1_bad, s2_bad, s3_bad = [], [], []
    for c in corpus:
        sc, cov = c["score"], c["coverage"]
        comps = sc["components"]
        pen = sum(W[x["severity"]] * mult(x["recurrence"]) for x in comps)
        val = max(0.0, 100.0 - pen)
        if cov["sessions_assessed"] == 0:
            exp_band = "INSUFFICIENT_EVIDENCE"
        elif cov["assessed_fraction"] < FLOOR:
            exp_band = "INSUFFICIENT_EVIDENCE"
        elif not comps and False:
            exp_band = "INSUFFICIENT_EVIDENCE"
        else:
            exp_band = band(val)
        # Schema 1.1 contract: a withheld posture serialises scored=false and value=null;
        # a graded one serialises the arithmetic value, which must equal the recomputation.
        withheld = sc["band"] == "INSUFFICIENT_EVIDENCE"
        if withheld:
            ok_val = sc.get("scored") is False and sc["value"] is None
        else:
            ok_val = sc.get("scored") is True and sc["value"] is not None and abs(val - sc["value"]) < 0.01
        ok_band = exp_band == sc["band"]
        ok_comp = all(abs(W[x["severity"]] * mult(x["recurrence"]) - x["penalty"]) < 0.001 for x in comps)
        if not (ok_val and ok_band and ok_comp):
            s1_bad.append({"capture": c["name"], "reported": [sc["value"], sc["band"]], "recomputed": [round(val, 2), exp_band]})
        penalising = [g for g in c["issue_groups"] if g.get("penalising")]
        if sorted((g["issue_class"], g["severity"], g["recurrence"]) for g in penalising) != \
                sorted((x["issue_class"], x["severity"], x["recurrence"]) for x in comps):
            s2_bad.append(c["name"])
        n_issue = sum(1 for f in c["findings"] if f["status"] == "OBSERVED_ISSUE")
        if (pen > 0) != (n_issue > 0):
            s3_bad.append({"capture": c["name"], "penalty": round(pen, 2), "observed_issue_findings": n_issue})
    out["S1_recompute"] = {"captures": len(corpus), "mismatches": s1_bad}
    out["S2_components_vs_groups"] = {"captures": len(corpus), "mismatches": s2_bad}
    out["S3_penalty_iff_observed_issue"] = {"captures": len(corpus), "violations": s3_bad}

    # ---- S4 determinism ------------------------------------------------------
    diffs: List[str] = []
    for c in corpus:
        path = os.path.join(ROOT, c["file"])
        a = run_pipeline(path).assessment.to_dict()
        b = run_pipeline(path).assessment.to_dict()
        if canon(a) != canon(b):
            diffs.append(c["name"])
    out["S4_determinism"] = {"captures": len(corpus), "runs_per_capture": 2, "non_identical": diffs}

    # ---- S5 properties on a real multi-group assessment ------------------------
    r = run_pipeline(os.path.join(ROOT, "demo", "captures", "deepdive_cross_session_control_endpoint.pcap"))
    groups = list(r.assessment.issue_groups)
    cov = r.assessment.coverage
    base = scoring.compute_score(groups, cov)
    pen = [g for g in groups if g.penalising]
    rows = []
    for g in pen:
        rest = [x for x in groups if x is not g]
        s = scoring.compute_score(rest, cov)
        removed_pen = next(x.penalty for x in base.components if x.issue_class == g.issue_class)
        rows.append({"remove": g.issue_class.value, "score_delta": round(s.value - base.value, 4),
                     "component_penalty": round(removed_pen, 4), "exact": abs((s.value - base.value) - removed_pen) < 1e-6})
    rec_rows = []
    g0 = pen[0]
    prev = None
    for n in (1, 2, 3, 6, 12, 50, 1000):
        s = scoring.compute_score([dataclasses.replace(g0, affected_stream_keys=tuple(f"k{i}" for i in range(n)))
                                   if hasattr(g0, "affected_stream_keys") else g0], cov)
        p = s.total_penalty
        rec_rows.append({"recurrence_proxy": n, "penalty": round(p, 4), "multiplier": round(p / scoring.SEVERITY_WEIGHT[g0.severity], 4)})
    obs_changed = dataclasses.replace(cov, observation_counts={"NOT_OBSERVABLE": 999, "UNKNOWN": 999})
    s_obs = scoring.compute_score(groups, obs_changed)
    out["S5_properties"] = {
        "capture": "deepdive_cross_session_control_endpoint.pcap",
        "base": {"score": round(base.value, 4), "band": base.band.value, "components": len(base.components)},
        "remove_one_group": rows,
        "recurrence_scaling_first_group": rec_rows,
        "observation_counts_changed_score": round(s_obs.value, 4),
        "observation_counts_changed_identical": abs(s_obs.value - base.value) < 1e-9 and s_obs.band == base.band,
    }

    # ---- S6 AI on vs off ------------------------------------------------------
    ai = []
    for name in ["demo/captures/scene_c_no_ai_equivalence.pcap", "demo/captures/deepdive_cross_session_control_endpoint.pcap",
                 "demo/captures/backup_weak_certificate.pcap", "research/experiments/oq36/corpus/genC/C04_strip_control.pcap",
                 "research/experiments/oq36/corpus/genB/B01_all_upgrade.pcap"]:
        p = os.path.join(ROOT, name)
        off = run_pipeline(p, ai_enabled=False).assessment
        on = run_pipeline(p, ai_enabled=True)
        a = on.assessment
        ai.append({"capture": os.path.basename(name), "ml_results": len(on.ml_results),
                   "score_equal": off.score.value == a.score.value, "band_equal": off.band == a.band,
                   "assessment_id_equal": off.assessment_id == a.assessment_id,
                   "off": [off.assessment_id, round(off.score.value, 2)], "on": [a.assessment_id, round(a.score.value, 2)],
                   "findings_equal": [f.rule_id + f.status.value for f in run_pipeline(p, ai_enabled=False).findings]
                   == [f.rule_id + f.status.value for f in on.findings]})
    out["S6_ai_on_off"] = ai

    with open(os.path.join(HERE, "results", "score_check.json"), "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True, default=str)
    print(json.dumps({k: (v if k in ("S5_properties", "S6_ai_on_off") else
                          {kk: (vv if not isinstance(vv, list) else (vv if len(vv) < 8 else f"{len(vv)} items"))
                           for kk, vv in v.items()}) for k, v in out.items()}, indent=1, default=str))


if __name__ == "__main__":
    main()
