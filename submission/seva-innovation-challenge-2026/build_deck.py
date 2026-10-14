"""
Build the NyaySaakshya Seva Innovation Challenge 2026 deck from the OFFICIAL template.

    /tmp/pptxenv/bin/python build_deck.py            # needs python-pptx; run from this folder

Reads  reference/Seva_Innovation_Challenge_2026_Presentation_Template.pptx  (never modified)
Writes NyaySaakshya_Seva_Innovation_Challenge_2026.pptx

Every statement placed on a slide is mapped to evidence in SLIDE_CLAIM_AUDIT.md. The deck carries no
placeholders: details only the applicant can confirm (contact, qualification, mentor) are left out
unless filled in APPLICANT below, and are listed in docs/submission/USER_INPUT_REQUIRED.md.
"""
import copy
import os
import sys

from lxml import etree
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.util import Emu, Inches, Pt

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "reference", "Seva_Innovation_Challenge_2026_Presentation_Template.pptx")
OUT = os.path.join(HERE, "NyaySaakshya_Seva_Innovation_Challenge_2026.pptx")
ASSETS = os.path.join(HERE, "assets")

NAVY, ORANGE, SLATE, WHITE = "1B2A5C", "F28C28", "2F3A56", "FFFFFF"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"

# Name as shown on the portal (taken from Aadhaar). Check the spelling against the portal.
# Optional details: leave as None to omit the line from the deck. Never guess these.
APPLICANT = {
    "name": "Siddhant Hiralal Patil",
    "contact": None,        # e.g. "name@example.com | +91 ..." (applicant's own, confirmed)
    "qualification": None,  # e.g. "B.E. Computer Engineering, 2025" (applicant's own, confirmed)
    "mentor": None,         # e.g. "Dr A. Kulkarni, Professor, XYZ College" (only if real)
}
SECTOR = "Law and Order"
SUB_THEME = "Cyber-fraud, digital extortion and financial-crime intelligence"

prs = Presentation(TEMPLATE)
slides = list(prs.slides)


def shape(slide, name):
    for sh in slide.shapes:
        if sh.name == name:
            return sh
    raise KeyError(name)


def _rpr_template(sh):
    para = sh.text_frame.paragraphs[0]
    return copy.deepcopy(para._p), (para.runs[0]._r.find("{%s}rPr" % A) if para.runs else None)


