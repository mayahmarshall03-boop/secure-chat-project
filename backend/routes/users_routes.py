from flask import Blueprint, jsonify
from database import get_db  # SQLite connection helper

users_bp = Blueprint("users", __name__)

@users_bp.route("/users", methods=["GET"])
def get_users():
    conn = get_db()
    cursor = conn.execute("SELECT user_id, username, public_key FROM users")
    rows = cursor.fetchall()

    users = []
    for row in rows:
        users.append({
            "user_id": row[0],
            "username": row[1],
            "public_key": row[2]
        })

    return jsonify({"users": users})
