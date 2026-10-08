"""
Insecure protocol configuration (deliverable D-16).

D-16 reads, verbatim: "Identification of insecure protocol configurations." The requirement
does not enumerate which configurations count (recorded as AMB-06). An open-ended requirement cannot be assessed, closed, or defended in
review, so Phase 11 resolves it by DECLARING a bounded checklist.

THE CHECKLIST IS CLOSED AND VERSIONED. Adding an item is a RULES_VERSION bump, not an
edit. That is what makes "D-16 satisfied" a statement with content.

Each item is evaluated independently and reports its own outcome, including when it
passes. An item whose evidence is absent returns NOT_OBSERVABLE -- never "pass". A
checklist that silently scored missing evidence as compliant would be worse than no
checklist, because it would manufacture reassurance.

ANTI-DOUBLE-COUNTING. Item 1 (deprecated TLS version) delegates to SEC-TLS-001 and is
reported here without emitting a second finding. Posture fusion groups on IssueClass, so
a duplicate would inflate recurrence damping and move the score for a condition already
counted once.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List, Optional, Tuple

from nyaysaakshya.analysis.model import FindingStatus, SecurityFinding, Severity
from nyaysaakshya.analysis.registry import SecurityRule, ref
from nyaysaakshya.crypto import oids
from nyaysaakshya.evidence.states import EvidenceState
from nyaysaakshya.session.model import SessionEvidence, TlsState

#: Bumped whenever an item is added, removed or re-specified.
CHECKLIST_VERSION = "1.1"   # B.3: "transport protection" passes only when TLS is established; COMPLIANT needs all 7 items


@dataclass(frozen=True)
class CheckOutcome:
    """One checklist item's result."""
    item: str
    status: FindingStatus
    detail: str


def _deprecated_version(session: SessionEvidence) -> CheckOutcome:
    version = session.tls_negotiated_version
    if not version.is_conclusive:
        return CheckOutcome("deprecated TLS version", FindingStatus.NOT_OBSERVABLE,
                            "the negotiated version was not established")
    weak = version.value in ("SSL2.0", "SSL3.0", "TLS1.0", "TLS1.1")
    return CheckOutcome(
        "deprecated TLS version",
        FindingStatus.OBSERVED_ISSUE if weak else FindingStatus.COMPLIANT,
        f"negotiated {version.value}" + (" (reported by SEC-TLS-001)" if weak else ""))


def _no_forward_secrecy(session: SessionEvidence) -> CheckOutcome:
    fs = session.tls_forward_secrecy
    if fs.state is EvidenceState.AMBIGUOUS:
        return CheckOutcome("forward secrecy", FindingStatus.AMBIGUOUS,
                            "the cipher suite was not recognised")
    if not fs.is_conclusive:
        # UNKNOWN, INCOMPLETE or NOT_OBSERVABLE: there is no value to judge, and a missing
        # value must never read as "forward secrecy not provided".
        return CheckOutcome("forward secrecy", FindingStatus.NOT_OBSERVABLE,
                            "no handshake was observed")
    return CheckOutcome(
        "forward secrecy",
        FindingStatus.COMPLIANT if fs.value else FindingStatus.OBSERVED_ISSUE,
        "provided" if fs.value else "not provided by the negotiated key exchange")


def _weak_rsa_key(session: SessionEvidence) -> CheckOutcome:
    from nyaysaakshya.analysis.rules.certificate_rules import MIN_RSA_BITS
    if not session.certificates:
        return CheckOutcome("RSA key length", FindingStatus.NOT_OBSERVABLE,
                            "no certificate was observable")
    sized = [c for c in session.certificates if c.key_bits is not None]
    if not sized:
        return CheckOutcome("RSA key length", FindingStatus.NOT_OBSERVABLE,
                            "no public key parameters could be read")
    weak = [c for c in sized
            if c.public_key_algorithm == "RSA" and c.key_bits < MIN_RSA_BITS]
    if weak:
        return CheckOutcome("RSA key length", FindingStatus.OBSERVED_ISSUE,
                            f"{weak[0].key_bits}-bit RSA key below the {MIN_RSA_BITS}-bit minimum")
    if len(sized) < len(session.certificates):
        # Follows its delegate (SEC-CERT-003): a chain in which some key could not be read is
        # not shown to meet the minimum, so the item was not fully evaluated.
        return CheckOutcome("RSA key length", FindingStatus.NOT_OBSERVABLE,
                            "the public key could not be read for every certificate")
    return CheckOutcome("RSA key length", FindingStatus.COMPLIANT,
                        f"all observed keys meet the {MIN_RSA_BITS}-bit minimum")


