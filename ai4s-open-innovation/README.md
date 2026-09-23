# AI4S Open Innovation — Phenotype Response Copilot

**Category:** End-to-End System

Phenotype Response Copilot is a lightweight, reproducible AI system for microscopy-based phenotype analysis. It uses public RxRx1 embeddings to identify perturbation-specific cellular phenotypes while reducing cross-experiment variability.

## Why this matters for organ-on-chip

Organ-on-chip experiments often combine multiple wells, imaging sites, batches, treatments and biological contexts. That makes it difficult to tell whether a phenotype shift reflects a real biological response or experimental variability.

Phenotype Response Copilot is designed as a reusable analysis layer:

**Microscopy images → embeddings → well-level aggregation → context-aware phenotype comparison → experimental triage/reporting**

The current validation uses RxRx1 rather than a real organ-on-chip dataset, so the reported accuracy is a proof of cross-experiment phenotype recovery, not an organ-on-chip performance claim.

## Current validated result

The current champion is **V7 Nested Blend**. It preserves the V2 same-cell-type, well-level prototype pipeline and learns how much RAW vs OAS-whitened similarity to use **inside each outer training fold only**.

Across 51 leave-one-experiment-out evaluations:

| Metric | V2 | V7 |
|---|---:|---:|
| Mean accuracy | 97.2882% | **97.4938%** |
| Median accuracy | 98.4553% | **98.6842%** |
| Experiments | 51 | 51 |
| Mean delta | — | **+0.2055 pp** |
| Fold outcomes | — | **35 wins / 11 ties / 5 losses** |

By cell type, mean accuracy moved from V2 → V7:

- HEPG2: 97.0254% → **97.3650%**
- HUVEC: 97.9930% → **98.0199%**
- RPE: 97.8350% → **98.0639%**
- U2OS: 93.2806% → **93.9973%**

Hard cases improved materially:
- U2OS-04: 80.1948% → **82.0617%**
- U2OS-05: 92.3770% → **93.6066%**
- RPE-08: 94.2370% → **94.9675%**

## Validation design and leakage control

Evaluation is leave-one-experiment-out across 51 experiments. For each outer fold:
1. one complete experiment is held out;
2. all preprocessing is fit on outer-train only;
3. V7 selects the RAW/OAS blend weight using nested leave-one-experiment-out validation inside the outer training set;
4. the held-out experiment is scored once with that frozen choice.

Held-out labels are never used to choose the blend weight.

## Important competition-metric note

AI4S Open Innovation is a judged hackathon, not a leaderboard competition with one official predictive metric. The 97.49% figure is therefore an **internal validation result**, not an official Kaggle score. The official judging criteria weight impact, technical innovation, validation, reproducibility and presentation.

## Dataset

V2/V7 use the public RxRx1 dataset from Recursion. The repository downloads official metadata and pretrained embeddings, avoiding the full image archive.

Dataset page:
https://www.rxrx.ai/rxrx1

## Reproduction

    git clone https://github.com/hgreco85/HG.git
    cd HG/ai4s-open-innovation
    pip install -r requirements.txt
    python download_data.py
    python v2_celltype.py
    python v7_nested_blend.py

For the automated comparison:

    python experiment_engine.py

The same benchmark is also wired to Railway → Modal for low-cost remote execution.

## Project files

- `download_data.py` — public-data downloader
- `v2_celltype.py` — frozen V2 baseline
- `v7_nested_blend.py` — current validated champion
- `experiment_engine.py` — reproducible V2/V7 comparison and promotion gate
- `V7_VALIDATION.md` — audit summary of the promoted result
- `demo.py` — lightweight Streamlit interface
- `TECHNICAL_REPORT.md` — technical report
- `KAGGLE_WRITEUP.md` — submission-ready writeup

## Intended use

Research prototype only. It is not a clinical or diagnostic system.
