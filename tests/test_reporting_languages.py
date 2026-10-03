"""
Report languages through the API: `?lang=en|mr|both`, one cache entry per language, the
filename suffix, and the language/translation fields in the response metadata.

What these pin, in order of importance:

* English is untouched: no `lang`, `lang=en` and the pre-existing renderer give the same bytes,
  and asking for Marathi never reads, replaces or invalidates the English artefact.
* A translated report is its own artefact, and it is regenerated when the translation
  catalogue changes (reviewed text swapped in, or `needs_review` flipped) -- so reviewed
  Marathi can replace the draft without touching this layer, and a stale draft is never served.
* PDF and JSON are English-only and *say so* (400) instead of quietly returning English.
"""
import dataclasses
import hashlib
import re

import pytest

fastapi = pytest.importorskip("fastapi", reason="backend extra not installed")
pytest.importorskip("httpx", reason="httpx required by TestClient")
from fastapi.testclient import TestClient                        # noqa: E402

from nyaysaakshya.backend.api import create_app                # noqa: E402
from nyaysaakshya.backend.lifecycle import JobState            # noqa: E402
from nyaysaakshya.backend.repository import RunRecord          # noqa: E402
from nyaysaakshya.backend.service import AnalysisService       # noqa: E402
from nyaysaakshya.reporting import i18n                        # noqa: E402
from nyaysaakshya.reporting import service as report_service   # noqa: E402
from nyaysaakshya.reporting.html import render_html            # noqa: E402
from nyaysaakshya.reporting.projection import project          # noqa: E402
from nyaysaakshya.reporting.service import (                   # noqa: E402
    ReportService, safe_filename,
)
from tests.reporting_fixtures import (                            # noqa: E402
    HOSTILE, base_assessment, critical_assessment, hostile_assessment,
)


def _seeded(tmp_path, assessment=None):
    assessment = assessment or critical_assessment()
    svc = AnalysisService(str(tmp_path / "data"))
    run = svc.repo.create_run(RunRecord.new())
    svc.repo.store_assessment(assessment)
    for target in (JobState.VALIDATING, JobState.QUEUED, JobState.RUNNING,
                   JobState.FINALIZING):
        svc.repo.transition(run, target, capture_id=assessment["capture_id"])
    svc.repo.transition(run, JobState.COMPLETED, assessment_id=assessment["assessment_id"])
    return svc, run.run_id, assessment


def _client(svc):
    return TestClient(create_app(service=svc), raise_server_exceptions=False)


def _url(run_id, fmt="html", lang=None, download=False):
    params = []
    if lang is not None:
        params.append("lang=%s" % lang)
    if download:
        params.append("download=true")
    return "/api/v1/analyses/%s/reports/%s%s" % (run_id, fmt, "?" + "&".join(params) if params else "")


def _artifacts(svc, run_id):
    return [a for a in svc.repo.list_artifacts(run_id)]


@pytest.fixture
def seeded(tmp_path):
    return _seeded(tmp_path)


# ====================================================================== English
def test_english_is_unchanged_with_or_without_the_parameter(seeded):
    svc, run_id, assessment = seeded
    client = _client(svc)
    plain = client.get(_url(run_id))
    explicit = client.get(_url(run_id, lang="en"))
    assert plain.status_code == explicit.status_code == 200
    assert plain.content == explicit.content
    assert plain.content == render_html(project(assessment)).encode("utf-8")
    assert plain.headers["x-report-language"] == "en"
    assert plain.headers["content-language"] == "en"
    assert "x-translation-status" not in plain.headers
    assert plain.headers["cache-control"] == "private, max-age=86400"


def test_english_filename_has_no_suffix(seeded):
    svc, run_id, assessment = seeded
    response = _client(svc).get(_url(run_id, download=True))
    assert 'filename="%s"' % safe_filename(assessment["assessment_id"], "html") \
        in response.headers["content-disposition"]
    assert "-mr" not in response.headers["content-disposition"]


# ====================================================================== Marathi
def test_marathi_report_is_served_with_language_headers(seeded):
    svc, run_id, assessment = seeded
    response = _client(svc).get(_url(run_id, lang="mr"))
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert response.headers["x-report-language"] == "mr"
    assert response.headers["content-language"] == "mr"
    assert response.headers["x-translation-status"] == "draft"
    # the catalogue can change under it, so a translation is revalidated, not cached a day
    assert response.headers["cache-control"] == "private, no-cache"
    body = response.text
    assert '<html lang="mr">' in body and 'class="notice draft"' in body
    assert assessment["assessment_id"] in body and assessment["capture_id"] in body


def test_both_stacks_marathi_then_english(seeded):
    svc, run_id, _ = seeded
    response = _client(svc).get(_url(run_id, lang="both"))
    assert response.status_code == 200
    assert response.headers["content-language"] == "mr, en"
    body = response.text
    assert body.index('id="mr-report"') < body.index('id="en-report"')


