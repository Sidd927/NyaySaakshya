#!/usr/bin/env python3
"""Hand the Marathi translation catalogue to a reviewer as a spreadsheet, and take the
corrections back. No third-party libraries; the .xlsx is written and read with the standard
library.

    python3 tools/catalogue_review.py export                 # -> i18n-review/marathi-review.xlsx (+ .csv)
    python3 tools/catalogue_review.py import reviewed.xlsx   # dry run: shows what would change
    python3 tools/catalogue_review.py import reviewed.xlsx --apply
    python3 tools/catalogue_review.py status

The reviewer sees, for each piece of report text: where it appears (in plain words), the
English original, the draft Marathi, a real or sample example, and what the ``{...}`` parts are.
They choose "OK as is", "Changed" (and type the corrected Marathi) or "Not sure". They never
see or edit JSON.

Importing is conservative: a row is applied only if it still matches the catalogue it was
exported from, and a correction is validated (placeholders, digits, fragment edges) before it
is accepted. Rows marked "OK as is" or "Changed" become reviewed (``needs_review`` false);
everything else stays a draft. Once every entry and glossary item is reviewed, the draft
notice disappears from translated reports by itself and cached translations regenerate.
"""
from __future__ import annotations

import argparse
import csv
import datetime
import io
import json
import os
import re
import sys
import zipfile
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from xml.etree import ElementTree as ET
from xml.sax.saxutils import escape

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CATALOGUE = os.path.join(REPO, "src", "nyaysaakshya", "reporting", "i18n", "mr")
DEFAULT_OUT = os.path.join(REPO, "i18n-review")

PLACEHOLDER = re.compile(r"\{([A-Za-z_][A-Za-z0-9_]*)(?::([a-z]+))?\}")
DEVANAGARI = re.compile("[ऀ-ॿ]")
DEV_DIGITS = str.maketrans("०१२३४५६७८९", "0123456789")
SPECIAL_FILES = {"meta.json", "glossary.json", "passthrough.json", "examples.json"}

DECISION_OK, DECISION_CHANGED, DECISION_UNSURE = "OK as is", "Changed", "Not sure"
DECISIONS = (DECISION_OK, DECISION_CHANGED, DECISION_UNSURE)

HEADERS = ["No.", "Where it appears", "English (original)", "Draft Marathi", "Your decision",
           "Your corrected Marathi", "Notes or questions", "What the {…} parts are",
           "Example (English)", "Example (draft Marathi)", "Technical ID (do not edit)"]
COL = {name: i for i, name in enumerate(HEADERS)}

#: Order in which report text is shown to the reviewer: how the report reads, top to bottom.
FILE_ORDER = ["report.json", "chrome.json", "labels.json", "findings.json", "crosssession.json",
              "remediation.json", "posture.json", "ml.json", "crypto.json", "extra.json"]
SECTION_ORDER = ["Top of every report", "Executive summary", "Assessment scope", "Overall security posture",
                 "Evidence coverage", "Protocol posture", "Prioritised findings", "Detailed findings",
                 "Standards basis", "Remediation guidance", "AI / ML transparency",
                 "Abstentions and observability limits", "Assessment limitations",
                 "Evidence and provenance", "Methodology"]

FILLIN_WORDS = {
    "num": "a number — keep it exactly as it is",
    "mk": "a severity marker such as [!! ] — keep it exactly as it is",
    "tr": "a phrase that is translated separately — keep the {…} in your sentence",
    "opt": "a value (translated if it is a known word) — keep the {…}",
    None: "a value filled in automatically — keep the {…} exactly as written",
}


# =============================================================================== catalogue
@dataclass
class Row:
    key: str                         # technical id used to write the correction back
    where: str
    english: str
    marathi: str
    fillin: str = ""
    example_en: str = ""
    example_mr: str = ""
    sort: Tuple = ()
    decision: str = ""
    corrected: str = ""
    notes: str = ""


def _read(path: str) -> Any:
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def _write(path: str, data: Any) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=1)
        handle.write("\n")


def _entry_files(directory: str) -> List[str]:
    names = [n for n in os.listdir(directory) if n.endswith(".json") and n not in SPECIAL_FILES]
    return sorted(names, key=lambda n: (FILE_ORDER.index(n) if n in FILE_ORDER else 99, n))


def _import_catalogue_module():
    sys.path.insert(0, os.path.join(REPO, "src"))
    from nyaysaakshya.reporting import i18n
    return i18n


def display_spec(spec: str) -> str:
    """The English as a reviewer should see it: ``{count:num}`` is shown as ``{count}``."""
    return PLACEHOLDER.sub(lambda m: "{%s}" % m.group(1), spec)


def describe_fillins(spec: str) -> str:
    seen, lines = set(), []
    for match in PLACEHOLDER.finditer(spec):
        name, mode = match.group(1), match.group(2)
        if name in seen:
            continue
        seen.add(name)
        lines.append("{%s} = %s" % (name, FILLIN_WORDS.get(mode, FILLIN_WORDS[None])))
    return "\n".join(lines)


