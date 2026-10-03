"""
The reviewer handoff: export the Marathi catalogue as a spreadsheet, take corrections back.

Everything here runs on a *copy* of the catalogue in a temporary directory, so no test can
change the shipped translations. The properties worth knowing about:

* a reviewer with no engineering background gets one row per piece of text, with where it
  appears, the English, the draft, and the meaning of every `{...}` part -- never raw JSON;
* a correction is accepted only if it still matches the catalogue it was exported from, and
  only after it passes validation (placeholders, digits, fragment edges);
* "OK as is" and "Changed" make a row reviewed; anything else stays a draft; and once everything
  is reviewed the draft notice disappears from translated reports by itself.
"""
import csv
import hashlib
import importlib.util
import io
import json
import os
import shutil
import sys
import zipfile

import pytest

from nyaysaakshya.reporting import i18n

CATALOGUE = "src/nyaysaakshya/reporting/i18n/mr"


def _load_tool():
    spec = importlib.util.spec_from_file_location("catalogue_review", "tools/catalogue_review.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module          # dataclasses resolves string annotations through sys.modules
    spec.loader.exec_module(module)
    return module


cr = _load_tool()


@pytest.fixture
def work(tmp_path):
    """A private copy of the catalogue the tool can freely modify."""
    target = str(tmp_path / "mr")
    shutil.copytree(CATALOGUE, target)
    return target


def _digest(directory):
    h = hashlib.sha256()
    for name in sorted(os.listdir(directory)):
        h.update(name.encode()); h.update(open(os.path.join(directory, name), "rb").read())
    return h.hexdigest()


def _rows_by_key(directory):
    return {r.key: r for r in cr.build_rows(directory)}


def _pick(rows, predicate, count=1):
    found = [r for r in rows if predicate(r)]
    assert len(found) >= count, "no suitable row"
    return found[:count]


def _decide(rows, decisions):
    """decisions: {key: (decision, corrected, notes)} applied onto fresh copies of the rows."""
    out = []
    for r in rows:
        decision, corrected, notes = decisions.get(r.key, ("", "", ""))
        out.append(cr.Row(key=r.key, where=r.where, english=r.english, marathi=r.marathi,
                          decision=decision, corrected=corrected, notes=notes))
    return out


# ================================================================== the data behind it
def test_every_entry_carries_reviewer_context():
    for name in sorted(os.listdir(CATALOGUE)):
        if name in cr.SPECIAL_FILES or not name.endswith(".json"):
            continue
        for entry in json.load(open(os.path.join(CATALOGUE, name), encoding="utf-8"))["entries"]:
            for key in ("area", "kind", "shown_in"):
                assert entry.get(key, "").strip(), "%s is missing '%s'" % (entry["id"], key)


def test_examples_translate_with_the_current_catalogue():
    catalogue = i18n.load_catalogue("mr")
    examples = json.load(open(os.path.join(CATALOGUE, "examples.json"), encoding="utf-8"))["examples"]
    assert len(examples) >= 15
    ids = {e.entry_id for e in catalogue.entries}
    for entry_id, english in examples.items():
        assert entry_id in ids
        assert catalogue.translate(english) is not None


# ======================================================================= the export
def test_one_row_per_unreviewed_item_in_reading_order(work):
    rows = cr.build_rows(work)
    catalogue = i18n.load_catalogue_from(work)
    glossary_rows = sum(1 for r in rows if r.key.startswith("glossary:"))
    assert len(rows) == len([e for e in catalogue.entries if e.needs_review]) + glossary_rows
    assert len({r.key for r in rows}) == len(rows)
    assert rows[0].key.startswith("glossary:"), "the 'how to read' block is section 1"
    for r in rows:
        assert r.where and r.english and r.marathi, r.key


def test_reviewer_never_sees_internal_markup(work):
    for r in cr.build_rows(work):
        assert ":tr}" not in r.english and ":num}" not in r.english and ":opt}" not in r.english, r.key
        assert ":mk}" not in r.english, r.key


def test_templated_rows_explain_their_fill_in_parts_and_show_an_example(work):
    rows = cr.build_rows(work)
    templated = [r for r in rows if "{" in r.english]
    assert len(templated) >= 80
    for r in templated:
        assert r.fillin, r.key
        assert r.example_en and r.example_mr, r.key
        assert "{" not in r.example_en.replace("{…}", ""), "an example still has an unfilled part: " + r.key
    real = [r for r in templated if not r.example_en.startswith("(sample values)")]
    assert len(real) >= 15                          # real sentences from real captures where they exist


def test_plain_text_rows_have_no_fill_in_help(work):
    plain = _pick(cr.build_rows(work), lambda r: "{" not in r.english and not r.key.startswith("glossary:"))[0]
    assert plain.fillin == "" and plain.example_en == ""


def test_already_reviewed_rows_are_left_out_unless_asked(work):
    rows = cr.build_rows(work)
    key = _pick(rows, lambda r: not r.key.startswith("glossary:"))[0].key
    report = cr.apply_review(_decide(rows, {key: ("OK as is", "", "")}), work, apply=True)
    assert report.approved == 1
    assert key not in {r.key for r in cr.build_rows(work)}
    assert key in {r.key for r in cr.build_rows(work, include_reviewed=True)}


# ===================================================================== xlsx and csv
def test_xlsx_is_a_valid_workbook_with_the_expected_sheets(work, tmp_path):
    [path] = [p for p in cr.export(work, str(tmp_path / "out"), "xlsx") if p.endswith(".xlsx")]
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None
        names = set(z.namelist())
        assert {"[Content_Types].xml", "xl/workbook.xml", "xl/styles.xml",
                "xl/worksheets/sheet1.xml", "xl/worksheets/sheet2.xml", "xl/worksheets/sheet3.xml"} <= names
        review = z.read("xl/worksheets/sheet2.xml").decode("utf-8")
        assert '<dataValidation type="list"' in review and "OK as is,Changed,Not sure" in review
        assert 'state="frozen"' in review and "<autoFilter" in review
        assert "_xlnm._FilterDatabase" in z.read("xl/workbook.xml").decode("utf-8")
    sheets = cr.read_xlsx(path)
    assert list(sheets) == ["Read me first", "Review", "Terms"]
    assert sheets["Review"][0] == cr.HEADERS
    assert len(sheets["Review"]) == len(cr.build_rows(work)) + 1


def test_xlsx_round_trips_marathi_text_exactly(work, tmp_path):
    cr.export(work, str(tmp_path / "out"), "xlsx")
    review = cr.read_xlsx(str(tmp_path / "out" / "marathi-review.xlsx"))["Review"]
    expected = {r.key: r for r in cr.build_rows(work)}
    seen = 0
    for line in review[1:]:
        row = expected[line[cr.COL["Technical ID (do not edit)"]]]
        assert line[cr.COL["Draft Marathi"]] == row.marathi
        assert line[cr.COL["English (original)"]] == row.english
        seen += 1
    assert seen == len(expected)


def test_xlsx_export_is_deterministic(work, tmp_path):
    a = cr.export(work, str(tmp_path / "a"), "xlsx")[0]
    b = cr.export(work, str(tmp_path / "b"), "xlsx")[0]
    assert open(a, "rb").read() == open(b, "rb").read()


def test_csv_opens_in_excel_and_has_the_same_rows(work, tmp_path):
    paths = cr.export(work, str(tmp_path / "out"), "csv")
    raw = open(paths[0], "rb").read()
    assert raw.startswith(b"\xef\xbb\xbf"), "needs a UTF-8 byte-order mark so Excel reads Devanagari"
    rows = list(csv.reader(io.StringIO(raw.decode("utf-8-sig"))))
    assert rows[0] == cr.HEADERS and len(rows) == len(cr.build_rows(work)) + 1


def test_reader_understands_files_resaved_by_excel(tmp_path):
    """Excel stores text in sharedStrings.xml; the tool writes inline strings. Handle both."""
    path = str(tmp_path / "excel.xlsx")
    main = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("xl/workbook.xml", '<workbook xmlns="%s" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
                   '<sheets><sheet name="Review" sheetId="1" r:id="rId1"/></sheets></workbook>' % main)
        z.writestr("xl/_rels/workbook.xml.rels", '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                   '<Relationship Id="rId1" Type="x" Target="/xl/worksheets/sheet1.xml"/></Relationships>')
        z.writestr("xl/sharedStrings.xml", '<sst xmlns="%s"><si><t>Hello</t></si>'
                   '<si><r><t>मराठी </t></r><r><t>मजकूर</t></r></si></sst>' % main)
        z.writestr("xl/worksheets/sheet1.xml", '<worksheet xmlns="%s"><sheetData><row r="1">'
                   '<c r="A1" t="s"><v>0</v></c><c r="C1" t="s"><v>1</v></c><c r="D1"><v>42</v></c></row></sheetData></worksheet>' % main)
    assert cr.read_xlsx(path)["Review"] == [["Hello", "", "मराठी मजकूर", "42"]]


# ======================================================================== importing
def _sample(work):
    rows = cr.build_rows(work)
    plain = [r for r in rows if not r.key.startswith("glossary:") and "{" not in r.english
             and r.english == r.english.strip() and not r.english.startswith((".", ";", ","))]
    return rows, plain


def test_dry_run_changes_nothing(work):
    rows, plain = _sample(work)
    before = _digest(work)
    decided = _decide(rows, {plain[0].key: ("OK as is", "", ""), plain[1].key: ("Changed", "नवीन मजकूर", "")})
    report = cr.apply_review(decided, work, apply=False)
    assert report.ok and report.approved == 1 and report.changed == 1 and not report.applied
    assert _digest(work) == before
    assert "DRY RUN" in cr.format_report(report, dry_run=True)


def test_apply_reviews_ok_and_changed_rows_and_leaves_the_rest_a_draft(work):
    rows, plain = _sample(work)
    a, b, c, d = plain[:4]
    pending_before = i18n.load_catalogue_from(work).pending_review
    decided = _decide(rows, {a.key: ("OK as is", "", ""), b.key: ("Changed", "सुधारित मजकूर", "better word"),
                             c.key: ("Not sure", "", "is this the right term?")})
    report = cr.apply_review(decided, work, apply=True)
    assert report.ok and report.applied
    assert (report.approved, report.changed, report.unsure) == (1, 1, 1)
    assert report.untouched == len(rows) - 3
    after = i18n.load_catalogue_from(work)
    by_id = {e.entry_id: e for e in after.entries}
    assert by_id[a.key].target == a.marathi and by_id[a.key].needs_review is False
    assert by_id[b.key].target == "सुधारित मजकूर" and by_id[b.key].needs_review is False
    assert by_id[c.key].target == c.marathi and by_id[c.key].needs_review is True
    assert by_id[d.key].needs_review is True
    assert after.pending_review == pending_before - 2 and report.pending_after == pending_before - 2
    assert ("%s" % c.key, "is this the right term?") in report.notes
    assert i18n.load_catalogue_from(CATALOGUE).fingerprint != after.fingerprint   # cached translations will regenerate


def test_a_changed_correction_is_what_the_report_prints(work, monkeypatch):
    from nyaysaakshya.reporting.html import render_localized
    from nyaysaakshya.reporting.projection import project
    from tests.reporting_fixtures import critical_assessment
    rows, _ = _sample(work)
    target = _pick(rows, lambda r: r.english == "Executive summary")[0]
    cr.apply_review(_decide(rows, {target.key: ("Changed", "कार्यकारी निष्कर्ष-सारांश", "")}), work, apply=True)
    corrected = i18n.load_catalogue_from(work)
    monkeypatch.setattr(i18n, "load_catalogue", lambda language: corrected)
    html, _report = render_localized(project(critical_assessment()), "mr")
    assert "कार्यकारी निष्कर्ष-सारांश" in html and "कार्यकारी सारांश" not in html


def test_reviewing_everything_removes_the_draft_notice(work, monkeypatch):
    from nyaysaakshya.reporting.html import render_localized
    from nyaysaakshya.reporting.projection import project
    from tests.reporting_fixtures import critical_assessment
    rows = cr.build_rows(work)
    report = cr.apply_review(_decide(rows, {r.key: ("OK as is", "", "") for r in rows}), work, apply=True)
    assert report.ok and report.approved == len(rows) and report.pending_after == 0
    reviewed = i18n.load_catalogue_from(work)
    assert reviewed.pending_review == 0
    assert json.load(open(os.path.join(work, "meta.json"), encoding="utf-8"))["status"].startswith("Reviewed")
    monkeypatch.setattr(i18n, "load_catalogue", lambda language: reviewed)
    html, _ = render_localized(project(critical_assessment()), "mr")
    assert 'class="notice draft"' not in html


def test_nothing_is_written_if_any_row_has_a_problem(work):
    rows, plain = _sample(work)
    templated = _pick(rows, lambda r: "{count}" in r.english)[0]
    before = _digest(work)
    decided = _decide(rows, {plain[0].key: ("OK as is", "", ""),
                             templated.key: ("Changed", "{cout} प्रमाणपत्रे", "")})       # typo in a {…} part
    report = cr.apply_review(decided, work, apply=True)
    assert not report.ok and not report.applied
    assert any("unknown {…}" in e for e in report.errors)
    assert _digest(work) == before                                  # the good row was not applied either


@pytest.mark.parametrize("decision,corrected,fragment", [
    ("Changed", "", "corrected Marathi is empty"),
    ("Maybe later", "", "unknown decision"),
    ("Changed", "बंद { कंस", "curly brackets"),
])
def test_bad_rows_are_rejected_with_a_reason(work, decision, corrected, fragment):
    rows, plain = _sample(work)
    report = cr.apply_review(_decide(rows, {plain[0].key: (decision, corrected, "")}), work, apply=True)
    assert not report.ok and any(fragment in e for e in report.errors), report.errors


def test_a_correction_without_the_decision_is_treated_as_changed_with_a_warning(work):
    rows, plain = _sample(work)
    report = cr.apply_review(_decide(rows, {plain[0].key: ("", "फक्त दुरुस्ती", "")}), work, apply=True)
    assert report.ok and report.changed == 1
    assert any("treated as Changed" in w for w in report.warnings)


def test_devanagari_digits_are_converted_to_ordinary_digits(work):
    rows, plain = _sample(work)
    report = cr.apply_review(_decide(rows, {plain[0].key: ("Changed", "एकूण १२ सत्रे", "")}), work, apply=True)
    assert report.ok and any("digits" in w for w in report.warnings)
    entry = {e.entry_id: e for e in i18n.load_catalogue_from(work).entries}[plain[0].key]
    assert entry.target == "एकूण 12 सत्रे"


def test_a_missing_number_is_a_warning_not_a_failure(work):
    rows, _ = _sample(work)
    templated = _pick(rows, lambda r: "{count}" in r.english)[0]
    report = cr.apply_review(_decide(rows, {templated.key: ("Changed", "प्रमाणपत्रे काढली", "")}), work, apply=True)
    assert report.ok and any("{count}" in w for w in report.warnings)


def test_sentence_pieces_keep_their_leading_mark_and_spacing(work):
    rows, _ = _sample(work)
    semicolon = _pick(rows, lambda r: r.english.startswith("; "))[0]
    bad = cr.apply_review(_decide(rows, {semicolon.key: ("Changed", "प्रत्येक प्रमाणपत्र जोडलेले आहे", "")}), work, apply=True)
    assert not bad.ok and any("must start with ';'" in e for e in bad.errors)

    good = cr.apply_review(_decide(rows, {semicolon.key: ("Changed", ";  प्रत्येक प्रमाणपत्र जोडलेले आहे", "")}), work, apply=True)
    assert good.ok
    spaced = _pick(rows, lambda r: r.english.startswith(" "))[0]       # " […truncated]"
    cr.apply_review(_decide(rows, {spaced.key: ("Changed", "[…छाटले]", "")}), work, apply=True)   # reviewer's spreadsheet trimmed the space
    entry = {e.entry_id: e for e in i18n.load_catalogue_from(work).entries}[spaced.key]
    assert entry.target.startswith(" ")


def test_stale_rows_are_skipped_not_applied(work):
    rows, plain = _sample(work)
    target = plain[0]
    # the catalogue moves on after the sheet was exported
    for name in cr._entry_files(work):
        path = os.path.join(work, name); doc = json.load(open(path, encoding="utf-8"))
        for e in doc["entries"]:
            if e["id"] == target.key:
                e["mr"] = e["mr"] + " (बदललेले)"
                json.dump(doc, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    report = cr.apply_review(_decide(rows, {target.key: ("OK as is", "", "")}), work, apply=True)
    assert report.ok and report.approved == 0 and len(report.stale) == 1
    assert {e.entry_id: e for e in i18n.load_catalogue_from(work).entries}[target.key].needs_review is True


def test_glossary_rows_round_trip(work):
    rows = cr.build_rows(work)
    text_row = _pick(rows, lambda r: r.key.startswith("glossary:item:") and r.key.endswith(":text"))[0]
    banner = _pick(rows, lambda r: r.key == "glossary:english_banner")[0]
    report = cr.apply_review(_decide(rows, {text_row.key: ("Changed", "नवीन स्पष्टीकरण", ""),
                                            banner.key: ("Changed", "इंग्रजी मूळ — प्रमाण", "")}), work, apply=True)
    assert report.ok
    glossary = i18n.load_catalogue_from(work).glossary
    item_id = text_row.key.split(":")[2]
    item = next(i for i in glossary["items"] if i["id"] == item_id)
    assert item["mr"] == "नवीन स्पष्टीकरण" and item["needs_review"] is False
    assert glossary["english_banner"]["mr"] == "इंग्रजी मूळ — प्रमाण"


# ===================================================================== end to end
def _edit_workbook(src, dst, decisions, term_comment=None):
    """What a reviewer does: open the workbook, fill columns E/F/G, save it again."""
    sheets = cr.read_xlsx(src)
    review = sheets["Review"]
    key_col = cr.COL["Technical ID (do not edit)"]
    for line in review[1:]:
        if line[key_col] in decisions:
            decision, corrected, notes = decisions[line[key_col]]
            line[cr.COL["Your decision"]], line[cr.COL["Your corrected Marathi"]], line[cr.COL["Notes or questions"]] = decision, corrected, notes
    terms = sheets["Terms"]
    if term_comment:
        terms[1] = (terms[1] + [""] * 5)[:5]; terms[1][3], terms[1][4] = term_comment
    cr.write_xlsx(dst, [{"name": n, "rows": [[(c, cr.S_WRAP) for c in row] for row in rows]} for n, rows in sheets.items()])


def test_full_loop_through_a_real_workbook_and_the_cli(work, tmp_path, capsys):
    out = tmp_path / "out"
    xlsx = cr.export(work, str(out), "xlsx")[0]
    rows, plain = _sample(work)
    edited = str(tmp_path / "reviewed.xlsx")
    _edit_workbook(xlsx, edited, {plain[0].key: ("OK as is", "", ""),
                                  plain[1].key: ("Changed", "वेगळा शब्द", "सोपा शब्द वापरा"),
                                  plain[2].key: ("Not sure", "", "what does this mean?")},
                   term_comment=("अधिक सोपा शब्द", "plain word please"))
    assert cr.main(["--catalogue-dir", work, "import", edited]) == 0               # dry run
    printed = capsys.readouterr().out
    assert "DRY RUN" in printed and "what does this mean?" in printed and "TERM PREFERENCES" in printed
    assert cr.main(["--catalogue-dir", work, "import", edited, "--apply"]) == 0
    assert "APPLIED" in capsys.readouterr().out
    by_id = {e.entry_id: e for e in i18n.load_catalogue_from(work).entries}
    assert by_id[plain[1].key].target == "वेगळा शब्द" and by_id[plain[2].key].needs_review is True
    assert cr.main(["--catalogue-dir", work, "status"]) == 0
    assert "still need review" in capsys.readouterr().out


def test_cli_reports_problems_and_a_bad_file(work, tmp_path, capsys):
    xlsx = cr.export(work, str(tmp_path / "out"), "xlsx")[0]
    rows, plain = _sample(work)
    edited = str(tmp_path / "bad.xlsx")
    _edit_workbook(xlsx, edited, {plain[0].key: ("Changed", "", "")})
    assert cr.main(["--catalogue-dir", work, "import", edited, "--apply"]) == 1
    assert "NOT APPLIED" in capsys.readouterr().out
    notes = tmp_path / "not-a-workbook.xlsx"; notes.write_bytes(b"this is not a zip")
    assert cr.main(["--catalogue-dir", work, "import", str(notes)]) == 2
    assert "cannot read" in capsys.readouterr().err


def test_csv_can_be_imported_too(work, tmp_path):
    csv_path = cr.export(work, str(tmp_path / "out"), "csv")[0]
    rows, plain = _sample(work)
    table = list(csv.reader(io.StringIO(open(csv_path, encoding="utf-8-sig").read())))
    key_col = cr.COL["Technical ID (do not edit)"]
    for line in table[1:]:
        if line[key_col] == plain[0].key:
            line[cr.COL["Your decision"]] = "OK as is"
    edited = tmp_path / "reviewed.csv"
    with open(edited, "w", encoding="utf-8-sig", newline="") as handle:
        csv.writer(handle).writerows(table)
    read_rows, _ = cr.read_review_file(str(edited))
    report = cr.apply_review(read_rows, work, apply=True)
    assert report.ok and report.approved == 1


def test_a_csv_not_saved_as_utf8_gets_a_helpful_message(tmp_path):
    bad = tmp_path / "ansi.csv"
    bad.write_bytes("a,b\n\xe0\xa4\x85".encode("latin-1"))
    with pytest.raises(ValueError):
        cr.read_review_file(str(bad))
