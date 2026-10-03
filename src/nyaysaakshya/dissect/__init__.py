"""Dissection layer: safe tshark adapter + normalization boundary (ADR-0001)."""
from nyaysaakshya.dissect.tshark import (
    TsharkAdapter, DissectResult, DissectStatus, TsharkNotFound, TsharkVersionError,
)
from nyaysaakshya.dissect.normalize import (
    FrameEvidence, TlsEvidence, MailEvidence,
    normalize, normalize_packet, normalize_stream, summarize, pick, pick_all,
)

__all__ = [
    "TsharkAdapter", "DissectResult", "DissectStatus",
    "TsharkNotFound", "TsharkVersionError",
    "FrameEvidence", "TlsEvidence", "MailEvidence",
    "normalize", "normalize_packet", "normalize_stream", "summarize", "pick", "pick_all",
]