_SAMPLE = {"num": "3", "mk": "[!! ]"}
_SAMPLE_BY_NAME = [("name", "mail.example.com"), ("role", "leaf"), ("when", "2026-01-15 10:30:00 UTC"),
                   ("reference", "2026-01-15 10:30:00 UTC"), ("not_", "Jan 1 00:00:00 2025 GMT"),
                   ("version", "1.2"), ("sev", "HIGH"), ("hash", "SHA-1"), ("state", "upgrading")]


def _sample_value(name: str, mode: Optional[str]) -> str:
    if mode in _SAMPLE:
        return _SAMPLE[mode]
    for needle, value in _SAMPLE_BY_NAME:
        if needle in name:
            return value
    return "‹value›"


def illustrate(entry: Dict[str, Any], real: Optional[str], catalogue) -> Tuple[str, str]:
    """(English example, draft Marathi example): a real sentence if one exists, else samples."""
    if real:
        return real, catalogue.translate(real) or ""
    if not PLACEHOLDER.search(entry["en"]):
        return "", ""
    values = {m.group(1): _sample_value(m.group(1), m.group(2)) for m in PLACEHOLDER.finditer(entry["en"])}
    english = PLACEHOLDER.sub(lambda m: values[m.group(1)], entry["en"])
    translated = {n: (catalogue.translate(v) or v) for n, v in values.items()}
    marathi = PLACEHOLDER.sub(lambda m: translated.get(m.group(1), values.get(m.group(1), "")), entry["mr"])
    return "(sample values) " + english, "(sample values) " + marathi


def build_rows(directory: str = DEFAULT_CATALOGUE, include_reviewed: bool = False) -> List[Row]:
    """One row per piece of report text, in the order a reader meets it."""
    i18n = _import_catalogue_module()
    catalogue = i18n.load_catalogue_from(directory)
    examples = _read(os.path.join(directory, "examples.json")).get("examples", {}) \
        if os.path.exists(os.path.join(directory, "examples.json")) else {}
    rows: List[Row] = []

    glossary = _read(os.path.join(directory, "glossary.json"))
    for index, (key, label, where_kind) in enumerate([
            ("title", glossary["title"], "Heading of the 'how to read this report' block"),
            ("lead", glossary["lead"], "Line under that heading"),
            ("draft_notice", glossary["draft_notice"], "Banner at the very top while the translation is a draft"),
            ("english_banner", glossary["english_banner"], "Label above the English copy in the bilingual report")]):
        rows.append(Row("glossary:" + key, "How to read this report (section 1) — " + where_kind,
                        label["en"], label["mr"], sort=(0, index, 0)))
    for index, notice in enumerate(glossary.get("notices", [])):
        rows.append(Row("glossary:notice:%d" % index, "How to read this report (section 1) — Highlighted notice",
                        notice["en"], notice["mr"], sort=(0, 10 + index, 0)))
    for index, item in enumerate(glossary["items"]):
        if item.get("needs_review", True) or include_reviewed:
            rows.append(Row("glossary:item:%s:term" % item["id"], "How to read this report (section 1) — term in the list",
                            item["term"]["en"], item["term"]["mr"], sort=(0, 20 + index, 0)))
            rows.append(Row("glossary:item:%s:text" % item["id"], "How to read this report (section 1) — explanation of: %s" % item["term"]["en"],
                            item["en"], item["mr"], sort=(0, 20 + index, 1)))

    for fnum, name in enumerate(_entry_files(directory), start=1):
        for index, entry in enumerate(_read(os.path.join(directory, name))["entries"]):
            if not (entry["needs_review"] or include_reviewed):
                continue
            shown = entry.get("shown_in", "")
            where = "%s\nPart of: %s\nSeen in: %s" % (entry.get("kind", ""), entry.get("area", ""), shown)
            fillin = describe_fillins(entry["en"])
            example_en, example_mr = illustrate(entry, examples.get(entry["id"]), catalogue)
            section_rank = SECTION_ORDER.index(shown.split(" / ")[0]) if shown.split(" / ")[0] in SECTION_ORDER else 50
            rows.append(Row(entry["id"], where.strip(), display_spec(entry["en"]), entry["mr"], fillin, example_en, example_mr,
                            sort=(1, fnum, section_rank, entry.get("area", ""), index)))
    rows.sort(key=lambda r: r.sort)
    return rows


