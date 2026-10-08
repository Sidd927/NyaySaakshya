"""
Phase B: real-vendor captures (Postfix, Dovecot) against expectations that hold BY CONSTRUCTION
(scripted client + configured real server; see oq33r/out/scenarios.json), not against the engine.
Expectations below are taken from each scenario's own `expected` text. Streams of <=3 packets
are reported separately because they are fragments of the harness's own readiness probe
(a connect/close with no dialogue), not mail sessions.

    python3 research/experiments/phaseb/oq33r_check.py     (after run_corpus.py)
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _corpus import load_captures  # noqa: E402
cap = {c["name"]: c for c in load_captures()}

E = {  # name: (advertised(state,value), requested, tls_state, version, required OBSERVED_ISSUE rules, allowed OBSERVED_ISSUE rules)
 "postfix_smtp_starttls_upgrade.pcap": (("OBSERVED", True), True, "ESTABLISHED", "TLS1.3", set(), set()),
 "postfix_smtp_client_declines.pcap": (("OBSERVED", True), False, "NONE", None, {"SEC-PLAIN-002"}, {"SEC-PLAIN-002"}),
 "postfix_smtp_plaintext_session.pcap": (("OBSERVED", True), False, "NONE", None, {"SEC-PLAIN-002"}, {"SEC-PLAIN-002"}),
 "postfix_smtp_no_starttls_offered.pcap": (("AMBIGUOUS", False), False, "NONE", None, {"SEC-PLAIN-002"}, {"SEC-PLAIN-002"}),
 "dovecot_imap_starttls_upgrade.pcap": (("OBSERVED", True), True, "ESTABLISHED", "TLS1.3", set(), set()),
 "dovecot_imap_plaintext_login.pcap": (("OBSERVED", True), False, "NONE", None, {"SEC-PLAIN-001", "SEC-PLAIN-002"}, {"SEC-PLAIN-001", "SEC-PLAIN-002"}),
 "dovecot_pop3_stls_upgrade.pcap": (("OBSERVED", True), True, "ESTABLISHED", "TLS1.3", set(), set()),
 "dovecot_pop3_plaintext_login.pcap": (("OBSERVED", True), False, "NONE", None, {"SEC-PLAIN-001", "SEC-PLAIN-002"}, {"SEC-PLAIN-001", "SEC-PLAIN-002"}),
 "dovecot_imap_imaps_implicit_tls.pcap": (("NOT_OBSERVABLE", None), None, "ESTABLISHED", "TLS1.3", set(), set()),
 "dovecot_pop3_pop3s_implicit_tls.pcap": (("NOT_OBSERVABLE", None), None, "ESTABLISHED", "TLS1.3", set(), set()),
}
rows, ok_all = [], 0
for name, (adv, req, tls, ver, need, allow) in E.items():
    c = cap[name]
    main = max(c["sessions"], key=lambda s: s["packets"])
    frag = [s for s in c["sessions"] if s["packets"] <= 3]
    f = main["fields"]
    issues = {x["rule_id"] for x in c["findings"] if x["kind"] == "single" and x["status"] == "OBSERVED_ISSUE" and x["stream"] == main["stream"]}
    frag_issues = {x["rule_id"] for x in c["findings"] if x["kind"] == "single" and x["status"] == "OBSERVED_ISSUE" and x["stream"] in {s["stream"] for s in frag}}
    checks = {
        "advertisement": (f["starttls_advertised"]["state"], f["starttls_advertised"]["value"]) == adv,
        "requested": req is None or f["starttls_requested"]["value"] is req,
        "tls_state": main["tls_state"] == tls,
        "version": f["tls_negotiated_version"]["value"] == ver,
        "required_issues_present": need <= issues,
        "no_unexpected_issues_main_session": issues <= allow,
    }
    ok = all(checks.values())
    ok_all += ok
    rows.append({"capture": name, "main_session_ok": ok, "failed": [k for k, v in checks.items() if not v],
                 "fragment_streams(<=3 packets)": len(frag), "issues_on_fragments": sorted(frag_issues),
                 "band": c["overall_posture"], "score": c["score"]["value"]})
res = {"captures": len(E), "main_session_expectations_met": ok_all, "rows": rows,
       "captures_whose_band_is_affected_by_fragment_findings": [r["capture"] for r in rows if r["issues_on_fragments"]]}
json.dump(res, open(os.path.join(HERE, "results", "oq33r_check.json"), "w"), indent=1)
print(json.dumps(res, indent=1))
