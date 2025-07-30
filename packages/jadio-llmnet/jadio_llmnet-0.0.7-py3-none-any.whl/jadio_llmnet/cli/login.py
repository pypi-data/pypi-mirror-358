from getpass import getpass
from jadio_llmnet.core import interpreter
import json
from pathlib import Path

CONFIG_DIR = Path.cwd() / "jadio_config"
GLOBAL_CONFIG = CONFIG_DIR / "llmnet_config.json"

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
        print("❌ Login failed.")
        return

    print("✅ Login successful!")

    # 4️⃣ Update global config to set current user
    try:
        if not GLOBAL_CONFIG.exists():
            # Create minimal global config if it doesn't exist
            global_data = {}
        else:
            with open(GLOBAL_CONFIG, encoding="utf-8") as f:
                global_data = json.load(f)

        # Set current account
        global_data["current_account"] = username
        
        with open(GLOBAL_CONFIG, "w", encoding="utf-8") as f:
            json.dump(global_data, f, indent=2)

        # 5️⃣ Update user-specific config
        user_config_file = CONFIG_DIR / f"llmnet_config_{username}.json"
        
        # If user config doesn't exist, copy from main config
        if not user_config_file.exists() and GLOBAL_CONFIG.exists():
            main_config_file = CONFIG_DIR / "llmnet_config.json"
            if main_config_file.exists():
                with open(main_config_file, "r") as f:
                    user_config = json.load(f)
            else:
                user_config = {
                    "version": "0.0.1",
                    "locked_ports": [47600, 47601, 47602],
                    "assigned": {},
                    "port": 47600
                }
        else:
            with open(user_config_file, "r") as f:
                user_config = json.load(f)

        user_config["logged_in"] = True
        
        with open(user_config_file, "w") as f:
            json.dump(user_config, f, indent=2)

        print(f"✅ Logged in as '{username}'.")

    except Exception as e:
        print(f"❌ Failed to update login state: {e}")