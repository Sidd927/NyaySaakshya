"""
Phase B.3 tests: the semantic contract from evidence to posture (defect D7 and what it implied).

The chain these tests hold together:

    session scope -> evidence state -> rule finding -> conclusion kind -> coverage ->
    posture -> API / report representation

THE CONTRACT (the vocabulary already existed; B.3 only enforces it):

  COMPLIANT / OBSERVED_ISSUE   a security property was actually established for the session
                               -> a CONCLUSION; the session counts as assessed.
  INFORMATIONAL                something was noticed or only part of a property was observed
                               (a partial checklist, a consistency note) -> NOT a conclusion.
  INSUFFICIENT_EVIDENCE        the evidence is missing or cut off          -> abstention.
  AMBIGUOUS                    the evidence supports more than one reading -> abstention.
  NOT_OBSERVABLE               structurally invisible to a passive capture -> abstention.

A session is "assessed" only through a conclusion from a single-session rule, an established
issue, or a behavioural deviation. Abstentions, notes, and cross-session "matches the
baseline" results never make a session assessed, and a withheld posture carries no score.

Unit tests use hand-built sessions. Capture-level tests use the committed research corpus
and skip cleanly when tshark or the corpus is absent.
"""
import json
import os
import re

import pytest

from nyaysaakshya.analysis import FindingStatus, SecurityAnalysisEngine, Severity
from nyaysaakshya.analysis.rules.configuration_rules import CHECKLIST, InsecureConfigurationRule
from nyaysaakshya.evidence.states import EvidenceField, EvidenceState
from nyaysaakshya.posture import PostureBand, PostureEngine
from nyaysaakshya.posture import scoring
from nyaysaakshya.posture.model import FactKind, PostureScore
from nyaysaakshya.session.model import Completeness, SessionEvidence, TlsState, TransportRole

from test_evidence_integrity import (
    DEMO, GEN_C, OQ28, OQ33R, OQ46, P11, _pipeline, _scapy_capture, needs_corpus, needs_tshark)
from test_phase11_rules import cert
from test_posture_engine import session as posture_session
from test_posture_fusion import cross, finding

AT = "2026-10-08T00:00:00Z"
ENGINE = SecurityAnalysisEngine()
CLOSED = (TransportRole.SETUP_OBSERVED, TransportRole.TEARDOWN_OBSERVED)
CONCLUSIVE = (FindingStatus.OBSERVED_ISSUE, FindingStatus.COMPLIANT)


# ===================================================================== scenario builders
def _base(**kw):
    d = dict(capture_id="c" * 8, tcp_stream_id=1, protocol="smtp", client_ip="10.0.0.5",
             client_port=40001, server_ip="10.0.0.80", server_port=25, first_frame=1,
             last_frame=10, packet_count=10, start_epoch=1_700_000_000.0)
    d.update(kw)
    return SessionEvidence(**d)


def _good_cert(index=0, **kw):
    return cert(index, public_key_algorithm="RSA", key_bits=2048,
                not_before_epoch=1_600_000_000, not_after_epoch=1_800_000_000,
                not_before_text="a", not_after_text="b",
                subject_key_id="aa", authority_key_id="bb", **kw)


def _scenarios():
    E = EvidenceField
    s = {}
    s["plain_complete"] = _base(
        tls_state=TlsState.NONE, completeness=Completeness.COMPLETE, transport_flags=CLOSED,
        starttls_advertised=E.observed(True, "adv", frames=[4]),
        starttls_requested=E.observed(False, "none"),
        tls_transition=E.observed(False, "no TLS records in this stream"),
        auth_activity=E.observed(True, "AUTH", frames=[7]))
    s["plain_fragment"] = _base(
        tls_state=TlsState.NONE, completeness=Completeness.TRUNCATED, packet_count=2,
        tls_transition=E.unknown("no client dialogue"))
    s["starttls_cut"] = _base(
        tls_state=TlsState.NONE, completeness=Completeness.TRUNCATED,
        starttls_advertised=E.observed(True, "adv"), starttls_requested=E.observed(True, "req"),
        starttls_accepted=E.incomplete("no reply"), tls_transition=E.incomplete("cut"))
    s["clienthello_only"] = _base(
        tls_state=TlsState.CLIENT_HELLO_OBSERVED, completeness=Completeness.TRUNCATED,
        starttls_advertised=E.observed(True, "adv"), starttls_requested=E.observed(True, "req"),
        starttls_accepted=E.incomplete("no reply"),
        tls_transition=E.ambiguous(None, "hello without completion"))
    s["serverhello_cut_tls12"] = _base(
        tls_state=TlsState.SERVER_HELLO_OBSERVED, completeness=Completeness.TRUNCATED,
        tls_transition=E.ambiguous(None, "no data"),
        tls_negotiated_version=E.observed("TLS1.2", "SH"),
        tls_forward_secrecy=E.inferred(True, "ECDHE"), tls_key_exchange=E.observed("ECDHE", "suite"))
    s["established_tls13_no_cert"] = _base(
        tls_state=TlsState.ESTABLISHED, completeness=Completeness.COMPLETE, implicit_tls=True,
        tls_transition=E.observed(True, "data"), tls_negotiated_version=E.observed("TLS1.3", "SH"),
        tls_forward_secrecy=E.inferred(True, "RFC8446"), tls_key_exchange=E.inferred("ECDHE", "x"))
    s["established_tls12_full_chain"] = _base(
        tls_state=TlsState.ESTABLISHED, completeness=Completeness.COMPLETE, implicit_tls=True,
        tls_transition=E.observed(True, "data"), tls_negotiated_version=E.observed("TLS1.2", "SH"),
        tls_forward_secrecy=E.inferred(True, "ECDHE"), tls_key_exchange=E.observed("ECDHE", "s"),
        certificates=(_good_cert(0), _good_cert(1)),
        tls_certificate_chain=E.observed(2, "Certificate"),
        chain_signature_oids=("1.2.840.113549.1.1.11",), chain_links=(True,))
    s["established_tls12_chain_partly_unreadable"] = _base(
        tls_state=TlsState.ESTABLISHED, completeness=Completeness.COMPLETE, implicit_tls=True,
        tls_transition=E.observed(True, "data"), tls_negotiated_version=E.observed("TLS1.2", "SH"),
        tls_forward_secrecy=E.inferred(True, "ECDHE"), tls_key_exchange=E.observed("ECDHE", "s"),
        certificates=(_good_cert(0), cert(1)), tls_certificate_chain=E.observed(2, "Certificate"),
        chain_signature_oids=("1.2.840.113549.1.1.11",), chain_links=(True,))
    s["established_tls10"] = _base(
        tls_state=TlsState.ESTABLISHED, completeness=Completeness.COMPLETE, implicit_tls=True,
        tls_transition=E.observed(True, "d"), tls_negotiated_version=E.observed("TLS1.0", "SH"),
        tls_forward_secrecy=E.inferred(False, "static"), tls_key_exchange=E.observed("RSA", "s"))
    s["starttls_upgraded"] = _base(
        tls_state=TlsState.ESTABLISHED, completeness=Completeness.COMPLETE,
        starttls_advertised=E.observed(True, "adv"), starttls_requested=E.observed(True, "req"),
        starttls_accepted=E.observed(True, "220"), tls_transition=E.observed(True, "d"),
        tls_negotiated_version=E.observed("TLS1.3", "SH"),
        tls_forward_secrecy=E.inferred(True, "x"), tls_key_exchange=E.inferred("ECDHE", "x"))
    s["starttls_refused"] = _base(
        tls_state=TlsState.NONE, completeness=Completeness.COMPLETE, transport_flags=CLOSED,
        starttls_advertised=E.observed(True, "adv"), starttls_requested=E.observed(True, "req"),
        starttls_accepted=E.observed(False, "454"), tls_transition=E.observed(False, "no TLS"))
    s["unsupported"] = _base(protocol=None, tls_state=TlsState.NONE)
    return s