# ============================================================================== xlsx output
_STYLES_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
<fonts count="4">
<font><sz val="11"/><name val="Calibri"/></font>
<font><b/><sz val="11"/><name val="Calibri"/></font>
<font><sz val="9"/><color rgb="FF7F7F7F"/><name val="Calibri"/></font>
<font><b/><sz val="16"/><name val="Calibri"/></font>
</fonts>
<fills count="5">
<fill><patternFill patternType="none"/></fill>
<fill><patternFill patternType="gray125"/></fill>
<fill><patternFill patternType="solid"><fgColor rgb="FFD9E2F3"/><bgColor indexed="64"/></patternFill></fill>
<fill><patternFill patternType="solid"><fgColor rgb="FFF2F2F2"/><bgColor indexed="64"/></patternFill></fill>
<fill><patternFill patternType="solid"><fgColor rgb="FFFFF9DB"/><bgColor indexed="64"/></patternFill></fill>
</fills>
<borders count="2">
<border><left/><right/><top/><bottom/><diagonal/></border>
<border><left style="thin"><color rgb="FFBFBFBF"/></left><right style="thin"><color rgb="FFBFBFBF"/></right><top style="thin"><color rgb="FFBFBFBF"/></top><bottom style="thin"><color rgb="FFBFBFBF"/></bottom><diagonal/></border>
</borders>
<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>
<cellXfs count="8">
<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>
<xf numFmtId="0" fontId="1" fillId="2" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment vertical="center" wrapText="1"/></xf>
<xf numFmtId="0" fontId="0" fillId="3" borderId="1" xfId="0" applyFill="1" applyBorder="1" applyAlignment="1"><alignment vertical="top" wrapText="1"/></xf>
<xf numFmtId="0" fontId="0" fillId="4" borderId="1" xfId="0" applyFill="1" applyBorder="1" applyAlignment="1"><alignment vertical="top" wrapText="1"/></xf>
<xf numFmtId="0" fontId="2" fillId="0" borderId="0" xfId="0" applyFont="1" applyAlignment="1"><alignment vertical="top"/></xf>
<xf numFmtId="0" fontId="3" fillId="0" borderId="0" xfId="0" applyFont="1"/>
<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0" applyAlignment="1"><alignment vertical="top" wrapText="1"/></xf>
<xf numFmtId="0" fontId="1" fillId="0" borderId="0" xfId="0" applyFont="1" applyAlignment="1"><alignment vertical="top" wrapText="1"/></xf>
</cellXfs>
</styleSheet>"""
S_DEFAULT, S_HEADER, S_READONLY, S_INPUT, S_TECH, S_TITLE, S_WRAP, S_BOLD = range(8)

_ILLEGAL_XML = re.compile("[\x00-\x08\x0b\x0c\x0e-\x1f]")


def _col_letter(index: int) -> str:
    letters = ""
    index += 1
    while index:
        index, rem = divmod(index - 1, 26)
        letters = chr(65 + rem) + letters
    return letters


def _col_index(letters: str) -> int:
    n = 0
    for ch in letters:
        n = n * 26 + (ord(ch) - 64)
    return n - 1


def _cell_xml(row: int, col: int, value: Any, style: int) -> str:
    ref = "%s%d" % (_col_letter(col), row)
    if value is None or value == "":
        return '<c r="%s" s="%d"/>' % (ref, style)
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return '<c r="%s" s="%d"><v>%s</v></c>' % (ref, style, value)
    text = escape(_ILLEGAL_XML.sub("", str(value)))
    return '<c r="%s" s="%d" t="inlineStr"><is><t xml:space="preserve">%s</t></is></c>' % (ref, style, text)


def _sheet_xml(sheet: Dict[str, Any]) -> str:
    rows, widths = sheet["rows"], sheet.get("widths", [])
    out = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
           '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">']
    last_col = max((len(r) for r in rows), default=1)
    out.append('<dimension ref="A1:%s%d"/>' % (_col_letter(last_col - 1), max(len(rows), 1)))
    pane = ('<pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" state="frozen"/>'
            if sheet.get("freeze") else "")
    out.append('<sheetViews><sheetView workbookViewId="0">%s</sheetView></sheetViews>' % pane)
    out.append('<sheetFormatPr defaultRowHeight="15"/>')
    if widths:
        out.append("<cols>%s</cols>" % "".join(
            '<col min="%d" max="%d" width="%s" customWidth="1"/>' % (i + 1, i + 1, w) for i, w in enumerate(widths)))
    out.append("<sheetData>")
    for r, row in enumerate(rows, start=1):
        cells = "".join(_cell_xml(r, c, v, s) for c, (v, s) in enumerate(row))
        out.append('<row r="%d">%s</row>' % (r, cells))
    out.append("</sheetData>")
    if sheet.get("filter") and rows:
        out.append('<autoFilter ref="A1:%s%d"/>' % (_col_letter(last_col - 1), len(rows)))
    validation = sheet.get("validation")
    if validation:
        col, first, last, options = validation
        out.append('<dataValidations count="1"><dataValidation type="list" allowBlank="1" showErrorMessage="1" '
                   'errorTitle="Please choose one" error="Choose: %s" sqref="%s%d:%s%d">'
                   '<formula1>"%s"</formula1></dataValidation></dataValidations>'
                   % (escape(", ".join(options)), col, first, col, last, escape(",".join(options))))
    out.append('<pageMargins left="0.7" right="0.7" top="0.75" bottom="0.75" header="0.3" footer="0.3"/>')
    out.append("</worksheet>")
    return "".join(out)


def write_xlsx(path: str, sheets: List[Dict[str, Any]]) -> None:
    """Write a workbook. Each sheet: name, rows ([(value, style)...]), widths, freeze, filter, validation."""
    names = [s["name"] for s in sheets]
    content_types = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                     '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                     '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
                     '<Default Extension="xml" ContentType="application/xml"/>'
                     '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
                     '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
                     + "".join('<Override PartName="/xl/worksheets/sheet%d.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>' % (i + 1)
                               for i in range(len(sheets))) + "</Types>")
    rels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
            "</Relationships>")
    defined = "".join(
        '<definedName name="_xlnm._FilterDatabase" localSheetId="%d" hidden="1">\'%s\'!$A$1:$%s$%d</definedName>'
        % (i, escape(sheet["name"]), _col_letter(max(len(r) for r in sheet["rows"]) - 1), len(sheet["rows"]))
        for i, sheet in enumerate(sheets) if sheet.get("filter") and sheet["rows"])
    workbook = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
                'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>'
                + "".join('<sheet name="%s" sheetId="%d" r:id="rId%d"/>' % (escape(n, {'"': "&quot;"}), i + 1, i + 1)
                          for i, n in enumerate(names)) + "</sheets>"
                + ("<definedNames>%s</definedNames>" % defined if defined else "") + "</workbook>")
    wb_rels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
               '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
               + "".join('<Relationship Id="rId%d" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet%d.xml"/>' % (i + 1, i + 1)
                         for i in range(len(sheets)))
               + '<Relationship Id="rId%d" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>' % (len(sheets) + 1)
               + "</Relationships>")
    # fixed timestamp and sorted parts: the same catalogue gives the same file bytes
    stamp = (2026, 1, 1, 0, 0, 0)
    parts = [("[Content_Types].xml", content_types), ("_rels/.rels", rels), ("xl/workbook.xml", workbook),
             ("xl/_rels/workbook.xml.rels", wb_rels), ("xl/styles.xml", _STYLES_XML)]
    parts += [("xl/worksheets/sheet%d.xml" % (i + 1), _sheet_xml(s)) for i, s in enumerate(sheets)]
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, data in parts:
            info = zipfile.ZipInfo(name, date_time=stamp)
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, data.encode("utf-8"))


# ============================================================================== xlsx input
_NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
       "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
       "rel": "http://schemas.openxmlformats.org/package/2006/relationships"}


def _text_of(element) -> str:
    return "".join(t.text or "" for t in element.iter("{%s}t" % _NS["m"]))


def read_xlsx(path: str) -> Dict[str, List[List[str]]]:
    """Read every sheet as rows of strings. Handles files re-saved by Excel, Numbers or Sheets."""
    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())
        shared: List[str] = []
        if "xl/sharedStrings.xml" in names:
            for si in ET.fromstring(archive.read("xl/sharedStrings.xml")).findall("m:si", _NS):
                shared.append(_text_of(si))
        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        rel_targets = {r.get("Id"): r.get("Target") for r in
                       ET.fromstring(archive.read("xl/_rels/workbook.xml.rels")).findall("rel:Relationship", _NS)}
        sheets: Dict[str, List[List[str]]] = {}
        for sheet in workbook.find("m:sheets", _NS).findall("m:sheet", _NS):
            target = rel_targets[sheet.get("{%s}id" % _NS["r"])]
            target = target.lstrip("/")
            part = target if target.startswith("xl/") else "xl/" + target
            rows: List[List[str]] = []
            for row in ET.fromstring(archive.read(part)).find("m:sheetData", _NS).findall("m:row", _NS):
                cells: Dict[int, str] = {}
                for cell in row.findall("m:c", _NS):
                    col = _col_index(re.match(r"[A-Z]+", cell.get("r")).group(0))
                    kind = cell.get("t")
                    if kind == "inlineStr":
                        value = _text_of(cell.find("m:is", _NS)) if cell.find("m:is", _NS) is not None else ""
                    elif kind == "s":
                        v = cell.find("m:v", _NS)
                        value = shared[int(v.text)] if v is not None and v.text else ""
                    else:
                        v = cell.find("m:v", _NS)
                        value = v.text if v is not None and v.text is not None else ""
                    cells[col] = value
                width = (max(cells) + 1) if cells else 0
                rows.append([cells.get(i, "") for i in range(width)])
            sheets[sheet.get("name")] = rows
    return sheets


# ================================================================================ the sheets
def _readme_rows(row_count: int, catalogue_version: str, fingerprint: str) -> List[List[Tuple[Any, int]]]:
    lines = [
        ("Marathi translation review — NyaySaakshya report", S_TITLE),
        ("", S_WRAP),
        ("What this is", S_BOLD),
        ("NyaySaakshya writes a security report in English. A Marathi version of that report has been drafted by a "
         "machine, and nobody has checked it yet. Your job is to check it and correct anything that is wrong, unclear "
         "or unnatural. You do not need any technical knowledge: each row shows where the text appears in the report, "
         "the English original, and the draft Marathi.", S_WRAP),
        ("", S_WRAP),
        ("What to do — sheet 'Review'", S_BOLD),
        ("1.  Read the English (column C) and the draft Marathi (column D). Use 'Where it appears' (column B) and the "
         "example columns (I and J) if the sentence is unclear on its own.", S_WRAP),
        ("2.  In 'Your decision' (column E), choose one: OK as is  /  Changed  /  Not sure.", S_WRAP),
        ("3.  If you chose Changed, type the corrected Marathi in column F. Write the whole corrected text, not just the "
         "changed words.", S_WRAP),
        ("4.  Use column G for any question or comment. It is read by the team even if you leave the decision blank.", S_WRAP),
        ("5.  You can skip rows. Anything you leave blank or mark 'Not sure' stays a draft.", S_WRAP),
        ("", S_WRAP),
        ("Please do NOT change", S_BOLD),
        ("•  Anything inside curly brackets, like {count} or {role}. It is replaced by a number or a name when the "
         "report is made. Keep it in your sentence, wherever it reads best in Marathi. Column H explains each one.", S_WRAP),
        ("•  Numbers. Please write them with ordinary digits (0 1 2 3 …) and not Devanagari digits, so that scores and "
         "IDs can be copied exactly.", S_WRAP),
        ("•  Technical names that are kept in English on purpose: TLS, STARTTLS, SMTP, IMAP, POP3, RSA, SHA-1, RFC 8446, "
         "NIST SP 800-52r2, rule codes such as SEC-CERT-001.", S_WRAP),
        ("•  Columns A, B, C, D, H, I, J and K. Only columns E, F and G are for you.", S_WRAP),
        ("", S_WRAP),
        ("Rows that start with ';' or '.' or a space", S_BOLD),
        ("Some report sentences are built from several pieces. A piece that starts with ';' or '.' continues an earlier "
         "piece. Keep that first mark in your corrected text, and write it so that it reads on naturally after the "
         "piece before it.", S_WRAP),
        ("", S_WRAP),
        ("Other sheets", S_BOLD),
        ("'Terms' lists the main words used throughout (for example 'evidence', 'abstention'). If you prefer a different "
         "Marathi word for any of them, write it there. The team will change it everywhere in one go.", S_WRAP),
        ("", S_WRAP),
        ("The English report is always the authoritative one. This Marathi version is a translation aid.", S_WRAP),
        ("", S_WRAP),
        ("When you are finished", S_BOLD),
        ("Save the file in the same format (.xlsx — please do not convert it to another format) and send it back.", S_WRAP),
        ("", S_WRAP),
        ("%d rows to review. Catalogue version %s (fingerprint %s). Exported %s."
         % (row_count, catalogue_version, fingerprint[:12], datetime.date.today().isoformat()), S_TECH),
    ]
    return [[(text, style)] for text, style in lines]


def _terms_rows(meta: Dict[str, Any]) -> List[List[Tuple[Any, int]]]:
    header = [(h, S_HEADER) for h in ("English term", "Marathi term used in the draft", "What it means",
                                      "Your preferred Marathi term (if different)", "Comments")]
    rows = [header]
    for term in meta.get("terminology", []):
        rows.append([(term["en"], S_READONLY), (term["mr"], S_READONLY), (term.get("note", ""), S_READONLY),
                     ("", S_INPUT), ("", S_INPUT)])
    return rows


def export(directory: str, out_dir: str, fmt: str = "both", include_reviewed: bool = False) -> List[str]:
    i18n = _import_catalogue_module()
    catalogue = i18n.load_catalogue_from(directory)
    meta = _read(os.path.join(directory, "meta.json"))
    rows = build_rows(directory, include_reviewed)
    os.makedirs(out_dir, exist_ok=True)
    written: List[str] = []

    table: List[List[Any]] = [HEADERS[:]]
    for number, r in enumerate(rows, start=1):
        table.append([number, r.where, r.english, r.marathi, "", "", "", r.fillin, r.example_en, r.example_mr, r.key])

    if fmt in ("xlsx", "both"):
        styled = [[(h, S_HEADER) for h in HEADERS]]
        for line in table[1:]:
            styled.append([(line[0], S_READONLY), (line[1], S_READONLY), (line[2], S_READONLY), (line[3], S_READONLY),
                           ("", S_INPUT), ("", S_INPUT), ("", S_INPUT), (line[7], S_READONLY), (line[8], S_READONLY),
                           (line[9], S_READONLY), (line[10], S_TECH)])
        sheets = [
            {"name": "Read me first", "rows": _readme_rows(len(rows), catalogue.version, catalogue.fingerprint),
             "widths": [110]},
            {"name": "Review", "rows": styled, "freeze": True, "filter": True,
             "widths": [6, 34, 48, 48, 16, 48, 32, 34, 40, 40, 30],
             "validation": ("E", 2, max(len(styled), 2), DECISIONS)},
            {"name": "Terms", "rows": _terms_rows(meta), "freeze": True, "widths": [26, 30, 40, 36, 40]},
        ]
        path = os.path.join(out_dir, "marathi-review.xlsx")
        write_xlsx(path, sheets)
        written.append(path)
    if fmt in ("csv", "both"):
        path = os.path.join(out_dir, "marathi-review.csv")
        with open(path, "w", encoding="utf-8-sig", newline="") as handle:     # BOM: Excel reads Devanagari correctly
            writer = csv.writer(handle)
            for line in table:
                writer.writerow(line)
        written.append(path)
    return written


# ================================================================================== importing
@dataclass
class ImportReport:
    approved: int = 0
    changed: int = 0
    unsure: int = 0
    untouched: int = 0
    stale: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    notes: List[Tuple[str, str]] = field(default_factory=list)
    term_requests: List[str] = field(default_factory=list)
    applied: bool = False
    pending_after: Optional[int] = None

    @property
    def ok(self) -> bool:
        return not self.errors


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").replace("\xa0", " ")).strip()


def clean_corrected(english: str, corrected: str) -> Tuple[str, List[str], List[str]]:
    """Normalise and validate a reviewer's correction. Returns (text, warnings, errors)."""
    warnings: List[str] = []
    errors: List[str] = []
    text = corrected.replace("\xa0", " ").replace("​", "").replace("﻿", "")
    if DEVANAGARI.search(text) and re.search("[०-९]", text):
        text = text.translate(DEV_DIGITS)
        warnings.append("Devanagari digits were converted to ordinary digits")
    if text.count("{") != text.count("}"):
        errors.append("the curly brackets { } do not match up")
    spec = {m.group(1) for m in PLACEHOLDER.finditer(english)}
    used = {m.group(1) for m in PLACEHOLDER.finditer(text)}
    if used - spec:
        errors.append("unknown {…} part(s) %s — only %s may be used" %
                      (", ".join("{%s}" % n for n in sorted(used - spec)),
                       ", ".join("{%s}" % n for n in sorted(spec)) or "none"))
    for m in PLACEHOLDER.finditer(english):
        if m.group(2) == "num" and m.group(1) not in used:
            warnings.append("the number {%s} is not in the corrected text — check that this is intended" % m.group(1))
    # pieces of longer sentences keep their edges
    lead = re.match(r"^\s*[.;,:]", english)
    if lead:
        mark = lead.group(0).strip()
        if not text.lstrip().startswith(mark):
            errors.append("this piece must start with '%s', like the English" % mark)
    if english != english.lstrip() and text == text.lstrip():
        text = " " + text
    if english != english.rstrip() and text == text.rstrip():
        text = text + " "
    if not (english.lstrip().startswith(tuple(".;,:")) or english != english.lstrip()):
        text = text.lstrip()
    if english == english.rstrip():
        text = text.rstrip()
    if not DEVANAGARI.search(text) and DEVANAGARI.search(english) is None and PLACEHOLDER.sub("", english).strip(" .;,:") != "":
        warnings.append("the corrected text has no Marathi letters")
    return text, warnings, errors


