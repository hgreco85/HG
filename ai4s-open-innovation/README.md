# AI4S Open Innovation — Phenotype Response Copilot

**Category:** End-to-End System

Phenotype Response Copilot is a lightweight, reproducible AI system for microscopy-based phenotype analysis. It uses public RxRx1 embeddings to identify perturbation-specific cellular phenotypes while reducing cross-experiment variability.

## Current validated result

The current V2 benchmark uses leave-one-experiment-out validation over **51 experiments** and reports:

- **Mean accuracy:** 97.29%
- **Median accuracy:** 98.46%
- **Experiments evaluated:** 51
- **U2OS-04:** 80.19%
- **U2OS-05:** 92.38%

The V2 improvement comes from two simple but biologically meaningful choices:

1. build perturbation prototypes only from the **same cell type** as the held-out experiment;
2. average image-site embeddings to the **well level** before classification.

This substantially improved the difficult U2OS experiments while maintaining strong performance across HEPG2, HUVEC and RPE.

## Dataset

V0/V2 use the public RxRx1 dataset from Recursion. The repository downloads the official metadata and pretrained deep-learning embeddings, avoiding the need to download the full image archive.

Dataset page:
https://www.rxrx.ai/rxrx1

## Reproduce

    cd ai4s-open-innovation
    pip install -r requirements.txt
    python download_data.py
    python v2_celltype.py

Or run the GitHub Actions workflow:

**Actions → AI4S Benchmark → Run workflow**

The workflow automatically downloads the public data, runs V0 and V2, builds the benchmark summary, and uploads the generated artifacts.

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