SCENARIOS = _scenarios()

#: Hand-reviewed expectation, per scenario, of EVERY rule's status. Written from the contract
#: above, not copied from output: each unresolved scenario may contain no OBSERVED_ISSUE and no
#: COMPLIANT except where the named property is genuinely established by the evidence given.
I, X, NO, A, ISS, OK = ("INSUFFICIENT_EVIDENCE", "INFORMATIONAL", "NOT_OBSERVABLE", "AMBIGUOUS",
                        "OBSERVED_ISSUE", "COMPLIANT")
EXPECTED = {
    # complete cleartext: both issues, plus the notes. The checklist is a note, never a pass.
    "plain_complete": {"SEC-STLS-002": X, "SEC-PLAIN-001": ISS, "SEC-PLAIN-002": ISS, "SEC-CFG-001": X},
    # a two-frame fragment: nothing is asserted; the checklist could evaluate nothing
    "plain_fragment": {"SEC-STLS-002": I, "SEC-CFG-001": NO},
    # STARTTLS requested, capture ends: abstains everywhere, never "no TLS"
    "starttls_cut": {"SEC-STLS-001": I, "SEC-CFG-001": NO},
    # D7: a ClientHello only. No conclusion of any kind.
    "clienthello_only": {"SEC-TLS-001": I, "SEC-TLS-002": I, "SEC-TLS-003": NO, "SEC-STLS-001": I,
                         "SEC-KEX-001": I, "SEC-FS-001": I, "SEC-CERT-001": NO, "SEC-CFG-001": NO},
    # cut after the ServerHello: the NEGOTIATED PARAMETERS are established (version, suite,
    # forward secrecy) and may be concluded; completion is not, and abstains.
    "serverhello_cut_tls12": {"SEC-TLS-001": OK, "SEC-TLS-002": I, "SEC-TLS-003": NO,
                              "SEC-STLS-002": I, "SEC-KEX-001": X, "SEC-FS-001": OK,
                              "SEC-CERT-001": NO, "SEC-CFG-001": X},
    # TLS 1.3, certificate encrypted: a partial checklist (3 of 7) is a note, not a pass
    "established_tls13_no_cert": {"SEC-TLS-001": OK, "SEC-TLS-002": OK, "SEC-TLS-003": NO,
                                  "SEC-STLS-003": X, "SEC-KEX-001": X, "SEC-FS-001": OK,
                                  "SEC-CERT-001": NO, "SEC-CFG-001": X},
    # everything observed and passing: the only case where the checklist may conclude
    "established_tls12_full_chain": {"SEC-TLS-001": OK, "SEC-TLS-002": OK, "SEC-TLS-003": NO,
                                     "SEC-STLS-003": X, "SEC-KEX-001": X, "SEC-FS-001": OK,
                                     "SEC-CERT-001": X, "SEC-CERT-002": OK, "SEC-CERT-003": OK,
                                     "SEC-CERT-004": OK, "SEC-CERT-005": X, "SEC-CFG-001": OK},
    # one certificate of two unreadable: validity and key strength of the CHAIN are not
    # established, so those two abstain, and the checklist items that delegate to them follow
    "established_tls12_chain_partly_unreadable": {
        "SEC-TLS-001": OK, "SEC-TLS-002": OK, "SEC-TLS-003": NO, "SEC-STLS-003": X,
        "SEC-KEX-001": X, "SEC-FS-001": OK, "SEC-CERT-001": X, "SEC-CERT-002": I,
        "SEC-CERT-003": I, "SEC-CERT-004": OK, "SEC-CERT-005": X, "SEC-CFG-001": X},
    "established_tls10": {"SEC-TLS-001": ISS, "SEC-TLS-002": OK, "SEC-TLS-003": NO,
                          "SEC-STLS-003": X, "SEC-KEX-001": X, "SEC-FS-001": ISS,
                          "SEC-CERT-001": NO, "SEC-CFG-001": X},
    "starttls_upgraded": {"SEC-TLS-001": OK, "SEC-TLS-002": OK, "SEC-TLS-003": NO,
                          "SEC-STLS-001": OK, "SEC-KEX-001": X, "SEC-FS-001": OK,
                          "SEC-CERT-001": NO, "SEC-CFG-001": X},
    "starttls_refused": {"SEC-STLS-001": ISS, "SEC-PLAIN-002": ISS, "SEC-CFG-001": X},
    # outside the supported scope: no single-session rule runs at all
    "unsupported": {},
}


@pytest.mark.parametrize("name", sorted(EXPECTED))
def test_rule_status_matrix(name):
    got = {f.rule_id: f.status.value for f in ENGINE.analyse_session(SCENARIOS[name])}
    assert got == EXPECTED[name], name


def test_every_scenario_is_in_the_matrix():
    assert set(SCENARIOS) == set(EXPECTED)


@pytest.mark.parametrize("name", ["plain_fragment", "starttls_cut", "clienthello_only", "unsupported"])
def test_an_unresolved_session_yields_no_conclusion_of_any_kind(name):
    """The D7 class: not one OBSERVED_ISSUE and not one COMPLIANT from a session whose
    security properties the capture does not establish."""
    findings = ENGINE.analyse_session(SCENARIOS[name])
    assert [f.rule_id for f in findings if f.status in CONCLUSIVE] == []


def test_non_issue_findings_never_carry_severity():
    for name, sess in SCENARIOS.items():
        for f in ENGINE.analyse_session(sess):
            if f.status is not FindingStatus.OBSERVED_ISSUE:
                assert f.severity is Severity.INFO, (name, f.rule_id)


