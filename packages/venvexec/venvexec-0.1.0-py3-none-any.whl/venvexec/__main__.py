import os
import sys
import subprocess
from pathlib import Path
import venv

CENTRAL_VENV = Path.home() / ".venvexec-central"

def get_venv_bin_path(venv_path):
    return venv_path / ("Scripts" if os.name == "nt" else "bin")

def ensure_central_venv():
    if not get_venv_bin_path(CENTRAL_VENV).exists():
        print(f"⚠️  Central venv not found. Creating one at {CENTRAL_VENV}...")
        venv.create(CENTRAL_VENV, with_pip=True)
    return CENTRAL_VENV

def run_command(venv_path, command):
    bin_path = get_venv_bin_path(venv_path)
    env = os.environ.copy()
    env["PATH"] = str(bin_path) + os.pathsep + env["PATH"]
    env["VIRTUAL_ENV"] = str(venv_path)
    subprocess.run(command, env=env)

def main():
    if len(sys.argv) < 2:
        print("Usage: venvexec command [args...]")
        sys.exit(1)

    command = sys.argv[1:]
    central_venv = ensure_central_venv()
    run_command(central_venv, command)
