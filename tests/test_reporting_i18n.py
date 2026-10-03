"""
Report localisation overlay (Marathi): catalogue integrity, matching, completeness, and the
guarantee that the English report is unchanged.

Three tests carry the weight and are worth reading first:

* `test_english_html_is_byte_identical_to_the_committed_demo_reports` -- the overlay and the
  renderer changes must leave English output exactly as it was.
* `test_corpus_report_text_is_fully_translated` -- runs the real pipeline over every capture
  the project holds and fails if any string the report prints has no catalogue entry.
* `test_source_literals_are_covered_or_ignored` -- the same guarantee for rule branches the
  captures never trigger, so a new or reworded English sentence cannot slip through.

Nothing here judges the *quality* of the Marathi. Every entry is still `needs_review`; that
is a property of the data, and the draft notice in the report exists because of it.
"""
import ast
import dataclasses
import glob
import hashlib
import json
import os
import re
import tempfile

import pytest

from nyaysaakshya.reporting import html as H
from nyaysaakshya.reporting import i18n, styles
from nyaysaakshya.reporting.projection import project
from tests.reporting_fixtures import (
    HOSTILE, ai_enabled_assessment, base_assessment, critical_assessment, empty_assessment,
    hostile_assessment, insufficient_evidence,
)

I18N_DIR = "src/nyaysaakshya/reporting/i18n/mr"
DEVANAGARI = re.compile("[ऀ-ॿ]")
PLACEHOLDER = re.compile(r"\{([A-Za-z_][A-Za-z0-9_]*)(?::([a-z]+))?\}")


@pytest.fixture(scope="module")
def catalogue():
    return i18n.load_catalogue("mr")


def _reviewed(catalogue):
    """The same catalogue with every entry and glossary item marked as reviewed."""
    import copy
    glossary = copy.deepcopy(catalogue.glossary)
    for item in glossary["items"]:
        item["needs_review"] = False
    return i18n.Catalogue(
        "mr", catalogue.meta,
        [dataclasses.replace(e, needs_review=False) for e in catalogue.entries],
        catalogue.passthrough, glossary)


def _catalogue(entries, patterns=()):
    """A small in-memory catalogue for testing the matcher in isolation."""
    compiled = [i18n._compile("t.%d" % n, en, mr, True) for n, (en, mr) in enumerate(entries)]
    import re as _re
    return i18n.Catalogue("mr", {}, compiled,
                          [(i, _re.compile(p), "test") for i, p in patterns], {})


def _all_fixtures():
    return [base_assessment(), critical_assessment(), insufficient_evidence(),
            ai_enabled_assessment(), empty_assessment()]


# ============================================================ catalogue integrity
def test_catalogue_loads_and_is_not_trivial(catalogue):
    assert catalogue.language == "mr"
    assert len(catalogue.entries) >= 500
    assert catalogue.version


def test_every_entry_declares_its_review_status(catalogue):
    # The loader already requires a boolean; this pins the contract for reviewers: approving
    # an entry means setting needs_review to false, and nothing else about it changes.
    for entry in catalogue.entries:
        assert isinstance(entry.needs_review, bool), entry.entry_id
    glossary_pending = sum(1 for i in catalogue.glossary['items'] if i['needs_review'])
    assert catalogue.pending_review == sum(e.needs_review for e in catalogue.entries) + glossary_pending


def test_ids_and_english_specs_are_unique(catalogue):
    ids = [e.entry_id for e in catalogue.entries]
    assert len(ids) == len(set(ids))
    english = [e.en for e in catalogue.entries]
    assert len(english) == len(set(english)), "two entries translate the same English"


def test_translations_use_ascii_digits_only():
    for path in glob.glob(os.path.join(I18N_DIR, "*.json")):
        text = open(path, encoding="utf-8").read()
        assert not re.search("[०-९]", text), "%s contains Devanagari digits" % path


