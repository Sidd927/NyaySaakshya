# Applicant input required

The definitive field-by-field entry guide is `PORTAL_FIELD_BY_FIELD_FINAL.md`. Applicant-provided statements (not independently verified): you agree with the compliance consent; you are not related to, employed by or professionally linked with the organisers or jury (portal answer: No); you submit as an individual; Dishita is a friend who helped with some frontend work and is not a team member.

Updated 15 October 2026 (Phase H). Only things that **you** must supply, decide or declare. Everything else is finished. The final deck (`submission/seva-innovation-challenge-2026/NyaySaakshya_Seva_Innovation_Challenge_2026.pptx`) has **no placeholders**: details only you can confirm are left out, not guessed.

## A. Personal facts to supply (before you submit)

| # | What | Why it matters |
|---|---|---|
| 1 | **IP and contributor facts.** Dishita (a friend who helped with some frontend work) is not a team member and is not added as one. Answer, in your own words: did she agree her frontend contributions can be included in this project and submitted by you (written is best)? Did she assign or license them to you, or keep rights? Should she be acknowledged? Does any employer, college or funder have a claim? Is `Sidd_927` your other GitHub account? | The IP declaration and due diligence (6 to 10 Nov) ask about ownership. The repository's older history shows a 29 Sep 2026 frontend commit by Dishita's GitHub account (48 files) and the current frontend is close to it. The deck makes no claim of sole authorship |
| 2 | **Domicile:** do you hold a certificate of Maharashtra, Chhattisgarh, Dadra and Nagar Haveli and Daman and Diu, or Goa? Have the file ready. | Required for the individual applicant (official guidelines) |
| 3 | **Name spelling:** your name (from Aadhaar) and the stored team name (`NYAYSAakshya` / `NYAYSAKSHYA` as transcribed) | The deck says "Siddhant Hiralal Patil" and "NyaySaakshya". If the portal differs, edit `APPLICANT["name"]` in `build_deck.py` or fix it in PowerPoint |

## B. Declarations only you can make (never answered by me)

Consent to verification and due diligence; conflict of interest; domicile; IP status; regulatory dependencies; originality and single submission under one sector; final accuracy declaration. Wording suggestions are in `PORTAL_APPLICATION_ANSWERS.md`.

## C. Decisions only you can make

| # | Decision | Recommendation |
|---|---|---|
| 0 | Tested/piloted dropdown | "Testing in progress" (internal testing, no external pilot); field 10 must say there is no external pilot |
| 1 | Stage option | "Working prototype (TRL 5-6)" if comfortable saying "lab-validated, no external pilot"; "Concept validated (TRL 3-4)" is the conservative alternative |
| 2 | Estimated number affected | "No verified estimate" (text); if number-only, ask the helpdesk, else `1` with explanation. Never 17.82 lakh |
| 3 | Beneficiaries | Government officials; Citizens only as an indirect, optional tick |
| 4 | AI/ML checkbox | Leave unticked |
| 5 | Support asks on slide 6 | Mentorship, supervised pilot unit, testing/IP guidance, funding for a secure pilot build ticked; untick funding if you do not want to ask |
| 6 | Whether to keep speaker notes in the PPTX | They hold public sources only; delete in PowerPoint if you prefer |

## D. Checks only you can do

1. Open the PPTX **in PowerPoint** and check all six slides (the deck was inspected through LibreOffice and, for slide 1, macOS Quick Look; never PowerPoint).
2. Log in and read every field's character limit and mandatory flag; shorten answers from the "Short version" lines where needed.
3. Confirm the live form's stage options match the public wizard's list.

## E. Optional, only if real

| Item | Effect |
|---|---|
| Your qualification or experience (one line) | The biggest credibility gain on slide 6; set `APPLICANT["qualification"]` in `build_deck.py` or type it in PowerPoint |
| A real mentor or faculty guide, with consent | `APPLICANT["mentor"]` |
| Contact line on the slides (the portal already holds your contact details) | `APPLICANT["contact"]` |
| A photo (replace the "SP" circle in PowerPoint) | cosmetic |
| One real conversation with an investigator, truthfully reported | strongest evidence for the problem premise; none exists today |
| A short demo video of the synthetic demo (script in `DEPLOYMENT_GO_NO_GO.md`) | No video exists. Only record, inspect and share it as an unlisted link if you choose |
| Choose a licence for NyaySaakshya | Resolves the "licence not yet chosen" line on slide 5 |

## F. Helpdesk (support@sevainnovationchallenge.in, +91 91377 78135)

Ask in one email: exact stored team-name spelling and whether it can be corrected; what "estimated number affected" accepts when no verified estimate exists; whether the "Law and Order / Cyber-Fraud, Digital Extortion and Financial-Crime Intelligence" sub-theme suits an evidence-handling tool; whether a separate identity or domicile upload is needed; whether team composition can change; whether the applicant manual can be shared.

## G. Repository facts (resolved)

`README.md` and `VALIDATION.md` said "1521 passed, 0 failed". That was not reproducible from the committed baseline because a code-freeze guard referenced the old tag `v1.0.0-nyaysaakshya`. In the final execution pass the guard was re-baselined to `v1.1.0-validation-baseline`, and the full suite now passes (1,521 passed, 0 failed). Nothing for you to do.
