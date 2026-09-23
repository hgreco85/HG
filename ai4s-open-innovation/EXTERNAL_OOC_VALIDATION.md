# External Gut-on-Chip Transfer Validation

## Purpose

Test whether the V7 adaptive RAW/OAS idea transfers beyond RxRx1 to a real organ-on-chip microscopy dataset.

## Dataset

Public Zenodo record **14745113**, gut-on-chip microscopy.

Subset used:
- modality: brightfield microscopy
- images: **95**
- days: **1, 2, 4, 6, 8**
- labels: culture seeding ratio **7:3 vs 9:1**

This is a proxy transfer task. The label is **not** phenotype quality, treatment response, toxicity or diagnosis.

## Protocol

Outer validation: **leave one full day out**.

For each held-out day:
1. fit image preprocessing on training days only;
2. extract pretrained ResNet18 embeddings;
3. fit RAW prototype baseline;
4. fit OAS-whitened alternative;
5. select RAW/OAS blend weight using nested validation inside training days only;
6. apply the frozen choice to the held-out day.

## Results

| Metric | Baseline | V7-style |
|---|---:|---:|
| Mean balanced accuracy | 0.6957143 | **0.7090476** |
| Mean accuracy | 0.6835088 | **0.7025564** |
| Delta balanced accuracy | — | **+0.0133333** |
| Held-out days | 5 | 5 |

Fold outcome:
- improved: **1**
- unchanged: **4**
- worse: **0**

Day 1:
- accuracy: 0.714286 → **0.809524**
- balanced accuracy: 0.800000 → **0.866667**

## Interpretation

The external signal is favorable but preliminary.

Positive evidence:
- no held-out day degraded;
- mean balanced accuracy increased by 1.33 pp;
- mean accuracy increased by 1.90 pp.

Limitations:
- only 95 images;
- only 5 outer folds;
- most gain comes from Day 1;
- target is seeding ratio rather than phenotype outcome.

Therefore the correct claim is:

> V7-style adaptation showed a positive preliminary transfer signal on a small real gut-on-chip microscopy dataset.

It should **not** be described as broad organ-on-chip validation.

## Modal run

https://modal.com/apps/hgreco85/main/ap-H85CmaMUR8PCAxELBnSRAc