def _parse_decision(value: str) -> Optional[str]:
    v = _norm(value).lower()
    if not v:
        return None
    if v in ("ok", "ok as is", "approved", "approve", "good", "yes", "correct"):
        return DECISION_OK
    if v in ("changed", "change", "corrected", "edited", "fixed"):
        return DECISION_CHANGED
    if v in ("not sure", "unsure", "question", "?", "unsure / question", "maybe"):
        return DECISION_UNSURE
    return "?" + value


def rows_from_sheet(sheet: List[List[str]]) -> List[Row]:
    header_at = next((i for i, row in enumerate(sheet) if "Technical ID (do not edit)" in [c.strip() for c in row]), None)
    if header_at is None:
        raise ValueError("this does not look like the review sheet (no 'Technical ID (do not edit)' column)")
    names = [c.strip() for c in sheet[header_at]]
    idx = {n: names.index(n) for n in HEADERS if n in names}
    for needed in ("Technical ID (do not edit)", "English (original)", "Draft Marathi", "Your decision",
                   "Your corrected Marathi", "Notes or questions"):
        if needed not in idx:
            raise ValueError("the column '%s' is missing" % needed)
    rows: List[Row] = []
    for line in sheet[header_at + 1:]:
        get = lambda name: line[idx[name]] if idx[name] < len(line) else ""
        key = get("Technical ID (do not edit)").strip()
        if not key:
            continue
        rows.append(Row(key=key, where="", english=get("English (original)"), marathi=get("Draft Marathi"),
                        decision=get("Your decision"), corrected=get("Your corrected Marathi"),
                        notes=get("Notes or questions")))
    return rows


