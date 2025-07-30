import json
from pathlib import Path

CONFIG_PATH = Path.cwd() / "jadio_config" / "llmnet_config.json"

def run(args=None):
    print("⚡️ LLMNet LOGOUT\n")

    if not CONFIG_PATH.exists():
        print("❌ llmnet_config.json not found. Did you run 'llmnet init'?")
        return

    try:
        with open(CONFIG_PATH, encoding="utf-8") as f:
            config = json.load(f)

        if not config.get("logged_in", False):
            print("ℹ️  Already logged out.")
            return

        config["logged_in"] = False

        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)

        print("✅ Logged out. You are now signed out of LLMNet.")

    except Exception as e:
        print(f"❌ Error during logout: {e}")