# ----------------------------------------------------------- SEC-CFG-001 contract
def _checklist_session(*, unevaluated=(), failing=()):
    """A TLS 1.2 session in which chosen checklist items are made unevaluable or failing."""
    E = EvidenceField
    kw = dict(
        tls_state=TlsState.ESTABLISHED, completeness=Completeness.COMPLETE, implicit_tls=True,
        tls_transition=E.observed(True, "d"), tls_negotiated_version=E.observed("TLS1.2", "SH"),
        tls_forward_secrecy=E.inferred(True, "ECDHE"), tls_key_exchange=E.observed("ECDHE", "s"),
        certificates=(_good_cert(0),), tls_certificate_chain=E.observed(1, "Certificate"),
        chain_signature_oids=("1.2.840.113549.1.1.11",))
    if "deprecated TLS version" in unevaluated:
        kw["tls_negotiated_version"] = E.unknown("none")
    if "forward secrecy" in unevaluated:
        kw["tls_forward_secrecy"] = E.unknown("none")
    if "RSA key length" in unevaluated:
        kw["certificates"] = (cert(0, not_before_epoch=1_600_000_000, not_after_epoch=1_800_000_000,
                                   subject_key_id="aa", authority_key_id="bb"),)
    if "certificate signature hash" in unevaluated:
        kw["chain_signature_oids"] = ()
    if "certificate validity window" in unevaluated:
        kw["start_epoch"] = None
    if "self-signed leaf certificate" in unevaluated:
        kw["certificates"] = (cert(0, public_key_algorithm="RSA", key_bits=2048,
                                   not_before_epoch=1_600_000_000, not_after_epoch=1_800_000_000),)
    if "transport protection" in unevaluated:
        kw["tls_state"] = TlsState.SERVER_HELLO_OBSERVED
    if "RSA key length" in failing:
        kw["certificates"] = (_good_cert(0, ),)
        kw["certificates"] = (cert(0, public_key_algorithm="RSA", key_bits=1024,
                                   not_before_epoch=1_600_000_000, not_after_epoch=1_800_000_000,
                                   subject_key_id="aa", authority_key_id="bb"),)
    return _base(**kw)


def test_checklist_is_compliant_only_when_every_item_was_evaluated_and_passed():
    out = InsecureConfigurationRule().evaluate(_checklist_session())
    assert [f.status for f in out] == [FindingStatus.COMPLIANT]
    assert out[0].conclusion == "Configuration checklist: 7 of 7 items passed."


@pytest.mark.parametrize("item", [name for name, _ in CHECKLIST])
def test_one_unevaluable_item_makes_the_checklist_a_note_not_a_pass(item):
    """The D7 rule, generalised: whichever single item cannot be evaluated, 'N of 7 passed'
    is INFORMATIONAL and never COMPLIANT."""
    out = InsecureConfigurationRule().evaluate(_checklist_session(unevaluated=(item,)))
    assert [f.status for f in out] == [FindingStatus.INFORMATIONAL], item
    assert "no overall compliance is claimed" in out[0].explanation
    assert any(item in lim for lim in out[0].limitations), "the unevaluated item must be named"


def test_checklist_with_nothing_evaluable_abstains():
    out = InsecureConfigurationRule().evaluate(_base(tls_state=TlsState.CLIENT_HELLO_OBSERVED))
    assert [f.status for f in out] == [FindingStatus.NOT_OBSERVABLE]


def test_transport_protection_item_needs_an_established_session_not_a_hello():
    """'TLS records were observed' is not 'the session was protected'."""
    for state in (TlsState.CLIENT_HELLO_OBSERVED, TlsState.SERVER_HELLO_OBSERVED):
        out = InsecureConfigurationRule().evaluate(_base(tls_state=state))
        assert out[0].status is not FindingStatus.COMPLIANT
        assert "transport protection" in " ".join(out[0].limitations)


# ----------------------------------------------------------- partial certificate chains
def test_partially_readable_chain_is_not_compliant_for_validity_or_key_strength():
    got = {f.rule_id: f.status for f in ENGINE.analyse_session(
        SCENARIOS["established_tls12_chain_partly_unreadable"])}
    assert got["SEC-CERT-002"] is FindingStatus.INSUFFICIENT_EVIDENCE
    assert got["SEC-CERT-003"] is FindingStatus.INSUFFICIENT_EVIDENCE


def test_an_established_defect_in_a_partial_chain_is_still_reported():
    """Partial readability must never hide what WAS read: a readable weak key is an issue."""
    sess = _base(
        tls_state=TlsState.ESTABLISHED, implicit_tls=True, completeness=Completeness.COMPLETE,
        tls_transition=EvidenceField.observed(True, "d"),
        certificates=(cert(0, public_key_algorithm="RSA", key_bits=1024), cert(1)),
        tls_certificate_chain=EvidenceField.observed(2, "Certificate"))
    from nyaysaakshya.analysis.rules.certificate_rules import CertificateKeyStrengthRule
    out = CertificateKeyStrengthRule().evaluate(sess)
    assert [f.status for f in out] == [FindingStatus.OBSERVED_ISSUE]


# ----------------------------------------------------------- rule x evidence-state sweeps
_NON_CONCLUSIVE = {
    "UNKNOWN": lambda: EvidenceField.unknown("b"),
    "AMBIGUOUS": lambda: EvidenceField.ambiguous(None, "b"),
    "INCOMPLETE": lambda: EvidenceField.incomplete("b"),
    "NOT_OBSERVABLE": lambda: EvidenceField.not_observable("b"),
}
#: (decisive field, session factory) for every rule whose conclusion hangs on one field.
_DECISIVE = {
    "tls_transition": lambda f: _base(tls_state=TlsState.NONE, tls_transition=f,
                                      completeness=Completeness.COMPLETE, transport_flags=CLOSED,
                                      starttls_advertised=EvidenceField.observed(True, "a")),
    "starttls_accepted": lambda f: _base(tls_state=TlsState.NONE, starttls_accepted=f,
                                         starttls_requested=EvidenceField.observed(True, "r"),
                                         tls_transition=EvidenceField.incomplete("c")),
    "starttls_advertised": lambda f: _base(tls_state=TlsState.NONE, starttls_advertised=f,
                                           tls_transition=EvidenceField.incomplete("c")),
    "tls_negotiated_version": lambda f: _base(tls_state=TlsState.SERVER_HELLO_OBSERVED,
                                              tls_negotiated_version=f),
    "tls_forward_secrecy": lambda f: _base(tls_state=TlsState.SERVER_HELLO_OBSERVED,
                                           tls_negotiated_version=EvidenceField.observed("TLS1.2", "s"),
                                           tls_forward_secrecy=f),
    "auth_activity": lambda f: _base(tls_state=TlsState.NONE, auth_activity=f,
                                     tls_transition=EvidenceField.observed(False, "n")),
}


