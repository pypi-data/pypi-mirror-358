import os

from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidTag

# --- Secure bytearray zeroing ---
def zero_bytes(b: bytearray):
    for i in range(len(b)):
        b[i] = 0

# --- Cryptographic functions ---
def derive_key(password: str, salt: bytes = None, n=2**18, r=8, p=1):
    if salt is None:
        salt = os.urandom(16)
    kdf = Scrypt(salt=salt, length=32, n=n, r=r, p=p, backend=default_backend())
    key_bytes = bytearray(kdf.derive(password.encode()))
    return key_bytes, salt

def encrypt_data_aesgcm(key: bytes, data: bytes) -> bytes:
    nonce = os.urandom(12)
    return nonce + AESGCM(key).encrypt(nonce, data, None)

def decrypt_data_aesgcm(key: bytes, enc: bytes) -> bytes:
    nonce, ciphertext = enc[:12], enc[12:]
    try:
        return AESGCM(key).decrypt(nonce, ciphertext, None)
    except InvalidTag:
        raise ValueError("Incorrect password or corrupted archive")

def encrypt_data(data: bytes, password: str, n: int, r: int, p: int):
    key = None
    
    try:
        key, salt = derive_key(password, n=n, r=r, p=p)
        encrypted_data = salt + encrypt_data_aesgcm(bytes(key), data)
    except:
        raise
    finally:
        if key:
            zero_bytes(key)
            
    return encrypted_data

def decrypt_data(encrypted_data: bytes, password: str, n: int, r: int, p: int):
    key = None
    
    try:
        salt, enc = encrypted_data[:16], encrypted_data[16:]
        key, _ = derive_key(password, salt, n=n, r=r, p=p)
        dec = decrypt_data_aesgcm(bytes(key), enc)
    except:
        raise
    finally:
        if key:
            zero_bytes(key)
            
    return dec