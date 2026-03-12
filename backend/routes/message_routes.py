# Mariyah Marshall senior project
from flask import Blueprint, request, jsonify
import sqlite3
import time

messages_bp = Blueprint('messages', __name__)

# SEND MESSAGE
@messages_bp.route('/messages/send', methods=['POST'])
def send_message():
    data = request.get_json()

    sender_id = data.get("sender_id")
    receiver_id = data.get("receiver_id")
    encrypted_message = data.get("encrypted_message")
    encrypted_key = data.get("encrypted_key")

    # Validation
    if not sender_id:
        return jsonify({"error": "sender_id is required"}), 400

    if not receiver_id:
        return jsonify({"error": "receiver_id is required"}), 400

    if not encrypted_message:
        return jsonify({"error": "encrypted_message is required"}), 400

    if not encrypted_key:
        return jsonify({"error": "encrypted_key is required"}), 400

    # Insert into database
    conn = sqlite3.connect("database.sqlite")
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO messages (sender_id, receiver_id, encrypted_message, encrypted_key)
        VALUES (?, ?, ?, ?)
    """, (sender_id, receiver_id, encrypted_message, encrypted_key))
    conn.commit()
    conn.close()
    
    return jsonify({"message": "Message sent successfully"}), 201

# GET MESSAGE
@messages_bp.route('/messages/get', methods=['GET'])
def get_messages():
    # Pulls the user_id from the URL (e.g., /messages/get?user_id=3)
    user_id = request.args.get("user_id")

    if not user_id:
        return jsonify({"error": "user_id is required"}), 400
    
    #connecting to the database
    conn = sqlite3.connect("database.sqlite")
    cur = conn.cursor()

    cur.execute("""
        SELECT message_id, sender_id, encrypted_message, encrypted_key, timestamp, delivered
        FROM messages
        WHERE receiver_id = ?
        ORDER BY timestamp ASC
    """, (user_id,))
    # Fetch all rows returned by the SELECT query
    rows = cur.fetchall()
    conn.close()
    
    # Convert each database row (tuple) into a JSON-friendly dictionary
    messages = [] #creating an empty list
    for row in rows: #each row is a tuple
        messages.append({ #add it to the list 
            #Coverts tuple into JSON dictionary
            "message_id": row[0],
            "sender_id": row[1],
            "encrypted_message": row[2],
            "encrypted_key": row[3],
            "timestamp": row[4],
            "delivered": row[5]
        })
    #return the list as JSON
    return jsonify({"messages": messages}), 200 