def test_every_translation_is_actually_marathi(catalogue):
    for entry in catalogue.entries:
        residue = PLACEHOLDER.sub("", entry.target)
        residue = re.sub(r"[\W\d_]", "", residue, flags=re.UNICODE)
        if not residue:
            continue                       # pure placeholders / punctuation, e.g. "{marker} {sev}"
        assert DEVANAGARI.search(entry.target), \
            "%s has no Devanagari text: %r" % (entry.entry_id, entry.target)


def test_target_placeholders_are_a_subset_of_the_english_ones(catalogue):
    for entry in catalogue.entries:
        en_names = {m.group(1) for m in PLACEHOLDER.finditer(entry.en)}
        mr_names = {m.group(1) for m in PLACEHOLDER.finditer(entry.target)}
        assert mr_names <= en_names, entry.entry_id


def test_passthrough_patterns_each_state_why(catalogue):
    assert catalogue.passthrough
    for ident, pattern, why in catalogue.passthrough:
        assert ident and why and hasattr(pattern, "fullmatch")


def test_glossary_is_complete_and_static(catalogue):
    g = catalogue.glossary
    for key in ("title", "lead", "draft_notice", "english_banner"):
        assert g[key]["en"] and g[key]["mr"], key
    assert len(g["items"]) >= 10
    ids = [item["id"] for item in g["items"]]
    assert len(ids) == len(set(ids))
    for item in g["items"]:
        assert item["term"]["en"] and item["term"]["mr"] and item["en"] and item["mr"]
        assert isinstance(item["needs_review"], bool)
        assert DEVANAGARI.search(item["mr"])
        assert not re.search("[०-९]", item["mr"])


def test_catalogue_is_shipped_as_package_data():
    assert "i18n" in open("pyproject.toml", encoding="utf-8").read()


def test_malformed_catalogue_is_rejected_at_load_time():
    with pytest.raises(i18n.CatalogueError):
        i18n._compile("x", "{a:bogus} text", "{a} पाठ", True)            # unknown mode
    with pytest.raises(i18n.CatalogueError):
        i18n._compile("x", "{a} text", "{b} पाठ", True)                   # target invents {b}
    with pytest.raises(i18n.CatalogueError):
        _catalogue([("same", "एक"), ("same", "दोन")])                      # duplicate English


# ================================================================= matching engine
def test_exact_entry_beats_template():
    cat = _catalogue([("{x} item", "{x} बाब"), ("1 item", "एक बाब")])
    assert cat.translate("1 item") == "एक बाब"
    assert cat.translate("2 item") == "2 बाब"


def test_passthrough_returns_the_text_unchanged():
    cat = _catalogue([], [("hex", r"^[0-9a-f]{8,}$")])
    assert cat.translate("deadbeef00") == "deadbeef00"
    assert cat.translate("not hex words") is None


def test_numeric_placeholder_only_matches_numbers():
    cat = _catalogue([("{n:num} sessions", "{n} सत्रे")])
    assert cat.translate("12 sessions") == "12 सत्रे"
    assert cat.translate("12.5 sessions") == "12.5 सत्रे"
    assert cat.translate("many sessions") is None


def test_tr_placeholder_requires_a_translatable_value():
    cat = _catalogue([("severity {s:tr}", "तीव्रता {s}"), ("HIGH", "उच्च")])
    assert cat.translate("severity HIGH") == "तीव्रता उच्च"
    assert cat.translate("severity UNKNOWN_THING") is None       # no half-translated sentence


def test_opt_placeholder_translates_when_it_can_and_passes_through_when_it_cannot():
    cat = _catalogue([("saw {v:opt}", "आढळले {v}"), ("'true'", "'होय'")])
    assert cat.translate("saw 'true'") == "आढळले 'होय'"
    assert cat.translate("saw TLS1.2") == "आढळले TLS1.2"


def test_marker_placeholder_carries_the_severity_marker():
    cat = _catalogue([("{m:mk} {s:tr}", "{m} {s}"), ("HIGH", "उच्च")])
    assert cat.translate("[!! ] HIGH") == "[!! ] उच्च"


