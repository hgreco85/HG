from pathlib import Path
import json
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score
from sklearn.covariance import OAS

DATA = Path("data")
ART = Path("artifacts")
ART.mkdir(exist_ok=True)

def first_csv(folder):
    fs = list(folder.rglob("*.csv"))
    if not fs:
        raise FileNotFoundError(folder)
    return fs[0]

meta = pd.read_csv(first_csv(DATA / "metadata"))
emb = pd.read_csv(first_csv(DATA / "embeddings"))

candidate_keys = [["experiment","plate","well","site"], ["id_code"]]
join_keys = next((k for k in candidate_keys if all(c in meta.columns and c in emb.columns for c in k)), None)
if join_keys is None:
    shared = [c for c in meta.columns if c in emb.columns]
    if not shared:
        raise RuntimeError("Could not infer join keys")
    join_keys = shared[:1]

df = meta.merge(emb, on=join_keys, how="inner")
label_col = next(c for c in ["sirna","siRNA","perturbation","target"] if c in df.columns)
exp_col = next(c for c in ["experiment","experiment_id"] if c in df.columns)
plate_col = next((c for c in ["plate","plate_id"] if c in df.columns), None)
well_col = next((c for c in ["well","well_id"] if c in df.columns), None)

meta_cols = set(meta.columns) | set(join_keys)
features = [c for c in emb.columns if c not in meta_cols and c in df.columns and pd.api.types.is_numeric_dtype(df[c])]
if not features:
    features = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c]) and c not in set(meta.columns)]

df = df.dropna(subset=[label_col, exp_col]).copy()
df["cell_type"] = df[exp_col].astype(str).str.split("-").str[0]

group_cols = [exp_col, label_col, "cell_type"]
if plate_col:
    group_cols.append(plate_col)
if well_col:
    group_cols.append(well_col)

agg = df[group_cols + features].groupby(group_cols, as_index=False).mean(numeric_only=True)

def prototypes(X, y):
    classes = np.unique(y)
    p = np.vstack([X[y == c].mean(axis=0) for c in classes])
    return classes, p

def cosine_scores(X, P):
    Xn = X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-12)
    Pn = P / (np.linalg.norm(P, axis=1, keepdims=True) + 1e-12)
    return Xn @ Pn.T

def euclidean_scores(X, P):
    x2 = np.sum(X * X, axis=1, keepdims=True)
    p2 = np.sum(P * P, axis=1)[None, :]
    return -(x2 + p2 - 2 * X @ P.T)

def oas_whiten(Xtr, ytr, Xte):
    classes, P = prototypes(Xtr, ytr)
    residuals = np.empty_like(Xtr)
    class_to_idx = {c:i for i,c in enumerate(classes)}
    for i, c in enumerate(ytr):
        residuals[i] = Xtr[i] - P[class_to_idx[c]]

    cov = OAS(assume_centered=True).fit(residuals).covariance_
    evals, evecs = np.linalg.eigh(cov)
    floor = max(float(np.median(evals)) * 1e-4, 1e-8)
    inv_sqrt = evecs @ np.diag(1.0 / np.sqrt(np.maximum(evals, floor))) @ evecs.T

    return Xtr @ inv_sqrt, Xte @ inv_sqrt

rows = []
for test_exp in sorted(agg[exp_col].astype(str).unique()):
    test = agg[agg[exp_col].astype(str) == test_exp].copy()
    if test.empty:
        continue

    cell_type = test["cell_type"].iloc[0]
    train = agg[(agg[exp_col].astype(str) != test_exp) & (agg["cell_type"] == cell_type)].copy()
    if train.empty:
        continue

    scaler = StandardScaler()
    Xtr = scaler.fit_transform(train[features].astype(float))
    Xte = scaler.transform(test[features].astype(float))
    ytr = train[label_col].astype(str).to_numpy()
    yte = test[label_col].astype(str).to_numpy()

    classes_raw, P_raw = prototypes(Xtr, ytr)
    raw_scores = cosine_scores(Xte, P_raw)
    pred_raw = classes_raw[np.argmax(raw_scores, axis=1)]

    Xtr_w, Xte_w = oas_whiten(Xtr, ytr, Xte)
    classes_w, P_w = prototypes(Xtr_w, ytr)

    cos_scores = cosine_scores(Xte_w, P_w)
    euc_scores = euclidean_scores(Xte_w, P_w)
    pred_cos = classes_w[np.argmax(cos_scores, axis=1)]
    pred_euc = classes_w[np.argmax(euc_scores, axis=1)]

    rows.append({
        "held_out_experiment": test_exp,
        "cell_type": cell_type,
        "n_test": int(len(test)),
        "v2_raw": float(accuracy_score(yte, pred_raw)),
        "v5_oas_cosine": float(accuracy_score(yte, pred_cos)),
        "v5_oas_euclidean": float(accuracy_score(yte, pred_euc)),
    })

results = pd.DataFrame(rows)
metric_cols = ["v2_raw", "v5_oas_cosine", "v5_oas_euclidean"]
means = {c: float(results[c].mean()) for c in metric_cols}
medians = {c: float(results[c].median()) for c in metric_cols}
best = max(["v5_oas_cosine", "v5_oas_euclidean"], key=means.get)

summary = {
    "means": means,
    "medians": medians,
    "best_method": best,
    "best_mean_accuracy": means[best],
    "n_experiments": int(len(results)),
    "worst5_best_method": (
        results[["held_out_experiment", best]]
        .sort_values(best)
        .head(5)
        .to_dict(orient="records")
    ),
    "note": "OAS covariance is estimated from within-class residuals on training folds only; held-out labels and feature moments are never used."
}

results.to_csv(ART / "v5_oas_metric_results.csv", index=False)
(ART / "v5_summary.json").write_text(json.dumps(summary, indent=2))

print("\n=== V5 POR EXPERIMENTO ===")
print(results.to_string(index=False))
print("\n=== RESUMEN V5 ===")
print(json.dumps(summary, indent=2))
