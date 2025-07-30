import json
from pathlib import Path
from getpass import getpass
from jadio_llmnet.core.hasher import hash_password
from jadio_llmnet.core.encryptor import encrypt_data
from jadio_llmnet.core.interpreter import validate_login

CONFIG_DIR = Path.cwd() / "jadio_config"
GLOBAL_CONFIG = CONFIG_DIR / "llmnet_config.json"

def get_account_file(username):
    return CONFIG_DIR / f"llmnet_accounts_{username}.json"

def get_user_config_file(username):
    return CONFIG_DIR / f"llmnet_config_{username}.json"

def load_global():
    if not GLOBAL_CONFIG.exists():
        print("❌ llmnet_config.json missing. Did you run 'llmnet init'?")
        exit(1)
    with open(GLOBAL_CONFIG) as f:
        return json.load(f)

def save_global(data):
    with open(GLOBAL_CONFIG, "w") as f:
        json.dump(data, f, indent=2)

def show(args):
    config = load_global()
    user = config.get("current_account", None)
    if not user:
        print("❌ No current account set.")
    else:
        print(f"✅ Current LLMNet Account: {user}")

def change_pw(args):
    config = load_global()
    username = config.get("current_account")
    if not username:
        print("❌ No current account set.")
        return

    print(f"⚡️ Changing password for account: {username}")

    # Verify current password
    current_pw = getpass("Enter current password: ").strip()
    if not validate_login(username, current_pw):
        print("❌ Incorrect current password. Aborting.")
        return

    # Prompt new password
    new_pw = getpass("Enter new password: ").strip()
    confirm_pw = getpass("Confirm new password: ").strip()
    if new_pw != confirm_pw:
        print("❌ Passwords do not match. Aborting.")
        return

    # Hash & encrypt
    salt, hashed = hash_password(new_pw)
    encrypted = encrypt_data(hashed)

    account_data = {
        "username": username,
        "salt": salt,
        "password": encrypted
    }

    with open(get_account_file(username), "w") as f:
        json.dump(account_data, f, indent=2)

    print("✅ Password updated successfully.")

def create(args):
    print("⚡️ Creating a new LLMNet account.")

    username = input("New username: ").strip()
    if not username:
        print("❌ Username cannot be empty.")
        return

    # Check for existing
    if get_account_file(username).exists():
        print("❌ Account already exists.")
        return

    password = getpass("New password: ").strip()
    confirm = getpass("Confirm password: ").strip()
    if password != confirm:
        print("❌ Passwords do not match.")
        return

    # Hash & encrypt
    salt, hashed = hash_password(password)
    encrypted = encrypt_data(hashed)

    # Create account file
    account_data = {
        "username": username,
        "salt": salt,
        "password": encrypted
    }
    with open(get_account_file(username), "w") as f:
        json.dump(account_data, f, indent=2)
    print(f"✅ Created account file for {username}.")

    # Create user-specific config
    user_config = {
        "version": "0.0.1",
        "locked_ports": [],
        "assigned": {},
        "logged_in": False,
        "users": [],
        "logs": [],
        "port": 47600
    }
    with open(get_user_config_file(username), "w") as f:
        json.dump(user_config, f, indent=2)
    print(f"✅ Created configuration for {username}.")

    # Set global to this user
    global_data = {
        "current_account": username,
        "logged_in": False
    }
    save_global(global_data)
    print(f"✅ Switched active user to {username}.")
