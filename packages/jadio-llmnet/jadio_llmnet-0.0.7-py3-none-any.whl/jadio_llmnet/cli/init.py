import json
from pathlib import Path
from getpass import getpass
from jadio_llmnet.core.hasher import hash_password
from jadio_llmnet.core.encryptor import encrypt_data, generate_secret_key

def run(args=None):
    print("⚡️ Running LLMNet INIT...")

    # 1️⃣ Make sure jadio_config/ exists
    config_dir = Path.cwd() / "jadio_config"
    config_dir.mkdir(exist_ok=True)

    # 2️⃣ Create llmnet_config.json with default server settings
    config_file = config_dir / "llmnet_config.json"
    default_config = {
        "version": "0.0.1",
        "locked_ports": [47600, 47601, 47602],
        "assigned": {},
        "logged_in": False,
        "users": [],
        "logs": [],
        "port": 47600
    }

    if config_file.exists():
        response = input("⚠️  llmnet_config.json already exists. Overwrite? (y/n): ").strip().lower()
        if response != "y":
            print("❌ Aborted. No changes made.")
            return

    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(default_config, f, indent=2)

    print(f"✅ Created llmnet_config.json in {config_dir}")

    # 3️⃣ Generate or ensure llmnet_secret.key exists
    generate_secret_key()
    print(f"✅ Encryption secret key ready at {config_dir / 'llmnet_secret.key'}")

    # 4️⃣ Prompt for admin user credentials
    print("\n🛡️  Set up your admin account:")
    username = input("Enter admin username: ").strip()
    while not username:
        username = input("Username cannot be empty. Enter admin username: ").strip()

    password = getpass("Enter admin password (input hidden): ").strip()
    while not password:
        password = getpass("Password cannot be empty. Enter admin password: ").strip()

    # 5️⃣ Hash and encrypt the password
    salt, hashed = hash_password(password)
    encrypted = encrypt_data(hashed)

    # 6️⃣ Store llmnet_accounts.json
    account_file = config_dir / "llmnet_accounts.json"
    account_data = {
        "username": username,
        "salt": salt,
        "password": encrypted
    }
    with open(account_file, "w", encoding="utf-8") as f:
        json.dump(account_data, f, indent=2)

    print(f"✅ Created llmnet_accounts.json with encrypted credentials.")
    print("\n🎯 LLMNet INIT complete!")