def read_review_file(path: str) -> Tuple[List[Row], List[str]]:
    """Rows from an .xlsx or .csv, plus any comments the reviewer wrote on the Terms sheet."""
    term_requests: List[str] = []
    if path.lower().endswith(".xlsx"):
        sheets = read_xlsx(path)
        if "Review" not in sheets:
            raise ValueError("the workbook has no 'Review' sheet")
        rows = rows_from_sheet(sheets["Review"])
        for line in sheets.get("Terms", [])[1:]:
            preferred = line[3].strip() if len(line) > 3 else ""
            comment = line[4].strip() if len(line) > 4 else ""
            if preferred or comment:
                term_requests.append("%s (draft: %s) — preferred: %s%s" % (
                    line[0], line[1] if len(line) > 1 else "", preferred or "—", "; comment: " + comment if comment else ""))
        return rows, term_requests
    raw = open(path, "rb").read()
    for encoding in ("utf-8-sig", "utf-16"):
        try:
            text = raw.decode(encoding)
            break
        except UnicodeError:
            continue
    else:
        raise ValueError("this CSV is not saved as UTF-8; in Excel use 'Save as → CSV UTF-8', or send the .xlsx")
    return rows_from_sheet(list(csv.reader(io.StringIO(text)))), term_requests


def _locate(directory: str) -> Tuple[Dict[str, Tuple[str, int]], Dict[str, Dict[str, Any]], Dict[str, Any]]:
    """entry id -> (file, index); the loaded files; the glossary."""
    files: Dict[str, Dict[str, Any]] = {}
    where: Dict[str, Tuple[str, int]] = {}
    for name in _entry_files(directory):
        files[name] = _read(os.path.join(directory, name))
        for i, e in enumerate(files[name]["entries"]):
            where[e["id"]] = (name, i)
    return where, files, _read(os.path.join(directory, "glossary.json"))


