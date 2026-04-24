# pulls the functions from hashing.py to test them
from backend.utils.hashing import hash_password, verify_password

print("=== Testing hash_password() and verify_password() ===")

# Hash a password
password = "mypassword123"
hashed, salt_hex = hash_password(password)

print("Hashed password:", hashed)
print("Salt (hex):", salt_hex)

# Verify the correct password
is_correct = verify_password(password, hashed, salt_hex)
print("Correct password verification:", is_correct)

# Verify a wrong password
is_wrong = verify_password("wrongpassword", hashed, salt_hex)
print("Wrong password verification:", is_wrong)

# Final result
if is_correct and not is_wrong:
    print("SUCCESS: hashing.py works correctly")
else:
    print("ERROR: hashing.py has a problem")