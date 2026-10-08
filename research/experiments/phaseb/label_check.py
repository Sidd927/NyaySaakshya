"""
Phase B, layer 2: do the engine's *verdicts* respect independent labels and its own rules?

Invariants are PRE-REGISTERED here, written before any verdict-level result was inspected,
and each carries its basis. They are derived from (a) rule definitions in
src/nyaysaakshya/analysis/rules, (b) wire facts from the tshark oracle (oracle_compare.json),
(c) per-stream generation labels (ground_truth.json sidecars written by the corpus
generators, never visible to the engine), or (d) the engine's own published invariants
(analysis/model.py: "unestablished conditions may not assert impact").

  INV-1  benign completed TLS >= 1.2 stream            -> no single-session OBSERVED_ISSUE
         basis: label BENIGN_TLS / BENIGN_IMPLICIT / LEGIT_* (TLS1.2+) ; rules cite RFC 8996 /
         RFC 8314 only for deprecated TLS or cleartext
  INV-2  stream whose oracle version is TLS1.0/1.1      -> SEC-TLS-001 OBSERVED_ISSUE
         basis: tls_rules.py (TLS1.0/1.1 -> HIGH, RFC 8996)
  INV-3  complete mail stream with no TLS on the wire   -> SEC-PLAIN-002 OBSERVED_ISSUE;
         and oracle cleartext auth -> SEC-PLAIN-001 OBSERVED_ISSUE (HIGH)
         basis: plaintext_rules.py
  INV-4  no finding text affirms an attack / attacker / interception (manual review of hits)
         basis: README + starttls_rules.py ("must never conclude STARTTLS was stripped")
  INV-5  absent-advertisement streams produce the SAME single-session evidence signature
         whether labelled ATTACK_STRIP_ADVERT or BENIGN_NO_SUPPORT/CONFIG_CHANGE
         basis: starttls_rules.py docstring ("B_strip_advert and I_no_support produce the
         same evidence ... AMBIGUOUS")
  INV-6  a stream that is not COMPLETE (or is a <=3-packet fragment) -> no OBSERVED_ISSUE
         basis: analysis/model.py invariant + evidence-provenance principle
         (INCOMPLETE must not become a security assertion)
  INV-7  capture-level cross-session: attack-labelled strip streams coexisting with
         upgrading control clients at the same server -> CS-STARTTLS-001 emitted;
         strip streams with no control population -> not emitted as a deviation
         basis: README "Why cross-session reasoning?" ; crosssession/rules.py
  INV-8  a capture containing attack-labelled streams is never banded STRONG
         basis: it must not give reassurance over labelled-hostile traffic
  OQ46   session completeness equals the manifest's expected_completeness
  OQ47   advertisement state/value equals manifest; segmented twins equal their reference

REVISIONS (recorded because a validation that quietly edits its own expectations is worthless).
First run, expectations exactly as registered above: INV-3 1094/1116 (22 "failures"),
INV-7 two capture-level misses (B06/C06 strip_command), OQ47 9 of 9 twins "unequal".
All three were errors in the EXPECTATION, not in the engine, and were corrected after triage:
  * INV-3: the 22 were failed-upgrade streams in which a TLS ClientHello WAS sent (the oracle
    now records tls_records); "no TLS on the wire" was a wrong precondition. INV-3 now applies
    only to streams with no TLS record in either direction.
  * INV-7: CS-STARTTLS-001 is an ADVERTISEMENT rule; strip_command streams advertise STARTTLS,
    never request it, and are wire-identical to a client that declined (see INV-5b), so no rule
    defines a deviation to expect. INV-7 is now scoped to ATTACK_STRIP_ADVERT only.
  * OQ47: the twin comparison included frame numbers, which legitimately change with
    segmentation. Frames are now excluded; states, values, findings and score are compared.
No expectation was changed because of an engine result that was inconvenient. The INV-6 result
(41 of 44 non-complete streams carry an OBSERVED_ISSUE) was NOT revised.

    python3 research/experiments/phaseb/label_check.py     (after run_corpus.py, oracle_check.py)
"""
from __future__ import annotations

import json
import os
import sys
import re
from collections import Counter, defaultdict
from typing import Any, Dict, List, Tuple

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _corpus import load_captures  # noqa: E402
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
EXP = os.path.join(ROOT, "research", "experiments")

corpus = {c["name"]: c for c in load_captures()}
oracle = defaultdict(dict)
for r in json.load(open(os.path.join(HERE, "results", "oracle_compare.json")))["rows"]:
    oracle[r["capture"]][r["stream"]] = r["oracle"]