def set_text(sh, paragraphs, size=None, italic=False, color=None, bold=None, bullet=False,
             space_after=None):
    """Replace a text box's content, keeping the template's font, alignment and box.

    `paragraphs`: list of paragraphs; each is a string or a list of (text, overrides) segments,
    overrides being a dict with optional color / bold / italic.
    """
    tf = sh.text_frame
    p0 = tf.paragraphs[0]._p
    base_p = copy.deepcopy(p0)
    run0 = tf.paragraphs[0].runs[0]._r if tf.paragraphs[0].runs else None
    base_rpr = copy.deepcopy(run0.find("{%s}rPr" % A)) if run0 is not None else None
    txBody = tf._txBody
    for p in list(txBody.findall("{%s}p" % A)):
        txBody.remove(p)
    for para in paragraphs:
        segs = [(para, {})] if isinstance(para, str) else para
        p = copy.deepcopy(base_p)
        for child in list(p):
            if child.tag != "{%s}pPr" % A:
                p.remove(child)
        ppr = p.find("{%s}pPr" % A)
        if ppr is None:
            ppr = etree.Element("{%s}pPr" % A)
            p.insert(0, ppr)
        for tag in ("buNone", "buChar", "buAutoNum", "spcAft"):
            for el in ppr.findall("{%s}%s" % (A, tag)):
                ppr.remove(el)
        # schema order inside a:pPr: spacing first, then the bullet
        pos = 0
        for k, child in enumerate(ppr):
            if child.tag in ("{%s}lnSpc" % A, "{%s}spcBef" % A):
                pos = k + 1
        if space_after is not None:
            sa = etree.Element("{%s}spcAft" % A)
            etree.SubElement(sa, "{%s}spcPts" % A).set("val", str(int(space_after * 100)))
            ppr.insert(pos, sa)
            pos += 1
        if bullet:
            ppr.set("marL", "114300")
            ppr.set("indent", "-114300")
            bu = etree.Element("{%s}buChar" % A)
            bu.set("char", "•")
            ppr.insert(pos, bu)
        else:
            ppr.append(etree.Element("{%s}buNone" % A))
        for text, ov in segs:
            r = etree.SubElement(p, "{%s}r" % A)
            if base_rpr is not None:
                rpr = copy.deepcopy(base_rpr)
                r.append(rpr)
            else:
                rpr = etree.SubElement(r, "{%s}rPr" % A)
            rpr.set("i", "1" if ov.get("italic", italic) else "0")
            b = ov.get("bold", bold)
            if b is not None:
                rpr.set("b", "1" if b else "0")
            if size:
                rpr.set("sz", str(int(size * 100)))
            col = ov.get("color", color)
            if col:
                for el in rpr.findall("{%s}solidFill" % A):
                    rpr.remove(el)
                fill = etree.Element("{%s}solidFill" % A)
                clr = etree.SubElement(fill, "{%s}srgbClr" % A)
                clr.set("val", col)
                rpr.insert(0, fill)
            t = etree.SubElement(r, "{%s}t" % A)
            t.text = text
        txBody.append(p)


def fit_box(sh, height_in):
    sh.height = Inches(height_in)


def remove(sh):
    sh._element.getparent().remove(sh._element)


def notes(slide, text):
    slide.notes_slide.notes_text_frame.text = text


# ----------------------------------------------------------------------------- slide 1
s = slides[0]
set_text(shape(s, "Text 0"), ["SEVA INNOVATION CHALLENGE 2026  •  MAHARASHTRA ZONE"])
set_text(shape(s, "Text 1"), ["NyaySaakshya"], bold=True)
sub = shape(s, "Text 2")
set_text(sub, ["Forensic triage for email-traffic captures. It tells cyber-cell investigators what a "
               "capture does, and does not, prove. It does not detect fraud or identify suspects."],
         size=13, italic=False, color="DCE3F5")
sub.top, sub.height, sub.width = Inches(1.55), Inches(0.95), Inches(5.3)

# applicant snapshot (new box cloned from the subtitle box so fonts match)
snap = copy.deepcopy(sub._element)
sub._element.addnext(snap)
snap_sh = [x for x in s.shapes if x._element is snap][0]
snap_sh.top, snap_sh.height, snap_sh.width = Inches(2.95), Inches(1.9), Inches(5.3)
LBL = {"color": "C9D2EC"}
snap_rows = [
    [("Applicant:  ", LBL), (APPLICANT["name"], {"bold": True})],
    [("Application type:  ", LBL), ("Individual (team size 1)", {})],
    [("Sector:  ", LBL), (SECTOR, {})],
    [("Sub-theme:  ", LBL), (SUB_THEME, {})],
    [("Stage:  ", LBL), ("Working Prototype", {"color": WHITE, "bold": True})],
]
if APPLICANT["contact"]:
    snap_rows.insert(4, [("Contact:  ", LBL), (APPLICANT["contact"], {})])
set_text(snap_sh, snap_rows, size=11, italic=False, color=WHITE, space_after=5)

# replace the "How to use this template" guidance box with prototype screens
panel = shape(s, "Shape 15")
remove(shape(s, "Text 16"))
remove(shape(s, "Text 17"))
panel.left, panel.top, panel.width, panel.height = Inches(6.05), Inches(0.85), Inches(3.45), Inches(3.75)
cap_style = shape(s, "Text 0")