def _glossary_target(glossary: Dict[str, Any], key: str):
    """(container, field) for a glossary row id, or None."""
    parts = key.split(":")
    if parts[:2] == ["glossary", "item"] and len(parts) == 4:
        item = next((i for i in glossary["items"] if i["id"] == parts[2]), None)
        if item is None:
            return None
        return (item["term"], "mr", item) if parts[3] == "term" else (item, "mr", item)
    if parts[:2] == ["glossary", "notice"] and len(parts) == 3 and parts[2].isdigit():
        notices = glossary.get("notices", [])
        return (notices[int(parts[2])], "mr", None) if int(parts[2]) < len(notices) else None
    if len(parts) == 2 and parts[1] in ("title", "lead", "draft_notice", "english_banner"):
        return (glossary[parts[1]], "mr", None)
    return None


def apply_review(rows: List[Row], directory: str, apply: bool = False,
                 term_requests: Optional[List[str]] = None) -> ImportReport:
    report = ImportReport(term_requests=list(term_requests or []))
    where, files, glossary = _locate(directory)
    changed_files = set()
    glossary_changed = False

    for row in rows:
        decision = _parse_decision(row.decision)
        if row.notes.strip():
            report.notes.append((row.key, row.notes.strip()))
        if decision and decision.startswith("?"):
            report.errors.append("%s: unknown decision %r — use OK as is, Changed or Not sure" % (row.key, decision[1:]))
            continue
        corrected = row.corrected.strip()
        if corrected and decision in (None, DECISION_OK):
            report.warnings.append("%s: a corrected text was given but the decision was not 'Changed'; treated as Changed" % row.key)
            decision = DECISION_CHANGED
        if decision == DECISION_CHANGED and not corrected:
            report.errors.append("%s: marked 'Changed' but the corrected Marathi is empty" % row.key)
            continue
        if decision is None:
            report.untouched += 1
            continue
        if decision == DECISION_UNSURE:
            report.unsure += 1
            continue

        # locate the thing to update, and make sure the sheet is not older than the catalogue
        target = None
        review_flag = None
        if row.key.startswith("glossary:"):
            found = _glossary_target(glossary, row.key)
            if found is None:
                report.stale.append("%s: no longer in the catalogue" % row.key)
                continue
            container, field_name, review_flag = found
            current_mr = container[field_name]
            current_en = container.get("en", "")
            spec = current_en
            target = ("glossary", container, field_name, review_flag)
        elif row.key in where:
            name, index = where[row.key]
            entry = files[name]["entries"][index]
            current_mr, current_en, spec = entry["mr"], entry["en"], entry["en"]
            target = (name, entry, "mr", entry)
        else:
            report.stale.append("%s: no longer in the catalogue" % row.key)
            continue
        if _norm(display_spec(row.english)) != _norm(display_spec(current_en)) or _norm(row.marathi) != _norm(current_mr):
            report.stale.append("%s: the catalogue has changed since this sheet was exported — row skipped" % row.key)
            continue

        new_text = current_mr
        if decision == DECISION_CHANGED:
            new_text, warns, errs = clean_corrected(spec, corrected)
            report.warnings.extend("%s: %s" % (row.key, w) for w in warns)
            if errs:
                report.errors.extend("%s: %s" % (row.key, e) for e in errs)
                continue
        scope, container, field_name, flag_holder = target
        container[field_name] = new_text
        if flag_holder is not None:
            flag_holder["needs_review"] = False
        if scope == "glossary":
            glossary_changed = True
        else:
            changed_files.add(scope)
        if decision == DECISION_OK:
            report.approved += 1
        else:
            report.changed += 1

    report.pending_after = (sum(1 for f in files.values() for e in f["entries"] if e["needs_review"])
                            + sum(1 for i in glossary["items"] if i.get("needs_review", True)))
    if apply and report.ok:
        for name in changed_files:
            _write(os.path.join(directory, name), files[name])
        if glossary_changed:
            _write(os.path.join(directory, "glossary.json"), glossary)
        # prove the result loads, and refresh the human-readable status line
        i18n = _import_catalogue_module()
        loaded = i18n.load_catalogue_from(directory)
        assert loaded.pending_review == report.pending_after
        meta_path = os.path.join(directory, "meta.json")
        meta = _read(meta_path)
        meta["status"] = ("Reviewed: every entry and glossary item has been reviewed by a person."
                          if not loaded.pending_review else
                          "PARTLY REVIEWED: %d of %d items still need review." %
                          (loaded.pending_review, len(loaded.entries) + len(loaded.glossary["items"])))
        _write(meta_path, meta)
        report.applied = True
    return report