BENIGN_TLS_LABELS = {"BENIGN_TLS", "BENIGN_IMPLICIT", "LEGIT_TLS", "LEGIT_IMPLICIT_TLS", "LEGIT_TLS12"}
ATTACK_LABELS = {"ATTACK_STRIP_ADVERT", "ATTACK_STRIP_COMMAND"}
NO_ADVERT_LABELS = {"ATTACK_STRIP_ADVERT", "BENIGN_NO_SUPPORT", "BENIGN_CONFIG_CHANGE", "LEGIT_PLAINTEXT_CFG"}


def labelled_streams() -> List[Dict[str, Any]]:
    """Unify the three ground-truth sidecars: one dict per labelled stream."""
    out: List[Dict[str, Any]] = []
    g = json.load(open(os.path.join(EXP, "oq28", "pcaps", "ground_truth.json")))
    for case in g:
        for s in case["streams"]:
            cip, rest = s["stream"].split("->")[0], s["stream"].split("->")[1]
            ip, port = cip.rsplit(":", 1)
            out.append({"corpus": "oq28", "capture": case["pcap"], "client_ip": ip, "client_port": int(port),
                        "server_ip": rest, "label": s["ground_truth"], "behaviour": s["kind"],
                        "protocol": s["protocol"], "tls_version": None})
    for gen in ("genB", "genC"):
        g = json.load(open(os.path.join(EXP, "oq36", "corpus", gen, "ground_truth.json")))
        for case in g["captures"]:
            for s in case["streams"]:
                out.append({"corpus": f"oq36-{gen}", "capture": case["pcap"], "client_ip": s["client"],
                            "client_port": s["client_port"], "server_ip": s["server"],
                            "label": s["ground_truth"], "behaviour": s["behaviour"],
                            "protocol": s["protocol"], "tls_version": s.get("tls_version")})
    return out


def engine_session(cap: Dict[str, Any], ls: Dict[str, Any]):
    for s in cap["sessions"]:
        if s["client_ip"] == ls["client_ip"] and s["client_port"] == ls["client_port"] and s["server_ip"] == ls["server_ip"]:
            return s
    return None


def single_findings(cap, stream):
    return [f for f in cap["findings"] if f["kind"] == "single" and f["stream"] == stream]


def issues(cap, stream):
    return [f for f in single_findings(cap, stream) if f["status"] == "OBSERVED_ISSUE"]


