from backend.utils.crypto import generate_keypair, private_key_to_pem, public_key_to_pem

print("=== Testing RSA key generation and PEM conversion ===")

# Generate keys
private_key, public_key = generate_keypair()
print("Private key generated:", private_key)
print("Public key generated:", public_key)

# Convert to PEM
private_pem = private_key_to_pem(private_key)
public_pem = public_key_to_pem(public_key)

print("\nPrivate Key PEM:\n", private_pem)
print("\nPublic Key PEM:\n", public_pem)

# Basic checks
if "BEGIN PRIVATE KEY" in private_pem and "BEGIN PUBLIC KEY" in public_pem:
    print("\nSUCCESS: crypto.py works correctly")
else:
    print("\nERROR: crypto.py PEM conversion failed")