def _deprecated_signature(session: SessionEvidence) -> CheckOutcome:
    if not session.certificates:
        return CheckOutcome("certificate signature hash", FindingStatus.NOT_OBSERVABLE,
                            "no certificate was observable")
    seen = False
    for oid in session.chain_signature_oids:
        entry = oids.signature_algorithm(oid)
        if entry is None:
            continue
        seen = True
        if oids.DEPRECATED_HASHES.get(entry[2]):
            return CheckOutcome("certificate signature hash", FindingStatus.OBSERVED_ISSUE,
                                f"{entry[2]} signature observed in the chain")
    if not seen:
        return CheckOutcome("certificate signature hash", FindingStatus.NOT_OBSERVABLE,
                            "no recognised signature algorithm was read")
    return CheckOutcome("certificate signature hash", FindingStatus.COMPLIANT,
                        "no deprecated signature hash observed")


def _certificate_validity(session: SessionEvidence) -> CheckOutcome:
    if not session.certificates:
        return CheckOutcome("certificate validity window", FindingStatus.NOT_OBSERVABLE,
                            "no certificate was observable")
    reference = session.start_epoch
    if reference is None:
        return CheckOutcome("certificate validity window", FindingStatus.NOT_OBSERVABLE,
                            "the capture carries no timestamp to evaluate against")
    dated = [c for c in session.certificates
             if c.not_after_epoch is not None and c.not_before_epoch is not None]
    if not dated:
        return CheckOutcome("certificate validity window", FindingStatus.NOT_OBSERVABLE,
                            "no validity window could be read")
    for cert in dated:
        if reference > cert.not_after_epoch:
            return CheckOutcome("certificate validity window", FindingStatus.OBSERVED_ISSUE,
                                "a certificate had expired at capture time")
        if reference < cert.not_before_epoch:
            return CheckOutcome("certificate validity window", FindingStatus.OBSERVED_ISSUE,
                                "a certificate was not yet valid at capture time")
    if len(dated) < len(session.certificates):
        # Follows its delegate (SEC-CERT-002), as above.
        return CheckOutcome("certificate validity window", FindingStatus.NOT_OBSERVABLE,
                            "the validity window could not be read for every certificate")
    return CheckOutcome("certificate validity window", FindingStatus.COMPLIANT,
                        "all observed certificates were valid at capture time")


def _self_signed_leaf(session: SessionEvidence) -> CheckOutcome:
    if not session.certificates:
        return CheckOutcome("self-signed leaf certificate", FindingStatus.NOT_OBSERVABLE,
                            "no certificate was observable")
    leaf = session.certificates[0]
    if leaf.is_self_signed is None:
        return CheckOutcome("self-signed leaf certificate", FindingStatus.NOT_OBSERVABLE,
                            "key identifiers were not present, so self-signing is undetermined")
    if leaf.is_self_signed and len(session.certificates) == 1:
        return CheckOutcome("self-signed leaf certificate", FindingStatus.OBSERVED_ISSUE,
                            "the server presented a single self-signed certificate")
    return CheckOutcome("self-signed leaf certificate", FindingStatus.COMPLIANT,
                        "the leaf certificate was issued by a separate key")


def _plaintext_transport(session: SessionEvidence) -> CheckOutcome:
    if session.tls_state is TlsState.NONE:
        # This item is DELEGATED to SEC-PLAIN-002, so it may only fail when that rule has
        # the evidence to report it: an observed absence of TLS. A stream that is cut off
        # or has no client dialogue does not establish an absence, so the item was not
        # tested rather than failed.
        transition = session.tls_transition
        if transition.state is EvidenceState.OBSERVED and transition.value is False:
            return CheckOutcome("transport protection", FindingStatus.OBSERVED_ISSUE,
                                "no TLS records were observed in this session "
                                "(reported by SEC-PLAIN-002)")
        return CheckOutcome("transport protection", FindingStatus.NOT_OBSERVABLE,
                            "the capture does not establish whether this session was "
                            "protected by TLS")
    # TLS records exist. That is "protected" only if the negotiation is shown to have
    # completed; a ClientHello (or both hellos) with no encrypted data after it is a
    # negotiation in progress, and SEC-TLS-002 reports it as incomplete. Passing the item
    # on a hello alone would be the same over-claim in the opposite direction.
    if session.tls_state is TlsState.ESTABLISHED:
        return CheckOutcome("transport protection", FindingStatus.COMPLIANT,
                            "TLS was established and encrypted application data was observed")
    return CheckOutcome("transport protection", FindingStatus.NOT_OBSERVABLE,
                        "TLS records were observed but the negotiation is not shown to have "
                        "completed")


#: THE CHECKLIST. Closed, ordered, and versioned; order is part of deterministic output.
CHECKLIST: Tuple[Tuple[str, Callable[[SessionEvidence], CheckOutcome]], ...] = (
    ("deprecated TLS version", _deprecated_version),
    ("forward secrecy", _no_forward_secrecy),
    ("RSA key length", _weak_rsa_key),
    ("certificate signature hash", _deprecated_signature),
    ("certificate validity window", _certificate_validity),
    ("self-signed leaf certificate", _self_signed_leaf),
    ("transport protection", _plaintext_transport),
)

#: Items already reported by a dedicated rule. Counted in the summary, never re-emitted
#: as a separate finding, because fusion groups on IssueClass.
DELEGATED = {"deprecated TLS version", "forward secrecy", "transport protection",
             "RSA key length", "certificate signature hash",
             "certificate validity window", "self-signed leaf certificate"}


