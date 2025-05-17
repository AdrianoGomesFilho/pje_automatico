import os
import json
from cryptography.fernet import Fernet

def get_key_file():
    return os.path.expanduser('~/encryption_key.key')

def ensure_key_exists():
    key_file = get_key_file()
    if not os.path.exists(key_file):
        with open(key_file, 'wb') as f:
            f.write(Fernet.generate_key())
    with open(key_file, 'rb') as f:
        return f.read()

ENCRYPTION_KEY = ensure_key_exists()
cipher = Fernet(ENCRYPTION_KEY)

def encrypt_credentials(credentials):
    credentials_json = json.dumps(credentials).encode('utf-8')
    return cipher.encrypt(credentials_json)

def decrypt_credentials(encrypted_credentials):
    decrypted_json = cipher.decrypt(encrypted_credentials).decode('utf-8')
    return json.loads(decrypted_json)

def save_credentials(file_path, credentials):
    encrypted = encrypt_credentials(credentials)
    with open(file_path, 'wb') as cred_file:
        cred_file.write(encrypted)

def load_credentials(file_path):
    with open(file_path, 'rb') as cred_file:
        encrypted = cred_file.read()
    return decrypt_credentials(encrypted)