def caption(slide, x, y, w, text, size=8.5, color="C9D2EC", bold=False):
    el = copy.deepcopy(cap_style._element)
    slide.shapes._spTree.append(el)
    sh = [x_ for x_ in slide.shapes if x_._element is el][0]
    sh.left, sh.top, sh.width, sh.height = Inches(x), Inches(y), Inches(w), Inches(0.3)
    set_text(sh, [text], size=size, color=color, bold=bold, italic=False)
    for rpr in sh._element.iter("{%s}rPr" % A):
        rpr.set("spc", "0")
    return sh


caption(s, 6.2, 0.95, 3.2, "Prototype screens (synthetic lab captures)", size=9, color=ORANGE, bold=True)
w = 3.15
img1 = s.shapes.add_picture(os.path.join(ASSETS, "screen_scored_flagship.png"), Inches(6.2), Inches(1.28), width=Inches(w))
caption(s, 6.2, 1.28 + w * 234 / 774 + 0.04, 3.2, "Scored: every finding cites its evidence")
y2 = 1.28 + w * 234 / 774 + 0.42
img2 = s.shapes.add_picture(os.path.join(ASSETS, "screen_withheld_not_scored.png"), Inches(6.2), Inches(y2), width=Inches(w))
caption(s, 6.2, y2 + w * 232 / 774 + 0.04, 3.2, "Withheld: no score when the capture cannot support one")
notes(s, "Title and applicant snapshot. Name, sector and sub-theme are as shown on the online application (name from Aadhaar). "
         "Positioning sentence: NyaySaakshya turns supported email-traffic captures into evidence-linked forensic findings and "
         "reproducible reports, while explicitly identifying what the evidence cannot establish. Maturity: Working Prototype "
         "(see claim audit). Screens are synthetic lab captures from the working prototype. "
         "The sub-theme is the portal's; NyaySaakshya supports the evidence-handling step and does not itself provide "
         "financial-crime intelligence or determine that fraud occurred. No live demo URL is configured for this product.")

# ----------------------------------------------------------------------------- slide 2
s = slides[1]
body = dict(size=10.5, italic=False, color=SLATE)
set_text(shape(s, "Text 7"), ["Investigators often hold a network capture that is cut short or encrypted. Reading more into it "
                              "than it shows can produce a conclusion the evidence cannot support, and weaken a cyber-fraud case."], **body)
set_text(shape(s, "Text 10"), ["Cyber-cell and forensic investigators, and the supervisors who must defend a finding.",
                               [("Proposed first users: ", {"bold": True}), ("a Maharashtra cyber cell or forensic lab. No partner has agreed yet.", {})]],
         space_after=4, **body)
set_text(shape(s, "Text 13"), [
    "PIB cites over 17.82 lakh CFCFRMS cyber-fraud complaints (7 Oct 2025; period not stated; not email-specific).",
    "Wireshark decrypts TLS only if keys are supplied (Wireshark docs).",
    "SMTP security \"favors failing open\" (Durumeric et al., IMC 2015)."],
         size=9.5, italic=False, color=SLATE, bullet=True, space_after=3)
set_text(shape(s, "Text 16"), ["Packet tools show packets; the analyst decides what is safe to conclude. "
                               "For cut-off or encrypted captures that judgement is manual and hard to repeat or check."], **body)
set_text(shape(s, "Text 18"), ["17.82 lakh"], size=28)
set_text(shape(s, "Text 19"), ["complaints cited for the national CFCFRMS cyber-fraud system (PIB, Oct 2025)"], italic=False, size=10)
set_text(shape(s, "Text 21"), ["Each case may rest on digital evidence that must be read carefully and defended. "
                               "How many involve email is not published, so we make no claim about it."], italic=False, size=9.5)
