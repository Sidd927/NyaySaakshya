"""
Phase B.2 tests: evidence-integrity corrections (D1, D2, D3).

Governing principle: when the evidence is insufficient the engine must ABSTAIN rather than
accidentally certify. Each test below pins one half of that principle:

  * what must no longer be asserted (a truncated stream is not a plaintext session; a
    session nothing could be read from is not "assessed"; unsupported traffic is not STRONG);
  * what must still be asserted (genuine cleartext is still flagged; a clean, complete TLS
    session is still clean; an abstention rule is never silently dropped).

Unit tests use hand-built sessions and findings. Capture-level tests use the committed
research corpus and skip cleanly when tshark or the corpus is absent.
"""
import os
import re
import tempfile

import pytest

from nyaysaakshya.analysis import FindingStatus, SecurityAnalysisEngine, Severity
from nyaysaakshya.analysis.rules.configuration_rules import InsecureConfigurationRule
from nyaysaakshya.analysis.rules.plaintext_rules import PlaintextSessionRule
from nyaysaakshya.analysis.rules.starttls_rules import StartTlsAdvertisementRule
from nyaysaakshya.dissect import TsharkAdapter
from nyaysaakshya.evidence.states import EvidenceField, EvidenceState
from nyaysaakshya.posture import PostureBand, PostureEngine
from nyaysaakshya.posture.fusion import FusionEngine
from nyaysaakshya.posture.model import FactKind
from nyaysaakshya.session.model import Completeness, SessionEvidence, TlsState

from test_posture_engine import session
from test_posture_fusion import finding

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXP = os.path.join(ROOT, "research", "experiments")
OQ33R = os.path.join(EXP, "oq33r", "out")
OQ46 = os.path.join(EXP, "oq46_47", "oq46")
OQ28 = os.path.join(EXP, "oq28", "pcaps")
P11 = os.path.join(EXP, "p11cert", "out")
GEN_C = os.path.join(EXP, "oq36", "corpus", "genC")
DEMO = os.path.join(ROOT, "demo", "captures")
AT = "2026-10-08T00:00:00Z"
ENGINE = PostureEngine()


def _tshark() -> bool:
    try:
        TsharkAdapter().version()
        return True
    except Exception:
        return False


needs_tshark = pytest.mark.skipif(not _tshark(), reason="tshark not installed")
needs_corpus = pytest.mark.skipif(not os.path.isdir(OQ46), reason="research corpus not present")


def _pipeline(path):
    from nyaysaakshya.backend.pipeline import run_pipeline
    return run_pipeline(path)


def _stream(result, stream_id):
    return next(s for s in result.sessions if s.tcp_stream_id == stream_id)


def _plain002(result, stream_id):
    return [f for f in result.findings
            if f.rule_id == "SEC-PLAIN-002" and f.tcp_stream_id == stream_id]


# ============================================================ D2b: fusion / coverage
def test_informational_finding_is_not_positive_evidence():
    fused = FusionEngine().fuse(
        [finding("SEC-CFG-001", status=FindingStatus.INFORMATIONAL, severity=Severity.INFO)],
        (), ()).findings
    assert [f.key.fact_kind for f in fused] == [FactKind.INFORMATIONAL]


def test_compliant_finding_is_still_positive_evidence():
    fused = FusionEngine().fuse(
        [finding("SEC-TLS-001", status=FindingStatus.COMPLIANT, severity=Severity.INFO)],
        (), ()).findings
    assert [f.key.fact_kind for f in fused] == [FactKind.POSITIVE_EVIDENCE]


def test_a_session_carrying_only_informational_notes_is_not_assessed():
    """The D2 defect: a note such as 'checklist: 1 item failed' made an unreadable session
    'assessed', and the posture engine then graded it STRONG."""
    note = finding("SEC-CFG-001", status=FindingStatus.INFORMATIONAL, severity=Severity.INFO)
    a = ENGINE.assess([session(1)], [note], [], capture_id="cap", generated_at=AT)
    assert a.coverage.sessions_assessed == 0
    assert a.band is PostureBand.INSUFFICIENT_EVIDENCE


