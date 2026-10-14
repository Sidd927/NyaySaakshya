# Applicant input required before submission

Updated 15 October 2026. The final deck (`submission/seva-innovation-challenge-2026/NyaySaakshya_Seva_Innovation_Challenge_2026.pptx`) has **no placeholders**: anything only the applicant can confirm is left out, not guessed. Items marked **MUST** block submission. Items marked **OPTIONAL** improve the deck.

## A. MUST: personal declarations and facts (portal)

| # | Item | Where | Notes |
|---|---|---|---|
| 1 | **Confirm contributors and IP.** Git history outside this branch shows another author: `Dishita0526` (a 29 Sep 2026 frontend commit touching 48 files, in the earlier `pre-rebrand-main` history) and a `Sidd_927` first commit. This branch's root commit (3 Oct 2026) is a re-initialisation under your name, and the current frontend is close to that commit's content. | IP declaration; team size; slide 6 | Decide who contributed, whether anyone else is a team member or needs to be acknowledged or consent, and what you can truthfully declare. The deck says only "individual application, no other team member named". The team lead cannot be changed after team creation (FAQ). Ask the helpdesk if team composition must change. |
| 2 | Conflict-of-interest declaration | Portal | Yours alone. |
| 3 | Consent to verification and due diligence | Portal | Yours alone. |
| 4 | Domicile: confirm you hold a certificate of Maharashtra, Chhattisgarh, DNH and DD, or Goa; upload if asked | Portal | Required for the individual (guidelines). |
| 5 | IP status and regulatory-dependency statements | Portal | Wording suggestions in `PORTAL_APPLICATION_ANSWERS.md`. The repo has no licence file. |
| 6 | Single submission under one primary sector | Portal | You submit this idea only once. |
| 7 | Final accuracy declaration | Portal | Read the exact text. |
| 8 | Team-name spelling as stored (shown as `NYAYSAakshya` / `NYAYSAKSHYA`); your name spelling (from Aadhaar) | Portal and deck | The deck uses "NyaySaakshya" and "Siddhant Hiralal Patil". Fix `APPLICANT["name"]` in `build_deck.py` if the portal differs. |
| 9 | Citizens tick and AI/ML decision | Portal | Recommended: Government officials only (Citizens optional, indirect); AI/ML unticked. |
| 10 | Open the PPTX in **PowerPoint** and check every slide | Deck | Not done: the deck was inspected only in LibreOffice with a substitute font. |

## B. OPTIONAL: deck lines left out (fill only with real, confirmed details)

Set in the `APPLICANT` block at the top of `build_deck.py`, then re-run `/tmp/pptxenv/bin/python build_deck.py` from `submission/seva-innovation-challenge-2026/` (needs `python-pptx`), or add the text in PowerPoint.

| Field | Currently | Add only if |
|---|---|---|
| `contact` (email, mobile) | omitted from slides 1 and 6 | you want it shown; the portal already holds your contact details |
| `qualification` | slide 6 shows "Individual application (team size 1)" | you give your real qualification |
| `mentor` | omitted | a real mentor or faculty guide agrees to be named |
| Photo | initials "SP" in a circle | you replace the circle with your photo in PowerPoint |
| Support ticks on slide 6 | mentorship, department pilot, funding, testing/IP ticked; incubation unticked | you disagree: change the ticks |
| Real interviews, pilots, partners, letters of support | none exist; deck says so | one becomes real and consented |

## C. Format

Guidelines say a single `.pptx`. The portal accepts PDF, PPT and PPTX up to 15 MB (transcription). Upload the **PPTX**. Do not upload `_PREVIEW.pdf` (LibreOffice render, substitute font).

## D. Helpdesk (support@sevainnovationchallenge.in, +91 91377 78135)

Team-name spelling; what the "estimated number" field accepts when no verified estimate exists; whether team composition can change after creation (relevant to item A1); whether the sub-theme fits a forensic evidence tool; whether a separate domicile or identity upload is needed; a copy of the applicant manual.
