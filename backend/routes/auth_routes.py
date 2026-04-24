# Mariyah Marshall senior project
from database import db
import sqlite3
from models.user_model import UserModel
from flask_cors import cross_origin
from flask import Blueprint, request, jsonify
import hashlib, os

from keys.key_utils import generate_keypair, save_private_key, public_key_to_pem


#blueprints
auth_bp = Blueprint('auth', __name__) #registers authication routes unter the auth blueprint so app.py can attach them

# REGISTER
@auth_bp.route('https://secure-chat-project.onrender.com/register', methods=['POST'])
@cross_origin() # Enables CORS so the frontend and backend can talk to each other

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
        UserModel.insert_user(db, username, password_hash, salt_hex, public_key_pem)
        # user registered successfully
        return jsonify({"message": "User registered successfully"}), 201

    except sqlite3.IntegrityError:
        return jsonify({"error": "Username already exists"}), 409
    #handles duplicate usernames


# LOGIN
@auth_bp.route('https://secure-chat-project.onrender.com/login', methods=['POST'])
@cross_origin()
def login():
    data = request.get_json()

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"success": False, "message": "Missing fields"}), 400

    row = UserModel.get_user_by_username(db, username)

    if row is None:
        return jsonify({"success": False, "message": "Invalid username or password"}), 401

    user_id = row[0]
    stored_hash = row[2]
    stored_salt_hex = row[3]
    public_key_pem = row[4]

    # Verify password
    if not verify_password(password, stored_hash, stored_salt_hex):
        return jsonify({"success": False, "message": "Invalid username or password"}), 401

    # Load private key PEM from file
    try:
        with open(f"keys/user_keys/{username}_private.pem", "r") as f:
            private_key_pem = f.read()
    except FileNotFoundError:
        return jsonify({"success": False, "message": "Private key not found"}), 500

    # SUCCESS RESPONSE (matches frontend expectations)
    return jsonify({
        "success": True,
        "message": "Login successful",
        "user_id": user_id,
        "publicKey": public_key_pem,
        "encryptedPrivateKey": private_key_pem
    }), 200


# PUBLIC KEY LOOKUP
@auth_bp.route('https://secure-chat-project.onrender.com/users/<username>/public_key', methods=['GET'])
@cross_origin()
def get_public_key(username):
    row = UserModel.get_user_by_username(db, username)

    if not row:
        return jsonify({"error": "User not found"}), 404

    return jsonify({"public_key": row[4]}), 200


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