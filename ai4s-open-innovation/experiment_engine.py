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
    return json.loads((ART / name).read_text())

# Cost-efficient active benchmark: rerun only the frozen champion and the new challenger.
run("V2 CHAMPION", "v2_celltype.py")
v2 = load("v2_summary.json")

run("V6 NESTED ADAPTIVE CHALLENGER", "v6_nested_adaptive.py")
v6 = load("v6_summary.json")

champion = float(v2["v2_mean_accuracy"])
challenger = float(v6["v6_mean_accuracy"])
delta = challenger - champion
threshold = 0.001

summary = {
    "champion": "v2_celltype",
    "champion_mean_accuracy": champion,
    "active_challenger": "v6_nested_adaptive",
    "active_challenger_mean_accuracy": challenger,
    "delta_accuracy": delta,
    "promotion_threshold": threshold,
    "decision": "PROMOTE" if delta >= threshold else "KEEP_V2",
    "n_experiments": int(v2["n_experiments"]),
    "archived_validated_challengers": {
        "v3_batch": 0.9729139389804619,
        "v4_fisher_0.25": 0.972882303119653,
        "v5_oas_cosine": 0.9724533641071925
    },
    "v6_selection_counts": v6["selection_counts"],
    "v6_by_cell_type": v6["by_cell_type"],
    "notes": [
        "Only V2 and the active challenger are rerun to reduce Modal compute and Railway log volume.",
        "Archived challenger scores are prior validated deterministic runs and are not used to choose V6.",
        "V6 method selection is nested inside each outer training fold."
    ]
}

(ART / "experiment_engine_summary.json").write_text(json.dumps(summary, indent=2))
print("\n=== AI4S EXPERIMENT ENGINE ===")
print(json.dumps(summary, indent=2))
