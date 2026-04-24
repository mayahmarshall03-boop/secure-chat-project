# Mariyah Marshall senior project

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import os

KEY_DIR = "keys/user_keys"
os.makedirs(KEY_DIR, exist_ok=True)

def generate_keypair():
    #Generate a 2048-bit RSA keypair.
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    public_key = private_key.public_key()
    return private_key, public_key

def save_private_key(username, private_key):
    #Save the private key as a PEM file inside keys/user_keys/.
    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption() #this saves the private key unencrpyted so it doent need a password to access
    )

    filepath = os.path.join(KEY_DIR, f"{username}_private.pem")
    with open(filepath, "wb") as f: #opens the file in binary mode because pem data is in bytes
        f.write(pem)



def public_key_to_pem(public_key):
    #Convert the public key to a PEM string for database storage.
    pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return pem.decode()