class InsecureConfigurationRule(SecurityRule):
    """SEC-CFG-001 -- bounded insecure-configuration checklist (D-16, closes AMB-06)."""

    rule_id = "SEC-CFG-001"
    title = "Insecure protocol configuration"
    description = (f"Evaluates a declared, versioned checklist (v{CHECKLIST_VERSION}) of "
                   "insecure protocol and certificate configurations.")
    standards = ("RFC 8996 (BCP 195): TLS 1.0 and TLS 1.1 MUST NOT be used",
                 "NIST SP 800-52r2: TLS server configuration guidance",
                 "NIST SP 800-57 Part 1 Rev.5: key length guidance",
                 "RFC 9155: SHA-1 must not be used for digital signatures")

    def evaluate(self, session: SessionEvidence) -> List[SecurityFinding]:
        outcomes = [check(session) for _name, check in CHECKLIST]
        issues = [o for o in outcomes if o.status is FindingStatus.OBSERVED_ISSUE]
        unobservable = [o for o in outcomes
                        if o.status in (FindingStatus.NOT_OBSERVABLE, FindingStatus.AMBIGUOUS)]
        passed = [o for o in outcomes if o.status is FindingStatus.COMPLIANT]

        refs = [ref("tls_negotiated_version", session.tls_negotiated_version),
                ref("tls_forward_secrecy", session.tls_forward_secrecy),
                ref("tls_certificate_chain", session.tls_certificate_chain)]

        summary = (f"{len(passed)} of {len(CHECKLIST)} checklist items passed, "
                   f"{len(issues)} failed, {len(unobservable)} were not observable")
        coverage = tuple(f"not evaluated -- {o.item}: {o.detail}" for o in unobservable)

        # Every failing item is already reported by its own rule with its own severity
        # and remediation. This rule reports COVERAGE of the checklist, so that D-16 is
        # answerable as a whole, without emitting a duplicate of each condition.
        if issues:
            detail = "; ".join(f"{o.item}: {o.detail}" for o in issues)
            return [self.finding(
                session,
                status=FindingStatus.INFORMATIONAL, severity=Severity.INFO,
                conclusion=f"Configuration checklist: {len(issues)} item(s) failed.",
                explanation=(f"{summary}. Failing items: {detail}. Each failing item is "
                             "reported as its own finding with its own severity and "
                             "remediation; this entry records checklist coverage and is "
                             "deliberately not a second copy of those findings."),
                evidence_refs=refs,
                limitations=coverage + (
                    f"The checklist is closed at version {CHECKLIST_VERSION}: conditions "
                    "outside it were not assessed and are not claimed to be absent.",))]

        if not passed:
            return [self.finding(
                session,
                status=FindingStatus.NOT_OBSERVABLE, severity=Severity.INFO,
                conclusion="No configuration checklist item could be evaluated.",
                explanation=(f"{summary}. No item is reported as compliant, because an "
                             "item with no evidence has not passed -- it was not tested."),
                evidence_refs=refs,
                limitations=coverage)]

        if unobservable:
            items = "; ".join(f"{o.item} ({o.detail})" for o in passed)
            # PARTIAL OBSERVATION. Some items passed and none failed, but the closed checklist
            # was not fully evaluated. "Compliant" would claim the property (no insecure
            # configuration among the declared items) for a session in which part of it was
            # never tested. That is a coverage note, not a conclusion, so it is INFORMATIONAL
            # exactly as the "some items failed" branch is. The properties that WERE
            # established are still concluded by their own rules (SEC-TLS-001, SEC-FS-001,
            # SEC-CERT-*), each of which is COMPLIANT only on its own evidence.
            return [self.finding(
                session,
                status=FindingStatus.INFORMATIONAL, severity=Severity.INFO,
                conclusion=(f"Configuration checklist: {len(passed)} of {len(CHECKLIST)} "
                            "items passed; the rest could not be evaluated."),
                explanation=(f"{summary}. No item failed, but the checklist was not fully "
                             f"evaluated, so no overall compliance is claimed. Items that passed: "
                             f"{items}. This entry records checklist coverage; each established "
                             f"property is concluded by its own rule."),
                evidence_refs=refs,
                limitations=coverage + (
                    f"The checklist is closed at version {CHECKLIST_VERSION}: conditions "
                    "outside it were not assessed and are not claimed to be absent.",))]

        return [self.finding(
            session,
            status=FindingStatus.COMPLIANT, severity=Severity.INFO,
            conclusion=f"Configuration checklist: {len(passed)} of {len(CHECKLIST)} items passed.",
            explanation=(f"{summary}. Items evaluated: "
                         + "; ".join(f"{o.item} ({o.detail})" for o in passed) + "."),
            evidence_refs=refs,
            limitations=(
                f"The checklist is closed at version {CHECKLIST_VERSION}: conditions "
                "outside it were not assessed and are not claimed to be absent.",))]
