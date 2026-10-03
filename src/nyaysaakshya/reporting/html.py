"""
Standalone HTML renderer (doc 22 §9, §16, ADR-0019 Decision 2).

Zero dependencies: `html.escape` plus string composition, no template engine. That keeps
JSON and HTML available to a core install, and it puts the escaping boundary at every
call site rather than behind an autoescape setting a later edit could switch off.

The output is one self-contained file. Inline CSS, no CDN, no webfont, no `<script>`, no
external image. It opens from disk with no server running.

**Every value that came from the assessment passes through `esc()`.** Assessment text
originates in a capture, and a capture is untrusted input; it is data, never markup.
CSS and structural markup are literals in this module and are never interpolated from
assessment content.
"""
from __future__ import annotations

from html import escape
from typing import Callable, Iterable, List, Tuple

from nyaysaakshya.reporting import i18n, styles
from nyaysaakshya.reporting.model import Bar, ReportDocument, Section, Table


def esc(value: object) -> str:
    """Escape for HTML text and attribute contexts. The only way content gets in."""
    return escape(str(value), quote=True)


# ------------------------------------------------------------------------ CSS
#: A literal. No assessment value is ever interpolated into this string.
_CSS = """
:root {
  --ink: %(ink)s; --muted: %(muted)s; --rule: %(rule)s; --panel: %(panel)s;
  --accent: %(accent)s; --critical: %(critical)s; --high: %(high)s;
  --medium: %(medium)s; --low: %(low)s; --info: %(info)s; --withheld: %(withheld)s;
}
* { box-sizing: border-box; }
html { -webkit-text-size-adjust: 100%%; }
body {
  margin: 0; padding: 0 0 4rem; color: var(--ink); background: #fff;
  font-family: %(font)s; font-size: 15px; line-height: 1.55;
}
.wrap { max-width: 60rem; margin: 0 auto; padding: 0 1.5rem; }
a { color: var(--accent); }

/* ---- masthead ---- */
.masthead { border-bottom: 3px solid var(--accent); padding: 2.5rem 0 1.25rem;
  margin-bottom: 2rem; }
.masthead h1 { margin: 0; font-size: 1.6rem; letter-spacing: .04em; }
.masthead p { margin: .25rem 0 0; color: var(--muted); font-size: 1rem; }
.ids { margin-top: 1rem; font-family: %(mono)s; font-size: .76rem;
  color: var(--muted); word-break: break-all; }
.ids span { display: inline-block; margin-right: 1.25rem; }

/* ---- verdict: posture and coverage are one block, never separable ---- */
.verdict { display: flex; flex-wrap: wrap; gap: 1px; background: var(--rule);
  border: 1px solid var(--rule); margin: 0 0 2rem; }
.verdict > div { background: #fff; padding: 1rem 1.25rem; flex: 1 1 11rem; }
.verdict .k { font-size: .7rem; letter-spacing: .09em; text-transform: uppercase;
  color: var(--muted); margin-bottom: .3rem; }
.verdict .v { font-size: 1.35rem; font-weight: 700; }
.verdict .v.small { font-size: 1.05rem; font-weight: 600; }
.verdict .note { font-size: .78rem; color: var(--muted); margin-top: .25rem; }

/* ---- sections ---- */
section { margin: 0 0 2.5rem; }
h2 { font-size: 1.1rem; margin: 0 0 .2rem; padding-bottom: .4rem;
  border-bottom: 2px solid var(--rule); letter-spacing: .02em; }
h2 .num { color: var(--muted); font-weight: 400; margin-right: .5rem; }
.lead { color: var(--muted); margin: .5rem 0 1rem; }
p { margin: .6rem 0; }

/* ---- facts ---- */
dl.facts { display: grid; grid-template-columns: minmax(10rem, 16rem) 1fr;
  gap: .4rem 1.25rem; margin: 1rem 0; }
dl.facts dt { color: var(--muted); font-size: .84rem; }
dl.facts dd { margin: 0; font-weight: 600; word-break: break-word; }
dl.facts dd .note { display: block; font-weight: 400; font-size: .78rem;
  color: var(--muted); }

/* ---- tables ---- */
figure { margin: 1.25rem 0; }
table { width: 100%%; border-collapse: collapse; font-size: .82rem; }
caption { text-align: left; font-size: .78rem; color: var(--muted);
  padding-bottom: .4rem; }
th, td { border: 1px solid var(--rule); padding: .4rem .55rem; text-align: left;
  vertical-align: top; word-break: break-word; }
th { background: var(--panel); font-size: .74rem; letter-spacing: .05em;
  text-transform: uppercase; color: var(--muted); font-weight: 700; }
td.wide { min-width: 12rem; }
tbody tr:nth-child(even) td { background: #fbfcfd; }
.empty { color: var(--muted); font-style: italic; padding: .6rem 0; }

/* ---- severity: colour is redundant with the text marker ---- */
.sev { font-family: %(mono)s; font-size: .78rem; white-space: nowrap; }
.sev-CRITICAL { color: var(--critical); font-weight: 700; }
.sev-HIGH { color: var(--high); font-weight: 700; }
.sev-MEDIUM { color: var(--medium); font-weight: 600; }
.sev-LOW { color: var(--low); }
.sev-INFO { color: var(--info); }

/* ---- notices ---- */
.notice { border-left: 4px solid var(--accent); background: var(--panel);
  padding: .7rem .9rem; margin: .6rem 0; font-size: .87rem; }
.notice.withheld { border-left-color: var(--withheld); }

/* ---- bars: numbers are shown as text beside every bar ---- */
.bars { margin: 1rem 0; }
.bar { display: grid; grid-template-columns: 6rem 1fr 3rem; align-items: center;
  gap: .6rem; margin: .3rem 0; font-size: .8rem; }
.bar .track { background: var(--panel); border: 1px solid var(--rule);
  height: .85rem; position: relative; }
.bar .fill { position: absolute; inset: 0 auto 0 0; background: var(--muted); }
.bar .n { text-align: right; font-family: %(mono)s; }

/* ---- footer ---- */
footer { border-top: 1px solid var(--rule); margin-top: 3rem; padding-top: 1rem;
  font-size: .76rem; color: var(--muted); }
footer code { font-family: %(mono)s; word-break: break-all; }

/* ---- print ---- */
@page { size: A4; margin: 16mm 14mm; }
@media print {
  body { font-size: 10.5pt; }
  .wrap { max-width: none; padding: 0; }
  section { break-inside: auto; }
  h2 { break-after: avoid; }
  figure, .notice, .bar { break-inside: avoid; }
  tr { break-inside: avoid; }
  thead { display: table-header-group; }
  .page-break { break-before: page; }
}
"""


