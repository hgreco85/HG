import os
import subprocess
import sys

print("AI4S_START: boot", flush=True)
print("AI4S_START: cwd=", os.getcwd(), flush=True)
print("AI4S_START: python=", sys.executable, flush=True)

if os.environ.get("AI4S_RUN_MODAL_ON_DEPLOY", "0") == "1":
    runner = [sys.executable, "-u", "run_modal_experiments.py"]
    print("AI4S_START: launching Modal runner", flush=True)
    rc = subprocess.call(runner)
    print(f"AI4S_MODAL_RC={rc}", flush=True)
else:
    print("AI4S_START: Modal experiments disabled", flush=True)

streamlit = os.path.join(os.path.dirname(sys.executable), "streamlit")
port = os.environ.get("PORT", "8080")
cmd = [
    streamlit,
    "run",
    "demo.py",
    "--server.address",
    "0.0.0.0",
    "--server.port",
    port,
]
print("AI4S_START: launching Streamlit", flush=True)
os.execv(streamlit, cmd)
