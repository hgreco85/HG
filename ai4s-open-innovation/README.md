# AI4S Open Innovation — Phenotype Response Copilot

**Category:** End-to-End System

Phenotype Response Copilot is a lightweight, reproducible AI system for microscopy-based phenotype analysis. It uses public RxRx1 embeddings to identify perturbation-specific cellular phenotypes while reducing cross-experiment variability.

## Why this matters for organ-on-chip

Organ-on-chip experiments often combine multiple wells, imaging sites, batches, treatments and biological contexts. Phenotype Response Copilot is designed as a reusable analysis layer:

**Microscopy images → embeddings → experimental-unit aggregation → context-aware phenotype comparison → experimental triage/reporting**

## Current champion: V7 Nested Blend

V7 preserves the V2 same-cell-type, well-level prototype pipeline and learns how much RAW vs OAS-whitened similarity to use **inside each outer training fold only**.

Across 51 leave-one-experiment-out RxRx1 evaluations:

| Metric | V2 | V7 |
|---|---:|---:|
| Mean accuracy | 97.2882% | **97.4938%** |
| Median accuracy | 98.4553% | **98.6842%** |
| Experiments | 51 | 51 |
| Mean delta | — | **+0.2055 pp** |
| Fold outcomes | — | **35 wins / 11 ties / 5 losses** |

By cell type:
- HEPG2: 97.0254% → **97.3650%**
- HUVEC: 97.9930% → **98.0199%**
- RPE: 97.8350% → **98.0639%**
- U2OS: 93.2806% → **93.9973%**

Selected hard cases:
- U2OS-04: 80.1948% → **82.0617%**
- U2OS-05: 92.3770% → **93.6066%**
- RPE-08: 94.2370% → **94.9675%**

## External gut-on-chip transfer check

A separate low-cost external validation was run on a public **gut-on-chip brightfield microscopy dataset** from Zenodo (record 14745113).

Task: recover the culture seeding ratio (7:3 vs 9:1) while holding out an entire day at a time.

- Images used: **95**
- Held-out days: **5**
- Baseline mean balanced accuracy: **69.57%**
- V7-style mean balanced accuracy: **70.90%**
- Delta: **+1.33 pp**
- Baseline mean accuracy: **68.35%**
- V7-style mean accuracy: **70.26%**
- Fold outcome: **1 improved / 4 unchanged / 0 worse**

The gain is preliminary and comes mainly from Day 1, so this is **evidence of transfer**, not proof of broad organ-on-chip generalization.

## Validation design and leakage control

RxRx1 evaluation is leave-one-experiment-out across 51 experiments. For each outer fold:
1. one complete experiment is held out;
2. all preprocessing is fit on outer-train only;
3. V7 selects the RAW/OAS blend weight using nested leave-one-experiment-out validation inside outer-train;
4. the held-out experiment is scored once with that frozen choice.

The gut-on-chip transfer test uses the same principle at the day level: weight selection occurs only inside the training days.

## Competition-metric note

AI4S Open Innovation is a judged hackathon, not a leaderboard competition with one official predictive metric. The 97.49% RxRx1 result and 70.90% external balanced accuracy are **internal validation metrics**, not official Kaggle scores.

## Reproduction

    git clone https://github.com/hgreco85/HG.git
    cd HG/ai4s-open-innovation
    pip install -r requirements.txt
    python download_data.py
    python v2_celltype.py
    python v7_nested_blend.py
    python experiment_engine.py

External OoC transfer:

    python external_ooc_validation.py

## Judge quick read

For a one-page competition summary focused on problem, technical contribution, evidence and claim boundaries, see `JUDGE_QUICK_READ.md`.

## Project files

- `download_data.py` — RxRx1 downloader
- `v2_celltype.py` — frozen V2 baseline
- `v7_nested_blend.py` — current champion
- `experiment_engine.py` — reproducible V2/V7 comparison
- `external_ooc_validation.py` — external gut-on-chip transfer test
- `V7_VALIDATION.md` — V7 audit
- `EXTERNAL_OOC_VALIDATION.md` — external transfer audit
- `JUDGE_QUICK_READ.md` — one-page judge summary
- `demo.py` — Streamlit interface
- `TECHNICAL_REPORT.md` — technical report
- `KAGGLE_WRITEUP.md` — submission-ready writeup

## Intended use

Research prototype only. It is not a clinical or diagnostic system.
