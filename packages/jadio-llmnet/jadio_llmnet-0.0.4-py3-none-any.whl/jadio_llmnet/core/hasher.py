import os
import hashlib
import binascii

def hash_password(password: str, salt: bytes = None) -> (str, str):
    if not salt:
        salt = os.urandom(16)
    pwd_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        100000
    )
    return binascii.hexlify(salt).decode(), binascii.hexlify(pwd_hash).decode()
