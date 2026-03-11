from flask import Blueprint, request, jsonify
import sqlite3
import hashlib, os

#blueprints
auth_bp = Blueprint('auth', __name__) #registers authication routes unter the auth blueprint so app.py can attach them

#Real Register Route
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    username = data.get("username")
    password = data.get("password")
    public_key = data.get("public_key")
    #pulls the files out of the json

    if not username or not password or not public_key:
        return jsonify({"error": "Missing fields"}), 400
    #if any of the feilds are missing it returns a bad request

    password_hash, salt_hex = hash_password(password) 
    #calls hashing function

    try: 
        #connecting to database
        conn = sqlite3.connect("database.sqlite") 
        cur = conn.cursor()
        #inserting new user
        cur.execute("""
        INSERT INTO users (username, password_hash, salt, public_key)
        VALUES (?, ?, ?, ?)
        """, (username, password_hash, salt_hex, public_key))
        conn.commit() 
        conn.close() #saves and close database connection

        # user registered successfully
        return jsonify({"message": "User registered successfully"}), 201

    except sqlite3.IntegrityError:
        return jsonify({"error": "Username already exists"}), 409
    #handles duplicate usernames



#Real login route
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Missing fields"}), 400

    conn = sqlite3.connect("database.sqlite")
    cur = conn.cursor()
    cur.execute("SELECT password_hash, salt FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    conn.close()

    if row is None:
        return jsonify({"error": "Invalid username or password"}), 401

    stored_hash, stored_salt_hex = row

    if verify_password(password, stored_hash, stored_salt_hex):
        return jsonify({"message": "Login successful"}), 200
    else:
        return jsonify({"error": "Invalid username or password"}), 401
  






#password hashing
def hash_password(password):
    salt = os.urandom(16)
    salt_hex = salt.hex() #converts the salt into a hex string so sqlit3 can store it
    hashed = hashlib.sha256(salt+password.encode()).hexdigest() #hexdigest converts the bytes into a hexidecimal string
    return hashed, salt_hex

#verifying password
def verify_password(password, stored_hash,stored_salt_hex):
    salt = bytes.fromhex(stored_salt_hex) #converts stored salt back into bytes
    hashed_attempt = hashlib.sha256(salt+password.encode()).hexdigest()
    return hashed_attempt == stored_hash #compares recomputed hash to stored hash