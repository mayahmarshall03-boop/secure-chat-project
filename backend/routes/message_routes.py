from flask import Blueprint, request, jsonify

messages_bp = Blueprint('messages', __name__)

@messages_bp.route('/messages/send', methods=['POST'])
def send_message():
    return jsonify({"message": "send endpoint works"})

@messages_bp.route('/messages/get', methods=['GET'])
def get_messages():
    return jsonify({"messages": []})