def main() -> None:
    res: Dict[str, Any] = {}
    L = labelled_streams()
    matched = unmatched = 0
    inv: Dict[str, List[Dict[str, Any]]] = defaultdict(list)   # inv -> list of records {ok, ...}

    sig_by_label: Dict[str, Counter] = defaultdict(Counter)
    sig_cmd: Dict[str, Counter] = defaultdict(Counter)

    for ls in L:
        cap = corpus[ls["capture"]]
        s = engine_session(cap, ls)
        if s is None:
            unmatched += 1
            continue
        matched += 1
        st = s["stream"]
        o = oracle[ls["capture"]].get(st, {})
        iss = issues(cap, st)
        rec = {"capture": ls["capture"], "stream": st, "label": ls["label"], "behaviour": ls["behaviour"],
               "issues": [(f["rule_id"], f["severity"]) for f in iss], "completeness": s["completeness"],
               "packets": s["packets"]}
        complete = s["completeness"] == "COMPLETE" and s["packets"] > 3

        # INV-1
        ver = o.get("version")
        tls12plus = ver in ("TLS1.2", "TLS1.3")
        if ls["label"] in BENIGN_TLS_LABELS or (ls["label"] == "BENIGN_LEGACY_TLS" and ver == "TLS1.2"):
            if tls12plus and complete:
                inv["INV-1"].append({**rec, "ok": not iss})
        # INV-2
        if ver in ("TLS1.0", "TLS1.1"):
            hit = any(r == "SEC-TLS-001" for r, _ in rec["issues"])
            inv["INV-2"].append({**rec, "ok": hit})
        # INV-3
        if s["protocol"] and complete and not o.get("tls_records", False):
            has = any(r == "SEC-PLAIN-002" for r, _ in rec["issues"])
            inv["INV-3"].append({**rec, "ok": has, "what": "PLAIN-002"})
            if o.get("auth"):
                has1 = any(r == "SEC-PLAIN-001" and sv == "HIGH" for r, sv in rec["issues"])
                inv["INV-3"].append({**rec, "ok": has1, "what": "PLAIN-001"})
        # INV-5 signature (compared across labels afterwards)
        if ls["label"] in NO_ADVERT_LABELS and ls["protocol"] == "smtp" and s["fields"]["starttls_advertised"]["state"] != "NOT_OBSERVABLE":
            sig = (s["fields"]["starttls_advertised"]["state"], s["fields"]["starttls_advertised"]["value"],
                   s["completeness"],
                   tuple(sorted((f["rule_id"], f["status"]) for f in single_findings(cap, st))))
            sig_by_label[ls["label"]][sig] += 1
        # INV-6
        if not complete:
            inv["INV-6"].append({**rec, "ok": not iss})
        # INV-5b: strip_command is wire-identical to a decline
        if ls["behaviour"] in ("strip_command", "decline", "legit_decline") and ls["protocol"] == "smtp":
            f = s["fields"]
            sig_cmd[ls["behaviour"]][(f["starttls_advertised"]["state"], f["starttls_advertised"]["value"],
                                      f["starttls_requested"]["value"], s["tls_state"], o.get("auth"))] += 1

    # INV-6 also over unlabelled fragments (oq33r probe streams, oq46 truncated cases)
    for cap in corpus.values():
        if cap["corpus"] in ("oq33r", "oq46", "oq47", "p11cert"):
            for s in cap["sessions"]:
                complete = s["completeness"] == "COMPLETE" and s["packets"] > 3
                if not complete and s["protocol"]:
                    iss = issues(cap, s["stream"])
                    inv["INV-6"].append({"capture": cap["name"], "stream": s["stream"], "label": None,
                                         "completeness": s["completeness"], "packets": s["packets"],
                                         "issues": [(f["rule_id"], f["severity"]) for f in iss], "ok": not iss})

    # INV-4: text scan
    pat = re.compile(r"(attacker|\battack\b|stripp|man-in-the-middle|intercept|compromis|stolen|hijack|malicious)", re.I)
    hits: List[Dict[str, str]] = []
    for cap in corpus.values():
        for f in cap["findings"]:
            for fld in ("conclusion", "explanation"):
                t = f.get(fld) or ""
                for m in pat.finditer(t):
                    hits.append({"capture": cap["name"], "rule": f["rule_id"], "status": f["status"], "field": fld,
                                 "context": t[max(0, m.start() - 70): m.end() + 70].replace("\n", " ")})
    uniq: Dict[Tuple[str, str, str], Dict[str, str]] = {}
    for h in hits:
        uniq.setdefault((h["rule"], h["status"], h["context"]), h)

    # INV-7 / INV-8 capture level
    cap_rows = []
    by_cap: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for ls in L:
        by_cap[ls["capture"]].append(ls)
    for name, lss in sorted(by_cap.items()):
        cap = corpus[name]
        attack = [x for x in lss if x["label"] == "ATTACK_STRIP_ADVERT"]
        attack_cmd = [x for x in lss if x["label"] == "ATTACK_STRIP_COMMAND"]
        servers_attack = {x["server_ip"] for x in attack}
        control = [x for x in lss if x["behaviour"] in ("upgrade", "normal_tls") and x["server_ip"] in servers_attack
                   and x["label"] in BENIGN_TLS_LABELS | {"BENIGN_LEGACY_TLS", "BENIGN_CONFIG_CHANGE", "LEGIT_TLS10", "LEGIT_TLS11"}
                   and x["client_ip"] not in {a["client_ip"] for a in attack}]
        cs001 = [f for f in cap["findings"] if f["rule_id"] == "CS-STARTTLS-001"]
        cs_issue = [f for f in cs001 if f["status"] in ("OBSERVED_ISSUE", "AMBIGUOUS")]
        cap_rows.append({"capture": name, "attack_streams": len(attack), "strip_command_streams": len(attack_cmd),
                         "control_streams": len(control), "any_attack_label": bool(attack or attack_cmd),
                         "cs_statuses": sorted(Counter(f["status"] for f in cs001).items()),
                         "band": cap["overall_posture"], "score": cap["score"]["value"],
                         "expect_cs": bool(attack and control), "got_cs_deviation": bool(cs_issue),
                         "cs001_issue_count": len([f for f in cs001 if f["status"] == "OBSERVED_ISSUE"])})

    # INV-9: CS-STARTTLS-001 OBSERVED_ISSUE in captures that carry no attack-advert label
    inv9 = []
    attack_caps = {x["capture"] for x in L if x["label"] == "ATTACK_STRIP_ADVERT"}
    for name in sorted({x["capture"] for x in L}):
        n_issue = len([f for f in corpus[name]["findings"] if f["rule_id"] == "CS-STARTTLS-001" and f["status"] == "OBSERVED_ISSUE"])
        if name not in attack_caps:
            inv9.append({"capture": name, "cs001_observed_issue": n_issue, "ok": n_issue == 0})
    res["INV-9"] = inv9

    # OQ46 / OQ47
    man = json.load(open(os.path.join(EXP, "oq46_47", "manifest.json")))
    o46 = []
    for c in man["oq46"]:
        cap = corpus[c["pcap"]]
        got = cap["sessions"][0]["completeness"]
        o46.append({"case": c["case"], "expected": c["expected_completeness"], "got": got, "ok": got == c["expected_completeness"]})
    def sig47(cap):
        s = cap["sessions"][0]
        fields = {k: (v["state"], v["value"]) for k, v in s["fields"].items()}
        return json.dumps([fields, sorted((f["rule_id"], f["status"], f["severity"]) for f in cap["findings"]),
                           cap["score"]["value"], cap["overall_posture"]], sort_keys=True)
    o47 = []
    for c in man["oq47"]:
        cap = corpus[c["pcap"]]
        f = cap["sessions"][0]["fields"]["starttls_advertised"]
        row = {"case": c["case"], "expected": [c["expected_state"], c["expected_advertised"]],
               "got": [f["state"], f["value"]], "ok_state": f["state"] == c["expected_state"] and f["value"] == c["expected_advertised"]}
        if c.get("equivalent_to"):
            ref = corpus[c["equivalent_to"] + ".pcap"]
            row["twin_equal"] = sig47(cap) == sig47(ref)
        o47.append(row)

    inv6_sub: Dict[str, int] = Counter()
    for r in inv["INV-6"]:
        if r["ok"]:
            inv6_sub["pass"] += 1
        elif r["packets"] <= 3:
            inv6_sub["fail: <=3-packet fragment"] += 1
        elif r["capture"].startswith("F_missing_setup"):
            inv6_sub["fail: missing setup, dialogue+teardown observed (arguable)"] += 1
        else:
            inv6_sub["fail: truncated before TLS could be observed"] += 1
    inv6_sub = dict(inv6_sub)

    def tally(name):
        rows = inv[name]
        return {"n": len(rows), "ok": sum(1 for r in rows if r["ok"]), "fail": sum(1 for r in rows if not r["ok"])}

    summary = {"labelled_streams": len(L), "matched_to_engine_session": matched, "unmatched": unmatched,
               **{k: tally(k) for k in ("INV-1", "INV-2", "INV-3", "INV-6")}}
    res.update({"summary": summary,
                "INV-1_failures": [r for r in inv["INV-1"] if not r["ok"]][:40],
                "INV-2_failures": [r for r in inv["INV-2"] if not r["ok"]][:40],
                "INV-3_failures": [r for r in inv["INV-3"] if not r["ok"]][:40],
                "INV-6_failures": [r for r in inv["INV-6"] if not r["ok"]],
                "INV-4_unique_hits": list(uniq.values()),
                "INV-5b_strip_command_vs_decline": {k: {str(sg): n for sg, n in v.items()} for k, v in sig_cmd.items()},
                "INV-6_by_subtype": inv6_sub,
                "INV-5_signatures": {k: {json.dumps(sig): n for sig, n in v.items()} for k, v in sig_by_label.items()},
                "INV-7_8_capture_rows": cap_rows, "OQ46": o46, "OQ47": o47})
    with open(os.path.join(HERE, "results", "label_check.json"), "w") as fh:
        json.dump(res, fh, indent=1, sort_keys=True, default=str)

    print(json.dumps(summary, indent=1))
    for k in ("INV-1", "INV-2", "INV-3", "INV-6"):
        bad = [r for r in inv[k] if not r["ok"]]
        caps = Counter(r["capture"] for r in bad)
        print(f"\n{k}: {len(inv[k])} streams, {len(bad)} fail; by capture: {dict(list(caps.items())[:20])}")
        for r in bad[:4]:
            print("   e.g.", {x: r[x] for x in ("capture", "stream", "label", "issues", "completeness", "packets")})
    print("\nINV-6 subtypes:", inv6_sub)
    print("\nINV-5b strip_command vs decline wire/engine signature:")
    for k, v in sig_cmd.items():
        for sg, n in v.items():
            print("  ", k, n, sg)
    print("\nINV-4 unique text hits:", len(uniq))
    print("\nINV-5 signatures by label:")
    for lab, v in sig_by_label.items():
        for sig, n in v.items():
            print("  ", lab, n, sig)
    print("\nINV-7/8 capture rows with attack streams:")
    for r in cap_rows:
        if r["attack_streams"]:
            print("  ", r)
    print("\nINV-9 captures without ATTACK_STRIP_ADVERT:", len(inv9), "| with CS-STARTTLS-001 OBSERVED_ISSUE:", [r["capture"] for r in inv9 if not r["ok"]] or "none")
    print("\nOQ46:", [(r["case"], r["expected"], r["got"]) for r in o46 if not r["ok"]] or "all match")
    print("OQ47 state mismatches:", [r for r in o47 if not r["ok_state"]] or "none", "| twin inequal:", [r["case"] for r in o47 if r.get("twin_equal") is False] or "none")


if __name__ == "__main__":
    main()
