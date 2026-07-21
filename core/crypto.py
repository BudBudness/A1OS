import os
import base64
from cryptography.fernet import Fernet

KEY_FILE = "cfg/storage.key"

def get_cipher():
    if not os.path.exists(KEY_FILE):
        os.makedirs(os.path.dirname(KEY_FILE), exist_ok=True)
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as f:
            f.write(key)
    else:
        with open(KEY_FILE, "rb") as f:
            key = f.read()
    return Fernet(key)

def encrypt_data(data: str) -> str:
    cipher = get_cipher()
    return cipher.encrypt(data.encode()).decode()

def decrypt_data(data: str) -> str:
    cipher = get_cipher()
    return cipher.decrypt(data.encode()).decode()
