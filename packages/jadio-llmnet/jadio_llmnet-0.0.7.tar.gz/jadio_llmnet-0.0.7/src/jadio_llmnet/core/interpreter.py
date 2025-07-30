import json
from pathlib import Path
from jadio_llmnet.core.hasher import hash_password
from jadio_llmnet.core.encryptor import encrypt_data

CONFIG_DIR = Path.cwd() / "jadio_config"

def validate_login(username_input: str, password_input: str) -> bool:
    """
    Validates a login attempt using the new multi-user system
    """
    # First check if there's a global config
    global_config_path = CONFIG_DIR / "llmnet_config.json"
    if not global_config_path.exists():
        print("❌ No llmnet_config.json found. Run 'llmnet init' first.")
        return False

    # Check for user-specific account file
    user_account_file = CONFIG_DIR / f"llmnet_accounts_{username_input}.json"
    
    # Fall back to legacy single account file if user-specific doesn't exist
    if not user_account_file.exists():
        user_account_file = CONFIG_DIR / "llmnet_accounts.json"
        if not user_account_file.exists():
            print(f"❌ No account found for user '{username_input}'.")
            return False

    try:
        with open(user_account_file, encoding="utf-8") as f:
            account_data = json.load(f)
    except Exception as e:
        print(f"❌ Failed to read account file: {e}")
        return False

    stored_username = account_data.get("username")
    stored_salt_hex = account_data.get("salt")
    stored_encrypted_password = account_data.get("password")

    if not all([stored_username, stored_salt_hex, stored_encrypted_password]):
        print("❌ Account file is missing required fields.")
        return False

    if username_input != stored_username:
        print("❌ Invalid username.")
        return False

    try:
        salt_bytes = bytes.fromhex(stored_salt_hex)
        # Reproduce the hash with the same salt
        _, hashed_input = hash_password(password_input, salt_bytes)
        # Encrypt it
        encrypted_input = encrypt_data(hashed_input)

        if encrypted_input == stored_encrypted_password:
            return True
        else:
            print("❌ Incorrect password.")
            return False

    except Exception as e:
        print(f"❌ Error during validation: {e}")
        return False