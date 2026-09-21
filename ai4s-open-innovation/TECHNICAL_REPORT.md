# Phenotype Response Copilot — Technical Report

## 1. Project summary

Phenotype Response Copilot is an end-to-end research prototype for AI-assisted cellular phenotype analysis. The system uses public microscopy-derived embeddings from RxRx1 to identify genetic perturbation phenotypes across experimental batches.

The project focuses on a practical challenge in high-content biological screening: preserving biologically meaningful perturbation signal while reducing variation caused by experimental context.

The current validated V2 system achieves **97.29% mean accuracy** and **98.46% median accuracy** across **51 leave-one-experiment-out evaluations**.

## 2. Application scenario and organ-on-chip relevance

High-content microscopy experiments generate large numbers of images across wells, plates, treatments, cell types and experimental batches. A useful analytical system should distinguish phenotype signal from nuisance variation and provide transparent, reproducible outputs.

This problem is directly relevant to organ-on-chip workflows, where one experiment may contain multiple biological compartments, treatments, time points and technical replicates.

The intended adaptation path is:

**Organ-on-chip microscopy → image embeddings → aggregation by experimental unit → context-aware phenotype comparison → treatment-response ranking → experiment report**

The current benchmark uses RxRx1 rather than a real organ-on-chip dataset. Therefore, the reported accuracy demonstrates cross-experiment phenotype recovery on a public high-content microscopy benchmark and should not be interpreted as direct organ-on-chip validation.

## 3. Data

The project uses the public **RxRx1** dataset from Recursion.

RxRx1 contains fluorescence microscopy experiments across multiple cell types with siRNA perturbations. To keep reproduction lightweight, this implementation uses the official metadata plus pretrained deep-learning embeddings instead of requiring the full raw-image archive.

No private, clinical or personally identifiable data are used.

## 4. System architecture

The pipeline is:

1. download public metadata and pretrained embeddings;
2. merge embeddings with experiment metadata;
3. identify the cell type from the experiment;
4. aggregate image-site embeddings to the well level;
5. hold out one complete experiment;
6. train perturbation prototypes only from experiments of the same cell type;
7. standardize features using training data;
8. compute one mean prototype per perturbation;
9. classify held-out wells using cosine similarity;
10. save experiment-level metrics and auditable predictions.

## 5. V0 baseline

The first baseline pooled all available experiments to build perturbation prototypes.

A first single-experiment test on U2OS-05 produced:

- Accuracy: 59.71%
- Test samples: 2,440
- Features: 128
- Classes: 1,139

A broader leave-one-experiment-out evaluation later showed a mean accuracy of approximately **92.35%** across 51 experiments, revealing that U2OS-05 was one of the difficult cases rather than representative of overall performance.

## 6. V1 ablations

Two exploratory variants were tested:

- plate normalization;
- plate normalization plus PCA whitening.

Plate normalization did not materially improve the mean result, while PCA whitening reduced performance. These variants were not retained.

## 7. V2 method

V2 introduces two domain-aware changes.

### Same-cell-type training

For each held-out experiment, perturbation prototypes are built only from training experiments with the same cell type.

This avoids mixing phenotype geometry across biologically distinct cellular contexts.

### Well-level aggregation

Multiple image sites from the same well are averaged before classification.

This reduces image-level noise and makes the representation closer to the experimental unit being evaluated.

## 8. Validation protocol

Evaluation uses leave-one-experiment-out validation across **51 experiments**.

For each fold:

- one complete experiment is held out;
- all remaining experiments of the same cell type form the training set;
- training features are standardized;
- one prototype is computed per perturbation;
- each held-out well is assigned to the perturbation with highest cosine similarity.

No held-out labels are used to construct the training prototypes.

## 9. Results

| Metric | V0 | V2 |
|---|---:|---:|
| Mean accuracy | 92.35% | **97.29%** |
| Median accuracy | — | **98.46%** |
| Experiments | 51 | 51 |
| U2OS-04 | 42.29% | **80.19%** |
| U2OS-05 | 59.71% | **92.38%** |

Additional difficult V2 experiments include:

- HUVEC-05: **86.85%**
- HUVEC-18: **94.07%**
- RPE-08: **94.24%**

Most other experiments score in the high-90% range.

The main result is not just a higher aggregate score: V2 specifically improves some of the experiments that were weakest under the original formulation.

## 10. Interpretability and reliability

The model is intentionally simple and inspectable.

Every prediction is based on cosine similarity between a held-out well representation and explicit perturbation prototypes. This makes it possible to inspect:

- the selected perturbation;
- competing nearby perturbations;
- similarity margins;
- experiment-level failure cases.

The classification itself does not depend on a black-box generative model.

Reliability is reinforced through leave-one-experiment-out validation rather than random row-level splitting, which better tests robustness to experiment-level distribution shift.

## 11. Reproducibility

The public repository contains:

- public data downloader;
- environment requirements;
- V0 and V2 scripts;
- Streamlit demo;
- GitHub Actions benchmark workflow;
- automatically generated result artifacts.

The simplest reproduction path is:

**GitHub → Actions → AI4S Benchmark → Run workflow**

The benchmark can be reproduced without paid APIs or proprietary datasets.

## 12. Limitations

This project uses RxRx1 rather than real organ-on-chip experimental data.

Therefore:

- the current results should not be interpreted as direct validation on organ-on-chip systems;
- performance may differ across laboratories, assays, imaging protocols and biological systems;
- the task is perturbation identification, not clinical diagnosis or treatment recommendation;
- the system has not been validated for patient-level or clinical use.

## 13. Future work

The most relevant next steps are:

- validation on real organ-on-chip datasets;
- image-level visual explanations;
- treatment-versus-control phenotype-shift scoring;
- uncertainty calibration;
- cross-dataset generalization;
- interactive experiment-report generation.

## 14. Practical impact

The main value of the approach is that it demonstrates a low-cost and highly reproducible way to recover biological phenotype signal across experimental batches while maintaining an interpretable pipeline.

For organ-on-chip use, the architecture could support experiment triage, treatment-response comparison and automated reporting once validated on appropriate domain data.

## 15. Reproduction

    git clone https://github.com/hgreco85/HG.git
    cd HG/ai4s-open-innovation
    pip install -r requirements.txt
    python download_data.py
    python v2_celltype.py

Alternatively, use the repository's **AI4S Benchmark** GitHub Actions workflow.
