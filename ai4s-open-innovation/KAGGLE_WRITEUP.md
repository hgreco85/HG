# Kaggle Writeup — Phenotype Response Copilot

## Category

**End-to-End System**

## Demo Video

Public demo video: https://youtu.be/tl43Blxi2JQ

## Public Code Repository

https://github.com/hgreco85/HG/tree/main/ai4s-open-innovation

## Project Summary

Phenotype Response Copilot is a reproducible AI system for microscopy-based phenotype analysis. It addresses a recurring problem in high-content biological experiments: biological perturbation signal can be obscured by variation between experiments and cellular contexts.

The current champion, **V7 Nested Blend**, combines two transparent prototype-based views of each held-out experiment: the original standardized embedding space and an OAS-whitened space. Crucially, the RAW/OAS blend weight is selected by nested leave-one-experiment-out validation using only the outer training data.

Across 51 held-out experiments, V7 achieves **97.4938% mean accuracy** and **98.6842% median accuracy**, improving the frozen V2 baseline by **+0.2055 percentage points**. V7 wins 35 folds, ties 11 and loses 5.

## Why this is relevant to organ-on-chip

Organ-on-chip experiments can contain multiple wells, imaging sites, treatments, time points and biological contexts. The same analytical challenge appears repeatedly: separate real phenotype response from technical and contextual variability.

Phenotype Response Copilot provides a reusable pattern:

**Microscopy → embeddings → well-level aggregation → context-aware phenotype comparison → experimental triage/reporting**

The current validation uses RxRx1 rather than a real organ-on-chip dataset. The result is therefore a cross-experiment microscopy benchmark, not a direct organ-on-chip performance claim.

## Key Results

| Metric | V2 | V7 |
|---|---:|---:|
| Mean accuracy | 97.2882% | **97.4938%** |
| Median accuracy | 98.4553% | **98.6842%** |
| Mean improvement | — | **+0.2055 pp** |
| Experiments | 51 | 51 |
| Fold outcomes | — | **35 W / 11 T / 5 L** |

Hard cases:
- U2OS-04: 80.19% → **82.06%**
- U2OS-05: 92.38% → **93.61%**
- RPE-08: 94.24% → **94.97%**

## Technical approach

The pipeline:
1. downloads public RxRx1 metadata and embeddings;
2. aggregates image sites to the well level;
3. holds out one complete experiment;
4. trains only on experiments from the same cell type;
5. fits preprocessing on training only;
6. computes RAW and OAS-whitened perturbation-prototype similarities;
7. chooses the blend weight through nested experiment-level CV inside the training data;
8. applies the frozen blend to the held-out experiment.

## Validation and leakage control

The outer evaluation is leave-one-experiment-out across 51 experiments. No held-out labels or feature moments are used for scaling, covariance estimation or blend selection.

The internal metric is perturbation-classification accuracy. **This is not an official Kaggle leaderboard score.** AI4S Open Innovation is an expert-judged hackathon, with evaluation based on impact, technical innovation, validation, reproducibility and presentation.

## Reproducibility

    git clone https://github.com/hgreco85/HG.git
    cd HG/ai4s-open-innovation
    pip install -r requirements.txt
    python download_data.py
    python v2_celltype.py
    python v7_nested_blend.py
    python experiment_engine.py

No proprietary dataset or paid model API is required.

## Technical Report

https://github.com/hgreco85/HG/blob/main/ai4s-open-innovation/TECHNICAL_REPORT.md

## Limitations

The benchmark uses RxRx1 rather than real organ-on-chip data. The system is a research prototype and does not provide diagnostic or treatment recommendations.

## Next step

The highest-value next step is a small external validation on real organ-on-chip microscopy or embeddings. Further micro-tuning on the same RxRx1 benchmark has lower expected value than proving transfer to the target domain.
