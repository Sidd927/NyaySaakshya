"""
Phase B, layer 1: does the engine read the packets correctly?

For every TCP stream in every capture, read the *reassembled raw bytes* straight from
tshark (`-z follow,tcp,raw`), decide a handful of wire facts with plain regular
expressions, and compare them with what the engine extracted (results/corpus_run.json).
This oracle shares no extraction logic with the engine: it never sees an EvidenceState,
a session object or a rule. What it shares is tshark itself (TCP reassembly, TLS dissector
for ServerHello version), which is stated as a limit in VALIDATION.md.

Wire facts checked (server side = the end on a well-known mail port):
  advertised  server bytes contain a STARTTLS / STLS capability line
  requested   client sent a STARTTLS / STLS command line
  version     ServerHello negotiated version (tshark's TLS dissector)
  auth        client sent AUTH / LOGIN / USER / PASS in cleartext before any TLS record

    PYTHONPATH=src python3 research/experiments/phaseb/run_corpus.py      # first
    python3 research/experiments/phaseb/oracle_check.py

Writes results/oracle_compare.json. Needs tshark.
"""
from __future__ import annotations

import json
import os
import sys
import re
import subprocess
from collections import Counter, defaultdict
from typing import Any, Dict, List, Optional

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _corpus import load_captures  # noqa: E402
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
MAIL_PORTS = {25, 587, 465, 2525, 143, 993, 110, 995}

ADV = re.compile(rb"(?im)\b(STARTTLS|STLS)\b")
REQ = re.compile(rb"(?im)^(?:[A-Za-z0-9.]+\s+)?(STARTTLS|STLS)\s*$")
AUTH = re.compile(rb"(?im)^(?:[A-Za-z0-9.]+\s+)?(AUTH(?:ENTICATE)?\s|LOGIN\s|USER\s|PASS\s)")
TLS_REC = re.compile(rb"\x16\x03[\x00-\x04]")
VERSION = {"0x0300": "SSL3.0", "0x0301": "TLS1.0", "0x0302": "TLS1.1", "0x0303": "TLS1.2", "0x0304": "TLS1.3"}


def tshark(args: List[str]) -> str:
    return subprocess.run(["tshark", "-r", *args], capture_output=True, text=True,
                          timeout=180).stdout


def follow(path: str, stream: int) -> Dict[str, Any]:
    out = tshark([path, "-q", "-z", f"follow,tcp,raw,{stream}"])
    nodes: List[str] = []
    to_node1 = b""   # node0 -> node1 (no leading tab)
    to_node0 = b""   # node1 -> node0 (leading tab)
    for line in out.splitlines():
        if line.startswith("Node "):
            nodes.append(line.split(": ", 1)[1].strip())
        elif re.fullmatch(r"\t?[0-9a-fA-F]+", line):
            data = bytes.fromhex(line.strip())
            if line.startswith("\t"):
                to_node0 += data
            else:
                to_node1 += data
    def port(n: str) -> int:
        return int(n.rsplit(":", 1)[1])
    if len(nodes) != 2:
        return {"ok": False}
    p0, p1 = port(nodes[0]), port(nodes[1])
    if p1 in MAIL_PORTS or (p0 not in MAIL_PORTS and p1 < p0):
        server, client = to_node0, to_node1
    else:
        server, client = to_node1, to_node0
    return {"ok": True, "server": server, "client": client}


def server_hello_versions(path: str) -> Dict[int, Optional[str]]:
    out = tshark([path, "-Y", "tls.handshake.type == 2", "-T", "fields", "-e", "tcp.stream",
                  "-e", "tls.handshake.version", "-e", "tls.handshake.extensions.supported_version"])
    res: Dict[int, Optional[str]] = {}
    for line in out.splitlines():
        parts = line.split("\t")
        if not parts[0].isdigit():
            continue
        sv = parts[2] if len(parts) > 2 else ""
        legacy = parts[1].split(",")[0] if len(parts) > 1 and parts[1] else ""
        res[int(parts[0])] = VERSION.get(sv.split(",")[0], None) if sv else VERSION.get(legacy)
    return res


def oracle(path: str, stream: int, hello: Dict[int, Optional[str]]) -> Dict[str, Any]:
    f = follow(path, stream)
    if not f["ok"]:
        return {"ok": False}
    server, client = f["server"], f["client"]
    first_tls = TLS_REC.search(client)
    clear_client = client[: first_tls.start()] if first_tls else client
    return {
        "ok": True,
        "advertised": bool(ADV.search(server[: server.find(b"\x16\x03")] if b"\x16\x03" in server else server)),
        "requested": bool(REQ.search(clear_client)),
        "version": hello.get(stream),
        "auth": bool(AUTH.search(clear_client)),
        "tls_records": bool(first_tls or TLS_REC.search(server)),
        "client_bytes": len(client), "server_bytes": len(server),
    }


def main() -> None:
    corpus = load_captures()
    rows: List[Dict[str, Any]] = []
    for cap in corpus:
        path = os.path.join(ROOT, cap["file"])
        hello = server_hello_versions(path)
        for s in cap["sessions"]:
            if s["stream"] is None:
                continue
            o = oracle(path, s["stream"], hello)
            if not o["ok"]:
                rows.append({"capture": cap["name"], "stream": s["stream"], "oracle_failed": True})
                continue
            fld = s["fields"]
            eng = {
                "advertised": fld["starttls_advertised"]["state"] == "OBSERVED" and fld["starttls_advertised"]["value"] is True,
                "requested": fld["starttls_requested"]["value"] is True,
                "version": fld["tls_negotiated_version"]["value"] if fld["tls_negotiated_version"]["state"] == "OBSERVED" else None,
                "auth": fld["auth_activity"]["state"] == "OBSERVED" and fld["auth_activity"]["value"] is True,
            }
            rows.append({"corpus": cap["corpus"], "capture": cap["name"], "stream": s["stream"],
                         "protocol": s["protocol"], "implicit_tls": s["implicit_tls"],
                         "oracle": {k: o[k] for k in ("advertised", "requested", "version", "auth", "tls_records")},
                         "engine": eng,
                         "disagree": [k for k in eng if eng[k] != o[k]],
                         "payload_bytes": [o["client_bytes"], o["server_bytes"]]})
    tally: Dict[str, Counter] = defaultdict(Counter)
    for r in rows:
        if r.get("oracle_failed"):
            tally["_oracle_failed"]["n"] += 1
            continue
        for k in ("advertised", "requested", "version", "auth"):
            tally[k]["agree" if k not in r["disagree"] else "disagree"] += 1
    summary = {k: dict(v) for k, v in tally.items()}
    with open(os.path.join(HERE, "results", "oracle_compare.json"), "w") as fh:
        json.dump({"summary": summary, "streams": len(rows), "rows": rows}, fh, indent=1, sort_keys=True)
    print(json.dumps({"streams": len(rows), **summary}, indent=1))
    bad = [r for r in rows if r.get("disagree")]
    print(f"{len(bad)} streams with >=1 disagreement")
    for r in bad[:60]:
        print(r["capture"], "stream", r["stream"], r["protocol"], "disagree", r["disagree"], "oracle", r["oracle"], "engine", r["engine"])


if __name__ == "__main__":
    main()
