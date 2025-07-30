import json
from pathlib import Path
from jadio_llmnet.core import manager

GLOBAL_CONFIG_PATH = Path.cwd() / "jadio_config" / "llmnet_config.json"

def run(args=None):
    print("⚡️ LLMNet STATUS\n")

    # 1️⃣ Check if logged in
    if not manager.is_logged_in():
        print("❌ You must be logged in to view assignments.")
        return

    # 2️⃣ Load global config to get current_account
    if not GLOBAL_CONFIG_PATH.exists():
        print("❌ llmnet_config.json not found. Did you run 'llmnet init'?")
        return

    try:
        with open(GLOBAL_CONFIG_PATH, encoding="utf-8") as f:
            global_data = json.load(f)
        current_user = global_data.get("current_account")
        if not current_user:
            print("❌ No active account set.")
            return
    except Exception as e:
        print(f"❌ Error reading global config: {e}")
        return

    print(f"✅ Logged in as: {current_user}\n")

    # 3️⃣ Get assignments for this user
    try:
        assignments = manager.get_assignments()
    except Exception as e:
        print(f"❌ Failed to load assignments: {e}")
        return

    if not assignments:
        print("ℹ️  No ports are currently assigned.")
        return

    print("Assigned Ports and Models:")

    for port, details in assignments.items():
        print(f"- Port {port}:")
        print(f"    Model: {details.get('model')}")
        print(f"    Path: {details.get('path')}")
        print(f"    Lazy: {details.get('lazy')}")
        print(f"    Name: {details.get('name')}\n")
