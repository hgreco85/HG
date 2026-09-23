# Kaggle Writeup — Phenotype Response Copilot

## Category

**End-to-End System**

## Demo Video

Public demo video: https://youtu.be/tl43Blxi2JQ

## Public Code Repository

https://github.com/hgreco85/HG/tree/main/ai4s-open-innovation

## Project Summary

Phenotype Response Copilot is a reproducible AI system for microscopy-based phenotype analysis.

The current champion, **V7 Nested Blend**, combines RAW and OAS-whitened prototype similarities. The blend weight is selected by nested experiment-level validation using only training data.

Across 51 held-out RxRx1 experiments, V7 achieves **97.4938% mean accuracy** and **98.6842% median accuracy**, improving frozen V2 by **+0.2055 percentage points**. It wins 35 folds, ties 11 and loses 5.

## Why this is relevant to organ-on-chip

Organ-on-chip experiments contain multiple wells, imaging sites, treatments, time points and biological contexts. The same analytical challenge appears repeatedly: distinguish biological signal from contextual and technical variability.

The reusable pattern is:

**Microscopy → embeddings → experimental-unit aggregation → context-aware phenotype comparison → experimental triage/reporting**

## Main RxRx1 validation

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

## External gut-on-chip transfer check

To test whether the adaptive idea transfers beyond RxRx1, we ran a separate public gut-on-chip microscopy experiment using Zenodo record 14745113.

We used **95 brightfield images** across **5 days** and predicted culture ratio 7:3 vs 9:1 under leave-one-day-out validation.

| Metric | Baseline | V7-style |
|---|---:|---:|
| Mean balanced accuracy | 69.57% | **70.90%** |
| Mean accuracy | 68.35% | **70.26%** |
| Balanced-accuracy delta | — | **+1.33 pp** |
| Held-out days | 5 | 5 |

Outcome: **1 improved / 4 unchanged / 0 worse**.

The signal is encouraging but preliminary: the dataset is small and most of the gain comes from Day 1. We present this as **proof of transfer**, not broad OoC validation.

## Technical approach

1. Aggregate microscopy sites to the experimental unit.
2. Hold out an entire experiment/day.
3. Fit preprocessing only on training data.
4. Compute RAW and OAS-whitened prototype similarities.
5. Select the blend weight through nested validation inside training.
6. Freeze the choice and score the held-out unit.

## Validation and leakage control

For RxRx1, the held-out experiment is never used for scaling, covariance estimation or blend selection.

For the external gut-on-chip test, the held-out day is likewise excluded from all adaptive selection.

The reported metrics are **internal validation results**, not official Kaggle leaderboard scores.

## Reproducibility

    git clone https://github.com/hgreco85/HG.git
    cd HG/ai4s-open-innovation
    pip install -r requirements.txt
    python download_data.py
    python v2_celltype.py
    python v7_nested_blend.py
    python experiment_engine.py
    python external_ooc_validation.py

## Technical Report

https://github.com/hgreco85/HG/blob/main/ai4s-open-innovation/TECHNICAL_REPORT.md

## Limitations

The external OoC dataset is small and its label is culture ratio, not treatment response or phenotype quality. The project is a research prototype and does not provide diagnostic or treatment recommendations.

## Next step

The most valuable next step is a larger external organ-on-chip validation with labels closer to treatment response, toxicity or phenotype quality.