@pytest.mark.parametrize("status,severity", [
    (FindingStatus.COMPLIANT, Severity.INFO),
    (FindingStatus.OBSERVED_ISSUE, Severity.HIGH),
])
def test_genuine_conclusions_still_count_as_assessed(status, severity):
    a = ENGINE.assess([session(1)], [finding(status=status, severity=severity)], [],
                      capture_id="cap", generated_at=AT)
    assert a.coverage.sessions_assessed == 1


def test_abstentions_do_not_count_as_assessed():
    f = finding("SEC-STLS-001", status=FindingStatus.INSUFFICIENT_EVIDENCE, severity=Severity.INFO)
    a = ENGINE.assess([session(1)], [f], [], capture_id="cap", generated_at=AT)
    assert a.coverage.sessions_assessed == 0
    assert a.band is PostureBand.INSUFFICIENT_EVIDENCE


# ============================================================ D2: supported-protocol scope
def test_engine_runs_no_single_session_rule_on_an_unidentified_stream():
    assert SecurityAnalysisEngine().analyse_session(session(1, protocol=None)) == []


def test_unsupported_sessions_leave_the_coverage_denominator():
    """Background traffic must not dilute genuinely assessed mail sessions below the floor."""
    ok = finding(status=FindingStatus.COMPLIANT, severity=Severity.INFO, stream="cap:1")
    sessions = [session(1)] + [session(i, protocol=None) for i in range(2, 8)]
    a = ENGINE.assess(sessions, [ok], [], capture_id="cap", generated_at=AT)
    cov = a.coverage
    assert (cov.sessions_total, cov.sessions_unsupported, cov.sessions_supported) == (7, 6, 1)
    assert cov.sessions_assessed == 1 and cov.assessed_fraction == 1.0
    assert a.band is PostureBand.STRONG
    assert a.to_dict()["coverage"]["sessions_unsupported"] == 6


def test_a_capture_with_no_supported_session_is_withheld_never_strong():
    sessions = [session(i, protocol=None) for i in range(1, 4)]
    a = ENGINE.assess(sessions, [], [], capture_id="cap", generated_at=AT)
    assert a.coverage.sessions_assessed == 0
    assert a.band is PostureBand.INSUFFICIENT_EVIDENCE


def test_coverage_of_a_fully_supported_capture_is_unchanged_on_the_wire():
    a = ENGINE.assess([session(1)], [finding(status=FindingStatus.COMPLIANT,
                                              severity=Severity.INFO)], [],
                      capture_id="cap", generated_at=AT)
    assert "sessions_unsupported" not in a.to_dict()["coverage"]


# ============================================================ D1/D3: rule preconditions (unit)
def _tls_less(transition: EvidenceField, **kw) -> SessionEvidence:
    base = dict(
        capture_id="cap", tcp_stream_id=1, protocol="smtp",
        client_ip="10.0.0.5", client_port=40001, server_ip="10.0.0.80", server_port=25,
        first_frame=1, last_frame=8, packet_count=8, tls_state=TlsState.NONE,
        tls_transition=transition,
        starttls_advertised=EvidenceField.observed(True, "advertised", frames=[4]))
    base.update(kw)
    return SessionEvidence(**base)


def test_plaintext_rule_fires_only_on_an_observed_absence_of_tls():
    observed = _tls_less(EvidenceField.observed(False, "no TLS records in this stream"))
    assert [f.status for f in PlaintextSessionRule().evaluate(observed)] == [
        FindingStatus.OBSERVED_ISSUE]
    for state in (EvidenceField.incomplete("cut off"), EvidenceField.unknown("nothing read")):
        assert PlaintextSessionRule().evaluate(_tls_less(state)) == []


def test_starttls_advertisement_rule_keeps_its_abstention_for_incomplete():
    """INCOMPLETE must not make SEC-STLS-002 fall through to 'no finding'."""
    for field, text in (
            (EvidenceField.unknown("none"), "No capability response was captured"),
            (EvidenceField.incomplete("cut"), "The capture ends before the capability response")):
        out = StartTlsAdvertisementRule().evaluate(_tls_less(
            EvidenceField.observed(False, "x"), starttls_advertised=field))
        assert len(out) == 1, field
        assert out[0].status is FindingStatus.INSUFFICIENT_EVIDENCE
        assert out[0].conclusion.startswith(text)


