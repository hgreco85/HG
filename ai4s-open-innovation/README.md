# AI4S Open Innovation — V0

**Category:** End-to-End System  
**Working title:** Phenotype Response Copilot

A lightweight, reproducible AI pipeline for microscopy phenotype analysis using public RxRx1 metadata and pretrained deep-learning embeddings.

## V0 workflow
1. Download public RxRx1 metadata and pretrained embeddings.
2. Join embeddings with experimental metadata.
3. Standardize embeddings.
4. Build phenotype prototypes for siRNA perturbations.
5. Evaluate cross-batch retrieval/classification.
6. Produce interpretable outputs and confidence margins.
7. Expose the pipeline through a Streamlit demo.

## Dataset
RxRx1 contains 125,510 fluorescence microscopy images across four cell types and 1,138 siRNA perturbations. V0 uses the official ~1 MB metadata archive and ~51 MB pretrained embedding archive instead of downloading ~46 GB of images.

Metadata: https://storage.googleapis.com/rxrx/rxrx1/rxrx1-metadata.zip

Embeddings: https://storage.googleapis.com/rxrx/rxrx1/rxrx1-dl-embeddings.zip

Dataset page: https://www.rxrx.ai/rxrx1

## Quick start

    python -m venv .venv
    pip install -r requirements.txt
    python download_data.py
    python baseline.py
    streamlit run demo.py

## Output
- artifacts/metrics.json
- artifacts/predictions.csv
- artifacts/prototypes.npz

## Competition deliverables
- Public reproducible code repository
- Demo video <= 5 minutes
- Technical report / Kaggle Writeup
- Required official registration form

## Status
V0 scaffold. Next: run cross-experiment validation, add batch-correction ablations, add microscopy visuals and package the final demo/report.

## Disclaimer
Research prototype only; not a diagnostic or clinical decision-support system.
