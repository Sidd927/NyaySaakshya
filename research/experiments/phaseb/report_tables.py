"""
Phase B: derive the evidence-state demonstration, the per-rule status matrix and the capture
inventory straight from the production pipeline output, so none of those tables is hand-typed.

    PYTHONPATH=src python3 research/experiments/phaseb/report_tables.py

Reads results/corpus_run.json (+ ground-truth sidecars / manifests), re-runs a handful of
captures to harvest the engine's own `basis` strings. Writes
  results/evidence_states.json   states census, one real example per state (with basis text),
                                 NOT_OBSERVABLE checks
  results/rule_matrix.json       rule x status counts over the whole corpus
  results/inventory.md           one row per capture (SHA-256, sessions, tags, source of expectation)
"""
from __future__ import annotations

import json
import os
import re
import sys
from collections import Counter, defaultdict
from typing import Any, Dict, List

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _corpus import load_captures  # noqa: E402
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
EXP = os.path.join(ROOT, "research", "experiments")
sys.path.insert(0, os.path.join(ROOT, "src"))

from nyaysaakshya.backend.pipeline import run_pipeline  # noqa: E402

cap = load_captures()
by_name = {c["name"]: c for c in cap}

FIELDS = ["starttls_advertised", "starttls_requested", "starttls_accepted", "tls_transition", "tls_negotiated_version",
          "tls_cipher_suite_name", "tls_key_exchange", "tls_named_group", "tls_forward_secrecy",
          "tls_certificate_chain", "plaintext_continuation", "auth_activity"]


def evidence_states() -> Dict[str, Any]:
    census = Counter()
    for c in cap:
        for s in c["sessions"]:
            for v in s["fields"].values():
                census[v["state"]] += 1
    wanted = {
        "OBSERVED": ("demo/captures/scene_b_certificate_honesty.pcap", "tls_negotiated_version"),
        "INFERRED": ("demo/captures/scene_b_certificate_honesty.pcap", "tls_forward_secrecy"),
        "UNKNOWN": ("research/experiments/oq33r/out/dovecot_imap_plaintext_login.pcap", "tls_cipher_suite_name"),
        "AMBIGUOUS": ("research/experiments/oq33r/out/postfix_smtp_no_starttls_offered.pcap", "starttls_advertised"),
        "NOT_OBSERVABLE": ("demo/captures/scene_b_certificate_honesty.pcap", "tls_certificate_chain"),
        "INCOMPLETE": ("research/experiments/oq46_47/oq46/D_cut_during_starttls.pcap", "tls_transition"),
    }
    examples = {}
    for state, (path, field) in wanted.items():
        r = run_pipeline(os.path.join(ROOT, path))
        hit = None
        for s in r.sessions:
            f = getattr(s, field)
            if f.state.value == state:
                hit = {"capture": os.path.basename(path), "stream": s.tcp_stream_id, "field": field, "state": f.state.value,
                       "value": f.value, "frames": list(f.frames), "basis": f.basis, "provenance": f.provenance.value}
                break
        examples[state] = hit or {"capture": os.path.basename(path), "field": field,
                                  "result": f"state {state} NOT produced; field states seen: "
                                            f"{sorted({getattr(s, field).state.value for s in r.sessions})}"}
    # NOT_OBSERVABLE never reported as invalid / a failure
    bad_words = re.compile(r"\b(invalid|untrusted|forged|fake|expired|compromised|weak)\b", re.I)
    no_findings = [f for c in cap for f in c["findings"] if f["status"] == "NOT_OBSERVABLE"]
    def affirmative_text(f: Dict[str, Any]) -> str:
        """Drop sentences that NEGATE the failure reading ("is not evidence of ... invalid")."""
        parts = re.split(r"(?<=[.;])\s+", (f.get("conclusion") or "") + " " + (f.get("explanation") or ""))
        return " ".join(x for x in parts if not re.search(r"\bnot (a finding|evidence of)|neither limitation", x, re.I))
    leaks = [{"capture": c["name"], "rule": f["rule_id"], "text": affirmative_text(f)}
             for c in cap for f in c["findings"] if f["status"] == "NOT_OBSERVABLE" and bad_words.search(affirmative_text(f))]
    sev = Counter(f["severity"] for f in no_findings)
    penalised = []
    for c in cap:
        has_no = any(f["status"] == "NOT_OBSERVABLE" for f in c["findings"])
        has_issue = any(f["status"] == "OBSERVED_ISSUE" for f in c["findings"])
        if has_no and not has_issue and c["score"]["total_penalty"] > 0:
            penalised.append(c["name"])
    scene_b = by_name["dovecot_imap_imaps_implicit_tls.pcap"]
    return {
        "field_observations": sum(census.values()), "census": dict(census),
        "captures": len(cap), "examples": examples,
        "not_observable_findings": {"count": len(no_findings), "by_severity": dict(sev),
                                    "texts_containing_invalid_untrusted_etc": leaks,
                                    "captures_with_NOT_OBSERVABLE_and_no_OBSERVED_ISSUE_but_penalised": penalised},
        "scene_b_like_example": {"capture": scene_b["name"], "band": scene_b["overall_posture"], "score": scene_b["score"]["value"],
                                 "observation_counts": scene_b["coverage"]["observation_counts"]},
    }


