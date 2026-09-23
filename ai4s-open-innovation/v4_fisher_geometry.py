from pathlib import Path
import json
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score

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

def class_prototypes(X, y):
    classes, inv = np.unique(y, return_inverse=True)
    counts = np.bincount(inv).astype(float)
    sums = np.zeros((len(classes), X.shape[1]), dtype=float)
    np.add.at(sums, inv, X)
    protos = sums / counts[:, None]
    return classes, inv, counts, protos

def cosine_scores(Xte, protos, weights=None):
    if weights is not None:
        sw = np.sqrt(weights)[None, :]
        Xte = Xte * sw
        protos = protos * sw
    protos = protos / (np.linalg.norm(protos, axis=1, keepdims=True) + 1e-12)
    Xte = Xte / (np.linalg.norm(Xte, axis=1, keepdims=True) + 1e-12)
    return Xte @ protos.T

def fisher_weights(Xtr, inv, counts, protos, gamma):
    global_mean = Xtr.mean(axis=0)
    total_var = Xtr.var(axis=0) + 1e-12
    between = ((protos - global_mean) ** 2 * counts[:, None]).sum(axis=0) / counts.sum()
    within = np.maximum(total_var - between, 1e-8)
    fisher = between / within
    positive = fisher[fisher > 0]
    scale = np.median(positive) if len(positive) else 1.0
    base = np.maximum(fisher / max(scale, 1e-12), 1e-6)
    w = np.clip(base ** gamma, 0.25, 4.0)
    return w

rows = []
experiments = sorted(agg[exp_col].astype(str).unique())

for test_exp in experiments:
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

    classes, inv, counts, protos = class_prototypes(Xtr, ytr)
    row = {
        "held_out_experiment": test_exp,
        "cell_type": cell_type,
        "n_test": int(len(test)),
    }

    raw = cosine_scores(Xte, protos)
    row["v2_raw"] = float(accuracy_score(yte, classes[np.argmax(raw, axis=1)]))

    for gamma in (0.25, 0.50, 1.00):
        w = fisher_weights(Xtr, inv, counts, protos, gamma)
        scores = cosine_scores(Xte, protos, w)
        pred = classes[np.argmax(scores, axis=1)]
        row[f"v4_fisher_{gamma:.2f}"] = float(accuracy_score(yte, pred))

    rows.append(row)

results = pd.DataFrame(rows)
metric_cols = ["v2_raw", "v4_fisher_0.25", "v4_fisher_0.50", "v4_fisher_1.00"]
means = {c: float(results[c].mean()) for c in metric_cols}
medians = {c: float(results[c].median()) for c in metric_cols}
best = max([c for c in metric_cols if c != "v2_raw"], key=means.get)

worst = (
    results[["held_out_experiment", best]]
    .sort_values(best)
    .head(5)
    .to_dict(orient="records")
)

summary = {
    "means": means,
    "medians": medians,
    "best_method": best,
    "best_mean_accuracy": means[best],
    "n_experiments": int(len(results)),
    "worst5_best_method": worst,
    "note": "Fisher feature weights are learned from training folds only; no held-out labels or feature moments are used."
}

results.to_csv(ART / "v4_geometry_results.csv", index=False)
(ART / "v4_summary.json").write_text(json.dumps(summary, indent=2))

print("\n=== V4 POR EXPERIMENTO ===")
print(results.to_string(index=False))
print("\n=== RESUMEN V4 ===")
print(json.dumps(summary, indent=2))