@pytest.mark.parametrize("field", sorted(_DECISIVE))
@pytest.mark.parametrize("state", sorted(_NON_CONCLUSIVE))
def test_a_non_conclusive_decisive_field_never_produces_the_conclusion_that_hangs_on_it(field, state):
    """UNKNOWN, AMBIGUOUS, INCOMPLETE and NOT_OBSERVABLE are each non-conclusive for the rule
    that depends on the field. Absence of evidence never becomes evidence of absence."""
    sess = _DECISIVE[field](_NON_CONCLUSIVE[state]())
    depends = {
        "tls_transition": {"SEC-PLAIN-002"},
        "starttls_accepted": {"SEC-STLS-001"},
        "starttls_advertised": {"SEC-STLS-002"},
        "tls_negotiated_version": {"SEC-TLS-001"},
        "tls_forward_secrecy": {"SEC-FS-001"},
        "auth_activity": {"SEC-PLAIN-001"},
    }[field]
    got = {f.rule_id: f.status for f in ENGINE.analyse_session(sess) if f.rule_id in depends}
    for rule_id, status in got.items():
        assert status not in CONCLUSIVE, (field, state, rule_id, status)


@pytest.mark.parametrize("state", sorted(_NON_CONCLUSIVE))
def test_unresolved_key_exchange_and_forward_secrecy_never_become_a_weakness(state):
    E = EvidenceField
    sess = _base(tls_state=TlsState.SERVER_HELLO_OBSERVED,
                 tls_negotiated_version=E.observed("TLS1.2", "s"),
                 tls_key_exchange=_NON_CONCLUSIVE[state](), tls_forward_secrecy=_NON_CONCLUSIVE[state]())
    got = {f.rule_id: f.status for f in ENGINE.analyse_session(sess)}
    assert got["SEC-FS-001"] not in CONCLUSIVE
    assert got["SEC-KEX-001"] not in CONCLUSIVE
    cfg = InsecureConfigurationRule().evaluate(sess)[0]
    assert cfg.status is not FindingStatus.COMPLIANT and "failed" not in cfg.conclusion


@pytest.mark.parametrize("state", ["UNKNOWN", "INCOMPLETE", "NOT_OBSERVABLE"])
def test_a_version_with_no_value_is_insufficient_evidence_not_an_unknown_version_string(state):
    sess = _base(tls_state=TlsState.SERVER_HELLO_OBSERVED,
                 tls_negotiated_version=_NON_CONCLUSIVE[state]())
    out = [f for f in ENGINE.analyse_session(sess) if f.rule_id == "SEC-TLS-001"]
    assert [f.status for f in out] == [FindingStatus.INSUFFICIENT_EVIDENCE]
    assert "'None'" not in out[0].conclusion


# ===================================================================== coverage invariants
def _assess(sessions, findings=(), cross_findings=()):
    return PostureEngine().assess(sessions=sessions, findings=findings,
                                  cross_findings=cross_findings, capture_id="cap", generated_at=AT)


def _sess(n, protocol="smtp"):
    return posture_session(n, protocol)


@pytest.mark.parametrize("status,severity", [
    (FindingStatus.INFORMATIONAL, Severity.INFO),
    (FindingStatus.INSUFFICIENT_EVIDENCE, Severity.INFO),
    (FindingStatus.NOT_OBSERVABLE, Severity.INFO),
    (FindingStatus.AMBIGUOUS, Severity.INFO),
])
def test_only_conclusions_make_a_session_assessed(status, severity):
    a = _assess([_sess(1)], [finding("SEC-CFG-001", status=status, severity=severity)])
    assert a.coverage.sessions_assessed == 0
    assert a.band is PostureBand.INSUFFICIENT_EVIDENCE


@pytest.mark.parametrize("status,severity", [
    (FindingStatus.COMPLIANT, Severity.INFO), (FindingStatus.OBSERVED_ISSUE, Severity.MEDIUM)])
def test_a_single_session_conclusion_makes_a_session_assessed(status, severity):
    a = _assess([_sess(1)], [finding("SEC-TLS-001", status=status, severity=severity)])
    assert a.coverage.sessions_assessed == 1


def test_a_cross_session_positive_alone_does_not_make_a_session_assessed():
    """'Matches the baseline' says the session resembles others, not that it is secure; it is
    reachable on a stream cut off mid-handshake."""
    a = _assess([_sess(1)], cross_findings=[
        cross("CS-STARTTLS-001", status=FindingStatus.COMPLIANT, severity=Severity.INFO,
              deviation=__import__("nyaysaakshya.crosssession.model", fromlist=["Deviation"]).Deviation.NONE)])
    assert a.coverage.sessions_assessed == 0
    assert a.band is PostureBand.INSUFFICIENT_EVIDENCE


def test_a_behavioural_deviation_is_a_conclusion():
    a = _assess([_sess(1)], cross_findings=[cross("CS-STARTTLS-001")])
    assert a.coverage.sessions_assessed == 1


def test_cross_session_positive_beside_a_single_session_conclusion_changes_nothing():
    from nyaysaakshya.crosssession.model import Deviation
    only_single = _assess([_sess(1)], [finding("SEC-TLS-001", status=FindingStatus.COMPLIANT,
                                              severity=Severity.INFO)])
    both = _assess([_sess(1)], [finding("SEC-TLS-001", status=FindingStatus.COMPLIANT,
                                       severity=Severity.INFO)],
                   [cross("CS-STARTTLS-001", status=FindingStatus.COMPLIANT, severity=Severity.INFO,
                          deviation=Deviation.NONE)])
    assert (only_single.coverage.sessions_assessed, only_single.band) == (
        both.coverage.sessions_assessed, both.band)


def test_unsupported_traffic_cannot_contaminate_the_denominator_or_create_positive_evidence():
    supported = [_sess(i) for i in range(1, 4)]
    noise = [_sess(i, protocol=None) for i in range(4, 20)]
    base = _assess(supported, [finding(f"SEC-TLS-001", status=FindingStatus.COMPLIANT,
                                       severity=Severity.INFO, stream=f"cap:{i}") for i in range(1, 4)])
    mixed = _assess(supported + noise, [finding(f"SEC-TLS-001", status=FindingStatus.COMPLIANT,
                                                severity=Severity.INFO, stream=f"cap:{i}")
                                        for i in range(1, 4)])
    assert mixed.coverage.sessions_unsupported == len(noise)
    assert mixed.coverage.assessed_fraction == base.coverage.assessed_fraction == 1.0
    assert mixed.band is base.band
    assert [g.issue_class for g in mixed.issue_groups] == [g.issue_class for g in base.issue_groups]


