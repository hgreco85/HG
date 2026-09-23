from pathlib import Path
from io import BytesIO
import json
import re
import zipfile

import numpy as np
import pandas as pd
import requests
from PIL import Image
import torch
from sklearn.covariance import OAS
from sklearn.decomposition import PCA
from sklearn.metrics import accuracy_score, balanced_accuracy_score
from sklearn.preprocessing import StandardScaler
from torchvision.models import resnet18, ResNet18_Weights

ART = Path("artifacts")
ART.mkdir(exist_ok=True)
DATA = Path("data_external_ooc")
DATA.mkdir(exist_ok=True)
ZIP_PATH = DATA / "GOC_mucus_poducing_protocol.zip"
URL = "https://zenodo.org/records/14745113/files/GOC_mucus_poducing_protocol.zip?download=1"

IMAGE_EXT = re.compile(r"\\.(?:tif|tiff|jpg|jpeg|png)$", re.I)

def parse_brightfield_name(name):
    base = Path(name).name
    if not IMAGE_EXT.search(base):
        return None
    stem = IMAGE_EXT.sub("", base)
    low = stem.lower()

    # Exclude staining/confocal names. Brightfield files follow GOC_[ratio]_[day]_[numerator].
    blocked = ("mucin", "dapi", "f-actin", "factin", "muc5ac", "vil1", "zo1")
    if any(tok in low for tok in blocked):
        return None
    if not low.startswith("goc_"):
        return None

    tail = stem[4:]
    # Accept common ratio encodings: 7to3, 7_3, 7-3, 7:3 (same for 9:1).
    ratio_match = re.search(r"(?i)(7\\s*(?:to|_|-|:)\\s*3|9\\s*(?:to|_|-|:)\\s*1)", tail)
    if not ratio_match:
        return None

    ratio_raw = re.sub(r"\\s+", "", ratio_match.group(1).lower())
    ratio = "7to3" if ratio_raw.startswith("7") else "9to1"

    rest = tail[ratio_match.end():].lstrip("_- :")
    nums = re.findall(r"\\d+", rest)
    if not nums:
        return None
    day = int(nums[0])
    if day not in {1, 2, 4, 6, 8}:
        return None
    return ratio, day

def download():
    if ZIP_PATH.exists() and ZIP_PATH.stat().st_size > 100_000_000:
        print(f"Using cached {ZIP_PATH} ({ZIP_PATH.stat().st_size/1e6:.1f} MB)", flush=True)
        return
    print("Downloading external gut-on-chip dataset...", flush=True)
    with requests.get(URL, stream=True, timeout=(30, 300)) as r:
        r.raise_for_status()
        with ZIP_PATH.open("wb") as f:
            for chunk in r.iter_content(chunk_size=8 * 1024 * 1024):
                if chunk:
                    f.write(chunk)
    print(f"Downloaded {ZIP_PATH.stat().st_size/1e6:.1f} MB", flush=True)

def list_brightfield(zf):
    rows = []
    samples = []
    for name in zf.namelist():
        if len(samples) < 30 and Path(name).suffix.lower() in {".tif", ".tiff", ".jpg", ".jpeg", ".png"}:
            samples.append(name)
        parsed = parse_brightfield_name(name)
        if not parsed:
            continue
        ratio, day = parsed
        rows.append({"member": name, "ratio": ratio, "day": day})

    frame = pd.DataFrame(rows)
    if frame.empty:
        print("Sample image names from archive:", flush=True)
        for s in samples:
            print("  ", s, flush=True)
        raise RuntimeError("No brightfield files matched flexible GOC_[ratio]_[day]_[numerator] pattern.")

    print(f"Matched {len(frame)} brightfield images", flush=True)
    return frame.sort_values(["day", "ratio", "member"]).reset_index(drop=True)

def extract_embeddings(zf, frame):
    weights = ResNet18_Weights.DEFAULT
    transform = weights.transforms()
    model = resnet18(weights=weights)
    model.fc = torch.nn.Identity()
    model.eval()

    feats = []
    batch_tensors = []
    batch_meta = []

    def flush():
        nonlocal batch_tensors, batch_meta, feats
        if not batch_tensors:
            return
        x = torch.stack(batch_tensors)
        with torch.no_grad():
            y = model(x).cpu().numpy()
        for meta, emb in zip(batch_meta, y):
            feats.append({**meta, "embedding": emb.astype(np.float32)})
        batch_tensors, batch_meta = [], []

    for i, row in frame.iterrows():
        raw = zf.read(row["member"])
        with Image.open(BytesIO(raw)) as img:
            img = img.convert("RGB")
            tensor = transform(img)
        batch_tensors.append(tensor)
        batch_meta.append({"member": row["member"], "ratio": row["ratio"], "day": int(row["day"])})
        if len(batch_tensors) >= 8:
            flush()
        if (i + 1) % 20 == 0:
            print(f"Embedded {i+1}/{len(frame)} images", flush=True)
    flush()
    return feats

def proto_scores(Xtr, ytr, Xte):
    classes = np.unique(ytr)
    P = np.vstack([Xtr[ytr == c].mean(axis=0) for c in classes])
    P = P / (np.linalg.norm(P, axis=1, keepdims=True) + 1e-12)
    X = Xte / (np.linalg.norm(Xte, axis=1, keepdims=True) + 1e-12)
    return classes, X @ P.T

