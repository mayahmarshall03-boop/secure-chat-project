from flask import Blueprint, request, jsonify

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    return jsonify({"message": "register endpoint works"})

@auth_bp.route('/login', methods=['POST'])
def login():
    return jsonify({"message": "login endpoint works"})
