from getpass import getpass
from jadio_llmnet.core import interpreter, manager
import json
from pathlib import Path

CONFIG_PATH = Path.cwd() / "jadio_config" / "llmnet_config.json"

def run(args=None):
    print("⚡️ LLMNet LOGIN\n")

    # 1️⃣ Prompt for username
    username = input("Username: ").strip()
    if not username:
        print("❌ No username entered. Aborting.")
        return

    # 2️⃣ Prompt for password (hidden)
    password = getpass("Password: ").strip()
    if not password:
        print("❌ No password entered. Aborting.")
        return

    # 3️⃣ Validate with interpreter
    if not interpreter.validate_login(username, password):
        print("❌ Login failed. Check username and password.")
        return

    print("✅ Login successful!")

    # 4️⃣ Update logged_in flag in llmnet_config.json
    try:
        if not CONFIG_PATH.exists():
            print("❌ llmnet_config.json not found. Did you run 'llmnet init'?")
            return

        with open(CONFIG_PATH, encoding="utf-8") as f:
            config = json.load(f)

        config["logged_in"] = True

        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)

        print("✅ LLMNet is now marked as logged in.")

    except Exception as e:
        print(f"❌ Failed to update login state: {e}")
