"""
Report localisation overlay (Marathi, with room for more languages).

**This module translates a finished `ReportDocument`. It never reinterprets one.**
`project()` still builds the document in English, exactly as before; this module then
walks every string in it and swaps in the catalogue's rendering. Because projection is
untouched, the English report is byte-for-byte what it always was, and the existing
determinism and hash tests are the regression guard for that.

Why an overlay and not message keys in the rules: the analysis, posture, cross-session
and ML packages are frozen. Their English sentences reach the report verbatim, so the
catalogue keys *on those sentences* (and on parameterised templates of them) instead of
asking the rules to emit message ids. A completeness test fails if any report string has
no entry, which also makes a later English rewording impossible to miss.

There is **no runtime machine translation** and no free-form text generation here. Every
Marathi string comes from the reviewed (or, today, review-pending) catalogue under
``i18n/<lang>/``. A string with no entry stays English and is *reported*, never guessed.

Matching, in order, for each string:

1. exact catalogue entry;
2. pass-through (identifiers, hashes, numbers, timestamps, standard names ...: data that
   must be shown unchanged -- see ``passthrough.json``, every pattern carries a reason);
3. parameterised template, e.g. ``"{n:num} issue group(s) penalise the posture score."``;
4. a ``"; "`` or `` " · "`` -joined list whose every item matches;
5. concatenation of fragments (the rules build some sentences as ``f"{a}{b}"``).

Placeholder modes in an ``en`` spec: ``{x}`` any text, carried through unchanged;
``{x:num}`` a number; ``{x:mk}`` a ``[!!!]``-style severity marker; ``{x:tr}`` text that is
itself translated recursively (a template whose ``tr`` parameter cannot be translated does
not match, so a half-translated sentence is never produced); ``{x:opt}`` is translated when
possible and otherwise carried through (for values such as ``'false'`` or a TLS version).

Digits are always ASCII: scores, counts, ids and hashes must copy and paste verbatim into
a case file, and must read identically in both languages.
"""
from __future__ import annotations

import functools
import glob
import hashlib
import json
import os
import re
from dataclasses import dataclass, field, replace
from typing import Callable, Dict, List, Optional, Sequence, Tuple

from nyaysaakshya.reporting.model import (
    Bar, KeyValue, ReportDocument, Section, Table,
)

LANG_EN = "en"
LANG_MR = "mr"
LANG_BOTH = "both"
SUPPORTED_LANGS = (LANG_EN, LANG_MR, LANG_BOTH)
#: Languages that have a catalogue. `both` is a layout of `en` + `mr`, not a catalogue.
CATALOGUE_LANGS = (LANG_MR,)

_I18N_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "i18n")

#: ``{name}``, ``{name:mode}``.
_PLACEHOLDER = re.compile(r"\{([A-Za-z_][A-Za-z0-9_]*)(?::([a-z]+))?\}")
_MODES = frozenset({"num", "mk", "tr", "opt"})
_NUM = r"[-+]?\d+(?:\.\d+)?"
_MARKER = r"\[[^\]\n]*\]"
_DEVANAGARI_DIGITS = re.compile("[०-९]")


class CatalogueError(ValueError):
    """The catalogue is malformed. Raised at load time, never while rendering."""


# --------------------------------------------------------------------- entries
@dataclass(frozen=True)
class Entry:
    """One catalogue entry: an English spec and its rendering in the target language."""
    entry_id: str
    en: str
    target: str
    needs_review: bool
    #: Spec split into literal and placeholder parts. A plain string has no placeholders.
    parts: Tuple[Tuple[str, Optional[str], Optional[str]], ...] = field(default=(), compare=False)
    regex: Optional["re.Pattern[str]"] = field(default=None, compare=False)
    literals: Tuple[str, ...] = field(default=(), compare=False)
    literal_size: int = field(default=0, compare=False)

    @property
    def is_template(self) -> bool:
        return self.regex is not None


def _parse_spec(spec: str) -> List[Tuple[str, Optional[str], Optional[str]]]:
    """Split a spec into ``(literal, name, mode)`` triples; the last literal may be ''."""
    parts: List[Tuple[str, Optional[str], Optional[str]]] = []
    position = 0
    for match in _PLACEHOLDER.finditer(spec):
        parts.append((spec[position:match.start()], match.group(1), match.group(2)))
        position = match.end()
    parts.append((spec[position:], None, None))
    return parts


