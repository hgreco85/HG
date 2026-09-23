# V7 Validation Audit

## Status

**PROMOTED** from V2 after a deterministic Railway → Modal run.

Modal run:
https://modal.com/apps/hgreco85/main/ap-aCMLTCujLHb7kgVTIJbuRm

## Same-validation comparison

Outer protocol: leave-one-experiment-out over 51 experiments.

| Metric | V2 | V7 |
|---|---:|---:|
| Mean accuracy | 0.9728823172 | **0.9749375598** |
| Median accuracy | 0.9845528455 | **0.9868421053** |
| Delta | — | **+0.0020552426** |

Fold-level:
- 35 wins
- 11 ties
- 5 losses
- mean delta: +0.0020553
- median delta: +0.001623
- standard deviation of fold delta: 0.0035366
- exact two-sided sign test (non-tied folds): p ≈ 1.38e-6

## By cell type

| Cell type | V2 | V7 | Delta |
|---|---:|---:|---:|
| HEPG2 | 0.9702542 | **0.9736495** | +0.0033953 |
| HUVEC | 0.9799303 | **0.9801989** | +0.0002687 |
| RPE | 0.9783495 | **0.9806393** | +0.0022897 |
| U2OS | 0.9328060 | **0.9399729** | +0.0071668 |

## Selected hard cases

- U2OS-04: 0.801948 → **0.820617**
- U2OS-05: 0.923770 → **0.936066**
- RPE-08: 0.942370 → **0.949675**

Largest degradations:
- HUVEC-15: 0.990132 → 0.986842
- HUVEC-18: 0.940699 → 0.937449

## Leakage audit

V7 is nested:
- outer held-out experiment is never used to fit StandardScaler;
- outer held-out experiment is never used to estimate OAS covariance;
- outer held-out labels are never used to select the RAW/OAS blend weight;
- blend selection is performed by inner leave-one-experiment-out CV using outer-train only.

## Reproduce

    python download_data.py
    python v2_celltype.py
    python v7_nested_blend.py
    python experiment_engine.py

Expected engine decision:

    PROMOTE

with a promotion threshold of +0.001 absolute mean accuracy.
