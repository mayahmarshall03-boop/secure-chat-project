# Mariyah Marshall senior project
from flask import Blueprint, request, jsonify
from database import db
from models.message_model import MessageModel
from flask_cors import cross_origin
import json

messages_bp = Blueprint('messages', __name__)

# SEND MESSAGE
@messages_bp.route('/messages/send', methods=['POST'])
@cross_origin() # Enables CORS so the frontend and backend can talk to each other
def send_message():
    data = request.get_json()

    sender_id = data.get("sender_id")
    receiver_id = data.get("receiver_id")
    client_timestamp = data.get("client_timestamp")

    print("TYPE OF encrypted_message:", type(data.get("encrypted_message")))
    print("VALUE OF encrypted_message:", data.get("encrypted_message"))

    encrypted_message = json.dumps(data.get("encrypted_message")) # Ensure encrypted_message is stored as a JSON string, not a Python dict
   
    print("AFTER DUMPS TYPE:", type(encrypted_message))
    print("AFTER DUMPS VALUE:", encrypted_message)

    encrypted_key_receiver = data.get("encrypted_key_receiver")
    encrypted_key_sender   = data.get("encrypted_key_sender")

    print("TYPE OF encrypted_key_receiver:", type(encrypted_key_receiver))
    print("VALUE OF encrypted_key_receiver:", encrypted_key_receiver)

    print("TYPE OF encrypted_key_sender:", type(encrypted_key_sender))
    print("VALUE OF encrypted_key_sender:", encrypted_key_sender)



    # Validation
    if not sender_id:
        return jsonify({"error": "sender_id is required"}), 400
    if not receiver_id:
        return jsonify({"error": "receiver_id is required"}), 400
    if not encrypted_message:
        return jsonify({"error": "encrypted_message is required"}), 400
    if not encrypted_key_receiver:
        return jsonify({"error": "encrypted_key_receiver is required"}), 400
    if not encrypted_key_sender:
        return jsonify({"error": "encrypted_key_sender is required"}), 400

    
    # Insert using model
    MessageModel.insert_message(
        db, 
        sender_id, 
        receiver_id, 
        encrypted_message, 
        encrypted_key_receiver, 
        encrypted_key_sender, 
        client_timestamp)
    
    return jsonify({"message": "Message sent successfully"}), 201

# GET MESSAGE
@messages_bp.route('/messages/get', methods=['GET'])
@cross_origin()
def get_messages():
    # Pulls the user_id from the URL (e.g., /messages/get?user_id=3)
    user_id = request.args.get("user_id")

    if not user_id:
        return jsonify({"error": "user_id is required"}), 400
    
    # Fetch using model
    rows = MessageModel.get_messages_for_user(db, user_id)
    
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

@messages_bp.route('/messages/conversation', methods=['GET'])
@cross_origin()
def get_conversation():
    user1 = request.args.get("user1")
    user2 = request.args.get("user2")

    if not user1 or not user2:
        return jsonify({"error": "user1 and user2 are required"}), 400

    rows = MessageModel.get_messages_between(db, user1, user2)

    messages = []
    for row in rows:
        messages.append({
            "message_id": row[0],
            "sender_id": row[1],
            "receiver_id": row[2],
            "encrypted_message": row[3],
            "encrypted_key_receiver": row[4],
            "timestamp": row[5],
            "delivered": row[6],
            "client_timestamp": row[7],
            "encrypted_key_sender": row[8]
        })

    return jsonify({"messages": messages}), 200