def test_filename_suffix_per_language(seeded):
    svc, run_id, assessment = seeded
    client = _client(svc)
    ident = assessment["assessment_id"]
    for lang, expected in (("mr", "nyaysaakshya-%s-mr.html"),
                           ("both", "nyaysaakshya-%s-both.html")):
        disposition = client.get(_url(run_id, lang=lang, download=True)).headers["content-disposition"]
        assert 'filename="%s"' % (expected % ident) in disposition, disposition
    assert safe_filename(ident, "html", "mr").endswith("-mr.html")
    assert safe_filename(ident, "html", "en").endswith(ident + ".html")


def test_marathi_report_is_deterministic(tmp_path):
    """Two independent services render byte-identical translated reports."""
    svc_a, run_a, _ = _seeded(tmp_path / "a")
    svc_b, run_b, _ = _seeded(tmp_path / "b")
    for lang in ("mr", "both"):
        a = _client(svc_a).get(_url(run_a, lang=lang)).content
        b = _client(svc_b).get(_url(run_b, lang=lang)).content
        assert hashlib.sha256(a).hexdigest() == hashlib.sha256(b).hexdigest(), lang


def test_hostile_assessment_text_is_escaped_in_every_language(tmp_path):
    svc, run_id, _ = _seeded(tmp_path, hostile_assessment())
    client = _client(svc)
    for lang in ("en", "mr", "both"):
        body = client.get(_url(run_id, lang=lang)).text
        assert "<script" not in body.lower() and HOSTILE not in body, lang


# ================================================================= cache entries
def test_each_language_is_its_own_artifact(seeded):
    svc, run_id, assessment = seeded
    client = _client(svc)
    english = client.get(_url(run_id)).content
    client.get(_url(run_id, lang="mr"))
    client.get(_url(run_id, lang="both"))
    kinds = sorted(a.kind for a in _artifacts(svc, run_id))
    assert kinds == ["html", "html_both", "html_mr"]
    shas = {a.kind: a.sha256 for a in _artifacts(svc, run_id)}
    assert len(set(shas.values())) == 3
    # asking again reuses all three; nothing is regenerated or duplicated
    client.get(_url(run_id)); client.get(_url(run_id, lang="mr")); client.get(_url(run_id, lang="both"))
    assert sorted(a.kind for a in _artifacts(svc, run_id)) == kinds
    # and the English bytes are exactly what they were before any translation existed
    assert client.get(_url(run_id)).content == english == render_html(project(assessment)).encode("utf-8")


def test_translating_never_touches_the_english_artifact(seeded):
    svc, run_id, _ = seeded
    client = _client(svc)
    client.get(_url(run_id))
    before = {a.kind: (a.artifact_id, a.sha256) for a in _artifacts(svc, run_id)}
    client.get(_url(run_id, lang="mr"))
    after = {a.kind: (a.artifact_id, a.sha256) for a in _artifacts(svc, run_id)}
    assert after["html"] == before["html"]


def test_stored_name_records_language_and_catalogue(seeded):
    svc, run_id, assessment = seeded
    client = _client(svc)
    client.get(_url(run_id)); client.get(_url(run_id, lang="mr"))
    names = {a.kind: a.original_filename for a in _artifacts(svc, run_id)}
    assert re.fullmatch(r"nyaysaakshya-[0-9a-f]+\.r[0-9.]+\.v[0-9.]+\.html", names["html"])
    assert re.fullmatch(r"nyaysaakshya-[0-9a-f]+\.r[0-9.]+\.v[0-9.]+\.lmr\.c[0-9a-f]{12}\.html",
                        names["html_mr"])


def test_current_is_language_aware(seeded):
    svc, run_id, _ = seeded
    client = _client(svc)
    client.get(_url(run_id)); client.get(_url(run_id, lang="mr"))
    records = {a.kind: a for a in _artifacts(svc, run_id)}
    assert report_service._is_current(records["html"]) is True
    assert report_service._is_current(records["html_mr"], "mr") is True
    # an English record is not a current Marathi one, and vice versa
    assert report_service._is_current(records["html"], "mr") is False
    assert report_service._is_current(records["html_mr"], "en") is False


def test_changed_catalogue_regenerates_the_translation_but_not_the_english(seeded, monkeypatch):
    """Swapping in reviewed text must not require touching this layer, and must not serve
    a stale draft."""
    svc, run_id, _ = seeded
    client = _client(svc)
    english = client.get(_url(run_id))
    draft = client.get(_url(run_id, lang="mr"))
    ids_before = {a.kind: a.artifact_id for a in _artifacts(svc, run_id)}
    assert 'class="notice draft"' in draft.text

    import copy
    catalogue = i18n.load_catalogue("mr")
    glossary = copy.deepcopy(catalogue.glossary)
    for item in glossary["items"]:
        item["needs_review"] = False
    reviewed = i18n.Catalogue(
        "mr", catalogue.meta,
        [dataclasses.replace(e, needs_review=False) for e in catalogue.entries],
        catalogue.passthrough, glossary)
    assert reviewed.fingerprint != catalogue.fingerprint
    monkeypatch.setattr(i18n, "load_catalogue", lambda language: reviewed)

    approved = client.get(_url(run_id, lang="mr"))
    assert 'class="notice draft"' not in approved.text           # regenerated, not the stale draft
    assert approved.headers["x-translation-status"] == "reviewed"
    ids_after = {a.kind: a.artifact_id for a in _artifacts(svc, run_id) if a.kind in ids_before}
    assert client.get(_url(run_id)).content == english.content   # English bytes unchanged
    html_ids = [a.artifact_id for a in _artifacts(svc, run_id) if a.kind == "html"]
    assert html_ids == [ids_before["html"]]                       # the English artefact was never replaced
    mr_ids = [a.artifact_id for a in _artifacts(svc, run_id) if a.kind == "html_mr"]
    assert len(mr_ids) == 2 and mr_ids[0] == ids_before["html_mr"]