def test_a_supported_session_beside_an_incomplete_one_is_graded_on_what_was_assessed():
    ok = finding("SEC-TLS-001", status=FindingStatus.COMPLIANT, severity=Severity.INFO, stream="cap:1")
    cut = finding("SEC-STLS-001", status=FindingStatus.INSUFFICIENT_EVIDENCE, severity=Severity.INFO,
                  stream="cap:2")
    a = _assess([_sess(1), _sess(2)], [ok, cut])
    assert a.coverage.sessions_assessed == 1 and a.coverage.sessions_abstained == 1
    assert a.coverage.assessed_fraction == 0.5          # at, not below, the floor: still graded
    a3 = _assess([_sess(1), _sess(2), _sess(3)], [ok, cut])
    assert a3.band is PostureBand.INSUFFICIENT_EVIDENCE   # one of three is below the floor


# ===================================================================== score contract
def test_a_graded_posture_serialises_a_score():
    d = _assess([_sess(1)], [finding("SEC-TLS-001", status=FindingStatus.COMPLIANT,
                                     severity=Severity.INFO)]).to_dict()["score"]
    assert d["scored"] is True and d["value"] == 100.0 and d["band"] == "STRONG"


@pytest.mark.parametrize("sessions,findings_", [
    ([], []),                                                                       # nothing at all
    ([_sess(1)], [finding("SEC-CFG-001", status=FindingStatus.INFORMATIONAL, severity=Severity.INFO)]),
])
def test_a_withheld_posture_serialises_no_score(sessions, findings_):
    d = _assess(sessions, findings_).to_dict()
    assert d["overall_posture"] == "INSUFFICIENT_EVIDENCE"
    assert d["score"]["scored"] is False
    assert d["score"]["value"] is None
    assert d["score"]["band"] == "INSUFFICIENT_EVIDENCE"


def test_a_floor_withheld_posture_with_established_issues_keeps_them_but_gives_no_score():
    """Below the coverage floor the issues that WERE found are still listed (components,
    total_penalty) but no number is published as a score."""
    issue = finding("SEC-PLAIN-001", stream="cap:1")
    a = _assess([_sess(i) for i in range(1, 6)], [issue])        # 1 of 5 assessed
    d = a.to_dict()["score"]
    assert d["scored"] is False and d["value"] is None
    assert d["total_penalty"] > 0 and d["components"]
    assert "computed" not in d["basis"]                          # no arithmetic score in the prose


def test_the_score_object_exposes_scored_for_internal_callers():
    score = scoring.compute_score([], None)
    assert isinstance(score, PostureScore) and score.scored is False


def test_dashboard_never_surfaces_the_arithmetic_value_of_a_withheld_posture():
    """A schema-1.0 document stored before B.3 still carries the number; it must not show."""
    from nyaysaakshya.dashboard import project
    a = _assess([], []).to_dict()
    a["score"]["value"] = 100.0                                   # as a legacy document had it
    a["score"].pop("scored", None)
    view = project(a)
    assert view.posture.withheld and view.posture.score_value is None
    assert view.posture.score_text == "Not scored"


def test_dashboard_protocol_rows_never_surface_a_withheld_protocol_score():
    from nyaysaakshya.dashboard import project
    a = _assess([_sess(1)], [finding("SEC-CFG-001", status=FindingStatus.INFORMATIONAL,
                                     severity=Severity.INFO)]).to_dict()
    a["protocol_posture"][0]["score"]["value"] = 100.0             # legacy form
    row = project(a).protocols[0]
    assert row.score_value is None


# ===================================================================== assessment identity
def _id(sessions, findings_, **kw):
    return _assess(sessions, findings_, **kw).assessment_id


_F = [finding("SEC-PLAIN-001", stream="cap:1")]


def test_assessment_id_is_deterministic_and_ignores_run_id_and_time():
    a = PostureEngine().assess(sessions=[_sess(1)], findings=_F, capture_id="cap",
                               run_id="run-one", generated_at="2026-01-01T00:00:00Z")
    b = PostureEngine().assess(sessions=[_sess(1)], findings=_F, capture_id="cap",
                               run_id="run-two", generated_at="2030-12-31T23:59:59Z")
    assert a.assessment_id == b.assessment_id


def test_assessment_id_differs_when_the_capture_differs():
    assert _assess([_sess(1)], _F).assessment_id != PostureEngine().assess(
        sessions=[_sess(1)], findings=_F, capture_id="other", generated_at=AT).assessment_id


def test_assessment_id_changes_when_the_outcome_changes_but_the_issue_groups_do_not(monkeypatch):
    """Two assessments of one capture with equal issue groups but a different band or
    coverage are not the same assessment. (Before schema 1.1 the id hashed only the groups.)"""
    sessions = [_sess(i) for i in range(1, 5)]
    findings_ = [finding("SEC-PLAIN-001", stream=f"cap:{i}") for i in range(1, 3)]   # 2 of 4 assessed
    graded = _assess(sessions, findings_)
    assert graded.band is not PostureBand.INSUFFICIENT_EVIDENCE
    monkeypatch.setattr(scoring, "MIN_ASSESSED_FRACTION", 0.9)
    withheld = _assess(sessions, findings_)
    assert withheld.band is PostureBand.INSUFFICIENT_EVIDENCE
    assert [g.recurrence for g in graded.issue_groups] == [g.recurrence for g in withheld.issue_groups]
    assert graded.assessment_id != withheld.assessment_id


def test_assessment_id_changes_with_the_analyser_version(monkeypatch):
    from nyaysaakshya.posture import engine as engine_module
    before = _id([_sess(1)], _F)
    monkeypatch.setattr(engine_module, "POSTURE_ENGINE_VERSION", "99.0.0")
    assert _id([_sess(1)], _F) != before


def test_assessment_id_changes_with_the_rule_set_version():
    old = finding("SEC-PLAIN-001", stream="cap:1")
    new = finding("SEC-PLAIN-001", stream="cap:1")
    object.__setattr__(new, "rules_version", "9.9")
    assert _id([_sess(1)], [old]) != _id([_sess(1)], [new])


