from pathlib import Path
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
ART = ROOT / "artifacts"
ART.mkdir(exist_ok=True)

def run(name, script):
    print(f"\n=== {name} ===", flush=True)
    subprocess.run([sys.executable, script], cwd=ROOT, check=True)

def load(name):
    p = ART / name
    return json.loads(p.read_text()) if p.exists() else None

run("V2 CHAMPION", "v2_celltype.py")
v2 = load("v2_summary.json")

run("V3 BATCH CHALLENGERS", "v3_ensemble.py")
v3 = load("v3_summary.json")

run("V4 FISHER-GEOMETRY CHALLENGERS", "v4_fisher_geometry.py")
v4 = load("v4_summary.json")

champion = float(v2["v2_mean_accuracy"])
challengers = [
    {
        "family": "v3_batch",
        "method": v3["best_method"],
        "mean_accuracy": float(v3["best_mean_accuracy"]),
    },
    {
        "family": "v4_fisher_geometry",
        "method": v4["best_method"],
        "mean_accuracy": float(v4["best_mean_accuracy"]),
    },
]
best = max(challengers, key=lambda x: x["mean_accuracy"])
delta = best["mean_accuracy"] - champion
threshold = 0.001

decision = "PROMOTE" if delta >= threshold else "KEEP_V2"
summary = {
    "champion": "v2_celltype",
    "champion_mean_accuracy": champion,
    "challengers": challengers,
    "best_challenger_family": best["family"],
    "best_challenger": best["method"],
    "best_challenger_mean_accuracy": best["mean_accuracy"],
    "delta_accuracy": delta,
    "promotion_threshold": threshold,
    "decision": decision,
    "n_experiments": int(v2["n_experiments"]),
    "notes": [
        "V2 remains frozen unless a challenger improves mean accuracy by >=0.10 percentage points.",
        "Any promoted challenger still requires review of worst-case experiments and leakage risk.",
        "V4 Fisher weights use training folds only."
    ]
}
(ART / "experiment_engine_summary.json").write_text(json.dumps(summary, indent=2))
print("\n=== AI4S EXPERIMENT ENGINE ===")
print(json.dumps(summary, indent=2))
