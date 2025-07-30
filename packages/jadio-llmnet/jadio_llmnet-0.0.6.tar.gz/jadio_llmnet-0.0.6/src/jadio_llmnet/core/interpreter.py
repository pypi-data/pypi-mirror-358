import json
from pathlib import Path
from jadio_llmnet.core.hasher import hash_password
from jadio_llmnet.core.encryptor import encrypt_data

ACCOUNTS_PATH = Path.cwd() / "jadio_config" / "llmnet_accounts.json"

def validate_login(username_input: str, password_input: str) -> bool:
    """
    Validates a login attempt:
    - Reads llmnet_accounts.json
    - Uses stored salt
    - Hashes input password with salt (PBKDF2)
    - Encrypts the hash (AES)
    - Compares to stored encrypted blob
    """
    if not ACCOUNTS_PATH.exists():
        print("❌ No llmnet_accounts.json found.")
        return False

    try:
        with open(ACCOUNTS_PATH, encoding="utf-8") as f:
            account_data = json.load(f)
    except Exception as e:
        print(f"❌ Failed to read llmnet_accounts.json: {e}")
        return False

    stored_username = account_data.get("username")
    stored_salt_hex = account_data.get("salt")
    stored_encrypted_password = account_data.get("password")

    if not all([stored_username, stored_salt_hex, stored_encrypted_password]):
        print("❌ llmnet_accounts.json is missing required fields.")
        return False

    if username_input != stored_username:
        print("❌ Invalid username.")
        return False

    try:
        salt_bytes = bytes.fromhex(stored_salt_hex)
        # Reproduce the hash
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
