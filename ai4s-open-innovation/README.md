# AI4S Open Innovation — Phenotype Response Copilot

**Category:** End-to-End System

Phenotype Response Copilot is a lightweight, reproducible AI system for microscopy-based phenotype analysis. It uses public RxRx1 embeddings to identify perturbation-specific cellular phenotypes while reducing cross-experiment variability.

## Why this matters for organ-on-chip

Organ-on-chip experiments often combine multiple wells, imaging sites, batches, treatments and biological contexts. That makes it difficult to tell whether a phenotype shift reflects a real biological response or experimental variability.

Phenotype Response Copilot is designed as a reusable analysis layer for that setting:

**Microscopy images → embeddings → well-level aggregation → context-aware phenotype comparison → experimental triage/reporting**

The current validation uses RxRx1 rather than a real organ-on-chip dataset, so the reported accuracy is a proof of cross-experiment phenotype recovery, not an organ-on-chip performance claim. The same pipeline can be adapted to organ-on-chip experiments by replacing the input embeddings and defining the relevant biological context and treatment labels.

## Current validated result

The current V2 benchmark uses leave-one-experiment-out validation over **51 experiments** and reports:

| Metric | V0 | V2 |
|---|---:|---:|
| Mean accuracy | 92.35% | **97.29%** |
| Median accuracy | — | **98.46%** |
| Experiments evaluated | 51 | 51 |
| U2OS-04 | 42.29% | **80.19%** |
| U2OS-05 | 59.71% | **92.38%** |

The V2 improvement comes from two simple but biologically meaningful choices:

1. build perturbation prototypes only from the **same cell type** as the held-out experiment;
2. average image-site embeddings to the **well level** before classification.

This substantially improved the difficult U2OS experiments while maintaining strong performance across HEPG2, HUVEC and RPE.

## Dataset

V0/V2 use the public RxRx1 dataset from Recursion. The repository downloads the official metadata and pretrained deep-learning embeddings, avoiding the need to download the full image archive.

Dataset page:
https://www.rxrx.ai/rxrx1

## One-click reproduction

The easiest way to reproduce the benchmark is:

**GitHub → Actions → AI4S Benchmark → Run workflow**

The workflow automatically:

1. installs dependencies;
2. downloads RxRx1 metadata and embeddings;
3. runs the benchmark;
4. prints the results;
5. uploads the generated artifacts.

No paid API or proprietary dataset is required.

## Local reproduction

    cd ai4s-open-innovation
    pip install -r requirements.txt
    python download_data.py
    python v2_celltype.py

## Project files

- `download_data.py` — public-data downloader
- `baseline.py` — original prototype baseline
- `v2_celltype.py` — validated V2 method
- `demo.py` — lightweight Streamlit interface
- `TECHNICAL_REPORT.md` — technical report
- `KAGGLE_WRITEUP.md` — submission-ready writeup
- `DEMO_SCRIPT.md` — <=5 minute demo-video script
- `SUBMISSION_CHECKLIST.md` — final submission checklist

## Intended use

This is a research prototype for phenotype analysis and experimental triage. It is **not** a clinical or diagnostic system.