#: Added only to non-English output. Devanagari needs a taller line, no letter-spacing and
#: no forced upper-case (they break conjuncts and mangle Latin tokens inside Marathi text),
#: and a font stack with Devanagari faces. Still no webfont: the reader's system supplies one.
_CSS_DEVANAGARI = """
[lang="mr"] { font-family: %(font)s, "Nirmala UI", "Noto Sans Devanagari", "Mangal",
  "Kohinoor Devanagari", "Devanagari Sangam MN", "Lohit Devanagari", sans-serif; }
[lang="mr"] body, body[lang="mr"] { line-height: 1.75; }
[lang="mr"] .masthead h1, [lang="mr"] th, [lang="mr"] .verdict .k, [lang="mr"] h2 {
  letter-spacing: 0; text-transform: none; }
[lang="mr"] th, [lang="mr"] td { font-size: .78rem; word-break: normal;
  overflow-wrap: break-word; hyphens: manual; }
[lang="mr"] figure { overflow-x: auto; }
[lang="mr"] table { min-width: 100%%; }
.notice.draft { border-left-color: var(--high); font-weight: 600; }
@media print { [lang="mr"] figure { overflow: visible; } [lang="mr"] table { font-size: 8pt; } }
.langbanner { background: var(--panel); border-left: 4px solid var(--accent);
  padding: .6rem 1rem; margin: 2.5rem 0 1rem; font-weight: 600; }
"""


def _css(lang: str = i18n.LANG_EN) -> str:
    tokens = dict(styles.COLOR)
    tokens["font"] = styles.HTML_FONT_STACK
    tokens["mono"] = styles.HTML_MONO_STACK
    css = _CSS % tokens
    if lang != i18n.LANG_EN:
        css += _CSS_DEVANAGARI % tokens
    return css


# -------------------------------------------------------------------- helpers
def _severity_class(cell: str) -> str:
    """Derive a CSS class from a severity cell. Returns a fixed literal or ''.

    Deliberately matches against the known severity vocabulary rather than
    interpolating the cell, so no assessment text can reach a class attribute.
    """
    for severity in styles.SEVERITY_ORDER:
        if severity in cell:
            return "sev sev-" + severity
    # A translated cell carries no English severity word, but the ASCII marker survives.
    for severity in styles.SEVERITY_ORDER:
        if styles.SEVERITY_MARKER[severity] in cell:
            return "sev sev-" + severity
    return ""


