# Mariyah Marshall senior project

from flask import Blueprint, request, jsonify
import sqlite3
import hashlib, os

from keys.key_utils import generate_keypair, save_private_key, public_key_to_pem


#blueprints
auth_bp = Blueprint('auth', __name__) #registers authication routes unter the auth blueprint so app.py can attach them

# REGISTER
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    username = data.get("username")
    password = data.get("password")
    #pulls the files out of the json

    if not username or not password:
        return jsonify({"error": "Missing fields"}), 400
    #if any of the feilds are missing it returns a bad request

    # Generate RSA keypair
    private_key, public_key = generate_keypair()

    # Save private key to file
    save_private_key(username, private_key)

    # Convert public key to PEM for database storage
    public_key_pem = public_key_to_pem(public_key)

    # Hash password
    password_hash, salt_hex = hash_password(password) 
   

    try: 
        #connecting to database
        conn = sqlite3.connect("database.sqlite") 
        cur = conn.cursor()
        #inserting new user
        cur.execute("""
        INSERT INTO users (username, password_hash, salt, public_key)
        VALUES (?, ?, ?, ?)
        """, (username, password_hash, salt_hex, public_key_pem))
        conn.commit() 
        conn.close() #saves and close database connection

        # user registered successfully
        return jsonify({"message": "User registered successfully"}), 201

    except sqlite3.IntegrityError:
        return jsonify({"error": "Username already exists"}), 409
    #handles duplicate usernames


# LOGIN
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Missing fields"}), 400

    conn = sqlite3.connect("database.sqlite")
    cur = conn.cursor()

     # Fetch user_id, password hash, and salt for login verification
    cur.execute("SELECT user_id, password_hash, salt FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    conn.close()

    if row is None:
        return jsonify({"error": "Invalid username or password"}), 401

    user_id, stored_hash, stored_salt_hex = row

    if verify_password(password, stored_hash, stored_salt_hex):
        return jsonify({
            "message": "Login successful",
            "user_id": user_id
        }), 200
    else:
        return jsonify({"error": "Invalid username or password"}), 401


# PUBLIC KEY LOOKUP
@auth_bp.route('/users/<username>/public_key', methods=['GET'])
def get_public_key(username):
    conn = sqlite3.connect("database.sqlite")
    cur = conn.cursor()

    #Returns the public key for a given username.
    cur.execute("SELECT public_key FROM users WHERE username = ?", (username,))
    # Fetch the first matching row from the query (returns None if no user found)
    row = cur.fetchone()
    conn.close()

    if not row:
        return jsonify({"error": "User not found"}), 404

    return jsonify({"public_key": row[0]}), 200


# PASSWORD HASHING
def hash_password(password):
    salt = os.urandom(16)
    salt_hex = salt.hex() #converts the salt into a hex string so sqlit3 can store it
    hashed = hashlib.sha256(salt+password.encode()).hexdigest() #hexdigest converts the bytes into a hexidecimal string
    return hashed, salt_hex


# PASSWORD VERIFICATION
def verify_password(password, stored_hash,stored_salt_hex):
    salt = bytes.fromhex(stored_salt_hex) #converts stored salt back into bytes
    hashed_attempt = hashlib.sha256(salt+password.encode()).hexdigest()
    return hashed_attempt == stored_hash #compares recomputed hash to stored hash