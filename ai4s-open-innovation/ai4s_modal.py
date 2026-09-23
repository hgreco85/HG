import json
from pathlib import Path
import subprocess
import sys

import modal

app = modal.App("ai4s-experiment-engine")

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "numpy>=1.26",
        "pandas>=2.2",
        "scikit-learn>=1.4",
        "scipy>=1.12",
        "joblib>=1.3",
        "requests>=2.31",
    )
    .add_local_dir(".", remote_path="/root/ai4s")
)

@app.function(image=image, timeout=1800, cpu=4, memory=8192)
def run_experiments():
    root = Path("/root/ai4s")
    subprocess.run([sys.executable, "download_data.py"], cwd=root, check=True)
    subprocess.run([sys.executable, "experiment_engine.py"], cwd=root, check=True)

    summary = json.loads(
        (root / "artifacts" / "experiment_engine_summary.json").read_text()
    )
    print(json.dumps(summary, indent=2))
    return summary

@app.local_entrypoint()
def main():
    result = run_experiments.remote()
    print(json.dumps(result, indent=2))