def test_lists_are_translated_item_by_item():
    cat = _catalogue([("A", "अ"), ("B", "ब")])
    assert cat.translate("A; B") == "अ; ब"
    assert cat.translate(" · ".join(["A", "B"])) == "अ · ब"
    assert cat.translate("A; Z") is None


def test_sentences_built_from_fragments_are_translated_piecewise():
    cat = _catalogue([("first part", "पहिला भाग"), ("; second part", "; दुसरा भाग"),
                      ("done", "पूर्ण")], [("dot", r"^\.$")])
    assert cat.translate("first part; second part") == "पहिला भाग; दुसरा भाग"
    assert cat.translate("first part. done.") == "पहिला भाग. पूर्ण."


def test_unknown_text_is_not_translated():
    assert _catalogue([("known", "ज्ञात")]).translate("unknown") is None


def test_translation_is_deterministic(catalogue):
    probe = "[!! ] HIGH"
    assert {catalogue.translate(probe) for _ in range(5)} == {"[!! ] उच्च"}


# ============================================================== real catalogue
@pytest.mark.parametrize("english,marathi", [
    ("CRITICAL", "अतिगंभीर"),
    ("INSUFFICIENT EVIDENCE", "अपुरा पुरावा"),
    ("[!!!] CRITICAL", "[!!!] अतिगंभीर"),
    ("Executive summary", "कार्यकारी सारांश"),
])
def test_known_strings_translate(catalogue, english, marathi):
    assert catalogue.translate(english) == marathi


@pytest.mark.parametrize("data", ["44 / 100", "22.15", "100.0%", "smtp", "NIST SP 800-52r2",
                                  "SEC-CERT-001", "2026-10-03T05:59:25Z", "10.0.0.6:25",
                                  "F2-group-damped", "ce5377348e22ad92c33d705e31388944bad8224534d478c38b57a75d3ba4a501"])
def test_data_values_pass_through_unchanged(catalogue, data):
    assert catalogue.translate(data) == data


def test_scores_and_hashes_keep_ascii_digits(catalogue):
    out = catalogue.translate("100.0% (12 of 12 sessions assessed)")
    assert out and "12" in out and not re.search("[०-९]", out)


# ============================================================ enum completeness
def _enum_labels():
    """Every English label the report can print for a closed enumeration."""
    from nyaysaakshya.analysis import model as am
    from nyaysaakshya.evidence import states as es
    from nyaysaakshya.posture import model as pm
    from nyaysaakshya.session import model as sm
    labels = set()
    labels.update(styles.POSTURE_LABEL.values())
    labels.update(styles.SEVERITY_ORDER)
    labels.update(styles.STATUS_LABEL.get(m.value, m.value) for m in am.FindingStatus)
    labels.update(styles.CERTAINTY_LABEL.get(m.value, m.value) for m in pm.EvidenceCertainty)
    labels.update(styles.OBSERVABILITY_LABEL.get(m.value, m.value) for m in pm.Observability)
    labels.update(styles.ABSTENTION_LABEL.get(m.value, m.value) for m in pm.AbstentionReason)
    labels.update(m.value.replace("_", " ") for m in es.EvidenceState)
    labels.update(m.value.replace("_", " ") for m in sm.Completeness)
    labels.update(styles.humanise(m.value) for m in pm.IssueClass)
    labels.update(styles.humanise(m.value) for m in pm.FactKind)
    labels.update(styles.humanise(m.value) for m in pm.RiskDimension)
    labels.update(m.value.replace("_", " ") for m in pm.RiskDimension)
    return sorted(labels)


def test_every_enum_label_has_a_marathi_rendering(catalogue):
    missing = [label for label in _enum_labels() if catalogue.translate(label) is None]
    assert missing == [], missing


# ========================================================== English is unchanged
def test_english_overlay_is_the_identity():
    doc = project(base_assessment())
    out, report = i18n.localize(doc, "en")
    assert out is doc and report.complete


