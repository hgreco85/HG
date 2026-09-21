# Demo Video Script — target duration 4:00–4:30

## 0:00–0:30 — Problem

Show the project title.

Narration:

"High-content microscopy experiments contain strong biological signals, but also substantial variation between cell types, experiments, plates and image sites. Phenotype Response Copilot is a reproducible AI system designed to recover perturbation-specific phenotype signal across these experimental contexts."

## 0:30–1:00 — Data

Show the RxRx1 dataset page and repository README.

Narration:

"We use the public RxRx1 dataset. To make reproduction lightweight, the system uses official pretrained microscopy embeddings and metadata rather than requiring the full raw-image archive."

## 1:00–1:40 — Pipeline

Show the repository files and briefly highlight `v2_celltype.py`.

Narration:

"The pipeline aggregates multiple image sites to the experimental well level. For each held-out experiment, it learns perturbation prototypes only from experiments of the same cell type. Each well is then classified using cosine similarity to those interpretable prototypes."

## 1:40–2:20 — Reproducibility

Open GitHub Actions → AI4S Benchmark.

Narration:

"The complete benchmark runs automatically in GitHub Actions. A reviewer can launch one workflow and the system downloads the public data, runs the benchmark, and saves the result artifacts. No proprietary dataset or paid API is required."

Show the successful green workflow.

## 2:20–3:20 — Results

Show the benchmark output or a simple result table.

Narration:

"Across 51 leave-one-experiment-out evaluations, V2 reaches 97.29 percent mean accuracy and 98.46 percent median accuracy. The improvement is especially visible in difficult U2OS experiments. U2OS-05, which scored about 59.7 percent in the initial baseline, reaches 92.4 percent with the V2 design."

Show:
- mean 97.29%
- median 98.46%
- U2OS-04 80.19%
- U2OS-05 92.38%

## 3:20–3:50 — Interpretability

Show the prototype approach / predictions output.

Narration:

"Predictions are based on similarity to explicit perturbation prototypes rather than an opaque generative output. This allows us to inspect competing phenotypes and failure cases."

## 3:50–4:20 — Practical value and limits

Narration:

"This is a research prototype, not a clinical system. The current validation uses RxRx1 rather than real organ-on-a-chip data. The next step is adapting the same workflow to organ-on-a-chip experiments for phenotype screening, treatment-response analysis and automated experiment triage."

## 4:20–4:30 — Closing

Show GitHub repository URL and project title.

Narration:

"Phenotype Response Copilot: lightweight, reproducible and interpretable AI for cellular phenotype analysis."