def _compile(entry_id: str, en: str, target: str, needs_review: bool) -> Entry:
    parts = _parse_spec(en)
    names = [n for _lit, n, _m in parts if n]
    if not names:
        return Entry(entry_id, en, target, needs_review)
    for _lit, name, mode in parts:
        if mode is not None and mode not in _MODES:
            raise CatalogueError("%s: unknown placeholder mode %r" % (entry_id, mode))
    seen: set = set()
    pattern = ["^"]
    literals: List[str] = []
    for literal, name, mode in parts:
        pattern.append(re.escape(literal))
        if len(literal.strip()) >= 3:
            literals.append(literal)
        if name is None:
            continue
        if name in seen:
            pattern.append("(?P=%s)" % name)
        else:
            seen.add(name)
            body = {"num": _NUM, "mk": _MARKER}.get(mode or "", ".+?")
            pattern.append("(?P<%s>%s)" % (name, body))
    pattern.append("$")
    target_names = {m.group(1) for m in _PLACEHOLDER.finditer(target)}
    unknown = target_names - set(names)
    if unknown:
        raise CatalogueError("%s: target uses placeholders not in the English spec: %s"
                             % (entry_id, ", ".join(sorted(unknown))))
    return Entry(entry_id, en, target, needs_review, tuple(parts),
                 re.compile("".join(pattern), re.DOTALL), tuple(literals),
                 sum(len(lit) for lit, _n, _m in parts))


