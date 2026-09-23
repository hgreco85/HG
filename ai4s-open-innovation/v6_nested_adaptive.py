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
    P = np.vstack([X[y == c].mean(axis=0) for c in classes])
    return classes, P

def cosine_predict(Xtr, ytr, Xte):
    classes, P = prototypes(Xtr, ytr)
    P = P / (np.linalg.norm(P, axis=1, keepdims=True) + 1e-12)
    X = Xte / (np.linalg.norm(Xte, axis=1, keepdims=True) + 1e-12)
    return classes[np.argmax(X @ P.T, axis=1)]

def oas_whiten(Xtr, ytr, Xte):
    classes, P = prototypes(Xtr, ytr)
    lookup = {c: i for i, c in enumerate(classes)}
    residuals = np.empty_like(Xtr)
    for i, c in enumerate(ytr):
        residuals[i] = Xtr[i] - P[lookup[c]]

    cov = OAS(assume_centered=True).fit(residuals).covariance_
    evals, evecs = np.linalg.eigh(cov)
    floor = max(float(np.median(evals)) * 1e-4, 1e-8)
    W = evecs @ np.diag(1.0 / np.sqrt(np.maximum(evals, floor))) @ evecs.T
    return Xtr @ W, Xte @ W

def fit_predict(train, test, method):
    scaler = StandardScaler()
    Xtr = scaler.fit_transform(train[features].astype(float))
    Xte = scaler.transform(test[features].astype(float))
    ytr = train[label_col].astype(str).to_numpy()

    if method == "oas":
        Xtr, Xte = oas_whiten(Xtr, ytr, Xte)

    return cosine_predict(Xtr, ytr, Xte)

def choose_method_nested(train):
    exps = sorted(train[exp_col].astype(str).unique())
    # Need at least 3 experiments so each inner training split still has replication.
    if len(exps) < 3:
        return "raw", {"raw": None, "oas": None, "reason": "insufficient_inner_experiments"}

    scores = {"raw": [], "oas": []}
    for inner_test_exp in exps:
        inner_test = train[train[exp_col].astype(str) == inner_test_exp].copy()
        inner_train = train[train[exp_col].astype(str) != inner_test_exp].copy()
        if inner_train.empty or inner_test.empty:
            continue
        y = inner_test[label_col].astype(str).to_numpy()
        for method in ("raw", "oas"):
            pred = fit_predict(inner_train, inner_test, method)
            scores[method].append(float(accuracy_score(y, pred)))

    means = {k: (float(np.mean(v)) if v else -np.inf) for k, v in scores.items()}
    # Require a small but real inner-CV advantage before using OAS.
    chosen = "oas" if means["oas"] - means["raw"] >= 0.001 else "raw"
    return chosen, means

rows = []
for test_exp in sorted(agg[exp_col].astype(str).unique()):
    test = agg[agg[exp_col].astype(str) == test_exp].copy()
    if test.empty:
        continue
    cell_type = test["cell_type"].iloc[0]
    train = agg[(agg[exp_col].astype(str) != test_exp) & (agg["cell_type"] == cell_type)].copy()
    if train.empty:
        continue

    yte = test[label_col].astype(str).to_numpy()
    pred_raw = fit_predict(train, test, "raw")
    chosen, inner = choose_method_nested(train)
    pred_adaptive = fit_predict(train, test, chosen)

    rows.append({
        "held_out_experiment": test_exp,
        "cell_type": cell_type,
        "n_test": int(len(test)),
        "selected_method": chosen,
        "inner_raw_mean": inner.get("raw"),
        "inner_oas_mean": inner.get("oas"),
        "v2_raw": float(accuracy_score(yte, pred_raw)),
        "v6_adaptive": float(accuracy_score(yte, pred_adaptive)),
    })

results = pd.DataFrame(rows)
mean_v2 = float(results["v2_raw"].mean())
mean_v6 = float(results["v6_adaptive"].mean())
summary = {
    "v2_mean_accuracy": mean_v2,
    "v6_mean_accuracy": mean_v6,
    "v6_median_accuracy": float(results["v6_adaptive"].median()),
    "delta_accuracy": mean_v6 - mean_v2,
    "n_experiments": int(len(results)),
    "selection_counts": results["selected_method"].value_counts().to_dict(),
    "by_cell_type": (
        results.groupby("cell_type")[["v2_raw","v6_adaptive"]]
        .mean()
        .reset_index()
        .to_dict(orient="records")
    ),
    "note": "V6 selects raw vs OAS using nested leave-one-experiment-out CV inside the outer training fold only; held-out labels are never used for method selection."
}

results.to_csv(ART / "v6_nested_adaptive_results.csv", index=False)
(ART / "v6_summary.json").write_text(json.dumps(summary, indent=2))

print("\n=== V6 NESTED ADAPTIVE SUMMARY ===")
print(json.dumps(summary, indent=2))
print("\n=== V6 METHOD SELECTIONS ===")
print(results[["held_out_experiment","cell_type","selected_method","v2_raw","v6_adaptive"]].to_string(index=False))
