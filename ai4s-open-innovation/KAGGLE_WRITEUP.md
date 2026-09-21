# Kaggle Writeup — Phenotype Response Copilot

## Category

**End-to-End System**

## Demo Video

Public demo video: **TO ADD BEFORE SUBMISSION**

Maximum duration: 5 minutes.

## Public Code Repository

https://github.com/hgreco85/HG/tree/main/ai4s-open-innovation

## Project Summary

Phenotype Response Copilot is a reproducible AI system for microscopy-based phenotype analysis. It addresses a common problem in high-content biological experiments: biological perturbation signals can be obscured by variation between experiments, plates and cellular contexts.

The system uses public RxRx1 microscopy embeddings and experimental metadata. Rather than relying on a large black-box model, it builds interpretable perturbation prototypes and classifies held-out experiments using cosine similarity.

The validated V2 method introduces two biologically motivated changes: image sites are aggregated to the well level, and each held-out experiment is compared only with perturbation prototypes learned from the same cell type.

Across 51 leave-one-experiment-out evaluations, V2 achieves **97.29% mean accuracy** and **98.46% median accuracy**. It also substantially improves difficult U2OS experiments, including U2OS-05 from approximately 59.7% in the original single-experiment baseline to 92.4% in V2.

The complete pipeline is public and reproducible without paid services or proprietary data. A GitHub Actions workflow downloads the public data, runs the benchmark, and saves the evaluation artifacts automatically.

The current system is a research prototype rather than a clinical tool. Its next step is adaptation and validation on real organ-on-a-chip experimental datasets.

## Technical Report

See:

https://github.com/hgreco85/HG/blob/main/ai4s-open-innovation/TECHNICAL_REPORT.md

## Key Result

| Metric | V2 |
|---|---:|
| Mean accuracy | 97.29% |
| Median accuracy | 98.46% |
| Experiments | 51 |
| U2OS-04 | 80.19% |
| U2OS-05 | 92.38% |

## Reproduction

    git clone https://github.com/hgreco85/HG.git
    cd HG/ai4s-open-innovation
    pip install -r requirements.txt
    python download_data.py
    python v2_celltype.py

A manual GitHub Actions workflow is also included under **AI4S Benchmark**.

## Limitations

The current benchmark uses RxRx1 rather than real organ-on-a-chip experimental data. Results therefore demonstrate cross-experiment phenotype recovery on a public high-content microscopy benchmark, not validated performance on an organ-on-a-chip system.

The model is intended for research use only and does not provide diagnostic or treatment recommendations.