def test_english_html_is_byte_identical_to_the_committed_demo_reports():
    """The demo reports were rendered before this feature existed. They must still match."""
    pairs = sorted(glob.glob("demo/reports/*.json"))
    assert pairs, "demo reports missing"
    for path in pairs:
        expected = open(path[:-5] + ".html", "rb").read()
        actual = H.render_html(project(json.load(open(path, encoding="utf-8")))).encode("utf-8")
        assert actual == expected, "English HTML changed for %s" % os.path.basename(path)


def test_render_localized_english_is_render_html():
    doc = project(critical_assessment())
    html, report = H.render_localized(doc, "en")
    assert html == H.render_html(doc) and report.complete


def test_unsupported_language_is_refused():
    with pytest.raises(ValueError):
        H.render_localized(project(base_assessment()), "fr")


# ================================================================== the overlay
@pytest.mark.parametrize("assessment", _all_fixtures(),
                         ids=["base", "critical", "insufficient", "ai", "empty"])
def test_overlay_preserves_structure_and_raw_enums(assessment):
    doc = project(assessment)
    out, _report = i18n.localize(doc, "mr")
    assert out.metadata == doc.metadata
    assert out.overall_posture == doc.overall_posture
    assert out.sections[0].section_id == "how-to-read"
    assert [s.section_id for s in out.sections[1:]] == [s.section_id for s in doc.sections]
    for before, after in zip(doc.sections, out.sections[1:]):
        assert [len(t.rows) for t in before.tables] == [len(t.rows) for t in after.tables]
        assert [len(t.columns) for t in before.tables] == [len(t.columns) for t in after.tables]
        assert len(before.facts) == len(after.facts)
        assert [b.severity for b in before.bars] == [b.severity for b in after.bars]
        assert [b.fraction for b in before.bars] == [b.fraction for b in after.bars]


def test_overlay_never_changes_a_number_or_an_identifier():
    assessment = critical_assessment()
    doc = project(assessment)
    out, _ = i18n.localize(doc, "mr")
    assert out.score_text == doc.score_text
    ids = (assessment["assessment_id"], assessment["capture_id"])
    html, _ = H.render_localized(doc, "mr")
    for ident in ids:
        assert ident in html


def test_untranslated_text_stays_english_and_is_reported():
    doc = project(base_assessment())
    doc.sections[0].paragraphs.append("A sentence nobody wrote a translation for.")
    out, report = i18n.localize(doc, "mr")
    assert "A sentence nobody wrote a translation for." in out.sections[1].paragraphs
    assert "A sentence nobody wrote a translation for." in report.untranslated
    assert not report.complete


def test_how_to_read_block_is_static():
    first = i18n.localize(project(base_assessment()), "mr")[0].sections[0]
    second = i18n.localize(project(critical_assessment()), "mr")[0].sections[0]
    assert (first.title, first.lead, first.facts, first.notices) == \
           (second.title, second.lead, second.facts, second.notices)
    assert len(first.facts) >= 10


# ==================================================================== HTML output
def _ids(html):
    return re.findall(r'\bid="([^"]+)"', html)


def test_marathi_html_is_marked_up_for_devanagari():
    html, report = H.render_localized(project(critical_assessment()), "mr")
    assert html.startswith("<!DOCTYPE html>") and '<html lang="mr">' in html
    assert "<h1>न्यायसाक्ष्य</h1>" in html
    assert "Nirmala UI" in html and "letter-spacing: 0" in html
    assert 'id="how-to-read"' in html
    assert len(_ids(html)) == len(set(_ids(html)))


def test_marathi_html_shows_the_draft_notice_while_entries_are_unreviewed(catalogue):
    assert catalogue.pending_review > 0          # the state this phase ships in
    html, _ = H.render_localized(project(base_assessment()), "mr")
    assert 'class="notice draft"' in html


