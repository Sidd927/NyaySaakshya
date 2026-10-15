# Final deck changelog

15 October 2026. Starting point: the deck at `d07463a`. Reproducible from `submission/seva-innovation-challenge-2026/build_deck.py`. Backend, scoring, rules, tests and all application code are untouched.

## What prompted the changes

Reading the official applicant guide linked from the guidelines page ("Be a Problem Solver", Government of Maharashtra, SEEID) and re-checking the implementation. The guide's "Judges' lens" and one-page checklist asked for things the deck could answer truthfully but did not yet: a working demo, one failure and its fix, before/after impact framing (or an honest "not yet tested"), the related government owner, cost honesty, and "name any AI and say exactly what it did". See `FINAL_DECK_RED_TEAM_REVIEW.md`.

## Slide by slide

| Slide | Change | Why |
|---|---|---|
| 1 | None | Scored and "Not scored" crops, identity, sector and sub-theme were already correct and legible |
| 2 | Added "Not yet known: how often investigators meet such captures; none consulted yet" to the navy card; shortened "Why it matters" and "Who is affected"; trimmed spacing | The guide's first criterion is a real problem with evidence; saying what is unknown is more credible than implying it is known. The 17.82 lakh strip is unchanged |
| 3 | Replaced the strip (Capture, Analysis, Evidence, Finding, Posture, Report) with the implemented architecture: web upload of PCAP or PCAPNG with SHA-256; read-only TShark parse (no live capture, no decryption); sessions rebuilt with an evidence state per fact; 19 versioned rules cited to RFC or NIST, "No AI in verdicts"; posture (a score, or Not scored); JSON/HTML/PDF with packet citations. Shifted the content below down 0.1 in | The old labels were vaguer than the code, and the guide asks applicants to say whether AI was used. Not a seventh slide and no new text blocks |
| 4 | Replaced the generic "validation found and fixed cases" bullet with the measured failure and fix (41 of 44 cut-off streams wrongly asserted "no TLS" before; 1, arguable, after). Replaced "Costs not yet estimated" with "Cost not priced; a technical pilot needs no cloud service or GPU". No hosting prices (already removed) | The guide calls one honest failure the strongest credibility line; the cost line answers the guide's cost question without inventing a figure |
| 5 | Step 2 now reads "One supervised unit: a cyber cell or forensic lab"; added "Likely owner: Home Department (police cyber cells); no office approached yet"; measures box now states before and after and "the existing cost it targets is analyst time, to be measured" | The guide asks for the related department and for before/after framing, or an honest "not yet tested" |
| 6 | Added "Demonstrable now" (local demo on synthetic captures: supported finding, withheld score, report export); folded the "no other team member, mentor, partner or funder" line into the applicant card | The guide says judges trust what they can see; a demo exists, and no public link is needed |

Speaker notes: slide 3's note now describes the implemented pipeline; notes still cite public sources only.

## Considered and not done

- A seventh slide or a separate architecture slide (the template allows six).
- Hosting or cost figures (none verified).
- Naming a department as a partner (none approached).
- Putting 13,822 cited frames on a slide (it demonstrates that cited frames exist in the cited stream, not that findings are correct).
- Enlarging the slide 1 screenshots further (legible at 3.84 in; more would crowd the identity block).

## Verification

- Rebuilt from source; 6 slides; 227,561 bytes (PPTX) and 413,538 bytes (preview PDF).
- All six slides rendered at 130 dpi in LibreOffice, in the default fallback font and in a wider-font stress render (Arial in place of Nirmala UI), and inspected; overflows found in the stress render (slides 2, 3, 6) were fixed and re-rendered. Slides unchanged between renders were compared by pixel equality to the inspected images.
- Text scan of slides and notes: no placeholders, paths, emails or draft marks. The only "AI" in the deck is "No AI in verdicts".
- **Not verified:** Microsoft PowerPoint (not available here; Keynote could not be scripted). Nirmala UI is not installed on the build machine, so the applicant must open the PPTX in PowerPoint and check each slide.
