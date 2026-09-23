# Phenotype Response Copilot — Technical Report

## 1. Project summary

Phenotype Response Copilot is an end-to-end research prototype for AI-assisted cellular phenotype analysis using public RxRx1 microscopy-derived embeddings.

The current validated champion, **V7 Nested Blend**, reaches **97.4938% mean accuracy** and **98.6842% median accuracy** across **51 leave-one-experiment-out evaluations**. Relative to the frozen V2 baseline, mean accuracy improves by **+0.2055 percentage points**.

## 2. Application scenario and organ-on-chip relevance

High-content microscopy experiments generate images across wells, plates, treatments, cell types and experimental batches. The intended analysis pattern is:

**Organ-on-chip microscopy → embeddings → aggregation by experimental unit → context-aware phenotype comparison → treatment-response ranking → experiment report**

Current validation uses RxRx1 rather than real organ-on-chip data. The reported accuracy demonstrates cross-experiment phenotype recovery on a public microscopy benchmark and is not a direct organ-on-chip performance claim.

## 3. Data

The project uses public RxRx1 metadata and pretrained embeddings from Recursion. No private, clinical or personally identifiable data are used.

## 4. Frozen V2 baseline

V2:
1. aggregates image sites to the well level;
2. holds out one complete experiment;
3. restricts training to the same cell type;
4. fits StandardScaler on training only;
5. builds one perturbation prototype per class;
6. classifies held-out wells by cosine similarity.

V2 result:
- mean accuracy: **97.2882%**
- median accuracy: **98.4553%**
- experiments: **51**

## 5. V3–V6 exploration

Several low-cost challengers were tested under the same 51-experiment outer validation:
- V3 batch correction: 97.2914%
- V4 Fisher-weighted geometry: 97.2882%
- V5 OAS metric: 97.2453%
- V6 nested adaptive RAW/OAS choice: 97.3553%

V5 revealed an important pattern: OAS helped U2OS but harmed HUVEC, motivating a leakage-safe adaptive approach.

## 6. V7 Nested Blend

V7 combines RAW and OAS-whitened cosine similarity scores.

Candidate RAW weights are:
- 0.25
- 0.50
- 0.75

For each outer fold, the weight is chosen by **nested leave-one-experiment-out cross-validation using only the outer training data**. The selected weight is then frozen and applied once to the held-out experiment.

This avoids selecting a method or weight using the outer evaluation labels.

## 7. Validation protocol

Outer validation: leave one complete experiment out across 51 experiments.

Within each outer training set:
- StandardScaler is fit on training only.
- OAS covariance is estimated from within-class residuals on training only.
- RAW/OAS blend weight is selected using nested experiment-level CV.
- The held-out experiment is not used in preprocessing or hyperparameter selection.

The task metric used internally is classification accuracy because the experiment measures perturbation recovery. However, AI4S Open Innovation itself does **not** define one official predictive leaderboard metric; it is judged on project-level criteria.

## 8. V7 results

| Metric | V2 | V7 |
|---|---:|---:|
| Mean accuracy | 97.2882% | **97.4938%** |
| Median accuracy | 98.4553% | **98.6842%** |
| Delta | — | **+0.2055 pp** |
| Experiments | 51 | 51 |

Per-fold comparison:
- wins: **35**
- ties: **11**
- losses: **5**
- median fold delta: **+0.1623 pp**
- standard deviation of fold delta: **0.3537 pp**

An exact sign test over non-tied folds gives a two-sided p-value of approximately **1.38×10⁻⁶**, supporting that the improvement is not driven by only one or two folds.

By cell type:
- HEPG2: 97.0254% → **97.3650%**
- HUVEC: 97.9930% → **98.0199%**
- RPE: 97.8350% → **98.0639%**
- U2OS: 93.2806% → **93.9973%**

Selected hard cases:
- U2OS-04: 80.1948% → **82.0617%**
- U2OS-05: 92.3770% → **93.6066%**
- RPE-08: 94.2370% → **94.9675%**

Largest observed degradations were small and concentrated in HUVEC:
- HUVEC-15: −0.3290 pp
- HUVEC-18: −0.3250 pp

## 9. Reliability and limitations

Strengths:
- complete experiment holdout rather than row-level random split;
- preprocessing fit on training only;
- nested selection for the blend weight;
- explicit, inspectable perturbation prototypes;
- deterministic public-data pipeline.

Limitations:
- RxRx1 is not an organ-on-chip dataset;
- perturbation identification is a proxy task, not treatment efficacy or toxicity prediction;
- no cross-dataset external validation has yet been performed;
- a strong internal accuracy result is not an official Kaggle judge score.

## 10. Competition alignment

AI4S Open Innovation is judged on:
- Problem Importance & Potential Impact — 30%
- Technical Approach & Innovation — 30%
- Results & Validation — 20%
- Reproducibility & Implementation Quality — 10%
- Presentation Quality — 10%

V7 primarily strengthens the Results & Validation and Technical Approach sections. The largest remaining gap is direct validation on real organ-on-chip data.

## 11. Reproduction

    git clone https://github.com/hgreco85/HG.git
    cd HG/ai4s-open-innovation
    pip install -r requirements.txt
    python download_data.py
    python v2_celltype.py
    python v7_nested_blend.py
    python experiment_engine.py

The Railway → Modal path provides the same low-cost automated benchmark.

## 12. Practical impact

The system demonstrates a reproducible method for recovering biological phenotype signal under experiment-level distribution shift while retaining a transparent prototype-based decision process. The next scientifically meaningful step is external organ-on-chip validation rather than further micro-tuning on RxRx1.
