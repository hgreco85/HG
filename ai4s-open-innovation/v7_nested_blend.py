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

def cosine_scores(X, P):
    Xn = X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-12)
    Pn = P / (np.linalg.norm(P, axis=1, keepdims=True) + 1e-12)
    return Xn @ Pn.T

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

def paired_scores(train, test):
    scaler = StandardScaler()
    Xtr = scaler.fit_transform(train[features].astype(float))
    Xte = scaler.transform(test[features].astype(float))
    ytr = train[label_col].astype(str).to_numpy()

    classes_raw, P_raw = prototypes(Xtr, ytr)
    s_raw = cosine_scores(Xte, P_raw)

    Xtr_w, Xte_w = oas_whiten(Xtr, ytr, Xte)
    classes_oas, P_oas = prototypes(Xtr_w, ytr)
    if not np.array_equal(classes_raw, classes_oas):
        raise RuntimeError("Class alignment mismatch")
    s_oas = cosine_scores(Xte_w, P_oas)
    return classes_raw, s_raw, s_oas

ALPHAS = (0.0, 0.25, 0.50, 0.75, 1.0)  # alpha = RAW weight

def choose_alpha_nested(train):
    exps = sorted(train[exp_col].astype(str).unique())
    if len(exps) < 3:
        return 1.0, {"reason": "insufficient_inner_experiments"}

    totals = {a: [] for a in ALPHAS}
    for inner_test_exp in exps:
        inner_test = train[train[exp_col].astype(str) == inner_test_exp].copy()
        inner_train = train[train[exp_col].astype(str) != inner_test_exp].copy()
        if inner_train.empty or inner_test.empty:
            continue
        y = inner_test[label_col].astype(str).to_numpy()
        classes, s_raw, s_oas = paired_scores(inner_train, inner_test)
        for a in ALPHAS:
            scores = a * s_raw + (1.0 - a) * s_oas
            pred = classes[np.argmax(scores, axis=1)]
            totals[a].append(float(accuracy_score(y, pred)))

    means = {a: (float(np.mean(v)) if v else -np.inf) for a, v in totals.items()}
    best_mean = max(means.values())

    # Conservative tie-break: among effectively tied alphas, prefer more RAW weight.
    tied = [a for a, m in means.items() if best_mean - m <= 1e-6]
    chosen = max(tied)
    return chosen, {str(a): means[a] for a in ALPHAS}

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
    classes, s_raw, s_oas = paired_scores(train, test)
    pred_v2 = classes[np.argmax(s_raw, axis=1)]

    alpha, inner = choose_alpha_nested(train)
    s = alpha * s_raw + (1.0 - alpha) * s_oas
    pred_v7 = classes[np.argmax(s, axis=1)]

    rows.append({
        "held_out_experiment": test_exp,
        "cell_type": cell_type,
        "n_test": int(len(test)),
        "selected_alpha_raw": alpha,
        "v2_raw": float(accuracy_score(yte, pred_v2)),
        "v7_blend": float(accuracy_score(yte, pred_v7)),
    })

results = pd.DataFrame(rows)
mean_v2 = float(results["v2_raw"].mean())
mean_v7 = float(results["v7_blend"].mean())
summary = {
    "v2_mean_accuracy": mean_v2,
    "v7_mean_accuracy": mean_v7,
    "v7_median_accuracy": float(results["v7_blend"].median()),
    "delta_accuracy": mean_v7 - mean_v2,
    "n_experiments": int(len(results)),
    "alpha_counts": {str(k): int(v) for k, v in results["selected_alpha_raw"].value_counts().sort_index().items()},
    "by_cell_type": (
        results.groupby("cell_type")[["v2_raw","v7_blend"]]
        .mean()
        .reset_index()
        .to_dict(orient="records")
    ),
    "note": "V7 chooses the RAW/OAS blend weight by nested leave-one-experiment-out CV inside each outer training fold only; held-out labels are never used."
}

results.to_csv(ART / "v7_nested_blend_results.csv", index=False)
(ART / "v7_summary.json").write_text(json.dumps(summary, indent=2))

print("\n=== V7 NESTED BLEND SUMMARY ===")
print(json.dumps(summary, indent=2))
print("\n=== V7 ALPHA SELECTIONS ===")
print(results[["held_out_experiment","cell_type","selected_alpha_raw","v2_raw","v7_blend"]].to_string(index=False))
