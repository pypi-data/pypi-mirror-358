import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
from pathlib import Path

SECRET_KEY_PATH = Path.cwd() / "jadio_config" / "llmnet_secret.key"

def generate_secret_key():
    key = os.urandom(32)
    SECRET_KEY_PATH.write_bytes(key)
    return key

def load_secret_key():
    if not SECRET_KEY_PATH.exists():
        return generate_secret_key()
    return SECRET_KEY_PATH.read_bytes()

def encrypt_data(plaintext_hex: str) -> str:
    key = load_secret_key()
    iv = os.urandom(16)

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(bytes.fromhex(plaintext_hex)) + padder.finalize()

    ciphertext = encryptor.update(padded_data) + encryptor.finalize()
    return iv.hex() + ciphertext.hex()

def decrypt_data(ciphertext_hex: str) -> str:
    key = load_secret_key()
    iv = bytes.fromhex(ciphertext_hex[:32])
    ciphertext = bytes.fromhex(ciphertext_hex[32:])

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()

    padded_data = decryptor.update(ciphertext) + decryptor.finalize()
    unpadder = padding.PKCS7(128).unpadder()
    plaintext = unpadder.update(padded_data) + unpadder.finalize()

    return plaintext.hex()