def _table(table: Table, t: Callable[[str], str] = lambda text: text) -> str:
    out: List[str] = ["<figure>"]
    if not table.rows:
        out.append('<p class="empty">%s</p>' % esc(
            table.empty_note or t("No data recorded for this table.")))
        out.append("</figure>")
        return "".join(out)
    out.append("<table><caption>%s</caption><thead><tr>" % esc(table.caption))
    out.extend("<th scope=\"col\">%s</th>" % esc(c) for c in table.columns)
    out.append("</tr></thead><tbody>")
    for row in table.rows:
        out.append("<tr>")
        for index, cell in enumerate(row):
            classes = []
            if index in table.wide_columns:
                classes.append("wide")
            severity_class = _severity_class(cell) if index <= 1 else ""
            if severity_class:
                classes.append(severity_class)
            attr = ' class="%s"' % " ".join(classes) if classes else ""
            out.append("<td%s>%s</td>" % (attr, esc(cell)))
        out.append("</tr>")
    out.append("</tbody></table></figure>")
    return "".join(out)


def _bars(bars: Iterable[Bar]) -> str:
    items = list(bars)
    if not items:
        return ""
    out = ['<div class="bars">']
    for bar in items:
        colour = styles.severity_color(bar.severity) if bar.severity else \
            styles.COLOR["muted"]
        # width and colour come from the fixed severity vocabulary / a computed
        # percentage, never from assessment text.
        out.append(
            '<div class="bar"><span>%s</span>'
            '<span class="track"><span class="fill" style="width:%.1f%%;'
            'background:%s"></span></span>'
            '<span class="n">%s</span></div>'
            % (esc(bar.label), max(0.0, min(1.0, bar.fraction)) * 100.0,
               esc(colour), esc(bar.value_text)))
    out.append("</div>")
    return "".join(out)


def _section(index: int, section: Section, t: Callable[[str], str] = lambda text: text,
             id_prefix: str = "") -> str:
    klass = ' class="page-break"' if section.page_break_before else ""
    out = ['<section id="%s"%s>' % (esc(id_prefix + section.section_id), klass)]
    out.append('<h2><span class="num">%d.</span>%s</h2>' % (index, esc(section.title)))
    if section.lead:
        out.append('<p class="lead">%s</p>' % esc(section.lead))
    if section.facts:
        out.append('<dl class="facts">')
        for fact in section.facts:
            note = '<span class="note">%s</span>' % esc(fact.note) if fact.note else ""
            out.append("<dt>%s</dt><dd>%s%s</dd>"
                       % (esc(fact.label), esc(fact.value), note))
        out.append("</dl>")
    for paragraph in section.paragraphs:
        out.append("<p>%s</p>" % esc(paragraph))
    out.append(_bars(section.bars))
    for table in section.tables:
        out.append(_table(table, t))
    for notice in section.notices:
        out.append('<div class="notice">%s</div>' % esc(notice))
    out.append("</section>")
    return "".join(out)


# --------------------------------------------------------------------- render
def _wrap(document: ReportDocument, t: Callable[[str], str], id_prefix: str = "",
          draft_notice: str = "") -> str:
    """One report, from ``<div class="wrap">`` to its closing tag.

    `t` translates the renderer's own fixed strings (identity for English). Everything that
    came from the assessment has already been through `esc()`/localisation by the time it
    reaches here; this function adds only literals.
    """
    m = document.metadata
    posture_colour = styles.posture_color(document.overall_posture)
    withheld = document.overall_posture == "INSUFFICIENT_EVIDENCE"

    out: List[str] = []
    out.append('<div class="wrap">')

    # masthead
    out.append('<header class="masthead">')
    out.append("<h1>%s</h1>" % esc(document.title))
    out.append("<p>%s</p>" % esc(document.subtitle))
    out.append('<div class="ids">')
    out.append("<span>%s <strong>%s</strong></span>" % (t("Assessment"), esc(m.assessment_id)))
    out.append("<span>%s <strong>%s</strong></span>" % (t("Capture"), esc(m.capture_id)))
    if m.run_id:
        out.append("<span>%s <strong>%s</strong></span>" % (t("Run"), esc(m.run_id)))
    out.append("<span>%s <strong>%s</strong></span>" % (t("Analysed"), esc(m.generated_at)))
    out.append("</div></header>")
    if draft_notice:
        out.append('<div class="notice draft" role="note">%s</div>' % esc(draft_notice))

    # verdict block: posture and coverage together, always (doc 22 §7)
    out.append('<div class="verdict">')
    out.append('<div><div class="k">%s</div>'
               '<div class="v" style="color:%s">%s</div>%s</div>'
               % (t("Overall posture"), esc(posture_colour), esc(document.overall_posture_label),
                  '<div class="note">%s</div>'
                  % t("band withheld: coverage below the assessment floor") if withheld else ""))
    out.append('<div><div class="k">%s</div>'
               '<div class="v small">%s</div></div>' % (t("Posture score"), esc(document.score_text)))
    out.append('<div><div class="k">%s</div>'
               '<div class="v small">%s</div></div>' % (t("Evidence coverage"),
                                                         esc(document.coverage_text)))
    out.append('<div><div class="k">%s</div><div class="v small">%s</div></div>'
               % (t("ML lane"), esc(t("Enabled" if m.ai_enabled else "Disabled"))))
    out.append("</div>")

    if document.truncations:
        out.append('<div class="notice">%s'
                   % t("Some content was truncated for rendering: ")
                   + esc("; ".join(document.truncations)) + "</div>")

    out.append("<main>")
    for index, section in enumerate(document.sections, start=1):
        out.append(_section(index, section, t, id_prefix))
    out.append("</main>")

    out.append("<footer>")
    out.append("<p>%s · %s · %s <code>%s</code></p>"
               % (esc(document.title), t("Forensic assessment"), t("Assessment"),
                  esc(m.assessment_id)))
    out.append("<p>%s %s · %s %s · %s %s · %s %s</p>"
               % (t("Report schema"), esc(m.report_schema_version),
                  t("Renderer"), esc(m.renderer_version),
                  t("Posture schema"), esc(m.posture_schema_version),
                  t("Posture engine"), esc(m.posture_engine_version)))
    out.append("<p>%s</p>" % t(
        "The timestamp shown is the time of analysis, not of report generation. This report "
        "is a rendering of the canonical assessment and introduces no security conclusion of "
        "its own."))
    out.append("</footer></div>")
    return "".join(out)


