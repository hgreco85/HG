import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "artifacts" / "modal_run_result.json"
OUT.parent.mkdir(exist_ok=True)

required = ["MODAL_TOKEN_ID", "MODAL_TOKEN_SECRET"]
missing = [k for k in required if not os.environ.get(k)]
if missing:
    raise RuntimeError("Missing Railway variables: " + ", ".join(missing))

cmd = ["modal", "run", "ai4s_modal.py"]
print("Launching AI4S experiments on Modal...")
p = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)

print(p.stdout)
if p.stderr:
    print(p.stderr)

result = {
    "returncode": p.returncode,
    "stdout_tail": p.stdout[-12000:],
    "stderr_tail": p.stderr[-8000:],
}
OUT.write_text(json.dumps(result, indent=2))

if p.returncode != 0:
    raise SystemExit(p.returncode)