notes(s, "Statistic: PIB backgrounder 'Curbing Cyber Frauds in Digital India', 7 Oct 2025: through CFCFRMS financial institutions "
         "saved more than Rs 5,489 crore in over 17.82 lakh complaints (period not stated). Maharashtra press figures were "
         "excluded because the primary record could not be opened. Wireshark TLS wiki: decryption needs supplied secrets. "
         "Durumeric et al., ACM IMC 2015 abstract: SMTP policies favour failing open. The email share of fraud is unknown.")

# ----------------------------------------------------------------------------- slide 3
s = slides[2]
set_text(shape(s, "Text 6"), ["NyaySaakshya reads a saved capture of email traffic and labels every fact: observed, inferred, "
                              "unknown, ambiguous, incomplete or not observable. Each finding points to its packets. "
                              "If the capture cannot support a score, it gives none."], size=10, italic=False, color=SLATE)
set_text(shape(s, "Text 12"), ["Investigator uploads a saved email-traffic capture"], size=9, italic=False, color=SLATE)
set_text(shape(s, "Text 18"), ["SHA-256 fingerprint; sessions rebuilt; standards-based rules judge only what is visible"], size=9, italic=False, color=SLATE)
set_text(shape(s, "Text 24"), ["Cited findings, a score or \"not scored\", and a report"], size=9, italic=False, color=SLATE)
tbl_shape = [x for x in s.shapes if x.has_table][0]
tbl = tbl_shape.table
rows = [["", "Packet tools alone", "NyaySaakshya"],
        ["What you get", "Packets, fields, logs", "Cited findings with an evidence state"],
        ["Cut-off or encrypted", "Analyst decides", "Marked incomplete or not observable"],
        ["Repeatable?", "Depends on the analyst", "Same capture + software, same ID"],
        ["Role", "General analysis", "Narrow: evidence-bounded triage"]]
for r, row in enumerate(rows):
    for c, txt in enumerate(row):
        cell = tbl.cell(r, c)
        tf = cell.text_frame
        p = tf.paragraphs[0]
        if p.runs:
            p.runs[0].text = txt
            for extra in p.runs[1:]:
                extra._r.getparent().remove(extra._r)
        elif txt:
            run = p.add_run()
            run.text = txt
            src = tbl.cell(0, 1).text_frame.paragraphs[0].runs[0]._r.find("{%s}rPr" % A)
            run._r.insert(0, copy.deepcopy(src))
        for run in p.runs:
            run.font.size = Pt(8.5)
            run.font.italic = False
            if r > 0 and c > 0:
                run.font.color.rgb = RGBColor.from_string(SLATE)
        if r > 0 and c == 0:
            for run in p.runs:
                run.font.bold = True
for r in tbl.rows:
    r.height = Inches(0.42)
note = copy.deepcopy(shape(s, "Text 26")._element)
s.shapes._spTree.append(note)
note_sh = [x for x in s.shapes if x._element is note][0]
note_sh.top, note_sh.height = Inches(3.86), Inches(0.2)
set_text(note_sh, ["Complements packet tools; no speed or cost comparison is made."], size=8, italic=True, color="6B7280", bold=False)
shape(s, "Text 26").top = Inches(4.08)
shape(s, "Text 27").top = Inches(4.38)
set_text(shape(s, "Text 27"), ["Every finding says how sure the evidence allows us to be, and which packets it rests on. "
                               "When a capture is not enough, it says so instead of guessing."], size=10, italic=False, color=SLATE)
notes(s, "Workflow: Capture > Analysis > Evidence-linked findings > Posture assessment > Report. Six evidence states are defined in "
         "src/nyaysaakshya/evidence/states.py and produced by reproducible captures. Frame provenance: 13,822 cited frames, 0 stream "
         "mismatches. Score withheld when unsupported (scored=false, value=null). Same capture and software give the same assessment "
         "ID (98/98 controlled captures). Comparison column for packet tools is from their documentation (Wireshark TLS wiki; Zeek "
         "smtp.log shows a tls true/false field in the documented example); we did not benchmark them. No claim of being first or only.")