def test_checklist_does_not_report_a_failure_that_its_delegate_would_not():
    """SEC-CFG-001 delegates 'transport protection' to SEC-PLAIN-002, so it may only fail
    that item when SEC-PLAIN-002 can actually report it."""
    rule = InsecureConfigurationRule()
    observed = rule.evaluate(_tls_less(EvidenceField.observed(False, "no TLS records")))
    assert "1 item(s) failed" in observed[0].conclusion
    cut = rule.evaluate(_tls_less(EvidenceField.incomplete("cut off")))
    assert "failed" not in cut[0].conclusion


def test_upgrade_rule_still_abstains_when_the_server_answer_is_incomplete():
    from nyaysaakshya.analysis.rules.starttls_rules import StartTlsUpgradeRule
    s = _tls_less(EvidenceField.incomplete("cut off"),
                  starttls_requested=EvidenceField.observed(True, "client asked"),
                  starttls_accepted=EvidenceField.incomplete("no reply captured"))
    out = StartTlsUpgradeRule().evaluate(s)
    assert [f.status for f in out] == [FindingStatus.INSUFFICIENT_EVIDENCE]


# ============================================================ D1/D3: evidence states (capture)
@needs_tshark
@needs_corpus
def test_case_a_complete_cleartext_session_is_observed_and_still_flagged():
    r = _pipeline(f"{OQ33R}/postfix_smtp_plaintext_session.pcap")
    s = max(r.sessions, key=lambda x: x.packet_count)
    assert s.completeness is Completeness.COMPLETE
    assert (s.tls_transition.state, s.tls_transition.value) == (EvidenceState.OBSERVED, False)
    assert len(_plain002(r, s.tcp_stream_id)) == 1


@needs_tshark
@needs_corpus
def test_case_b_starttls_requested_but_capture_ends_is_incomplete_not_plaintext():
    r = _pipeline(f"{OQ46}/D_cut_during_starttls.pcap")
    s = _stream(r, 0)
    assert s.starttls_requested.value is True
    assert s.tls_transition.state is EvidenceState.INCOMPLETE
    assert s.starttls_accepted.state is EvidenceState.INCOMPLETE
    assert _plain002(r, 0) == []
    # the abstention that describes the same situation is still present
    assert any(f.rule_id == "SEC-STLS-001" and f.status is FindingStatus.INSUFFICIENT_EVIDENCE
               for f in r.findings)
    assert r.assessment.band is PostureBand.INSUFFICIENT_EVIDENCE


@needs_tshark
@needs_corpus
def test_case_b_server_accepted_starttls_then_stream_stops_is_incomplete():
    r = _pipeline(f"{GEN_C}/C19_truncated.pcap")
    s = _stream(r, 0)
    assert s.starttls_accepted.value is True and s.tls_state is TlsState.NONE
    assert s.tls_transition.state is EvidenceState.INCOMPLETE
    assert _plain002(r, 0) == []


@needs_tshark
@needs_corpus
def test_truncated_capture_abstains_rather_than_certifying():
    """Not STRONG, and not a plaintext verdict either: the honest answer is a withheld band."""
    r = _pipeline(f"{GEN_C}/C19_truncated.pcap")
    assert r.assessment.band is PostureBand.INSUFFICIENT_EVIDENCE
    assert r.assessment.abstentions
    assert not [g for g in r.assessment.issue_groups if g.penalising]


@needs_tshark
@needs_corpus
def test_case_c_clienthello_without_completion_keeps_its_ambiguous_state():
    r = _pipeline(f"{OQ46}/E_cut_during_handshake.pcap")
    assert _stream(r, 0).tls_transition.state is EvidenceState.AMBIGUOUS
    assert _plain002(r, 0) == []


