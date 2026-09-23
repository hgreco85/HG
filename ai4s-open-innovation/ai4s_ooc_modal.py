import json
from pathlib import Path
import subprocess
import sys
import modal

app = modal.App("ai4s-ooc-transfer")

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "numpy>=1.26",
        "pandas>=2.2",
        "scikit-learn>=1.4",
        "requests>=2.31",
        "pillow>=10.0",
        "torch>=2.3",
        "torchvision>=0.18",
    )
    .add_local_dir(".", remote_path="/root/ai4s")
)

@app.function(image=image, timeout=3600, cpu=4, memory=8192, retries=0)
def run_external_ooc():
    root = Path("/root/ai4s")
    subprocess.run([sys.executable, "external_ooc_validation.py"], cwd=root, check=True)
    summary = json.loads((root / "artifacts" / "external_ooc_transfer_summary.json").read_text())
    print(json.dumps(summary, indent=2))
    return summary

@app.local_entrypoint()
def main():
    result = run_external_ooc.remote()
    print(json.dumps(result, indent=2))
