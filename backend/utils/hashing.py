import hashlib
import os


def hash_password(password: str):
    # hashes a password using SHA-256 with a random 16 byte salt
    #returns hashed_password_hex, salt_hex
    salt = os.urandom(16)
    salt_hex = salt.hex()
    hashed = hashlib.sha256(salt + password.encode()).hexdigest()
    return hashed, salt_hex


def verify_password(password: str, stored_hash: str, stored_salt_hex: str):
    #recomputes the hash using the stored salt and compare them
    #if the password matches it returns True
    salt = bytes.fromhex(stored_salt_hex)
    hashed_attempt = hashlib.sha256(salt + password.encode()).hexdigest()
    return hashed_attempt == stored_hash