def preprocess_fit(train_X):
    scaler = StandardScaler()
    Xs = scaler.fit_transform(train_X)
    n_comp = max(2, min(64, Xs.shape[0] - 2, Xs.shape[1]))
    pca = PCA(n_components=n_comp, svd_solver="full")
    Xp = pca.fit_transform(Xs)
    return scaler, pca, Xp

def preprocess_apply(scaler, pca, X):
    return pca.transform(scaler.transform(X))

def oas_transform(Xtr, ytr, Xte):
    classes = np.unique(ytr)
    P = np.vstack([Xtr[ytr == c].mean(axis=0) for c in classes])
    lookup = {c: i for i, c in enumerate(classes)}
    residuals = np.vstack([Xtr[i] - P[lookup[c]] for i, c in enumerate(ytr)])
    cov = OAS(assume_centered=True).fit(residuals).covariance_
    evals, evecs = np.linalg.eigh(cov)
    floor = max(float(np.median(evals)) * 1e-4, 1e-8)
    W = evecs @ np.diag(1.0 / np.sqrt(np.maximum(evals, floor))) @ evecs.T
    return Xtr @ W, Xte @ W

def paired_scores(train_X, train_y, test_X):
    scaler, pca, Xtr = preprocess_fit(train_X)
    Xte = preprocess_apply(scaler, pca, test_X)

    classes_raw, s_raw = proto_scores(Xtr, train_y, Xte)
    Xtr_w, Xte_w = oas_transform(Xtr, train_y, Xte)
    classes_oas, s_oas = proto_scores(Xtr_w, train_y, Xte_w)
    if not np.array_equal(classes_raw, classes_oas):
        raise RuntimeError("Class mismatch")
    return classes_raw, s_raw, s_oas

ALPHAS = (0.25, 0.50, 0.75, 1.0)

def choose_alpha_nested(train_X, train_y, train_day):
    days = sorted(np.unique(train_day))
    per_alpha = {a: [] for a in ALPHAS}
    for d in days:
        inner_test = train_day == d
        inner_train = ~inner_test
        if len(np.unique(train_y[inner_train])) < 2 or len(np.unique(train_y[inner_test])) < 2:
            continue
        classes, s_raw, s_oas = paired_scores(train_X[inner_train], train_y[inner_train], train_X[inner_test])
        for a in ALPHAS:
            s = a * s_raw + (1 - a) * s_oas
            pred = classes[np.argmax(s, axis=1)]
            per_alpha[a].append(balanced_accuracy_score(train_y[inner_test], pred))

    means = {a: (float(np.mean(v)) if v else -np.inf) for a, v in per_alpha.items()}
    best = max(means.values())
    tied = [a for a, v in means.items() if best - v <= 1e-8]
    return max(tied), means

def evaluate(feats):
    X = np.vstack([r["embedding"] for r in feats]).astype(float)
    y = np.array([r["ratio"] for r in feats])
    day = np.array([r["day"] for r in feats])

    rows = []
    for held_day in sorted(np.unique(day)):
        te = day == held_day
        tr = ~te
        if len(np.unique(y[te])) < 2:
            continue

        classes, s_raw, s_oas = paired_scores(X[tr], y[tr], X[te])
        pred_raw = classes[np.argmax(s_raw, axis=1)]
        alpha, inner = choose_alpha_nested(X[tr], y[tr], day[tr])
        pred_blend = classes[np.argmax(alpha * s_raw + (1 - alpha) * s_oas, axis=1)]

        rows.append({
            "held_out_day": int(held_day),
            "n_test": int(te.sum()),
            "alpha_raw": float(alpha),
            "raw_accuracy": float(accuracy_score(y[te], pred_raw)),
            "raw_balanced_accuracy": float(balanced_accuracy_score(y[te], pred_raw)),
            "blend_accuracy": float(accuracy_score(y[te], pred_blend)),
            "blend_balanced_accuracy": float(balanced_accuracy_score(y[te], pred_blend)),
        })

    results = pd.DataFrame(rows)
    summary = {
        "dataset": "Zenodo 14745113 gut-on-chip brightfield subset",
        "task": "seeding-ratio recovery (7:3 vs 9:1) under leave-one-day-out shift",
        "n_images": int(len(feats)),
        "n_days": int(results.shape[0]),
        "raw_mean_balanced_accuracy": float(results["raw_balanced_accuracy"].mean()),
        "v7_style_mean_balanced_accuracy": float(results["blend_balanced_accuracy"].mean()),
        "delta_balanced_accuracy": float((results["blend_balanced_accuracy"] - results["raw_balanced_accuracy"]).mean()),
        "raw_mean_accuracy": float(results["raw_accuracy"].mean()),
        "v7_style_mean_accuracy": float(results["blend_accuracy"].mean()),
        "folds": results.to_dict(orient="records"),
        "note": "External transfer proxy: label is culture seeding ratio, not phenotype quality. Blend selection is nested inside outer training days only."
    }
    results.to_csv(ART / "external_ooc_transfer_folds.csv", index=False)
    (ART / "external_ooc_transfer_summary.json").write_text(json.dumps(summary, indent=2))
    print("\n=== EXTERNAL OOC TRANSFER SUMMARY ===")
    print(json.dumps(summary, indent=2))
    return summary

download()
with zipfile.ZipFile(ZIP_PATH) as zf:
    frame = list_brightfield(zf)
    print(frame.groupby(["day", "ratio"]).size().unstack(fill_value=0), flush=True)
    feats = extract_embeddings(zf, frame)

evaluate(feats)