@needs_tshark
@needs_corpus
@pytest.mark.parametrize("path,stream", [
    (f"{OQ33R}/postfix_smtp_starttls_upgrade.pcap", 0),
    (f"{OQ33R}/dovecot_imap_starttls_upgrade.pcap", 0),
])
def test_case_d_probe_fragment_is_unknown_and_flags_nothing(path, stream):
    r = _pipeline(path)
    s = _stream(r, stream)
    assert s.packet_count <= 3
    assert s.tls_transition.state is EvidenceState.UNKNOWN
    assert _plain002(r, stream) == []


@needs_tshark
@needs_corpus
def test_case_e_closed_session_with_observed_cleartext_dialogue_is_observed():
    """Capture began mid-session (no SYN) but the dialogue and the close were both seen."""
    r = _pipeline(f"{OQ46}/F_missing_setup.pcap")
    s = _stream(r, 0)
    assert s.completeness is Completeness.INCOMPLETE
    assert (s.tls_transition.state, s.tls_transition.value) == (EvidenceState.OBSERVED, False)
    assert len(_plain002(r, 0)) == 1


@needs_tshark
@needs_corpus
def test_unanswered_capability_request_is_incomplete_and_still_abstains():
    r = _pipeline(f"{OQ46}/G_incomplete_exchange.pcap")
    s = _stream(r, 0)
    assert s.starttls_advertised.state is EvidenceState.INCOMPLETE
    assert any(f.rule_id == "SEC-STLS-002" and f.status is FindingStatus.INSUFFICIENT_EVIDENCE
               for f in r.findings)


@needs_tshark
@needs_corpus
def test_all_six_evidence_states_are_produced_by_real_captures():
    """The reproducible fixture set behind the claim 'six evidence states are demonstrated'."""
    fixtures = [
        f"{DEMO}/scene_b_certificate_honesty.pcap",           # OBSERVED, INFERRED, NOT_OBSERVABLE
        f"{OQ33R}/postfix_smtp_no_starttls_offered.pcap",      # AMBIGUOUS
        f"{OQ33R}/dovecot_imap_plaintext_login.pcap",          # UNKNOWN
        f"{OQ46}/D_cut_during_starttls.pcap",                  # INCOMPLETE
    ]
    seen = set()
    for path in fixtures:
        for s in _pipeline(path).sessions:
            for name in ("starttls_advertised", "starttls_accepted", "tls_transition",
                         "tls_negotiated_version", "tls_forward_secrecy",
                         "tls_certificate_chain"):
                seen.add(getattr(s, name).state)
    assert seen == set(EvidenceState)


# ============================================================ D1: true positives preserved
@needs_tshark
@needs_corpus
def test_real_cleartext_findings_are_unchanged():
    deep = _pipeline(f"{DEMO}/deepdive_cross_session_control_endpoint.pcap").assessment
    # Band and score are unchanged. The assessment ID is NOT asserted: it hashes the issue-group
    # summary, and informational groups are now a separate kind from positive evidence, so the
    # ID of almost every capture changed in Phase B.2 (documented in VALIDATION.md).
    assert (deep.band, round(deep.score.value, 2)) == (PostureBand.CRITICAL, 22.15)
    decline = _pipeline(f"{OQ33R}/postfix_smtp_client_declines.pcap").assessment
    assert (decline.band, decline.score.value) == (PostureBand.ADEQUATE, 88.0)
    login = _pipeline(f"{OQ33R}/dovecot_imap_plaintext_login.pcap").assessment
    assert (login.band, login.score.value) == (PostureBand.WEAK, 60.0)


@needs_tshark
@needs_corpus
def test_clean_complete_tls_is_still_clean():
    for name in ("scene_b_certificate_honesty.pcap", "backup_healthy_chain.pcap"):
        a = _pipeline(f"{DEMO}/{name}").assessment
        assert (a.band, a.score.value) == (PostureBand.STRONG, 100.0), name


@needs_tshark
@needs_corpus
def test_corrected_assessments_are_deterministic():
    for path in (f"{OQ33R}/postfix_smtp_starttls_upgrade.pcap",
                 f"{OQ46}/D_cut_during_starttls.pcap"):
        a, b = (_pipeline(path).assessment.to_dict() for _ in range(2))
        for d in (a, b):
            d.pop("generated_at"), d.pop("run_id")
        assert a == b


