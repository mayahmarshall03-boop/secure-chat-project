
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

def generate_keypair():
    #generates a 2048-bit RSA keypair
    #returns private_key, public_key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    public_key = private_key.public_key() #public key is derived from the private key
    return private_key, public_key

def private_key_to_pem(private_key):
    #converts a private to PEM unencrypted
    #returns a UTF-8 string
    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM, #output key in PEM format
        format=serialization.PrivateFormat.PKCS8, #use the PKCS8 standard for private keys
        encryption_algorithm=serialization.NoEncryption() #save the key unencrypted
    )
    return pem.decode()

def public_key_to_pem(public_key):
    #converts public key to PEM
    #returns a UTF-8 string
    pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return pem.decode()