# Phenotype Response Copilot — Technical Report

## 1. Project summary

Phenotype Response Copilot is an end-to-end research prototype for AI-assisted cellular phenotype analysis.

The current validated champion, **V7 Nested Blend**, reaches **97.4938% mean accuracy** and **98.6842% median accuracy** across **51 leave-one-experiment-out RxRx1 evaluations**. Relative to frozen V2, mean accuracy improves by **+0.2055 percentage points**.

A second, external proof-of-transfer was also run on a public gut-on-chip microscopy dataset. On 95 brightfield images evaluated with leave-one-day-out validation, the V7-style adaptive blend improved mean balanced accuracy from **69.57% to 70.90%** and mean accuracy from **68.35% to 70.26%**.

## 2. Application scenario and organ-on-chip relevance

The intended analysis pattern is:

**Organ-on-chip microscopy → embeddings → aggregation by experimental unit → context-aware phenotype comparison → treatment-response ranking → experiment report**

RxRx1 remains the main controlled benchmark. The external gut-on-chip test adds a small real-domain transfer check, but it is not sufficient to claim broad organ-on-chip validation.

## 3. Data

### RxRx1
Public metadata and pretrained embeddings from Recursion.

### External gut-on-chip transfer dataset
Public Zenodo record 14745113, using the brightfield subset only. The transfer task is culture seeding-ratio recovery (7:3 vs 9:1), not phenotype quality, diagnosis or treatment efficacy.

No private, clinical or personally identifiable data are used.

## 4. Frozen V2 baseline

V2:
1. aggregates image sites to the well level;
2. holds out one complete experiment;
3. restricts training to the same cell type;
4. fits StandardScaler on training only;
5. builds one perturbation prototype per class;
6. classifies held-out wells by cosine similarity.

V2:
- mean accuracy: **97.2882%**
- median accuracy: **98.4553%**
- experiments: **51**

## 5. V3–V6 exploration

Low-cost challengers under the same 51-experiment outer validation:
- V3 batch correction: 97.2914%
- V4 Fisher geometry: 97.2882%
- V5 OAS metric: 97.2453%
- V6 nested adaptive RAW/OAS choice: 97.3553%

V5 showed that OAS helped U2OS but could hurt HUVEC, motivating a blend rather than a hard switch.

## 6. V7 Nested Blend

V7 combines RAW and OAS-whitened cosine similarity scores.

Candidate RAW weights:
- 0.25
- 0.50
- 0.75

For each outer fold, the weight is chosen by **nested leave-one-experiment-out cross-validation using only outer training data**. The selected weight is frozen before the held-out experiment is scored.

## 7. RxRx1 validation

| Metric | V2 | V7 |
|---|---:|---:|
| Mean accuracy | 97.2882% | **97.4938%** |
| Median accuracy | 98.4553% | **98.6842%** |
| Delta | — | **+0.2055 pp** |
| Experiments | 51 | 51 |

Per-fold:
- wins: **35**
- ties: **11**
- losses: **5**
- median delta: **+0.1623 pp**
- std. dev. of fold delta: **0.3537 pp**

By cell type:
- HEPG2: 97.0254% → **97.3650%**
- HUVEC: 97.9930% → **98.0199%**
- RPE: 97.8350% → **98.0639%**
- U2OS: 93.2806% → **93.9973%**

## 8. External gut-on-chip transfer validation

The external test uses pretrained ResNet18 image embeddings from 95 brightfield microscopy images and predicts culture ratio 7:3 vs 9:1.

Validation: **leave one complete day out** across five days.

| Metric | Baseline | V7-style |
|---|---:|---:|
| Mean balanced accuracy | 69.57% | **70.90%** |
| Mean accuracy | 68.35% | **70.26%** |
| Delta balanced accuracy | — | **+1.33 pp** |
| Days | 5 | 5 |

Fold outcome:
- **1 improved**
- **4 unchanged**
- **0 worse**

Day 1:
- accuracy: 71.43% → **80.95%**
- balanced accuracy: 80.00% → **86.67%**

The other four held-out days were unchanged by the adaptive selection.

Interpretation: this is a favorable **proof-of-transfer signal**, not conclusive external validation. The sample is small and most of the gain comes from one held-out day.

## 9. Leakage and reliability

RxRx1:
- outer held-out experiment never used for scaling;
- outer held-out experiment never used for OAS covariance;
- outer held-out labels never used for blend selection;
- blend selection occurs inside outer-train only.

Gut-on-chip:
- one day is held out entirely;
- blend selection uses training days only;
- held-out day labels are not used for weight selection.

## 10. Limitations

- RxRx1 remains the primary benchmark.
- The external dataset is small: 95 images and 5 held-out days.
- The external label is seeding ratio, not phenotype quality or therapeutic response.
- The external improvement is concentrated in one day.
- No clinical claims are supported.
- Neither internal metric is an official Kaggle leaderboard score.

## 11. Reproducibility

    git clone https://github.com/hgreco85/HG.git
    cd HG/ai4s-open-innovation
    pip install -r requirements.txt
    python download_data.py
    python v2_celltype.py
    python v7_nested_blend.py
    python experiment_engine.py
    python external_ooc_validation.py

## 12. Practical impact

The project now demonstrates two complementary forms of evidence:
1. strong experiment-level validation on RxRx1;
2. a small but positive external transfer signal on real gut-on-chip microscopy.

The highest-value next scientific step is a larger external OoC dataset with labels closer to phenotype quality, treatment response or toxicity—not further micro-tuning on RxRx1.