def test_draft_notice_disappears_only_when_every_entry_and_glossary_item_is_reviewed(catalogue, monkeypatch):
    reviewed = _reviewed(catalogue)
    assert reviewed.pending_review == 0
    monkeypatch.setattr(i18n, "load_catalogue", lambda language: reviewed)
    html, _ = H.render_localized(project(base_assessment()), "mr")
    assert 'class="notice draft"' not in html


def test_both_stacks_marathi_first_then_the_english_original():
    doc = project(critical_assessment())
    html, report = H.render_localized(doc, "both")
    assert html.count("<!DOCTYPE html>") == 1 and html.count("</html>") == 1
    assert html.index('id="mr-report"') < html.index('id="en-report"')
    assert len(_ids(html)) == len(set(_ids(html)))
    assert 'id="mr-executive-summary"' in html and 'id="en-executive-summary"' in html
    assert "English original — authoritative copy" in html
    # the English part is the ordinary English report, only wrapped and given distinct ids
    assert H._wrap(doc, lambda text: text, "en-") in html


def test_both_html_is_complete_and_deterministic():
    doc = project(critical_assessment())
    first, _ = H.render_localized(doc, "both")
    second, _ = H.render_localized(doc, "both")
    assert first == second
    assert hashlib.sha256(first.encode()).hexdigest() == hashlib.sha256(second.encode()).hexdigest()


def test_severity_colour_survives_translation():
    html, _ = H.render_localized(project(critical_assessment()), "mr")
    assert re.search(r'class="sev sev-(CRITICAL|HIGH|MEDIUM)"', html)


def test_hostile_assessment_text_is_escaped_in_marathi_output():
    html, _ = H.render_localized(project(hostile_assessment()), "both")
    assert "<script" not in html.lower()
    assert "onerror=alert" not in html or "&lt;" in html
    assert HOSTILE not in html


# ========================================================= completeness (the guards)
def _tshark_available():
    try:
        from nyaysaakshya.dissect import TsharkAdapter
        TsharkAdapter().version()
        return True
    except Exception:
        return False


def _capture_paths():
    found = sorted({os.path.realpath(p) for p in
                    glob.glob("research/experiments/**/*.pcap", recursive=True)
                    + glob.glob("frontend/public/test_caps/*.pcap")})
    return found


@pytest.mark.skipif(not _tshark_available(), reason="tshark not installed")
@pytest.mark.skipif(not _capture_paths(), reason="capture corpus absent")
def test_corpus_report_text_is_fully_translated():
    """Every string the report prints, for every real capture, has a catalogue entry."""
    from nyaysaakshya.backend.service import AnalysisService
    service = AnalysisService(tempfile.mkdtemp())
    captures = _capture_paths()
    gaps = {}
    for index, path in enumerate(captures):
        for ai in ((False, True) if index % 9 == 0 else (False,)):   # include the ML-lane text
            submitted = service.submit_path(path, ai_enabled=ai)
            assessment = service.get_assessment(submitted.run.run_id)
            assessment = assessment.get("assessment", assessment)
            html, report = H.render_localized(project(assessment), "mr")
            for text in report.untranslated:
                gaps.setdefault(text, os.path.basename(path))
            assert not re.search("[०-९]", html), "Devanagari digit in %s" % path
    assert gaps == {}, "report text with no Marathi entry:\n" + "\n".join(
        "  [%s] %s" % (cap, text[:160]) for text, cap in gaps.items())


