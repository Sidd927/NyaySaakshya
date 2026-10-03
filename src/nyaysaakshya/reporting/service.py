"""
Report generation and storage (doc 22 §12, §13, ADR-0021).

Renders a report, stores it through the **Phase-8 artifact store** — not a second one —
and returns identity plus integrity metadata.

The store and repository are injected, and their types are imported only under
`TYPE_CHECKING`. `reporting/` therefore imports nothing from `backend/` at runtime: the
dependency runs one way, `backend/api.py` composing `reporting/` and not the reverse.
An import cycle between the two would otherwise be real, and a lazy import hiding it
would be worse than not having one.

Two properties this module exists to hold:

* **A report failure never touches the assessment.** It raises a `ReportError`; the run
  stays `COMPLETED` and every other format remains available (ADR-0019 Decision 4).
* **A report is regenerated rather than served** when the stored artefact is missing,
  fails verification, or was produced under a different report schema or renderer
  version. A report from an incompatible renderer is never silently handed over.
"""
from __future__ import annotations

import io
import json
import re
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

if TYPE_CHECKING:            # pragma: no cover - typing only
    from nyaysaakshya.backend.artifacts import ArtifactStore
    from nyaysaakshya.backend.repository import ArtifactRecord, Repository

from nyaysaakshya.reporting import i18n
from nyaysaakshya.reporting.errors import (
    ReportError, ReportTooLarge, UnsupportedFormat, UnsupportedLanguage,
)
from nyaysaakshya.reporting.html import render_html, render_localized
from nyaysaakshya.reporting.model import (
    RENDERER_VERSION, REPORT_SCHEMA_VERSION, ReportDocument,
)
from nyaysaakshya.reporting.projection import project

FORMAT_HTML = "html"
FORMAT_PDF = "pdf"
FORMAT_JSON = "json"
SUPPORTED_FORMATS = (FORMAT_HTML, FORMAT_PDF, FORMAT_JSON)

MEDIA_TYPE = {
    FORMAT_HTML: "text/html; charset=utf-8",
    FORMAT_PDF: "application/pdf",
    FORMAT_JSON: "application/json",
}

#: Artifact kinds. Extends the Phase-8 vocabulary; the store was already
#: kind-parameterised and reserved this use.
KIND = {FORMAT_HTML: "html", FORMAT_PDF: "pdf"}

LANG_EN = i18n.LANG_EN
SUPPORTED_LANGUAGES = i18n.SUPPORTED_LANGS
#: Which languages each format can be rendered in. JSON is the canonical document and is
#: never translated; PDF cannot yet draw Devanagari (the renderer embeds no font), so it
#: stays English-only rather than producing a broken Marathi PDF.
LANGUAGES_BY_FORMAT = {
    FORMAT_HTML: SUPPORTED_LANGUAGES,
    FORMAT_PDF: (LANG_EN,),
    FORMAT_JSON: (LANG_EN,),
}
TRANSLATED_LANGUAGES = tuple(l for l in SUPPORTED_LANGUAGES if l != LANG_EN)

#: doc 22 §15. Bounds artifact growth from one pathological assessment.
MAX_REPORT_BYTES = 32 * 1024 * 1024

#: Encoded into the artifact's display name so a stored report records the renderer
#: that produced it. Parsed back out to decide regeneration.
#: A translated report additionally records its language and the translation catalogue it was
#: built from (`.l<lang>.c<fingerprint>`); an English name has neither, exactly as before.
_STAMP = re.compile(r"^securemailscope-(?P<assessment>[0-9a-f]+)"
                    r"\.r(?P<report>[0-9.]+)\.v(?P<renderer>[0-9.]+)"
                    r"(?:\.l(?P<lang>[a-z]+)\.c(?P<catalogue>[0-9a-f]+))?\.(?P<ext>\w+)$")
_FINGERPRINT_CHARS = 12