# ----------------------------------------------------------------------------- slide 4
s = slides[3]
set_text(shape(s, "Text 5"), ["Current stage: Working Prototype"], size=12, bold=True, color=NAVY)
tick = shape(s, "Shape 11")
tick.fill.solid()
tick.fill.fore_color.rgb = RGBColor.from_string(ORANGE)
tf = tick.text_frame
tf.text = "✓"
tf.paragraphs[0].alignment = 2
for r in tf.paragraphs[0].runs:
    r.font.size = Pt(12)
    r.font.bold = True
    r.font.color.rgb = RGBColor.from_string(WHITE)
set_text(shape(s, "Text 12"), ["Working Prototype"], size=10, bold=True, color=ORANGE)
box = dict(size=8.5, italic=False, color=SLATE)
set_text(shape(s, "Text 19"), [
    [("Built and running: ", {"bold": True}), ("Python, TShark, React console, FastAPI, SQLite.", {})],
    [("Internal validation only: ", {"bold": True}), ("1,521 automated tests; 98 controlled captures. No external pilot, real-world accuracy benchmark or approval.", {})],
    [("Not production-ready. Missing: ", {"bold": True, "color": "B4531B"}), ("login, audit log, encrypted storage, backups, a concurrency fix.", {})]],
    space_after=3, **box)
set_text(shape(s, "Text 22"), [
    [("Local synthetic demo: ", {"bold": True}), ("no extra cost.", {})],
    [("Hosted prototype: ", {"bold": True}), ("free tiers wipe stored data when idle; Vercel Hobby is $0 for personal use only.", {})],
    [("On-premise pilot: ", {"bold": True}), ("not priced. Needs vendor quotes for a server and encrypted storage, plus security engineering.", {})],
    "Estimates only, not quotations."], space_after=3, **box)
set_text(shape(s, "Text 25"), [
    [("3 months: ", {"bold": True}), ("close the security gaps; tests pass.", {})],
    [("6 months: ", {"bold": True}), ("technical pilot on synthetic or consented captures; collect baselines.", {})],
    [("12 months: ", {"bold": True}), ("supervised single-unit pilot, only if a department agrees.", {})],
    "Proposed, not committed."], space_after=3, **box)
set_text(shape(s, "Text 28"), [
    [("None yet. ", {"bold": True}), ("Seeking one cyber cell or forensic lab for a supervised pilot. No department has agreed.", {})]],
    space_after=4, **box)
notes(s, "Stage: Working Prototype. Evidence: 1,521 tests collected and passing at baseline c0f77b9 (VALIDATION.md, DEPLOYMENT.md). "
         "Blockers are documented in DEPLOYMENT.md sections 6 and 17: no authentication or audit trail, SQLite shared-connection defect "
         "(TECH-DEBT #10), analysis time limit not enforced, no TLS or encryption at rest, no retention or backup. Costs: Vercel pricing "
         "page (Hobby $0 non-commercial); Render docs (free instances spin down and wipe files). Render paid prices and on-premise "
         "costs were not verified, so no totals are stated. Milestones are proposed, not commitments.")

# ----------------------------------------------------------------------------- slide 5
s = slides[4]
big = dict(size=20, bold=True)
set_text(shape(s, "Text 6"), ["1 pilot (target)"], **big)
set_text(shape(s, "Text 8"), ["Target: one supervised cyber-cell pilot in year one. None reached yet; no partner yet."], size=9, italic=False, color=SLATE)
set_text(shape(s, "Text 10"), ["To be measured"], **big)
set_text(shape(s, "Text 12"), ["Pilot to compare time to a first assessment and to a finished report with current practice. No baseline yet."], size=9, italic=False, color=SLATE)
set_text(shape(s, "Text 14"), ["Not claimed"], **big)
set_text(shape(s, "Text 16"), ["No evidence of job creation, so none is claimed."], size=9, italic=False, color=SLATE)
for nm in ("Text 8", "Text 12", "Text 16"):
    shape(s, nm).height = Inches(0.55)
    shape(s, nm).top = Inches(2.35)