# ============================================================ D2: unsupported traffic (capture)
@needs_tshark
@needs_corpus
@pytest.mark.parametrize("name", ["tls12_chain_rsa2048.pcap", "tls12_selfsigned_rsa2048.pcap",
                                  "tls12_weak_sha1_rsa1024.pcap"])
def test_raw_tls_outside_the_mail_scope_is_not_graded_or_claimed_assessed(name):
    """Raw TLS 1.2 on a non-mail port, including one with an RSA-1024/SHA-1 certificate.
    Its certificate posture was not assessed, so it must not be reported as STRONG."""
    r = _pipeline(f"{P11}/{name}")
    a = r.assessment
    assert a.band is PostureBand.INSUFFICIENT_EVIDENCE
    assert a.coverage.sessions_assessed == 0
    assert a.coverage.sessions_unsupported == a.coverage.sessions_total == 1
    assert r.findings == []        # nothing was concluded, so nothing is claimed


def _scapy_capture(directory, name, port, client, server, proto="tcp"):
    scapy = pytest.importorskip("scapy.all")
    Ether, IP, TCP, UDP, Raw, wrpcap = (scapy.Ether, scapy.IP, scapy.TCP, scapy.UDP,
                                        scapy.Raw, scapy.wrpcap)
    eth = Ether(src="02:00:00:00:09:01", dst="02:00:00:00:09:02")
    pkts, t = [], 0.0
    if proto == "udp":
        pkts.append(eth / IP(src="10.9.0.2", dst="10.9.0.3") / UDP(sport=5353, dport=53) / Raw(b"\x00" * 20))
    else:
        seq_c, seq_s = 1000, 5000

        def add(src, dst, sp, dp, flags, seq, ack, payload=b""):
            nonlocal t
            p = eth / IP(src=src, dst=dst) / TCP(sport=sp, dport=dp, flags=flags, seq=seq, ack=ack)
            if payload:
                p = p / Raw(payload)
            p.time = 1_700_000_000 + t
            t += 0.01
            pkts.append(p)
        c, s = "10.9.0.2", "10.9.0.3"
        add(c, s, 40000, port, "S", seq_c, 0)
        add(s, c, port, 40000, "SA", seq_s, seq_c + 1)
        add(c, s, 40000, port, "A", seq_c + 1, seq_s + 1)
        seq_c += 1
        seq_s += 1
        for srv, cli in zip(server, client):
            add(s, c, port, 40000, "PA", seq_s, seq_c, srv)
            seq_s += len(srv)
            add(c, s, 40000, port, "PA", seq_c, seq_s, cli)
            seq_c += len(cli)
        add(c, s, 40000, port, "FA", seq_c, seq_s)
        add(s, c, port, 40000, "FA", seq_s, seq_c + 1)
    path = os.path.join(directory, name)
    wrpcap(path, pkts)
    return path


@needs_tshark
@pytest.mark.parametrize("name,port,client,server,proto", [
    ("http", 80, [b"POST /login HTTP/1.1\r\n\r\nuser=a&pass=b"], [b"HTTP/1.1 200 OK\r\n\r\n"], "tcp"),
    ("ftp", 21, [b"USER alice\r\n", b"PASS secret\r\n"], [b"220 ftp\r\n", b"331 pw\r\n"], "tcp"),
    ("dns", 53, [], [], "udp"),
    ("smtp_2626", 2626, [b"EHLO c\r\n", b"AUTH PLAIN AGFsaWNlAHNlY3JldA==\r\n"],
     [b"220 mail ESMTP\r\n", b"250 AUTH PLAIN\r\n"], "tcp"),
])
def test_non_mail_traffic_never_receives_a_reassuring_posture(name, port, client, server, proto):
    with tempfile.TemporaryDirectory() as d:
        path = _scapy_capture(d, name + ".pcap", port, "c", "s", proto) if proto == "udp" else \
            _scapy_capture(d, name + ".pcap", port, client, server)
        a = _pipeline(path).assessment
    assert a.band is PostureBand.INSUFFICIENT_EVIDENCE
    assert a.coverage.sessions_assessed == 0 and a.coverage.sessions_unsupported >= 1