@needs_tshark
@needs_corpus
def test_reanalysis_after_an_engine_upgrade_is_a_new_assessment_not_an_identity_conflict(tmp_path, monkeypatch):
    """The Phase B.3 reproducibility defect: with the old formula an upgrade that changed no
    issue group reproduced the OLD id for a NEW document and the store answered 409."""
    from fastapi.testclient import TestClient
    from nyaysaakshya.backend.api import create_app
    from nyaysaakshya.backend.service import AnalysisService
    from nyaysaakshya.posture import engine as engine_module
    client = TestClient(create_app(service=AnalysisService(str(tmp_path / "data"))))
    data = open(f"{DEMO}/scene_b_certificate_honesty.pcap", "rb").read()
    post = lambda: client.post("/api/v1/analyses?force=true",                  # noqa: E731
                               files={"file": ("x.pcap", data, "application/octet-stream")})
    first = post()
    assert first.status_code == 201
    monkeypatch.setattr(engine_module, "POSTURE_ENGINE_VERSION", "99.0.0")
    second = post()
    assert second.status_code == 201, second.text
    ids = [client.get(f"/api/v1/analyses/{r.json()['run_id']}/assessment").json()["assessment"]["assessment_id"]
           for r in (first, second)]
    assert ids[0] != ids[1]


def test_assessment_id_covers_whether_the_ml_lane_was_on_even_if_it_flags_nothing():
    """The ML-on document differs from the ML-off one (flag, model summary) whether or not any
    session is anomalous, so the two must not share an id."""
    from nyaysaakshya.posture.engine import PostureConfig
    off = PostureEngine(PostureConfig(ai_enabled=False)).assess(
        sessions=[_sess(1)], findings=_F, capture_id="cap", generated_at=AT)
    on = PostureEngine(PostureConfig(ai_enabled=True)).assess(
        sessions=[_sess(1)], findings=_F, capture_id="cap", generated_at=AT)
    assert not [g for g in on.issue_groups if g.fact_kind is FactKind.ANOMALY_SIGNAL]
    assert off.assessment_id != on.assessment_id


@needs_tshark
@needs_corpus
def test_analysing_with_the_ml_lane_on_after_off_is_not_an_identity_conflict(tmp_path):
    """The second Phase B.3 identity defect: for a capture in which the model flags no session
    (F_missing_setup is one) the AI-on assessment reproduced the AI-off id, and the store
    answered HTTP 409 ASSESSMENT_IDENTITY_CONFLICT."""
    from fastapi.testclient import TestClient
    from nyaysaakshya.backend.api import create_app
    from nyaysaakshya.backend.service import AnalysisService
    client = TestClient(create_app(service=AnalysisService(str(tmp_path / "data"))))
    data = open(f"{OQ46}/F_missing_setup.pcap", "rb").read()
    up = lambda q: client.post(f"/api/v1/analyses?{q}", files={"file": ("x.pcap", data, "application/octet-stream")})  # noqa: E731
    first, second = up("ai=false"), up("ai=true&force=true")
    assert (first.status_code, second.status_code) == (201, 201), second.text
    ids = [client.get(f"/api/v1/analyses/{r.json()['run_id']}/assessment").json()["assessment"]["assessment_id"]
           for r in (first, second)]
    assert ids[0] != ids[1]


@needs_tshark
@needs_corpus
def test_same_capture_same_software_gives_the_same_identity_and_content():
    def run():
        a = _pipeline(f"{DEMO}/deepdive_cross_session_control_endpoint.pcap").assessment.to_dict()
        for key in ("generated_at", "run_id"):
            a.pop(key, None)
        return a
    first, second = run(), run()
    assert first == second


# ===================================================================== capture-level (D7)
def _sole_conclusion_rules(result):
    """session id -> set of rules supplying its conclusions."""
    per = {}
    for f in list(result.findings) + list(result.cross_findings):
        if f.status in CONCLUSIVE:
            per.setdefault(f.tcp_stream_id, set()).add(f.rule_id)
    return per


@needs_tshark
@needs_corpus
def test_d7_a_capture_cut_inside_the_handshake_is_withheld_not_strong():
    r = _pipeline(f"{OQ46}/E_cut_during_handshake.pcap")
    a = r.assessment
    assert a.band is PostureBand.INSUFFICIENT_EVIDENCE
    assert a.coverage.sessions_assessed == 0
    assert a.to_dict()["score"] == {**a.to_dict()["score"], "scored": False, "value": None}
    assert [f for f in r.findings if f.status in CONCLUSIVE] == []
    cfg = [f for f in r.findings if f.rule_id == "SEC-CFG-001"]
    assert [f.status for f in cfg] == [FindingStatus.NOT_OBSERVABLE]


@needs_tshark
@needs_corpus
def test_cross_session_positives_exist_on_cut_off_sessions_but_do_not_assess_them():
    """C19 is 30 benign STARTTLS upgrades cut by the end of the capture. The cross-session lane
    still says 'matches the baseline' for 14 of them (the advertisement WAS observed), and that
    must not turn a stream whose TLS outcome is unknown into an assessed session."""
    r = _pipeline(f"{GEN_C}/C19_truncated.pcap")
    cs_positive = [f for f in r.cross_findings if f.status is FindingStatus.COMPLIANT]
    assert len(cs_positive) == 14
    assert r.assessment.coverage.sessions_assessed == 0
    assert r.assessment.band is PostureBand.INSUFFICIENT_EVIDENCE


@needs_tshark
@needs_corpus
@pytest.mark.parametrize("path,assessed,total", [
    (f"{OQ28}/E_incomplete.pcap", 1, 5),
    (f"{OQ46}/D_cut_during_starttls.pcap", 0, 1),
    (f"{OQ46}/G_incomplete_exchange.pcap", 0, 1),
    (f"{OQ46}/C_cut_mid_dialogue.pcap", 0, 1),
])
def test_cut_off_sessions_are_not_counted_as_assessed(path, assessed, total):
    r = _pipeline(path)
    assert (r.assessment.coverage.sessions_assessed, r.assessment.coverage.sessions_total) == (assessed, total)
    assert r.assessment.band is PostureBand.INSUFFICIENT_EVIDENCE


@needs_tshark
@needs_corpus
def test_failed_upgrade_sessions_are_not_assessed_by_a_checklist_note():
    """oq28 D: 5 sessions completed their upgrade; 2 did not (outcome unknown). Previously all 7
    were 'assessed', the 2 solely through SEC-CFG-001 and a consistency result."""
    r = _pipeline(f"{OQ28}/D_failed_upgrade.pcap")
    assert (r.assessment.coverage.sessions_assessed, r.assessment.coverage.sessions_total) == (5, 7)
    assert r.assessment.band is not PostureBand.INSUFFICIENT_EVIDENCE      # 5/7 is above the floor
    cfg = [f for f in r.findings if f.rule_id == "SEC-CFG-001"]
    assert FindingStatus.COMPLIANT not in {f.status for f in cfg}


