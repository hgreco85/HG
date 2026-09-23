# Phenotype Response Copilot — Judge Quick Read

## 30-second summary

Phenotype Response Copilot is a transparent, reproducible AI system for microscopy-based phenotype analysis under experiment-level distribution shift.

The current champion, **V7 Nested Blend**, combines RAW and OAS-whitened prototype similarities and chooses the blend weight using nested validation **inside training only**.

## Why it matters

Organ-on-chip and high-content microscopy experiments often vary across wells, batches, days, treatments and biological contexts. A useful system should recover biological signal without learning shortcuts from the held-out experiment.

The system is designed around that exact failure mode.

## What is technically different

- experimental-unit aggregation instead of image-level voting;
- same-context prototype construction;
- RAW + OAS feature geometry;
- nested leave-one-experiment-out blend selection;
- explicit leakage control;
- auditable, non-generative predictions.

## Main evidence

### RxRx1 controlled benchmark

Across **51 leave-one-experiment-out experiments**:

- V2 mean accuracy: **97.2882%**
- V7 mean accuracy: **97.4938%**
- improvement: **+0.2055 pp**
- median accuracy: **98.6842%**
- fold outcomes: **35 wins / 11 ties / 5 losses**

Selected hard cases:
- U2OS-04: 80.19% → **82.06%**
- U2OS-05: 92.38% → **93.61%**
- RPE-08: 94.24% → **94.97%**

### External gut-on-chip transfer check

Public gut-on-chip brightfield microscopy, Zenodo record 14745113.

- images: **95**
- held-out days: **5**
- baseline balanced accuracy: **69.57%**
- V7-style balanced accuracy: **70.90%**
- delta: **+1.33 pp**
- outcome: **1 improved / 4 unchanged / 0 worse**

This is presented as **preliminary transfer evidence**, not broad organ-on-chip validation.

## Reproducibility

Everything is public and scriptable:

- data downloader
- V2 baseline
- V7 implementation
- experiment engine
- external OoC validation script
- technical report
- validation audits
- Streamlit demo

Repository:
https://github.com/hgreco85/HG/tree/main/ai4s-open-innovation

## Video note

The public demo video was recorded with the validated V2 system. The core workflow remains unchanged. V7 and the external OoC validation were completed afterward and are documented in the repository and current writeup.

Video:
https://youtu.be/tl43Blxi2JQ

## Claim boundary

The project does **not** claim clinical validity or broad organ-on-chip generalization. The strongest supported claim is:

> A transparent, leakage-controlled phenotype-matching system showed strong cross-experiment validation on RxRx1 and a positive preliminary transfer signal on a small real gut-on-chip microscopy dataset.
