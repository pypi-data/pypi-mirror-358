import json
from pathlib import Path

CONFIG_DIR = Path.cwd() / "jadio_config"
GLOBAL_CONFIG = CONFIG_DIR / "llmnet_config.json"

def run(args=None):
    print("⚡️ LLMNet LOGOUT\n")

    if not GLOBAL_CONFIG.exists():
        print("❌ llmnet_config.json not found. Did you run 'llmnet init'?")
        return

    try:
        with open(GLOBAL_CONFIG, encoding="utf-8") as f:
            global_data = json.load(f)
    except Exception as e:
        print(f"❌ Error reading global config: {e}")
        return

    current_user = global_data.get("current_account")
    if not current_user:
        print("❌ No active account is set. Are you logged in?")
        return

    user_config_file = CONFIG_DIR / f"llmnet_config_{current_user}.json"
    if not user_config_file.exists():
        print(f"❌ Config for user '{current_user}' not found.")
        return

    try:
        with open(user_config_file, encoding="utf-8") as f:
            user_data = json.load(f)
    except Exception as e:
        print(f"❌ Error reading user config: {e}")
        return

    if not user_data.get("logged_in", False):
        print(f"ℹ️ User '{current_user}' is already logged out.")
        return

    user_data["logged_in"] = False

    try:
        with open(user_config_file, "w", encoding="utf-8") as f:
            json.dump(user_data, f, indent=2)
        print(f"✅ User '{current_user}' logged out successfully.")
    except Exception as e:
        print(f"❌ Error saving logout state: {e}")