@needs_tshark
@needs_corpus
@pytest.mark.parametrize("path", [
    f"{DEMO}/scene_b_certificate_honesty.pcap",
    f"{DEMO}/deepdive_cross_session_control_endpoint.pcap",
    f"{OQ33R}/postfix_smtp_plaintext_session.pcap",
    f"{OQ33R}/dovecot_imap_plaintext_login.pcap",
])
def test_genuinely_assessed_captures_are_unaffected_by_the_d7_semantics(path):
    a = _pipeline(path).assessment
    assert a.band is not PostureBand.INSUFFICIENT_EVIDENCE
    assert a.coverage.assessed_fraction == 1.0
    assert a.to_dict()["score"]["scored"] is True


@needs_tshark
@needs_corpus
def test_the_fixed_expected_scores_are_unchanged():
    """No threshold, weight or constant moved in B.3: the golden scores still hold."""
    expected = {f"{DEMO}/deepdive_cross_session_control_endpoint.pcap": ("CRITICAL", 22.15),
                f"{DEMO}/backup_weak_certificate.pcap": ("CRITICAL", 44.0),
                f"{DEMO}/scene_b_certificate_honesty.pcap": ("STRONG", 100.0),
                f"{DEMO}/deepdive_cross_session_no_control.pcap": ("CRITICAL", 34.15)}
    for path, (band, score) in expected.items():
        a = _pipeline(path).assessment
        assert (a.band.value, round(a.score.value, 2)) == (band, score), path


# ===================================================================== API / report agreement
@needs_tshark
@needs_corpus
@pytest.mark.parametrize("path", [f"{OQ46}/E_cut_during_handshake.pcap",
                                  f"{P11}/tls12_weak_sha1_rsa1024.pcap",
                                  f"{GEN_C}/C19_truncated.pcap"])
def test_every_surface_agrees_that_a_withheld_assessment_has_no_score(path, tmp_path):
    from fastapi.testclient import TestClient
    from nyaysaakshya.backend.api import create_app
    from nyaysaakshya.backend.service import AnalysisService
    client = TestClient(create_app(service=AnalysisService(str(tmp_path / "data"))))
    with open(path, "rb") as fh:
        created = client.post("/api/v1/analyses", files={"file": ("x.pcap", fh.read(), "application/octet-stream")})
    run_id = created.json()["run_id"]
    get = lambda suffix, **kw: client.get(f"/api/v1/analyses/{run_id}{suffix}", **kw)       # noqa: E731
    a = get("/assessment").json()["assessment"]
    assert a["overall_posture"] == "INSUFFICIENT_EVIDENCE"
    assert a["score"]["scored"] is False and a["score"]["value"] is None
    listing = next(r for r in client.get("/api/v1/analyses").json()["items"] if r["run_id"] == run_id)
    assert listing["overall_posture"] == "INSUFFICIENT_EVIDENCE" and listing["score_value"] is None
    dash = get("/dashboard").json()["posture"]
    assert dash["withheld"] is True and dash["score_value"] is None and dash["score_text"] == "Not scored"
    assert get("/reports/json").json() == a
    html = get("/reports/html").text
    text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))
    assert "Not scored" in text
    assert not re.search(r"\b\d{1,3}(\.\d+)?\s*/\s*100\b", text)
    for lang in ("mr", "both"):
        t = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", get(f"/reports/html?lang={lang}").text))
        assert not re.search(r"\b\d{1,3}(\.\d+)?\s*/\s*100\b", t), lang
    import io
    import pypdf
    pdf = " ".join((p.extract_text() or "") for p in pypdf.PdfReader(io.BytesIO(get("/reports/pdf").content)).pages)
    assert "Not scored" in pdf and not re.search(r"\b\d{1,3}(\.\d+)?\s*/\s*100\b", pdf)


@needs_tshark
@needs_corpus
def test_a_graded_assessment_agrees_across_surfaces(tmp_path):
    from fastapi.testclient import TestClient
    from nyaysaakshya.backend.api import create_app
    from nyaysaakshya.backend.service import AnalysisService
    client = TestClient(create_app(service=AnalysisService(str(tmp_path / "data"))))
    with open(f"{DEMO}/deepdive_cross_session_control_endpoint.pcap", "rb") as fh:
        run_id = client.post("/api/v1/analyses", files={"file": ("x.pcap", fh.read(), "application/octet-stream")}).json()["run_id"]
    a = client.get(f"/api/v1/analyses/{run_id}/assessment").json()["assessment"]
    assert a["score"]["scored"] is True and a["score"]["value"] == 22.15
    listing = next(r for r in client.get("/api/v1/analyses").json()["items"] if r["run_id"] == run_id)
    assert listing["score_value"] == 22.15
    assert client.get(f"/api/v1/analyses/{run_id}/dashboard").json()["posture"]["score_text"] == "22.15 / 100"
    assert "22.15 / 100" in re.sub(r"\s+", " ", re.sub(
        r"<[^>]+>", " ", client.get(f"/api/v1/analyses/{run_id}/reports/html").text))


# ===================================================================== ML lane isolation
@needs_tshark
@needs_corpus
@pytest.mark.parametrize("path", [f"{DEMO}/deepdive_cross_session_control_endpoint.pcap",
                                  f"{OQ46}/D_cut_during_starttls.pcap",
                                  f"{GEN_C}/C19_truncated.pcap",
                                  f"{OQ33R}/postfix_smtp_plaintext_session.pcap"])
def test_the_ml_lane_cannot_change_a_security_conclusion(path):
    """AI on versus AI off: findings, band, score, coverage, abstentions and issue groups of
    the security conclusion are identical. Only ML-owned fields may differ."""
    from nyaysaakshya.backend.pipeline import run_pipeline
    off = run_pipeline(path, ai_enabled=False).assessment.to_dict()
    on = run_pipeline(path, ai_enabled=True).assessment.to_dict()
    assert on["overall_posture"] == off["overall_posture"]
    assert on["score"] == off["score"]
    assert on["coverage"] == off["coverage"]
    assert on["abstentions"] == off["abstentions"]
    non_ml = lambda a: [g for g in a["issue_groups"] if g["fact_kind"] != "ANOMALY_SIGNAL"]   # noqa: E731
    assert non_ml(on) == non_ml(off)
    changed = {k for k in on if on[k] != off[k]} - {"generated_at", "run_id"}
    assert changed <= {"assessment_id", "ai_enabled", "risk_summary", "issue_groups", "prioritised",
                       "model_summary", "provenance", "limitations"}, changed