for nm in ("Text 7", "Text 11", "Text 15"):
    shape(s, nm).top = Inches(2.05)
b5 = dict(size=9, italic=False, color=SLATE)
set_text(shape(s, "Text 19"), ["Helps investigators avoid unsupported conclusions, supporting fairer and stronger cyber-fraud cases.",
                               "Links to SDG 16 (institutions that combat crime, target 16.a).",
                               "Social impact is not yet measured."], space_after=4, **b5)
set_text(shape(s, "Text 22"), ["No revenue model is decided. The stack is open source; licences are to be confirmed.",
                               "Option to discuss with a partner: department budget or grant. No commitment exists."],
         space_after=4, **b5)
set_text(shape(s, "Text 25"), ["Demo, then close the security gaps, then one supervised cyber-cell pilot, then further units.",
                               "Each unit would run locally so evidence stays in the unit; central administration only.",
                               "Proposed; nothing is deployed."], space_after=4, **b5)
meas = copy.deepcopy(shape(s, "Text 4")._element)
s.shapes._spTree.append(meas)
meas_sh = [x for x in s.shapes if x._element is meas][0]
meas_sh.left, meas_sh.top, meas_sh.width, meas_sh.height = Inches(0.5), Inches(5.1), Inches(5.4), Inches(0.4)
for para in meas_sh.text_frame.paragraphs:
    para.alignment = 1
set_text(meas_sh, ["Pilot measures: time to first assessment, time to report, share of findings with usable provenance, correct "
                   "handling of unresolved evidence, reproducibility, supervisor confidence."], size=7.5, color="6B7280", italic=True)
notes(s, "No beneficiary, saving or jobs figure is claimed: there is no measured baseline. Targets and measurement methods are from "
         "SUBMISSION_EVIDENCE.md section 9. SDG 16 wording (target 16.a: strengthen national institutions to prevent violence and "
         "combat terrorism and crime) from the UN SDG 16 page. Technical validation (not social impact): 98 controlled captures, "
         "deterministic 98/98, 13,822 cited frames with 0 mismatches.")

# ----------------------------------------------------------------------------- slide 6
s = slides[5]
# Team of one: keep card 1 (widened), drop cards 2-4 and the mentor line.
for nm in ("Shape 10", "Shape 11", "Text 12", "Text 13", "Text 14", "Text 15",
           "Shape 16", "Shape 17", "Text 18", "Text 19", "Text 20", "Text 21",
           "Shape 22", "Shape 23", "Text 24", "Text 25", "Text 26", "Text 27", "Text 28"):
    remove(shape(s, nm))
card = shape(s, "Shape 4")
card.left, card.top, card.width, card.height = Inches(0.5), Inches(1.3), Inches(4.85), Inches(1.45)
ring = shape(s, "Shape 5")
ring.left, ring.top, ring.width, ring.height = Inches(0.72), Inches(1.5), Inches(0.9), Inches(0.9)
ini = shape(s, "Text 6")
ini.left, ini.top, ini.width, ini.height = Inches(0.72), Inches(1.5), Inches(0.9), Inches(0.9)
initials = "".join(w[0] for w in APPLICANT["name"].split() if w[0].isupper())
initials = initials[0] + initials[-1] if len(initials) > 2 else initials
set_text(ini, [initials], size=16, bold=True, color=WHITE)
for para in ini.text_frame.paragraphs:
    para.alignment = 2
nm_box, role_box, qual_box = shape(s, "Text 7"), shape(s, "Text 8"), shape(s, "Text 9")
for sh, top, h in ((nm_box, 1.46, 0.36), (role_box, 1.86, 0.3), (qual_box, 2.16, 0.5)):
    sh.left, sh.top, sh.width, sh.height = Inches(1.78), Inches(top), Inches(3.45), Inches(h)
