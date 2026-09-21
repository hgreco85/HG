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

def proto_scores(Xtr, ytr, Xte):
    classes = np.unique(ytr)
    protos = np.vstack([Xtr[ytr == c].mean(axis=0) for c in classes])
    protos /= np.linalg.norm(protos, axis=1, keepdims=True) + 1e-12
    Xte_n = Xte / (np.linalg.norm(Xte, axis=1, keepdims=True) + 1e-12)
    return classes, Xte_n @ protos.T

def global_standardize(train, test):
    sc = StandardScaler()
    return sc.fit_transform(train[features].astype(float)), sc.transform(test[features].astype(float))

def experiment_center(train, test):
    Xtr = train[features].astype(float).copy()
    Xte = test[features].astype(float).copy()

    # Unsupervised batch correction: normalize each experiment using feature moments only.
    tr_keys = train[exp_col].astype(str)
    te_keys = test[exp_col].astype(str)

    tr_mean = Xtr.groupby(tr_keys).transform("mean")
    tr_std = Xtr.groupby(tr_keys).transform("std").replace(0, 1).fillna(1)
    Xtrn = ((Xtr - tr_mean) / tr_std).replace([np.inf, -np.inf], 0).fillna(0)

    te_mean = Xte.groupby(te_keys).transform("mean")
    te_std = Xte.groupby(te_keys).transform("std").replace(0, 1).fillna(1)
    Xten = ((Xte - te_mean) / te_std).replace([np.inf, -np.inf], 0).fillna(0)

    return Xtrn.to_numpy(float), Xten.to_numpy(float)

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

    ytr = train[label_col].astype(str).to_numpy()
    yte = test[label_col].astype(str).to_numpy()

    Xtr_raw, Xte_raw = global_standardize(train, test)
    classes_raw, s_raw = proto_scores(Xtr_raw, ytr, Xte_raw)

    Xtr_bc, Xte_bc = experiment_center(train, test)
    classes_bc, s_bc = proto_scores(Xtr_bc, ytr, Xte_bc)

    if not np.array_equal(classes_raw, classes_bc):
        raise RuntimeError("Class alignment mismatch")

    pred_raw = classes_raw[np.argmax(s_raw, axis=1)]
    pred_bc = classes_raw[np.argmax(s_bc, axis=1)]

    row = {
        "held_out_experiment": test_exp,
        "cell_type": cell_type,
        "n_test": int(len(test)),
        "v2_raw": float(accuracy_score(yte, pred_raw)),
        "v3_batch": float(accuracy_score(yte, pred_bc)),
    }

    for alpha in (0.25, 0.50, 0.75):
        # alpha weights the V2/raw signal; remaining weight is batch-corrected signal.
        s = alpha * s_raw + (1 - alpha) * s_bc
        pred = classes_raw[np.argmax(s, axis=1)]
        row[f"v3_ens_{alpha:.2f}"] = float(accuracy_score(yte, pred))

    rows.append(row)

results = pd.DataFrame(rows)
metric_cols = ["v2_raw","v3_batch","v3_ens_0.25","v3_ens_0.50","v3_ens_0.75"]
means = {c: float(results[c].mean()) for c in metric_cols}
medians = {c: float(results[c].median()) for c in metric_cols}
best = max(means, key=means.get)

summary = {
    "means": means,
    "medians": medians,
    "best_method": best,
    "best_mean_accuracy": means[best],
    "n_experiments": int(len(results)),
    "note": "V3 exploratory benchmark; ensemble weight selection uses the evaluation folds and should be locked before final reporting."
}

results.to_csv(ART / "v3_results.csv", index=False)
(ART / "v3_summary.json").write_text(json.dumps(summary, indent=2))

print("\n=== V3 POR EXPERIMENTO ===")
print(results.to_string(index=False))
print("\n=== RESUMEN V3 ===")
print(json.dumps(summary, indent=2))
