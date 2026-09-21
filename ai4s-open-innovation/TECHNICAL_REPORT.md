# Phenotype Response Copilot — Technical Report Draft

## Category
End-to-End System

## 1. Problem
High-content biological experiments are affected by technical variation across batches, plates and experimental conditions. A useful AI system should preserve biologically meaningful phenotype information while remaining robust to nuisance variation.

## 2. Proposed system
Phenotype Response Copilot converts microscopy-derived embeddings and experiment metadata into normalized phenotype representations, perturbation prototypes, cross-batch predictions, confidence diagnostics and an auditable interactive report.

## 3. Data
V0 uses public RxRx1 data from Recursion. To keep reproduction lightweight, it consumes the official pretrained embedding archive and metadata rather than requiring the full image archive.

## 4. Method
V0 joins embeddings to metadata, standardizes features on training batches, holds out an experiment, estimates a normalized centroid per perturbation and classifies held-out samples by cosine similarity.

## 5. Validation plan
Final validation will include multiple held-out experiments, cell-type stratification, batch-correction ablations, PCA/whitening, nearest-centroid versus linear models, bootstrap intervals and failure-case analysis.

## 6. Interpretability
Prototype similarity is inspectable and confidence margin exposes ambiguous cases rather than hiding uncertainty.

## 7. Reliability and limitations
RxRx1 is a research dataset and does not directly represent an organ-on-a-chip clinical workflow. Performance may not transfer to other assays, labs, cell types or imaging systems. This system is not for diagnosis or treatment decisions.

## 8. Next step
V1 will add batch-aware correction plus an agentic experiment-report layer that compares perturbation/control phenotype shifts and generates evidence-linked research summaries.