def test_an_anomaly_signal_is_structurally_unable_to_penalise_or_make_a_session_assessed():
    from test_posture_fusion import ml
    a = PostureEngine(__import__("nyaysaakshya.posture.engine", fromlist=["PostureConfig"]).PostureConfig(
        ai_enabled=True)).assess(sessions=[_sess(1)], findings=[], ml_results=[ml("cap:1")],
                                 capture_id="cap", generated_at=AT)
    assert a.coverage.sessions_assessed == 0
    assert not [g for g in a.issue_groups if g.penalising]
    assert a.band is PostureBand.INSUFFICIENT_EVIDENCE
    assert FactKind.ANOMALY_SIGNAL in {g.fact_kind for g in a.issue_groups}


# ===================================================================== withheld wording
@needs_tshark
@needs_corpus
def test_a_capture_where_no_session_could_be_assessed_says_so_on_every_surface():
    """D7's capture: one supported session, cut inside the handshake. The reason shown is not the
    generic 'coverage below the floor' and not the 'no SMTP/IMAP/POP3' text (there was SMTP)."""
    from nyaysaakshya.dashboard import project
    from nyaysaakshya.reporting.service import render_bytes
    a = _pipeline(f"{OQ46}/E_cut_during_handshake.pcap").assessment.to_dict()
    view = project(a)
    assert view.posture.withheld
    assert view.posture.withheld_note.startswith("Posture withheld: no session in this capture could be assessed")
    assert "SMTP, IMAP or POP3 dialogue was identified" not in view.posture.withheld_note
    assert any("No session in this capture could be assessed" in n for n in view.notices)
    text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", render_bytes(a, "html", "en")[0].decode()))
    assert "band withheld: no session could be assessed" in text
    assert "A withheld band is not a passing result" in text
    assert render_bytes(a, "html", "mr")[0] and render_bytes(a, "pdf", "en")[0][:4] == b"%PDF"


@needs_tshark
@needs_corpus
def test_below_the_floor_withholding_keeps_its_own_wording():
    """C19-style: some sessions assessed in principle but too few; still the floor wording."""
    from nyaysaakshya.dashboard import project
    a = _assess([_sess(i) for i in range(1, 6)], [finding("SEC-PLAIN-001", stream="cap:1")]).to_dict()
    view = project(a)
    assert view.posture.withheld and view.coverage.sessions_assessed == 1
    assert view.posture.withheld_note == "band withheld: evidence coverage below the assessment floor"


@needs_tshark
@needs_corpus
@pytest.mark.parametrize("path,reason", [
    (f"{OQ46}/E_cut_during_handshake.pcap", "band withheld: no session could be assessed"),
    (f"{P11}/tls12_weak_sha1_rsa1024.pcap", "band withheld: no supported session was assessed"),
])
def test_masthead_and_summary_give_the_same_withholding_reason(path, reason):
    """B.2 left the masthead saying 'coverage below the floor' while the summary gave the real
    reason. One note, one place it is decided, shown identically in HTML and PDF."""
    import io
    import pypdf
    from nyaysaakshya.reporting.projection import project
    from nyaysaakshya.reporting.service import render_bytes
    a = _pipeline(path).assessment.to_dict()
    assert project(a).withheld_note == reason
    html = render_bytes(a, "html", "en")[0].decode()
    verdict = html.split('<div class="verdict">')[1].split("<main>")[0]
    assert reason in verdict
    assert html.count(reason) >= 2                     # masthead and summary table
    assert "coverage below the assessment floor" not in html
    pdf = " ".join(p.extract_text() or "" for p in pypdf.PdfReader(
        io.BytesIO(render_bytes(a, "pdf", "en")[0])).pages)
    assert re.sub(r"\s+", " ", reason) in re.sub(r"\s+", " ", pdf)
    assert "coverage below the assessment floor" not in re.sub(r"\s+", " ", pdf)


# ===================================================================== B.4: post-ServerHello decision
def _by_rule(name):
    return {f.rule_id: f for f in ENGINE.analyse_session(SCENARIOS[name])}


def test_conclusions_from_the_serverhello_say_they_concern_the_negotiated_parameters():
    """Decision B.4: parameters the server selected may be concluded when the handshake is cut
    off, but the finding must not read as a statement about the complete session."""
    got = _by_rule("serverhello_cut_tls12")
    for rule_id in ("SEC-TLS-001", "SEC-FS-001"):
        f = got[rule_id]
        assert f.status is FindingStatus.COMPLIANT
        assert any("parameters the server selected" in lim and "SEC-TLS-002" in lim
                   and "does not establish the security of the complete session" in lim
                   for lim in f.limitations), rule_id
    assert got["SEC-FS-001"].conclusion == "The negotiated key exchange provides forward secrecy."
    assert "session provides" not in got["SEC-FS-001"].conclusion


def test_the_scope_note_is_absent_once_the_session_is_shown_to_be_established():
    got = _by_rule("established_tls13_no_cert")
    assert got["SEC-TLS-001"].limitations == () and got["SEC-FS-001"].limitations == ()


def test_completion_and_certificate_still_abstain_after_a_serverhello_cut():
    got = _by_rule("serverhello_cut_tls12")
    assert got["SEC-TLS-002"].status is FindingStatus.INSUFFICIENT_EVIDENCE
    assert got["SEC-CERT-001"].status is FindingStatus.NOT_OBSERVABLE
    assert got["SEC-CFG-001"].status is FindingStatus.INFORMATIONAL


# ===================================================================== B.4: SEC-CERT-004 decision
def test_signature_rule_states_its_chain_level_scope_in_both_outcomes_and_abstains_without_names():
    """SEC-CERT-004 reads one chain-wide OID list from a closed table. It never invents a weakness
    for an unrecognised OID, abstains when nothing is recognised, and its compliant outcome now
    carries the same chain-level limitation as its issue outcome."""
    from nyaysaakshya.analysis.rules.certificate_rules import CertificateSignatureRule
    E = EvidenceField
    def run(oids):
        sess = _base(tls_state=TlsState.ESTABLISHED, implicit_tls=True,
                     certificates=(_good_cert(0),), tls_certificate_chain=E.observed(1, "c"),
                     chain_signature_oids=oids)
        return CertificateSignatureRule().evaluate(sess)[0]
    sha256, sha1, rsa_key = "1.2.840.113549.1.1.11", "1.2.840.113549.1.1.5", "1.2.840.113549.1.1.1"
    assert run((sha256, rsa_key)).status is FindingStatus.COMPLIANT        # key OID is not a signature
    assert any("chain as a whole" in x for x in run((sha256, rsa_key)).limitations)
    assert run((sha256, "9.9.9.9")).status is FindingStatus.COMPLIANT      # unknown OID is never "weak"
    assert run((sha1, sha256)).status is FindingStatus.OBSERVED_ISSUE
    assert run(("9.9.9.9", rsa_key)).status is FindingStatus.INSUFFICIENT_EVIDENCE
    assert run(()).status is FindingStatus.INSUFFICIENT_EVIDENCE
