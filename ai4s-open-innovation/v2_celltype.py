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

candidate_keys = [
    ["experiment", "plate", "well", "site"],
    ["id_code"],
]
join_keys = next((k for k in candidate_keys if all(c in meta.columns and c in emb.columns for c in k)), None)
if join_keys is None:
    shared = [c for c in meta.columns if c in emb.columns]
    if not shared:
        raise RuntimeError("Could not infer join keys")
    join_keys = shared[:1]

df = meta.merge(emb, on=join_keys, how="inner")

label_col = next(c for c in ["sirna", "siRNA", "perturbation", "target"] if c in df.columns)
exp_col = next(c for c in ["experiment", "experiment_id"] if c in df.columns)
plate_col = next((c for c in ["plate", "plate_id"] if c in df.columns), None)
well_col = next((c for c in ["well", "well_id"] if c in df.columns), None)

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

def classify(train, test):
    scaler = StandardScaler()
    Xtr = scaler.fit_transform(train[features].astype(float))
    Xte = scaler.transform(test[features].astype(float))
    ytr = train[label_col].astype(str).to_numpy()
    yte = test[label_col].astype(str).to_numpy()
    classes = np.unique(ytr)
    prototypes = np.vstack([Xtr[ytr == c].mean(axis=0) for c in classes])
    prototypes /= np.linalg.norm(prototypes, axis=1, keepdims=True) + 1e-12
    Xte /= np.linalg.norm(Xte, axis=1, keepdims=True) + 1e-12
    sim = Xte @ prototypes.T
    pred = classes[np.argmax(sim, axis=1)]
    return float(accuracy_score(yte, pred))

rows = []
experiments = sorted(agg[exp_col].astype(str).unique())
for test_exp in experiments:
    test = agg[agg[exp_col].astype(str) == test_exp].copy()
    if len(test) == 0:
        continue
    cell_type = test["cell_type"].iloc[0]
    train = agg[(agg[exp_col].astype(str) != test_exp) & (agg["cell_type"] == cell_type)].copy()
    if len(train) == 0:
        continue
    rows.append({
        "held_out_experiment": test_exp,
        "cell_type": cell_type,
        "n_train": int(len(train)),
        "n_test": int(len(test)),
        "v2_accuracy": classify(train, test),
    })

results = pd.DataFrame(rows)
summary = {
    "v2_mean_accuracy": float(results["v2_accuracy"].mean()),
    "v2_median_accuracy": float(results["v2_accuracy"].median()),
    "n_experiments": int(len(results)),
}
results.to_csv(ART / "v2_celltype_results.csv", index=False)
(ART / "v2_summary.json").write_text(json.dumps(summary, indent=2))

print("\n=== V2 POR EXPERIMENTO ===")
print(results.to_string(index=False))
print("\n=== RESUMEN V2 ===")
print(json.dumps(summary, indent=2))
