# Mariyah Marshall senior project
# This file creates ONE shared SQLite connection for the entire backend.
# It also ensures the tables exist without deleting data every time.
import os
print("USING DATABASE:", os.path.abspath("database.sqlite"))


import sqlite3

# Create a single shared database connection.
# check_same_thread=False allows Flask to use this connection
# across multiple threads (each request runs in its own thread).
db = sqlite3.connect("database.sqlite", check_same_thread=False)

# Create the USERS table if it does not already exist.
# This prevents wiping the data every time the server restarts.
db.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    salt TEXT NOT NULL,
    public_key TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")


# Create the MESSAGES table if it does not already exist.
# Stores encrypted messages and encrypted symmetric keys.
db.execute("""
CREATE TABLE IF NOT EXISTS messages (
    message_id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender_id INTEGER NOT NULL,
    receiver_id INTEGER NOT NULL,
    encrypted_message TEXT NOT NULL,
    encrypted_key TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    delivered BOOLEAN DEFAULT 0,
    client_timestamp INTEGER,
    encrypted_key_sender TEXT,
    FOREIGN KEY (sender_id) REFERENCES users(user_id),
    FOREIGN KEY (receiver_id) REFERENCES users(user_id)
)
""")
# Save changes to the database.
db.commit()

def get_db():
    return db