def _check_language(fmt: str, lang: str) -> None:
    """Refuse an unknown language, or one this format cannot be rendered in."""
    if lang not in SUPPORTED_LANGUAGES:
        raise UnsupportedLanguage(
            "unsupported report language",
            detail={"language": lang, "supported": list(SUPPORTED_LANGUAGES)})
    if fmt in LANGUAGES_BY_FORMAT and lang not in LANGUAGES_BY_FORMAT[fmt]:
        raise UnsupportedLanguage(
            "this report format is not available in that language",
            detail={"format": fmt, "language": lang,
                    "supported_for_format": list(LANGUAGES_BY_FORMAT[fmt])})


def artifact_kind(fmt: str, lang: str = LANG_EN) -> str:
    """Artifact kind under which a rendition is stored: one cache entry per language."""
    return KIND[fmt] if lang == LANG_EN else "%s_%s" % (KIND[fmt], lang)


def safe_filename(assessment_id: str, fmt: str, lang: str = LANG_EN) -> str:
    """Download filename built from internal identifiers only (doc 22 §14).

    The uploaded PCAP name never contributes. `assessment_id` is hex from a hash, but it
    is filtered anyway rather than trusted for being usually-safe. A translated report
    carries its language as a suffix (``-mr``, ``-both``); English is unchanged.
    """
    if fmt not in SUPPORTED_FORMATS:
        raise UnsupportedFormat("unsupported report format",
                                detail={"format": fmt,
                                        "supported": list(SUPPORTED_FORMATS)})
    _check_language(fmt, lang)
    ident = re.sub(r"[^A-Za-z0-9_-]", "", str(assessment_id))[:64] or "assessment"
    suffix = "" if lang == LANG_EN else "-" + lang
    return "securemailscope-{0}{1}.{2}".format(ident, suffix, fmt)


def _catalogue_stamp() -> str:
    return i18n.load_catalogue(i18n.LANG_MR).fingerprint[:_FINGERPRINT_CHARS]


def _stamped_name(assessment_id: str, fmt: str, lang: str = LANG_EN) -> str:
    ident = re.sub(r"[^A-Za-z0-9_-]", "", str(assessment_id))[:64] or "assessment"
    language = "" if lang == LANG_EN else ".l{0}.c{1}".format(lang, _catalogue_stamp())
    return "securemailscope-{0}.r{1}.v{2}{3}.{4}".format(
        ident, REPORT_SCHEMA_VERSION, RENDERER_VERSION, language, fmt)


def _is_current(record: "ArtifactRecord", lang: str = LANG_EN) -> bool:
    """Whether a stored artefact was produced by this report schema and renderer.

    A translated artefact must also have been built from the *current* translation
    catalogue: swapping in reviewed text changes the fingerprint, and the stale rendition
    is then regenerated rather than served.
    """
    match = _STAMP.match(record.original_filename or "")
    if not match:
        return False
    if not (match.group("report") == REPORT_SCHEMA_VERSION
            and match.group("renderer") == RENDERER_VERSION):
        return False
    if lang == LANG_EN:
        return match.group("lang") is None
    return (match.group("lang") == lang
            and match.group("catalogue") == _catalogue_stamp())


def render_report(assessment: Dict[str, Any], fmt: str, lang: str = LANG_EN
                  ) -> Tuple[bytes, ReportDocument, Optional[i18n.LocalizationReport]]:
    """Render one format in one language, also returning what the translation left over.

    Raises `ReportError` subclasses; never returns a stub.
    """
    _check_language(fmt, lang)
    document = project(assessment)
    localization: Optional[i18n.LocalizationReport] = None
    if fmt == FORMAT_HTML:
        html, localization = render_localized(document, lang)
        payload = html.encode("utf-8")
    elif fmt == FORMAT_PDF:
        from nyaysaakshya.reporting.pdf import render_pdf
        payload = render_pdf(document)
    elif fmt == FORMAT_JSON:
        # The canonical document, unaltered. Identical to the assessment endpoint.
        payload = json.dumps(assessment, indent=2, sort_keys=True).encode("utf-8")
    else:
        raise UnsupportedFormat("unsupported report format",
                                detail={"format": fmt,
                                        "supported": list(SUPPORTED_FORMATS)})
    if len(payload) > MAX_REPORT_BYTES:
        raise ReportTooLarge("rendered report exceeds the size ceiling",
                             detail={"bytes": len(payload),
                                     "max_bytes": MAX_REPORT_BYTES})
    return payload, document, localization


