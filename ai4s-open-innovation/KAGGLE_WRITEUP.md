# Kaggle Writeup — Phenotype Response Copilot

## Category

**End-to-End System**

## Demo Video

Public demo video: https://youtu.be/tl43Blxi2JQ

## Public Code Repository

https://github.com/hgreco85/HG/tree/main/ai4s-open-innovation

## Project Summary

Phenotype Response Copilot is a reproducible AI system for microscopy-based phenotype analysis. It addresses a common problem in high-content biological experiments: biological perturbation signals can be obscured by variation between experiments, plates and cellular contexts.

The system uses public RxRx1 microscopy embeddings and experimental metadata. Rather than relying on a large black-box model, it builds interpretable perturbation prototypes and classifies held-out experiments using cosine similarity.

The validated V2 method introduces two biologically motivated changes: image sites are aggregated to the well level, and each held-out experiment is compared only with perturbation prototypes learned from the same cell type.

Across 51 leave-one-experiment-out evaluations, V2 achieves **97.29% mean accuracy** and **98.46% median accuracy**.

## Why this is relevant to organ-on-chip

Organ-on-chip experiments can contain multiple wells, imaging sites, treatments, time points and biological contexts. The same problem appears repeatedly: separate true phenotype response from technical and contextual variability.

Phenotype Response Copilot provides a reusable analysis pattern:

**Microscopy → embeddings → well-level aggregation → context-aware phenotype comparison → experimental triage/reporting**

The current validation uses RxRx1 rather than a real organ-on-chip dataset, so the reported accuracy is not presented as organ-on-chip validation. The contribution is a reproducible cross-experiment phenotype-analysis pipeline that can be transferred to organ-on-chip data once domain-specific embeddings and labels are available.

## Key Results

| Metric | V0 | V2 |
|---|---:|---:|
| Mean accuracy | 92.35% | **97.29%** |
| Median accuracy | — | **98.46%** |
| Experiments | 51 | 51 |
| U2OS-04 | 42.29% | **80.19%** |
| U2OS-05 | 59.71% | **92.38%** |

The improvement is particularly important in difficult U2OS experiments. This suggests that respecting biological context and using the well as the experimental unit can be more valuable than adding generic dimensionality reduction or normalization.

## Technical approach

The pipeline:

1. downloads public RxRx1 metadata and embeddings;
2. joins experiment metadata with embeddings;
3. aggregates multiple image sites to the well level;
4. holds out one complete experiment;
5. trains perturbation prototypes using only experiments from the same cell type;
6. standardizes training features;
7. classifies held-out wells by cosine similarity to perturbation prototypes;
8. saves experiment-level metrics and auditable predictions.

The model is intentionally simple and interpretable: every prediction comes from similarity to an explicit perturbation prototype.

## Validation

Evaluation uses **leave-one-experiment-out** validation across 51 experiments rather than random row-level splitting. This better tests robustness to experiment-level distribution shift.

The earlier V0 formulation achieved approximately 92.35% mean accuracy. V2 raises this to 97.29% while strongly improving the weakest U2OS cases.

## Reproducibility

The complete pipeline is public and does not require paid services or proprietary data.

The easiest reproduction path is:

**GitHub → Actions → AI4S Benchmark → Run workflow**

That workflow automatically downloads the public data, runs the benchmark, prints the metrics and uploads the generated artifacts.

Local reproduction is also available:

    git clone https://github.com/hgreco85/HG.git
    cd HG/ai4s-open-innovation
    pip install -r requirements.txt
    python download_data.py
    python v2_celltype.py

## Technical Report

https://github.com/hgreco85/HG/blob/main/ai4s-open-innovation/TECHNICAL_REPORT.md

## Limitations

The current benchmark uses RxRx1 rather than real organ-on-chip experimental data. Results therefore demonstrate cross-experiment phenotype recovery on a public high-content microscopy benchmark, not validated performance on an organ-on-chip system.

The model is intended for research use only and does not provide diagnostic or treatment recommendations.

## Next step

The highest-value next step is validation on a real organ-on-chip dataset, followed by treatment-versus-control phenotype-shift scoring, uncertainty calibration and automated experiment reporting.