def rule_matrix() -> Dict[str, Any]:
    m: Dict[str, Counter] = defaultdict(Counter)
    caps_with_issue: Dict[str, set] = defaultdict(set)
    for c in cap:
        for f in c["findings"]:
            m[f["rule_id"]][f["status"]] += 1
            if f["status"] == "OBSERVED_ISSUE":
                caps_with_issue[f["rule_id"]].add(c["name"])
    return {r: {"statuses": dict(v), "captures_with_OBSERVED_ISSUE": len(caps_with_issue[r])} for r, v in sorted(m.items())}


def _graded(c) -> str:
    """Band and score, or 'withheld' (a withheld band is not a grade; the JSON still stores a number)."""
    if c["overall_posture"] == "INSUFFICIENT_EVIDENCE":
        return "INSUFFICIENT_EVIDENCE (withheld)"
    return f"{c['overall_posture']} {c['score']['value']:g}"


def inventory() -> str:
    gt28 = {c["pcap"]: c for c in json.load(open(os.path.join(EXP, "oq28", "pcaps", "ground_truth.json")))}
    man = json.load(open(os.path.join(EXP, "oq46_47", "manifest.json")))
    man46 = {c["pcap"]: c for c in man["oq46"]}
    man47 = {c["pcap"]: c for c in man["oq47"]}
    scen = {s["pcap"]: s for s in json.load(open(os.path.join(EXP, "oq33r", "out", "scenarios.json")))}
    demo = {}
    for line in open(os.path.join(ROOT, "demo", "hashes", "SHA256SUMS.txt")):
        m = re.match(r"([0-9a-f]{64})\s+(\S+)\s+\(-> (.+)\)", line.strip())
        if m:
            demo[os.path.basename(m.group(3))] = m.group(2)
    gen_gt: Dict[str, Dict[str, Any]] = {}
    for g in ("genB", "genC"):
        for c in json.load(open(os.path.join(EXP, "oq36", "corpus", g, "ground_truth.json")))["captures"]:
            gen_gt[c["pcap"]] = c
    p11 = {"smtps_tls12_chain_rsa2048.pcap": "RSA-2048 chain (openssl-generated); expected: no certificate issue",
           "smtps_tls12_selfsigned_rsa2048.pcap": "self-signed RSA-2048; expected: SEC-CERT-005",
           "smtps_tls12_weak_sha1_rsa1024.pcap": "RSA-1024 + SHA-1; expected: SEC-CERT-003 and SEC-CERT-004",
           "tls12_chain_rsa2048.pcap": "raw TLS 1.2 on a non-mail port (outside stated scope)",
           "tls12_selfsigned_rsa2048.pcap": "raw TLS 1.2 on a non-mail port (outside stated scope)",
           "tls12_weak_sha1_rsa1024.pcap": "raw TLS 1.2 on a non-mail port (outside stated scope)"}
    rows = ["| # | Capture | Corpus | SHA-256 | Protocol / sessions | Scenario and expectation source | Tags | Engine result |",
            "|---|---|---|---|---|---|---|---|"]
    for i, c in enumerate(cap, 1):
        n, corp = c["name"], c["corpus"]
        protos = sorted({s["protocol"] or "unidentified" for s in c["sessions"]})
        if corp == "oq33r":
            sc = scen[n]
            src = f"{sc['vendor']} {sc['scenario']}: \"{sc['expected']}\" (real server, scripted client; independent by construction)"
        elif corp == "oq28":
            if n in gt28:
                kinds = Counter(s["kind"] for s in gt28[n]["streams"])
                src = "per-stream labels by construction: " + ", ".join(f"{v}x {k}" for k, v in kinds.items()) + " (scapy-crafted; independent of engine)"
            else:
                src = "no ground-truth entry (hostile-content capture: prompt-injection text in message body)" if n.startswith("X_") else "crafted; no ground-truth entry"
        elif corp == "oq46":
            src = f"manifest: expected completeness {man46[n]['expected_completeness']} ({man46[n]['note']})"
        elif corp == "oq47":
            src = f"manifest: advertisement {man47[n]['expected_state']}/{man47[n]['expected_advertised']}" + (f"; must equal {man47[n]['equivalent_to']}" if man47[n].get('equivalent_to') else "")
        elif corp == "p11cert":
            src = p11[n] + " (by construction)"
        else:
            beh = Counter((s["behaviour"], s["ground_truth"]) for s in gen_gt[n]["streams"])
            src = "per-stream labels: " + ", ".join(f"{v}x {b}/{g}" for (b, g), v in sorted(beh.items())) + " (synthetic generator; independent of engine)"
        f = c["findings"]
        st = {x["status"] for x in f}
        tags = []
        if any(x["status"] == "OBSERVED_ISSUE" for x in f): tags.append("A")
        else: tags.append("B")
        if st & {"NOT_OBSERVABLE", "INSUFFICIENT_EVIDENCE"}: tags.append("C")
        if "AMBIGUOUS" in st or any(v["state"] == "AMBIGUOUS" for s in c["sessions"] for v in s["fields"].values()): tags.append("D")
        if any(s["completeness"] != "COMPLETE" for s in c["sessions"]): tags.append("E")
        if any(s["fields"]["tls_negotiated_version"]["state"] == "OBSERVED" for s in c["sessions"]): tags.append("F")
        if any(s["fields"]["starttls_advertised"]["state"] in ("OBSERVED", "AMBIGUOUS") for s in c["sessions"]): tags.append("G")
        if any(x["rule_id"].startswith("SEC-PLAIN") and x["status"] == "OBSERVED_ISSUE" for x in f): tags.append("H")
        if any(x["kind"] == "cross" and x["status"] in ("OBSERVED_ISSUE", "AMBIGUOUS") for x in f): tags.append("I")
        if n in demo: tags.append("J")
        if corp in ("oq46", "oq47") or n.startswith("X_") or corp == "p11cert" and n.startswith("tls12"): tags.append("K")
        demo_name = f" (demo: `{demo[n]}`)" if n in demo else ""
        rows.append(f"| {i} | `{n}`{demo_name} | {corp} | `{c['sha256']}` | {'/'.join(protos)}, {len(c['sessions'])} | {src} | {''.join(tags)} | {_graded(c)} |")
    return "\n".join(rows)


def main() -> None:
    es = evidence_states()
    json.dump(es, open(os.path.join(HERE, "results", "evidence_states.json"), "w"), indent=1, sort_keys=True, default=str)
    rm = rule_matrix()
    json.dump(rm, open(os.path.join(HERE, "results", "rule_matrix.json"), "w"), indent=1, sort_keys=True)
    open(os.path.join(HERE, "results", "inventory.md"), "w").write(inventory() + "\n")
    print(json.dumps(es, indent=1, default=str)[:4500])
    print(json.dumps(rm, indent=0)[:2500])


if __name__ == "__main__":
    main()