def format_report(report: ImportReport, dry_run: bool) -> str:
    lines = ["%s" % ("DRY RUN — nothing was changed. Add --apply to write the corrections." if dry_run and report.ok
                     else "APPLIED." if report.applied else "NOT APPLIED — fix the problems below first."),
             "",
             "  marked OK as is      : %d" % report.approved,
             "  corrected            : %d" % report.changed,
             "  marked Not sure      : %d  (stay a draft)" % report.unsure,
             "  left blank           : %d  (stay a draft)" % report.untouched,
             "  skipped as out of date: %d" % len(report.stale)]
    if report.pending_after is not None:
        lines.append("  %s: %d" % ("would still need review" if dry_run else "still needing review  ", report.pending_after))
    for title, items in (("PROBLEMS (these rows were not accepted)", report.errors),
                         ("OUT OF DATE", report.stale), ("WARNINGS", report.warnings)):
        if items:
            lines += ["", "%s:" % title] + ["  - " + i for i in items]
    if report.notes:
        lines += ["", "REVIEWER NOTES AND QUESTIONS:"] + ["  - [%s] %s" % (k, n) for k, n in report.notes]
    if report.term_requests:
        lines += ["", "TERM PREFERENCES (not applied automatically — a global change is needed):"] + \
                 ["  - " + t for t in report.term_requests]
    return "\n".join(lines)