@needs_tshark
@needs_corpus
def test_the_same_smtp_dialogue_on_a_supported_port_is_still_assessed():
    """Scope is explicit, not silent: port 25 with cleartext AUTH is a genuine finding."""
    with tempfile.TemporaryDirectory() as d:
        path = _scapy_capture(d, "smtp25.pcap", 25, [b"EHLO c\r\n", b"AUTH PLAIN AGFsaWNlAHNlY3JldA==\r\n"],
                              [b"220 mail ESMTP\r\n", b"250 AUTH PLAIN\r\n"])
        a = _pipeline(path).assessment
    assert a.band is not PostureBand.INSUFFICIENT_EVIDENCE
    assert any(g.penalising for g in a.issue_groups)


@needs_tshark
@needs_corpus
def test_background_traffic_does_not_withhold_a_genuinely_assessed_capture():
    scapy = pytest.importorskip("scapy.all")
    base = list(scapy.rdpcap(f"{DEMO}/deepdive_cross_session_control_endpoint.pcap"))
    with tempfile.TemporaryDirectory() as d:
        extra = []
        for i in range(13):                    # more unsupported streams than supported ones
            p = _scapy_capture(d, f"n{i}.pcap", 80, [b"GET / HTTP/1.1\r\n\r\n"], [b"HTTP/1.1 200 OK\r\n\r\n"])
            for pkt in scapy.rdpcap(p):
                ip, tcp = pkt[scapy.IP], pkt[scapy.TCP]
                ip.src = ip.src.replace("10.9.0.", f"10.9.{i + 1}.")     # both directions, so every
                ip.dst = ip.dst.replace("10.9.0.", f"10.9.{i + 1}.")     # stream stays one stream
                if tcp.sport == 40000:
                    tcp.sport = 40000 + i
                if tcp.dport == 40000:
                    tcp.dport = 40000 + i
                del ip.chksum, tcp.chksum
                extra.append(pkt)
        merged = os.path.join(d, "mixed.pcap")
        scapy.wrpcap(merged, base + extra)
        a = _pipeline(merged).assessment
    assert a.coverage.sessions_supported == 12
    assert a.coverage.sessions_unsupported >= 13
    assert a.coverage.assessed_fraction == 1.0
    assert a.band is PostureBand.CRITICAL and round(a.score.value, 2) == 22.15


# ============================================================ D2: visible explanation
@needs_tshark
@needs_corpus
def test_withheld_unsupported_capture_explains_itself_on_every_surface():
    from nyaysaakshya.dashboard import project
    from nyaysaakshya.reporting.service import render_bytes
    a = _pipeline(f"{P11}/tls12_weak_sha1_rsa1024.pcap").assessment.to_dict()

    view = project(a)
    assert view.posture.withheld
    assert "no SMTP, IMAP or POP3 dialogue was identified" in view.posture.withheld_note
    assert "not a pass" in view.posture.withheld_note
    assert view.coverage.sessions_unsupported == 1
    assert view.coverage.summary_text.startswith("No supported sessions to assess")
    assert any("no supported evidence to assess" in n for n in view.notices)

    html = render_bytes(a, "html", "en")[0].decode()
    text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))
    assert "No SMTP, IMAP or POP3 dialogue was identified in this capture" in text
    assert "withheld: no supported session was assessed" in text
    assert "No supported sessions to assess" in text
    assert "[]" not in text                       # empty rule-id list is a placeholder, not "[]"
    assert render_bytes(a, "pdf", "en")[0][:4] == b"%PDF"
    assert render_bytes(a, "html", "mr")[0]       # Marathi draft renders, catalogue complete


@needs_tshark
@needs_corpus
def test_a_normal_assessed_capture_shows_no_unsupported_wording():
    from nyaysaakshya.dashboard import project
    a = _pipeline(f"{DEMO}/scene_b_certificate_honesty.pcap").assessment.to_dict()
    view = project(a)
    assert not view.posture.withheld and view.coverage.sessions_unsupported == 0
    assert not any("SMTP, IMAP or POP3 dialogue" in n for n in view.notices)
    assert view.coverage.summary_text == "100.0% (1 of 1 sessions assessed)"