# ------------------------------------------------------------------- catalogue
class Catalogue:
    """A loaded catalogue plus its matcher. Instances are cached and read-only."""

    def __init__(self, language: str, meta: dict, entries: Sequence[Entry],
                 passthrough: Sequence[Tuple[str, "re.Pattern[str]", str]],
                 glossary: dict) -> None:
        self.language = language
        self.meta = meta
        self.entries = tuple(entries)
        self.passthrough = tuple(passthrough)
        self.glossary = glossary
        #: Content identity of everything that can change a rendered report. Stored reports
        #: carry it, so swapping in reviewed text (or flipping needs_review) makes them stale.
        self.fingerprint = hashlib.sha256(json.dumps(
            {"entries": [[e.entry_id, e.en, e.target, e.needs_review] for e in entries],
             "glossary": glossary, "passthrough": [[i, p.pattern] for i, p, _w in passthrough]},
            sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()
        self._exact: Dict[str, Entry] = {}
        templates: List[Entry] = []
        for entry in entries:
            if entry.is_template:
                templates.append(entry)
            elif entry.en in self._exact:
                raise CatalogueError("duplicate English entry: %r (%s and %s)"
                                     % (entry.en, self._exact[entry.en].entry_id,
                                        entry.entry_id))
            else:
                self._exact[entry.en] = entry
        # Most specific first: more literal text means fewer accidental matches.
        self._templates = tuple(sorted(templates, key=lambda e: (-e.literal_size, e.entry_id)))

    # -- public ----------------------------------------------------------------
    @property
    def version(self) -> str:
        return str(self.meta.get("catalogue_version", ""))

    @property
    def pending_review(self) -> int:
        """Items not yet reviewed by a person: catalogue entries and the "how to read" text.

        While this is non-zero every translated report carries a draft notice, so the text
        of the static glossary cannot be approved by accident while the rest is.
        """
        return (sum(1 for entry in self.entries if entry.needs_review)
                + sum(1 for item in self.glossary.get("items", []) if item.get("needs_review", True)))

    def translate(self, text: str) -> Optional[str]:
        """The target-language rendering of `text`, or None if it cannot be translated.

        Pass-through strings (identifiers, numbers ...) return unchanged.
        """
        return self._translate(text, {})

    def is_passthrough(self, text: str) -> bool:
        return any(pattern.fullmatch(text) for _i, pattern, _w in self.passthrough)

    def exact_entry(self, text: str) -> Optional[Entry]:
        return self._exact.get(text)

    # -- matching --------------------------------------------------------------
    def _translate(self, text: str, memo: Dict[str, Optional[str]]) -> Optional[str]:
        if text in memo:
            return memo[text]
        memo[text] = None            # guards against pathological self-reference
        result = self._translate_uncached(text, memo)
        memo[text] = result
        return result

    def _translate_uncached(self, text: str, memo: Dict[str, Optional[str]]) -> Optional[str]:
        exact = self._exact.get(text)
        if exact is not None:
            return exact.target
        if not text.strip() or self.is_passthrough(text):
            return text
        result = self._match_template(text, memo)
        if result is not None:
            return result
        for separator in ("; ", " · "):
            result = self._translate_list(text, separator, memo)
            if result is not None:
                return result
        return self._translate_concatenation(text, memo)

    def _match_template(self, text: str, memo: Dict[str, Optional[str]]) -> Optional[str]:
        for entry in self._templates:
            if any(lit not in text for lit in entry.literals):
                continue
            match = entry.regex.match(text)
            if match is None:
                continue
            values = match.groupdict()
            modes = {name: mode for _lit, name, mode in entry.parts if name}
            for name, mode in modes.items():
                if mode == "tr":
                    translated = self._translate(values[name], memo)
                    if translated is None:
                        break
                    values[name] = translated
                elif mode == "opt":
                    translated = self._translate(values[name], memo)
                    if translated is not None:
                        values[name] = translated
            else:
                return _PLACEHOLDER.sub(lambda m: values[m.group(1)], entry.target)
        return None

    def _translate_list(self, text: str, separator: str,
                        memo: Dict[str, Optional[str]]) -> Optional[str]:
        items = text.split(separator)
        if len(items) < 2:
            return None
        out = []
        for item in items:
            translated = self._translate(item, memo)
            if translated is None:
                return None
            out.append(translated)
        return separator.join(out)

    def _translate_concatenation(self, text: str,
                                 memo: Dict[str, Optional[str]]) -> Optional[str]:
        """Split at punctuation and translate the pieces, e.g. ``"<a>. Items: <b>."``.

        Some rules assemble a sentence as ``f"{part}{fragment}"``; the fragment (``". No
        anomaly ..."``, ``"; each ..."``) is its own catalogue entry that begins with its
        punctuation, so the cut goes *before* the punctuation. A cut after ``". "`` covers
        sentences simply placed side by side.
        """
        for left, separator, right in _cuts(text):
            a = self._translate(left, memo)
            if a is None:
                continue
            b = self._translate(right, memo)
            if b is not None:
                return a + separator + b
        return None


def _cuts(text: str):
    """Candidate (left, separator, right) splits, most balanced first."""
    cuts = []
    for index, char in enumerate(text):
        if char in ".;,:" and 0 < index < len(text):
            cuts.append((text[:index], "", text[index:]))
            if text[index + 1:index + 2] == " " and index + 2 < len(text):
                cuts.append((text[:index + 1], " ", text[index + 2:]))
                if char in ".;":
                    # the separator itself is consumed: "<a>. <b>" with entries that carry no
                    # trailing full stop of their own
                    cuts.append((text[:index], char + " ", text[index + 2:]))
        elif char == " " and index + 1 < len(text) and text[index + 1] in "[(" and index > 0:
            cuts.append((text[:index], "", text[index:]))
    middle = len(text) / 2.0
    cuts.sort(key=lambda c: abs(len(c[0]) - middle))
    return cuts


# --------------------------------------------------------------------- loading
def _read_json(path: str) -> dict:
    try:
        with open(path, encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError) as exc:
        raise CatalogueError("cannot read %s: %s" % (path, exc))


@functools.lru_cache(maxsize=None)
def load_catalogue(language: str) -> Catalogue:
    """Load and validate ``i18n/<language>/``. Cached; raises `CatalogueError` if malformed."""
    if language not in CATALOGUE_LANGS:
        raise CatalogueError("no catalogue for language %r" % language)
    return load_catalogue_from(os.path.join(_I18N_DIR, language), language)


def load_catalogue_from(directory: str, language: str = LANG_MR) -> Catalogue:
    """Load and validate a catalogue from any directory (not cached).

    Used by the review tool to check a corrected copy before it replaces the shipped one.
    """
    meta = _read_json(os.path.join(directory, "meta.json"))
    glossary = _read_json(os.path.join(directory, "glossary.json"))
    patterns_doc = _read_json(os.path.join(directory, "passthrough.json"))

    passthrough = []
    for item in patterns_doc.get("patterns", []):
        for key in ("id", "pattern", "why"):
            if not item.get(key):
                raise CatalogueError("passthrough pattern missing %r: %r" % (key, item))
        try:
            passthrough.append((item["id"], re.compile(item["pattern"]), item["why"]))
        except re.error as exc:
            raise CatalogueError("passthrough %s: bad pattern: %s" % (item["id"], exc))

    entries: List[Entry] = []
    ids: set = set()
    skip = {"meta.json", "glossary.json", "passthrough.json", "examples.json"}
    for path in sorted(glob.glob(os.path.join(directory, "*.json"))):
        if os.path.basename(path) in skip:
            continue
        for raw in _read_json(path).get("entries", []):
            for key in ("id", "en", "mr", "needs_review"):
                if key not in raw:
                    raise CatalogueError("%s: entry missing %r: %r"
                                         % (os.path.basename(path), key, raw.get("id", raw)))
            if raw["id"] in ids:
                raise CatalogueError("duplicate entry id %r" % raw["id"])
            ids.add(raw["id"])
            if not isinstance(raw["needs_review"], bool):
                raise CatalogueError("%s: needs_review must be true/false" % raw["id"])
            if not raw["mr"].strip():
                raise CatalogueError("%s: empty translation" % raw["id"])
            if _DEVANAGARI_DIGITS.search(raw["mr"]):
                raise CatalogueError("%s: Devanagari digits are not allowed (ASCII digits only)"
                                     % raw["id"])
            entries.append(_compile(raw["id"], raw["en"], raw["mr"], raw["needs_review"]))
    return Catalogue(language, meta, entries, passthrough, glossary)


# -------------------------------------------------------------------- overlay
@dataclass
class LocalizationReport:
    """What the overlay did, so a gap is visible rather than silent."""
    language: str
    translated: int = 0
    passthrough: int = 0
    #: English strings that had no rendering and were left as they were, in first-seen order.
    untranslated: List[str] = field(default_factory=list)

    @property
    def complete(self) -> bool:
        return not self.untranslated


class _Translator:
    def __init__(self, catalogue: Catalogue) -> None:
        self.catalogue = catalogue
        self.report = LocalizationReport(language=catalogue.language)
        self._memo: Dict[str, Optional[str]] = {}

    def __call__(self, text: str) -> str:
        if not text or not text.strip():
            return text
        translated = self.catalogue._translate(text, self._memo)
        if translated is None:
            if text not in self.report.untranslated:
                self.report.untranslated.append(text)
            return text
        if translated == text and self.catalogue.is_passthrough(text):
            self.report.passthrough += 1
        else:
            self.report.translated += 1
        return translated


def make_translator(language: str) -> "_Translator":
    """A translator that records what it could not translate (``.report``).

    Pass the same one to `localize` and to the renderer's chrome so the report covers both.
    """
    return _Translator(load_catalogue(language))


def localize(document: ReportDocument, language: str,
             translator: Optional["_Translator"] = None
             ) -> Tuple[ReportDocument, LocalizationReport]:
    """Translate every string of `document`. English returns the document untouched.

    The returned document keeps the raw enum fields (``overall_posture``, ``Bar.severity``,
    ids, metadata) exactly as they were: those drive colour and logic, not wording.
    """
    if language == LANG_EN:
        return document, LocalizationReport(language=LANG_EN)
    catalogue = load_catalogue(language)
    t = translator or _Translator(catalogue)

    def kv(item: KeyValue) -> KeyValue:
        return KeyValue(t(item.label), t(item.value), t(item.note))

    def table(item: Table) -> Table:
        return Table(caption=t(item.caption), columns=tuple(t(c) for c in item.columns),
                     rows=tuple(tuple(t(cell) for cell in row) for row in item.rows),
                     empty_note=t(item.empty_note), wide_columns=item.wide_columns)

    def bar(item: Bar) -> Bar:
        return replace(item, label=t(item.label), value_text=t(item.value_text))

    sections = []
    for section in document.sections:
        sections.append(replace(
            section, title=t(section.title), lead=t(section.lead),
            facts=[kv(f) for f in section.facts], tables=[table(x) for x in section.tables],
            bars=[bar(b) for b in section.bars],
            paragraphs=[t(p) for p in section.paragraphs],
            notices=[t(n) for n in section.notices]))

    localized = replace(
        document, title=t(document.title), subtitle=t(document.subtitle),
        overall_posture_label=t(document.overall_posture_label),
        score_text=t(document.score_text), coverage_text=t(document.coverage_text),
        sections=sections, truncations=[t(x) for x in document.truncations])
    localized.sections.insert(0, how_to_read_section(catalogue))
    return localized, t.report


def how_to_read_section(catalogue: Catalogue) -> Section:
    """The static "how to read this report" block. Fixed text: it adds no analysis.

    The draft-translation notice is not part of this block: the renderer shows it at the very
    top of the report for as long as `Catalogue.pending_review` is non-zero.
    """
    g, lang = catalogue.glossary, catalogue.language
    notices = [n[lang] for n in g.get("notices", [])]
    return Section(
        section_id="how-to-read", title=g["title"][lang], lead=g["lead"][lang],
        facts=[KeyValue(item["term"][lang], item[lang]) for item in g["items"]],
        notices=notices)
