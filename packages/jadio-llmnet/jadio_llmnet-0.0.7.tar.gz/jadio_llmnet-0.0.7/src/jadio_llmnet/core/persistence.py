import subprocess
import sys
from pathlib import Path

TASK_NAME = "LLMNetServer"

def enable():
    print("⚡️ Enabling Windows Scheduled Task for LLMNet...")

    python_exe = sys.executable
    server_script = str(Path.cwd() / "src" / "jadio_llmnet" / "core" / "server.py")

    cmd = [
        "schtasks", "/Create",
        "/TN", TASK_NAME,
        "/TR", f'"{python_exe}" "{server_script}"',
        "/SC", "ONSTART",
        "/RL", "HIGHEST",
        "/F"
    ]

    try:
        subprocess.run(cmd, check=True)
        print(f"✅ Windows Scheduled Task '{TASK_NAME}' created.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create Scheduled Task: {e}")

def disable():
    print(f"⚡️ Removing Windows Scheduled Task '{TASK_NAME}'...")

    cmd = [
        "schtasks", "/Delete",
        "/TN", TASK_NAME,
        "/F"
    ]

    try:
        subprocess.run(cmd, check=True)
        print(f"✅ Windows Scheduled Task '{TASK_NAME}' deleted.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to delete Scheduled Task: {e}")
