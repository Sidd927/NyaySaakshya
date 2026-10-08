# research/experiments

**Research infrastructure. NOT product code. NOT a prototype.**

Scripts here exist solely to execute and reproduce the experiments that informed the analysis engine.
They must never be imported by, depended on, or promoted into an application. When implementation
begins, this directory stays where it is.

| Dir | Experiment |
|---|---|
| `oq25/` | Does cross-session baselining reduce false positives? |
| `oq28/` | Does the OQ-25 result replicate on real packets? |
| `oq36/` | Does any ML model add value beyond the deterministic lanes? |
| `oq48/` | Which posture scoring formulation is defensible? |
| `oq46_47/` | Are truncated sessions classified, and does segmentation change semantics? |
| `oq33r/` | Does the pipeline behave correctly on real Postfix/Dovecot traffic? |

## Reproducing OQ-25

```bash
python3 research/experiments/oq25/run.py    # scenarios A-F
python3 research/experiments/oq25/run2.py   # keys, history sweep, adversarial cases
python3 research/experiments/oq25/run3.py   # ablation, time-aware, infrastructure framing
```

Deterministic: every corpus is seeded. No network access, no ML, no external dependencies
beyond the Python standard library.

**Design constraint honoured throughout:** ground truth lives in a separate structure
(`Corpus.truth`) and is never visible to a detector. Detectors receive only
`Corpus.observations()` — the passively observable feature vector.


## Reproducing OQ-36 (Phase-6 ML evaluation)

```bash
python3 research/experiments/oq36/genb.py      # generator B corpus (Exim dialect)
python3 research/experiments/oq36/genc.py      # generator C corpus (Zimbra/Dovecot dialect)
python3 research/experiments/oq36/dataset.py   # inventory + split integrity
python3 research/experiments/oq36/bakeoff.py   # 9 candidates, held-out evaluation
python3 research/experiments/oq36/probes.py    # ablation, generator artifact, circularity
```

Needs `scapy` (corpus generation) and `scikit-learn` (four of the nine candidates; the
stdlib candidates run without it). Results land in `oq36/results/*.json`.

Generators B and C are seeded and byte-reproducible — `tests/test_ml_dataset.py` asserts
regeneration matches the committed captures exactly. The committed corpus is ~3.2 MB;
it is kept in the repository because the evaluation in doc 17 is not independently
checkable without it.

**Design constraint honoured throughout:** labels are used for evaluation only. No fit
receives them, and the threshold is chosen from normal-session scores on a generator that
never contributed a training row.


## Reproducing OQ-48 (Phase-7 posture scoring review)

```bash
python3 research/experiments/oq48/score_review.py
```

Scores all 60 captures (OQ-28 generator A, Phase-6 generators B and C) under all three
candidate formulations and runs the property probes -- monotonicity, duplicate
resistance, recurrence behaviour, severe-finding sensitivity, long-tail behaviour and
the missing-evidence case. Results land in `oq48/results/score-review.json` and the
verdict is ADR-0016.

Needs `tshark`; no ML dependency (the review scores deterministic and cross-session
findings only, since the ML lane cannot penalise a posture score by design).


## Reproducing OQ-46 / OQ-47 (Phase-7 hardening)

```bash
python3 research/experiments/oq46_47/craft_hardening.py
PYTHONPATH=src python3 -m pytest tests/test_hardening_oq46_oq47.py -q
```

22 crafted captures with real TCP sequencing, hash-pinned in `manifest.json` and
byte-reproducible from a fixed clock and fixed MACs. Needs `scapy` to build and `tshark`
to analyse.

## Reproducing OQ-33r (real-vendor validation)

Needs Docker. See the scripts in `oq33r/` for the command sequence. The captures are
committed (64 KB); the per-run test certificate and key are git-ignored, and the pcaps
are deliberately NOT byte-reproducible because packet timings and TLS randoms differ
between runs.


## Reproducing Phase B (technical validation)

Scripts in `phaseb/` run every capture in this directory through the production pipeline and
check the result against independent expectations (raw-byte tshark oracle, generator labels,
manifests, published scoring constants). The write-up is `VALIDATION.md` at the repository root.

```bash
PYTHONPATH=src python3 research/experiments/phaseb/run_corpus.py        # first: 98 captures
python3        research/experiments/phaseb/oracle_check.py              # then, in any order:
python3        research/experiments/phaseb/label_check.py
PYTHONPATH=src python3 research/experiments/phaseb/score_check.py
python3        research/experiments/phaseb/provenance_check.py
python3        research/experiments/phaseb/oq33r_check.py
PYTHONPATH=src python3 research/experiments/phaseb/api_check.py         # starts its own backend on :8011
PYTHONPATH=src python3 research/experiments/phaseb/edge_cases.py
PYTHONPATH=src python3 research/experiments/phaseb/supplement_check.py
PYTHONPATH=src python3 research/experiments/phaseb/report_tables.py
PYTHONPATH=src python3 research/experiments/phaseb/probe_counterfactual.py
```

Outputs land in `phaseb/results/`. Needs `tshark` (validated on 4.6.8), `editcap` for the
counterfactual, and the project's test dependencies (`fastapi`, `httpx`, `pypdf`, `reportlab`,
`scapy`, `scikit-learn`). No script modifies product code, fixtures or committed result files.