set_text(nm_box, [APPLICANT["name"]], size=15, bold=True, color=WHITE)
set_text(role_box, ["Applicant and team lead"], size=10, bold=False, color=ORANGE)
set_text(qual_box, [APPLICANT["qualification"] or "Individual application (team size 1)"], size=9, italic=False, color="DCE3F5")


def clone_box(slide, src, left, top, w, h, paragraphs, **kw):
    el = copy.deepcopy(src._element)
    slide.shapes._spTree.append(el)
    sh = [x for x in slide.shapes if x._element is el][0]
    sh.left, sh.top, sh.width, sh.height = Inches(left), Inches(top), Inches(w), Inches(h)
    set_text(sh, paragraphs, **kw)
    return sh


panel2 = copy.deepcopy(card._element)
s.shapes._spTree.insert(list(s.shapes._spTree).index(card._element) + 1, panel2)
p2 = [x for x in s.shapes if x._element is panel2][0]
p2.left, p2.top, p2.width, p2.height = Inches(0.5), Inches(2.95), Inches(4.85), Inches(1.3)
clone_box(s, nm_box, 0.72, 3.07, 4.4, 0.3, ["Individual application"], size=12, bold=True, color=WHITE)
p2_rows = ["No other team member, mentor, partner or funder is named.",
           "Evidence of work to date: 1,521 automated tests and 98 controlled captures (internal validation; see slide 4)."]
if APPLICANT["mentor"]:
    p2_rows.insert(1, "Mentor: " + APPLICANT["mentor"])
clone_box(s, qual_box, 0.72, 3.4, 4.4, 1.0, p2_rows, size=9, italic=False, color="DCE3F5", space_after=4)
for nm in ("Shape 31", "Shape 33", "Shape 35", "Shape 39"):
    sh = shape(s, nm)
    sh.fill.solid()
    sh.fill.fore_color.rgb = RGBColor.from_string(ORANGE)
    sh.text_frame.text = "✓"
    sh.text_frame.paragraphs[0].alignment = 2
    for r_ in sh.text_frame.paragraphs[0].runs:
        r_.font.size = Pt(9)
        r_.font.bold = True
        r_.font.color.rgb = RGBColor.from_string(WHITE)
set_text(shape(s, "Text 32"), ["Mentorship & technical guidance (security)"], size=10.5, bold=True, color=SLATE)
set_text(shape(s, "Text 34"), ["Pilot with a government department"], size=10.5, bold=True, color=SLATE)
set_text(shape(s, "Text 36"), ["Funding / grant support (secure deployment)"], size=10.5, bold=True, color=SLATE)
set_text(shape(s, "Text 40"), ["Testing, certification or IP support"], size=10.5, bold=True, color=SLATE)
set_text(shape(s, "Text 41"), ["With security mentorship and one supervised pilot, we can move from a tested prototype to a measured "
                               "trial of whether NyaySaakshya helps investigators avoid unsupported conclusions."], size=9.5, italic=False, color=SLATE)
thanks = "Thank you  |  " + APPLICANT["name"] + ("  |  " + APPLICANT["contact"] if APPLICANT["contact"] else "")
set_text(shape(s, "Text 42"), [thanks], size=11)
shape(s, "Text 42").top = Inches(4.6)
notes(s, "Individual application, team size 1; name as on the portal. No teammate, mentor, qualification or contact is invented; "
         "optional lines are filled only from the APPLICANT block in build_deck.py. Support ticked (orange): "
         "mentorship and technical guidance, a supervised pilot introduction (no department has agreed), funding for secure "
         "deployment and testing, and testing/IP guidance. Incubation and workspace left unticked; the applicant may change it.")

prs.save(OUT)
print("saved", OUT, "slides:", len(prs.slides))