# ====================================================================================== CLI
def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--catalogue-dir", default=DEFAULT_CATALOGUE, help="the catalogue to read/update")
    sub = parser.add_subparsers(dest="command", required=True)
    e = sub.add_parser("export", help="write the review spreadsheet")
    e.add_argument("--out", default=DEFAULT_OUT)
    e.add_argument("--format", choices=("xlsx", "csv", "both"), default="both")
    e.add_argument("--all", action="store_true", help="include rows that are already reviewed")
    i = sub.add_parser("import", help="read a reviewed spreadsheet back")
    i.add_argument("file")
    i.add_argument("--apply", action="store_true", help="write the corrections (default is a dry run)")
    sub.add_parser("status", help="how much is still draft")
    args = parser.parse_args(argv)

    if args.command == "export":
        for path in export(args.catalogue_dir, args.out, args.format, args.all):
            print("wrote", path)
        return 0
    if args.command == "status":
        i18n = _import_catalogue_module()
        cat = i18n.load_catalogue_from(args.catalogue_dir)
        total = len(cat.entries) + len(cat.glossary["items"])
        print("%d of %d items still need review (catalogue %s)" % (cat.pending_review, total, cat.version))
        return 0
    try:
        rows, term_requests = read_review_file(args.file)
    except (ValueError, OSError, zipfile.BadZipFile, ET.ParseError) as exc:
        print("cannot read %s: %s" % (args.file, exc), file=sys.stderr)
        return 2
    report = apply_review(rows, args.catalogue_dir, apply=args.apply, term_requests=term_requests)
    print(format_report(report, dry_run=not args.apply))
    return 0 if report.ok else 1


if __name__ == "__main__":
    sys.exit(main())