def _scan_source(path):
    """English literals of >=3 words that can reach a report, as the catalogue was built."""
    skip_attrs = {"description", "standards", "rule_id", "name"}
    tree = ast.parse(open(path, encoding="utf-8").read())
    skip, out = set(), []

    def mark(node):
        for child in ast.walk(node):
            skip.add(id(child))

    class Scan(ast.NodeVisitor):
        def __init__(self):
            self.stack = []

        def _doc(self, n):
            if n.body and isinstance(n.body[0], ast.Expr) and \
                    isinstance(getattr(n.body[0], "value", None), ast.Constant):
                skip.add(id(n.body[0].value))

        def visit_Module(self, n):
            self._doc(n); self.generic_visit(n)

        def visit_ClassDef(self, n):
            self._doc(n); self.stack.append("class"); self.generic_visit(n); self.stack.pop()

        def visit_FunctionDef(self, n):
            self._doc(n); self.stack.append("def"); self.generic_visit(n); self.stack.pop()

        visit_AsyncFunctionDef = visit_FunctionDef

        def visit_Raise(self, n):
            mark(n)

        def visit_Assign(self, n):
            names = [t.id for t in n.targets if isinstance(t, ast.Name)]
            if any(x in skip_attrs for x in names) and self.stack and self.stack[-1] == "class":
                mark(n.value)
            self.generic_visit(n)

        def visit_keyword(self, k):
            if k.arg in skip_attrs:
                mark(k.value)
            self.generic_visit(k)

        def _emit(self, n):
            if id(n) in skip:
                return
            if isinstance(n, ast.Constant) and isinstance(n.value, str):
                text = n.value
            elif isinstance(n, ast.JoinedStr):
                text = "".join(v.value if isinstance(v, ast.Constant) else "{}" for v in n.values)
            else:
                return
            text = re.sub(r"\s+", " ", text).strip()
            if len(text.split()) >= 3 and not re.fullmatch(r"[A-Z0-9_ ./:-]+", text):
                out.append((n.lineno, text))

        def visit_Constant(self, n):
            self._emit(n)

        def visit_JoinedStr(self, n):
            self._emit(n)
            for v in n.values:
                mark(v)
            self.generic_visit(n)

    Scan().visit(tree)
    return out


_SKELETON = re.compile(r"\{[A-Za-z0-9_]*(?::[a-z]+)?\}")


def _anonymous(text):
    """Placeholder names differ between source f-strings and catalogue specs; shapes must not."""
    return _SKELETON.sub("{}", text)


def _covered_by_catalogue(text, catalogue):
    skeleton = _SKELETON
    key = skeleton.sub("{}", text)
    specs = [e.en for e in catalogue.entries]
    if text in specs or key in {skeleton.sub("{}", s) for s in specs}:
        return True
    fragments = [f.strip() for f in skeleton.split(text) if len(f.strip()) >= 3]
    return any(fragments and all(f in spec for f in fragments) for spec in specs)


def test_source_literals_are_covered_or_ignored(catalogue):
    """A reworded or newly added rule sentence fails here instead of shipping in English."""
    config = catalogue.meta["source_scan"]
    ignored = {_anonymous(item["en"]) for item in config["ignore"]}
    uncovered = []
    for module in config["modules"]:
        for line, text in _scan_source("src/nyaysaakshya/" + module):
            if _anonymous(text) in ignored or _covered_by_catalogue(text, catalogue):
                continue
            uncovered.append("%s:%d %s" % (module, line, text[:150]))
    assert uncovered == [], "source text with no catalogue entry:\n" + "\n".join(uncovered)


def test_ignored_source_literals_still_exist_and_say_why(catalogue):
    config = catalogue.meta["source_scan"]
    present = set()
    for module in config["modules"]:
        present.update(_anonymous(text)
                       for _line, text in _scan_source("src/nyaysaakshya/" + module))
    for item in config["ignore"]:
        assert item["why"], item
        assert _anonymous(item["en"]) in present, "stale ignore entry: %r" % item["en"]


def test_one_unreviewed_glossary_item_keeps_the_draft_notice(catalogue, monkeypatch):
    partly = _reviewed(catalogue)
    partly.glossary["items"][0]["needs_review"] = True
    assert partly.pending_review == 1
    monkeypatch.setattr(i18n, "load_catalogue", lambda language: partly)
    html, _ = H.render_localized(project(base_assessment()), "mr")
    assert 'class="notice draft"' in html
