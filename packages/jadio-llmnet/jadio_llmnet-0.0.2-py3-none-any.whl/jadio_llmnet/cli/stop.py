import os
import signal
from pathlib import Path

def run(args=None):
    pid_file = Path.cwd() / "jadio_config" / "llmnet.pid"

    if not pid_file.exists():
        print("❌ No llmnet.pid file found. Server may not be running.")
        return

    try:
        pid = int(pid_file.read_text().strip())
    except ValueError:
        print("❌ Invalid PID file. Cannot stop server.")
        return

    try:
        os.kill(pid, signal.SIGTERM)
        print(f"✅ Sent SIGTERM to server process (PID {pid}).")

        pid_file.unlink()  # remove the PID file
        print("🗑️  Removed llmnet.pid file.")

    except ProcessLookupError:
        print("⚠️  No process found with that PID. Cleaning up PID file.")
        pid_file.unlink()

    except Exception as e:
        print(f"❌ Failed to stop server: {e}")