@needs_tshark
@needs_corpus
@pytest.mark.parametrize("path", [f"{GEN_C}/C19_truncated.pcap",
                                  f"{P11}/tls12_weak_sha1_rsa1024.pcap",
                                  f"{OQ46}/D_cut_during_starttls.pcap"])
def test_a_withheld_band_is_never_printed_beside_a_numeric_score(path):
    """The engine keeps its arithmetic value for a withheld band (100 for C19, 0 for a capture
    with nothing assessed), but no human-facing surface may show it as a grade."""
    from nyaysaakshya.dashboard import project
    from nyaysaakshya.reporting.service import render_bytes
    a = _pipeline(path).assessment.to_dict()
    assert a["overall_posture"] == "INSUFFICIENT_EVIDENCE"
    assert project(a).posture.score_text == "Not scored"
    text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", render_bytes(a, "html", "en")[0].decode()))
    assert "Posture score Not scored" in text
    assert not re.search(r"Posture score \d+(\.\d+)? / 100", text)


@needs_tshark
@needs_corpus
def test_a_graded_band_still_prints_its_score():
    from nyaysaakshya.dashboard import project
    a = _pipeline(f"{DEMO}/deepdive_cross_session_control_endpoint.pcap").assessment.to_dict()
    assert project(a).posture.score_text == "22.15 / 100"


# ============================================================ rule x state interaction matrix
_NON_OBSERVED = {
    "UNKNOWN": lambda: EvidenceField.unknown("b"),
    "AMBIGUOUS": lambda: EvidenceField.ambiguous(None, "b"),
    "INCOMPLETE": lambda: EvidenceField.incomplete("b"),
    "NOT_OBSERVABLE": lambda: EvidenceField.not_observable("b"),
}


@pytest.mark.parametrize("state", sorted(_NON_OBSERVED))
def test_plaintext_rule_never_fires_on_any_non_observed_transition(state):
    assert PlaintextSessionRule().evaluate(_tls_less(_NON_OBSERVED[state]())) == []


@pytest.mark.parametrize("state,expected", [
    ("UNKNOWN", FindingStatus.INSUFFICIENT_EVIDENCE),
    ("INCOMPLETE", FindingStatus.INSUFFICIENT_EVIDENCE),
    ("AMBIGUOUS", FindingStatus.AMBIGUOUS),
])
def test_advertisement_rule_gives_each_unresolved_state_an_abstaining_finding(state, expected):
    """INCOMPLETE is not UNKNOWN (its conclusion differs) but must be just as visible."""
    out = StartTlsAdvertisementRule().evaluate(_tls_less(
        EvidenceField.observed(False, "x"), starttls_advertised=_NON_OBSERVED[state]()))
    assert [f.status for f in out] == [expected]


@pytest.mark.parametrize("state", ["UNKNOWN", "INCOMPLETE"])
def test_upgrade_rule_abstains_for_an_unanswered_request_in_either_state(state):
    from nyaysaakshya.analysis.rules.starttls_rules import StartTlsUpgradeRule
    s = _tls_less(EvidenceField.observed(False, "x"),
                  starttls_requested=EvidenceField.observed(True, "asked"),
                  starttls_accepted=_NON_OBSERVED[state]())
    assert [f.status for f in StartTlsUpgradeRule().evaluate(s)] == [
        FindingStatus.INSUFFICIENT_EVIDENCE]


def test_no_rule_turns_an_incomplete_field_into_an_issue():
    """Whatever field is INCOMPLETE, no single-session rule may assert an OBSERVED_ISSUE
    because of it."""
    engine = SecurityAnalysisEngine()
    for field in ("starttls_advertised", "starttls_accepted", "tls_transition"):
        s = _tls_less(EvidenceField.incomplete("b"),
                      starttls_requested=EvidenceField.observed(True, "asked"))
        setattr(s, field, EvidenceField.incomplete("b"))
        issues = [f.rule_id for f in engine.analyse_session(s)
                  if f.status is FindingStatus.OBSERVED_ISSUE]
        assert issues == [], (field, issues)
