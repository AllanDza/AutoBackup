# secure_utils.py
import hashlib, json, os
from cryptography.fernet import Fernet
import logging

def hash_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            h.update(chunk)
    return h.hexdigest()

def save_hash_manifest(files, output='hash_manifest.json'):
    manifest = {f: hash_file(f) for f in files}
    with open(output, 'w') as fp:
        json.dump(manifest, fp, indent=4)

def encrypt_file(input_path, key_path="secret.key"):
    if not os.path.exists(key_path):
        key = Fernet.generate_key()
        with open(key_path, 'wb') as kf:
            kf.write(key)
    else:
        key = open(key_path, 'rb').read()
    
    fernet = Fernet(key)
    with open(input_path, 'rb') as f:
        data = f.read()
    encrypted = fernet.encrypt(data)
    with open(input_path + '.enc', 'wb') as ef:
        ef.write(encrypted)
    return input_path + '.enc'

from cryptography.fernet import Fernet
import os

def decrypt_file(encrypted_path, key_path="secret.key"):
    if not os.path.exists(key_path):
        raise Exception("Encryption key not found.")

    key = open(key_path, 'rb').read()
    fernet = Fernet(key)

    with open(encrypted_path, 'rb') as ef:
        encrypted_data = ef.read()

    decrypted_data = fernet.decrypt(encrypted_data)

    decrypted_path = encrypted_path.replace(".enc", "")
    with open(decrypted_path, 'wb') as df:
        df.write(decrypted_data)

    return decrypted_path

def verify_file_hashes(hash_manifest_path):
    """
    Verifies file integrity using SHA-256 hashes stored in hash_manifest.json.
    Returns a list of files that have been modified or deleted.
    """
    modified_files = []
    
    with open(hash_manifest_path, "r") as f:
        hash_data = json.load(f)

    for file_path, original_hash in hash_data.items():
        current_hash = hash_file(file_path)

        # File might be deleted or changed
        if current_hash != original_hash:
            modified_files.append(file_path)

    return modified_files