def render_bytes(assessment: Dict[str, Any], fmt: str,
                 lang: str = LANG_EN) -> Tuple[bytes, ReportDocument]:
    """Render one format. Raises `ReportError` subclasses; never returns a stub."""
    payload, document, _localization = render_report(assessment, fmt, lang)
    return payload, document


def _translation_status(document: ReportDocument) -> Dict[str, Any]:
    """How trustworthy the translation of this report is, for the response metadata."""
    catalogue = i18n.load_catalogue(i18n.LANG_MR)
    _doc, localization = i18n.localize(document, i18n.LANG_MR)
    return {
        "catalogue_version": catalogue.version,
        "catalogue_fingerprint": catalogue.fingerprint[:_FINGERPRINT_CHARS],
        # "draft" for as long as any catalogue entry has not been reviewed by a person.
        "status": "draft" if catalogue.pending_review else "reviewed",
        "pending_review_entries": catalogue.pending_review,
        "untranslated_strings": len(localization.untranslated),
        "authoritative_language": LANG_EN,
    }


class ReportService:
    """Renders, stores and verifies report artifacts for completed runs."""

    def __init__(self, repository: "Repository",
                 artifacts: "ArtifactStore") -> None:
        self.repo = repository
        self.artifacts = artifacts

    # ------------------------------------------------------------- generation
    def get_or_create(self, run_id: str, assessment: Dict[str, Any], fmt: str,
                      lang: str = LANG_EN) -> Tuple[bytes, Dict[str, Any]]:
        """Return report bytes plus metadata, rendering only when necessary.

        JSON is never stored as an artefact: it is the canonical document, already
        persisted by Phase 8, and storing a second copy would create a second place for
        it to drift. Each language of a stored format is its own artefact, so asking for
        Marathi never returns (or overwrites) the English report.
        """
        _check_language(fmt, lang)
        if fmt == FORMAT_JSON:
            payload, document = render_bytes(assessment, fmt)
            return payload, self._metadata(None, document, fmt, len(payload))

        existing = self._usable_artifact(run_id, fmt, lang)
        if existing is not None:
            path = self.artifacts.absolute(existing.relative_path)
            with open(path, "rb") as handle:
                payload = handle.read()
            document = project(assessment)
            return payload, self._metadata(existing, document, fmt, len(payload), lang)

        payload, document, _localization = render_report(assessment, fmt, lang)
        record = self._store(run_id, assessment, fmt, payload, lang)
        return payload, self._metadata(record, document, fmt, len(payload), lang)

    def _usable_artifact(self, run_id: str, fmt: str,
                         lang: str = LANG_EN) -> Optional["ArtifactRecord"]:
        """The newest stored report of this format and language that is current AND intact.

        Missing, tampered or stale-renderer artefacts are ignored so the caller
        regenerates, rather than being served something this build did not produce. For a
        translated report "current" also means built from today's translation catalogue.
        """
        kind = artifact_kind(fmt, lang)
        candidates = [a for a in self.repo.list_artifacts(run_id) if a.kind == kind]
        for record in reversed(candidates):
            if _is_current(record, lang) and self.artifacts.is_intact(record):
                return record
        return None

    def _store(self, run_id: str, assessment: Dict[str, Any], fmt: str,
               payload: bytes, lang: str = LANG_EN) -> "ArtifactRecord":
        capture_id = str(assessment.get("capture_id") or run_id)
        record = self.artifacts.store_stream(
            io.BytesIO(payload), run_id=run_id, capture_id=capture_id,
            kind=artifact_kind(fmt, lang),
            original_filename=_stamped_name(
                str(assessment.get("assessment_id") or ""), fmt, lang))
        self.repo.add_artifact(record)
        return record

    # --------------------------------------------------------------- metadata
    def _metadata(self, record: Optional["ArtifactRecord"], document: ReportDocument,
                  fmt: str, size: int, lang: str = LANG_EN) -> Dict[str, Any]:
        meta: Dict[str, Any] = {
            "format": fmt,
            "language": lang,
            "media_type": MEDIA_TYPE[fmt],
            "filename": safe_filename(document.metadata.assessment_id, fmt, lang),
            "assessment_id": document.metadata.assessment_id,
            "capture_id": document.metadata.capture_id,
            "report_schema_version": document.metadata.report_schema_version,
            "renderer_version": document.metadata.renderer_version,
            "posture_schema_version": document.metadata.posture_schema_version,
            "posture_engine_version": document.metadata.posture_engine_version,
            "size_bytes": size,
            "sections": list(document.section_ids),
            "truncations": list(document.truncations),
        }
        if lang != LANG_EN:
            # The Marathi report opens with the static "how to read" section.
            meta["sections"] = ["how-to-read"] + meta["sections"]
            meta["translation"] = _translation_status(document)
        if record is not None:
            meta.update({
                "artifact_id": record.artifact_id,
                "report_sha256": record.sha256,
                "created_at": record.created_at,
                "integrity": "OK" if self.artifacts.is_intact(record) else "MISMATCH",
            })
        else:
            # JSON is served from the canonical document and is not an artefact.
            meta.update({"artifact_id": None, "report_sha256": None,
                         "created_at": None, "integrity": "NOT_STORED"})
        return meta

    def list_translations(self, run_id: str,
                          assessment: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """The translated renditions (HTML only, for now) and their stored state.

        Kept apart from `list_reports` so the English list is exactly what it always was.
        """
        stored = {a.kind: a for a in self.repo.list_artifacts(run_id)}
        assessment_id = str((assessment or {}).get("assessment_id") or "")
        catalogue = i18n.load_catalogue(i18n.LANG_MR)
        out: List[Dict[str, Any]] = []
        for lang in TRANSLATED_LANGUAGES:
            entry: Dict[str, Any] = {
                "format": FORMAT_HTML, "language": lang,
                "media_type": MEDIA_TYPE[FORMAT_HTML],
                "filename": safe_filename(assessment_id, FORMAT_HTML, lang),
                "renderer_available": True,
                "report_schema_version": REPORT_SCHEMA_VERSION,
                "renderer_version": RENDERER_VERSION,
                "catalogue_version": catalogue.version,
                "translation_status": "draft" if catalogue.pending_review else "reviewed",
            }
            record = stored.get(artifact_kind(FORMAT_HTML, lang))
            if record is not None:
                entry.update({
                    "generated": True, "artifact_id": record.artifact_id,
                    "report_sha256": record.sha256, "size_bytes": record.size_bytes,
                    "created_at": record.created_at,
                    "current": _is_current(record, lang),
                    "integrity": "OK" if self.artifacts.is_intact(record) else "MISMATCH",
                })
            else:
                entry.update({"generated": False, "artifact_id": None,
                              "report_sha256": None, "size_bytes": None,
                              "created_at": None, "current": None, "integrity": None})
            out.append(entry)
        return out

    def list_reports(self, run_id: str,
                     assessment: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Available report formats, with integrity for anything already stored."""
        from nyaysaakshya.reporting.pdf import available as pdf_available

        stored = {a.kind: a for a in self.repo.list_artifacts(run_id)
                  if a.kind in KIND.values()}
        out: List[Dict[str, Any]] = []
        assessment_id = str((assessment or {}).get("assessment_id") or "")
        for fmt in SUPPORTED_FORMATS:
            entry: Dict[str, Any] = {
                "format": fmt,
                "media_type": MEDIA_TYPE[fmt],
                "filename": safe_filename(assessment_id, fmt),
                "renderer_available": True if fmt != FORMAT_PDF else pdf_available(),
                "report_schema_version": REPORT_SCHEMA_VERSION,
                "renderer_version": RENDERER_VERSION,
            }
            record = stored.get(KIND.get(fmt, ""))
            if record is not None:
                entry.update({
                    "generated": True,
                    "artifact_id": record.artifact_id,
                    "report_sha256": record.sha256,
                    "size_bytes": record.size_bytes,
                    "created_at": record.created_at,
                    "current": _is_current(record),
                    "integrity": "OK" if self.artifacts.is_intact(record)
                                 else "MISMATCH",
                })
            else:
                entry.update({"generated": False, "artifact_id": None,
                              "report_sha256": None, "size_bytes": None,
                              "created_at": None, "current": None,
                              "integrity": None})
            out.append(entry)
        return out