def _head(document: ReportDocument, lang: str, html_lang: str) -> str:
    m = document.metadata
    out: List[str] = []
    out.append("<!DOCTYPE html>")
    out.append('<html lang="%s"><head><meta charset="utf-8">' % html_lang)
    out.append('<meta name="viewport" content="width=device-width, initial-scale=1">')
    out.append("<title>%s — %s — %s</title>"
               % (esc(document.title), esc(document.subtitle), esc(m.assessment_id)))
    out.append('<meta name="generator" content="%s %s">'
               % (esc(document.title), esc(m.renderer_version)))
    out.append("<style>%s</style></head><body>" % _css(lang))
    return "".join(out)


def render_html(document: ReportDocument) -> str:
    """Render a complete, standalone English HTML document."""
    return (_head(document, i18n.LANG_EN, "en") + _wrap(document, lambda text: text)
            + "</body></html>")


def render_localized(document: ReportDocument,
                     lang: str) -> Tuple[str, i18n.LocalizationReport]:
    """Render `document` (always the English projection) as ``en``, ``mr`` or ``both``.

    ``both`` stacks the Marathi report first and the unmodified English original after it,
    in one file. The English part is the same report `render_html` produces; it is only
    wrapped, labelled as the authoritative copy, and given distinct section ids.
    Returns the HTML and the localisation report (what, if anything, was left in English).
    """
    if lang == i18n.LANG_EN:
        return render_html(document), i18n.LocalizationReport(language=i18n.LANG_EN)
    if lang not in i18n.SUPPORTED_LANGS:
        raise ValueError("unsupported report language: %r" % (lang,))

    translator = i18n.make_translator(i18n.LANG_MR)
    marathi, _ = i18n.localize(document, i18n.LANG_MR, translator)
    glossary = translator.catalogue.glossary
    # Shown at the very top for as long as any catalogue entry is unreviewed.
    draft = glossary["draft_notice"][i18n.LANG_MR] if translator.catalogue.pending_review else ""
    if lang == i18n.LANG_MR:
        return (_head(marathi, i18n.LANG_MR, "mr") + _wrap(marathi, translator, "", draft)
                + "</body></html>"), translator.report

    banner = glossary["english_banner"]
    parts = [
        _head(marathi, i18n.LANG_MR, "mr"),
        '<div lang="mr" id="mr-report">', _wrap(marathi, translator, "mr-", draft), "</div>",
        '<div lang="en" id="en-report" class="page-break">',
        '<div class="wrap"><div class="langbanner">%s · <span lang="mr">%s</span></div></div>'
        % (esc(banner["en"]), esc(banner["mr"])),
        _wrap(document, lambda text: text, "en-"), "</div>",
        "</body></html>",
    ]
    return "".join(parts), translator.report


def render(assessment: dict, lang: str = i18n.LANG_EN) -> str:
    """Convenience: project then render."""
    from nyaysaakshya.reporting.projection import project
    return render_localized(project(assessment), lang)[0]
