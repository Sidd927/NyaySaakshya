"""
Phase B: edge cases the controlled corpora do not contain. Crafts small captures with scapy
into a temp dir (deterministic, nothing committed) and records what the production pipeline
says. Expectations are the project's own stated behaviour:
  * README / landing: "Anything outside email protocols ... A capture too thin to show
    anything is reported as insufficient evidence, not as a good grade."
  * pcapng is a supported input (.pcap/.pcapng/.cap)
  * the analysis must not depend on the container format

    PYTHONPATH=src python3 research/experiments/phaseb/edge_cases.py
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))

from scapy.all import DNS, DNSQR, Ether, IP, IPv6, TCP, UDP, Raw, wrpcap  # noqa: E402

from nyaysaakshya.backend.pipeline import run_pipeline  # noqa: E402

CLIENT, SERVER = "10.9.0.2", "10.9.0.3"
ETH = Ether(src="02:00:00:00:09:01", dst="02:00:00:00:09:02")   # explicit MACs: never resolve anything on a live network


def tcp_dialogue(ip, sport, dport, client_msgs, server_msgs, v6=False):
    """A plausible TCP exchange: handshake, alternating payloads, FIN."""
    pkts, seq_c, seq_s, t = [], 1000, 5000, 0
    base = (lambda s, d: ETH / (IPv6(src=s, dst=d) if v6 else IP(src=s, dst=d)))
    c, s = (ip[0], ip[1])
    def add(src, dst, sp, dp, flags, seq, ack, payload=b""):
        nonlocal t
        p = base(src, dst) / TCP(sport=sp, dport=dp, flags=flags, seq=seq, ack=ack) / (Raw(payload) if payload else b"")
        p.time = 1_700_000_000 + t
        t += 0.01
        pkts.append(p)
    add(c, s, sport, dport, "S", seq_c, 0); seq_c += 1
    add(s, c, dport, sport, "SA", seq_s, seq_c); seq_s += 1
    add(c, s, sport, dport, "A", seq_c, seq_s)
    for i in range(max(len(client_msgs), len(server_msgs))):
        if i < len(server_msgs):
            add(s, c, dport, sport, "PA", seq_s, seq_c, server_msgs[i]); seq_s += len(server_msgs[i])
        if i < len(client_msgs):
            add(c, s, sport, dport, "PA", seq_c, seq_s, client_msgs[i]); seq_c += len(client_msgs[i])
    add(c, s, sport, dport, "FA", seq_c, seq_s); seq_c += 1
    add(s, c, dport, sport, "FA", seq_s, seq_c)
    return pkts


def main() -> None:
    d = tempfile.mkdtemp(prefix="sms-edge-")
    cases = {}

    # 1 plain HTTP on 80 (not an email protocol)
    cases["http_plaintext_port80"] = tcp_dialogue((CLIENT, SERVER), 40000, 80,
        [b"GET /login HTTP/1.1\r\nHost: x\r\n\r\n", b"POST /login HTTP/1.1\r\nHost: x\r\n\r\nuser=a&pass=b"],
        [b"HTTP/1.1 200 OK\r\nContent-Length: 2\r\n\r\nok", b"HTTP/1.1 302 Found\r\n\r\n"])
    # 2 DNS over UDP
    dns = [ETH / IP(src=CLIENT, dst=SERVER) / UDP(sport=5353, dport=53) / DNS(rd=1, qd=DNSQR(qname="example.org"))]
    dns[0].time = 1_700_000_000
    cases["dns_udp_only"] = dns
    # 3 FTP cleartext credentials (a non-mail cleartext-auth protocol)
    cases["ftp_cleartext_login_port21"] = tcp_dialogue((CLIENT, SERVER), 40001, 21,
        [b"USER alice\r\n", b"PASS secret\r\n", b"QUIT\r\n"], [b"220 ftp ready\r\n", b"331 pw\r\n", b"230 ok\r\n", b"221 bye\r\n"])
    # 4 SMTP over IPv6, cleartext with AUTH
    cases["smtp_ipv6_cleartext_auth"] = tcp_dialogue(("fd00::2", "fd00::3"), 40002, 25,
        [b"EHLO c\r\n", b"AUTH PLAIN AGFsaWNlAHNlY3JldA==\r\n", b"QUIT\r\n"],
        [b"220 mail ESMTP\r\n", b"250-mail\r\n250 AUTH PLAIN\r\n", b"235 ok\r\n", b"221 bye\r\n"], v6=True)
    # 5 same SMTP over IPv4 (control for 4)
    cases["smtp_ipv4_cleartext_auth"] = tcp_dialogue((CLIENT, SERVER), 40003, 25,
        [b"EHLO c\r\n", b"AUTH PLAIN AGFsaWNlAHNlY3JldA==\r\n", b"QUIT\r\n"],
        [b"220 mail ESMTP\r\n", b"250-mail\r\n250 AUTH PLAIN\r\n", b"235 ok\r\n", b"221 bye\r\n"])
    # 6 SMTP on a NON-STANDARD port (2626)
    cases["smtp_nonstandard_port_2626"] = tcp_dialogue((CLIENT, SERVER), 40004, 2626,
        [b"EHLO c\r\n", b"AUTH PLAIN AGFsaWNlAHNlY3JldA==\r\n", b"QUIT\r\n"],
        [b"220 mail ESMTP\r\n", b"250-mail\r\n250 AUTH PLAIN\r\n", b"235 ok\r\n", b"221 bye\r\n"])

    results = []
    for name, pkts in cases.items():
        path = os.path.join(d, name + ".pcap")
        wrpcap(path, pkts)
        results.append(analyse(name, path))

    # 7 pcapng conversion of a known capture (tshark does the conversion)
    src = os.path.join(ROOT, "demo", "captures", "deepdive_cross_session_control_endpoint.pcap")
    ng = os.path.join(d, "deepdive.pcapng")
    subprocess.run(["tshark", "-r", src, "-F", "pcapng", "-w", ng], capture_output=True, timeout=120)
    ref = analyse("ref: deepdive .pcap", src)
    conv = analyse("deepdive converted to .pcapng", ng)
    conv["same_score_band_findings_as_pcap"] = (conv["score"], conv["band"], conv["issue_groups"]) == (ref["score"], ref["band"], ref["issue_groups"])
    results += [ref, conv]

    with open(os.path.join(HERE, "results", "edge_cases.json"), "w") as fh:
        json.dump(results, fh, indent=1, sort_keys=True, default=str)
    for r in results:
        print(json.dumps(r, default=str))


def analyse(name: str, path: str) -> dict:
    try:
        r = run_pipeline(path)
    except Exception as exc:
        return {"case": name, "exception": f"{type(exc).__name__}: {exc}"[:140]}
    a = r.assessment
    return {"case": name, "status": r.run.status.value, "packets": r.run.packet_count,
            "sessions": len(r.sessions), "protocols": sorted({s.protocol or "unidentified" for s in r.sessions}),
            "band": a.band.value, "score": round(a.score.value, 2) if a.score.scored else None,
            "assessed": f"{a.coverage.sessions_assessed}/{a.coverage.sessions_total}",
            "issue_groups": sorted((g.issue_class.value, g.severity.value, g.recurrence) for g in a.issue_groups if g.penalising),
            "obs": dict(a.coverage.observation_counts)}


if __name__ == "__main__":
    main()