# ================================================================== refusals
@pytest.mark.parametrize("fmt,lang", [("pdf", "mr"), ("pdf", "both"), ("json", "mr"),
                                      ("json", "both")])
def test_pdf_and_json_refuse_translation_instead_of_returning_english(seeded, fmt, lang):
    svc, run_id, _ = seeded
    response = _client(svc).get(_url(run_id, fmt=fmt, lang=lang))
    assert response.status_code == 400
    error = response.json()["error"]
    assert error["code"] == "UNSUPPORTED_REPORT_LANGUAGE"
    assert error["detail"]["format"] == fmt and error["detail"]["language"] == lang
    assert error["detail"]["supported_for_format"] == ["en"]
    assert _artifacts(svc, run_id) == []                          # nothing was generated


@pytest.mark.parametrize("lang", ["fr", "MR", "mr,en", "", "english"])
def test_unknown_language_is_refused(seeded, lang):
    svc, run_id, _ = seeded
    response = _client(svc).get(_url(run_id, lang=lang))
    assert response.status_code == 400
    error = response.json()["error"]
    assert error["code"] == "UNSUPPORTED_REPORT_LANGUAGE"
    assert set(error["detail"]["supported"]) == {"en", "mr", "both"}


def test_pdf_and_json_still_work_in_english_after_a_refusal(seeded):
    svc, run_id, _ = seeded
    client = _client(svc)
    assert client.get(_url(run_id, fmt="json", lang="mr")).status_code == 400
    assert client.get(_url(run_id, fmt="json", lang="en")).status_code == 200
    assert client.get(_url(run_id, fmt="json")).status_code == 200


# ==================================================================== metadata
def test_service_metadata_carries_language_and_translation_status(seeded):
    svc, run_id, assessment = seeded
    reports = ReportService(svc.repo, svc.artifacts)
    _payload, en = reports.get_or_create(run_id, assessment, "html")
    _payload, mr = reports.get_or_create(run_id, assessment, "html", "mr")
    assert en["language"] == "en" and "translation" not in en
    assert mr["language"] == "mr"
    assert mr["filename"].endswith("-mr.html")
    assert mr["sections"][0] == "how-to-read" and mr["sections"][1:] == en["sections"]
    translation = mr["translation"]
    assert translation["status"] == "draft"
    assert translation["pending_review_entries"] > 0
    assert translation["untranslated_strings"] >= 0
    assert translation["authoritative_language"] == "en"
    assert translation["catalogue_version"] and len(translation["catalogue_fingerprint"]) == 12
    # identity is the same in every language; only the artefact differs
    assert mr["assessment_id"] == en["assessment_id"] and mr["capture_id"] == en["capture_id"]
    assert mr["report_sha256"] != en["report_sha256"]


def test_listing_keeps_the_english_items_and_adds_translations(seeded):
    svc, run_id, assessment = seeded
    client = _client(svc)
    body = client.get("/api/v1/analyses/%s/reports" % run_id).json()
    assert [i["format"] for i in body["items"]] == ["html", "pdf", "json"]
    assert {i["language"] for i in body["items"]} == {"en"}
    translations = {t["language"]: t for t in body["translations"]}
    assert set(translations) == {"mr", "both"}
    for lang, item in translations.items():
        assert item["format"] == "html" and item["generated"] is False
        assert item["translation_status"] == "draft" and item["catalogue_version"]
        assert item["filename"].endswith("-%s.html" % lang)

    client.get(_url(run_id, lang="mr"))
    after = {t["language"]: t for t in client.get("/api/v1/analyses/%s/reports" % run_id).json()["translations"]}
    assert after["mr"]["generated"] is True and after["mr"]["current"] is True
    assert after["mr"]["integrity"] == "OK" and after["mr"]["report_sha256"]
    assert after["both"]["generated"] is False
    # the English items are still reported as English and unaffected
    english = {i["format"]: i for i in client.get("/api/v1/analyses/%s/reports" % run_id).json()["items"]}
    assert english["html"]["generated"] is False


def test_unknown_run_still_404s_for_a_translation(seeded):
    svc, _run_id, _ = seeded
    response = _client(svc).get(_url("0" * 32, lang="mr"))
    assert response.status_code == 404
