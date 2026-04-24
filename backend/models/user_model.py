# UserModel handles all database operations for the users table
class UserModel:
    @staticmethod
    # @staticmethod means this method doesn't need an object or class data, so you call it directly on the class.

    def create_table():
        # Table is created in database.py
        pass

    @staticmethod
    def insert_user(conn, username, password_hash, salt, public_key):
        # Inserts a new user into the database
        conn.execute("""
            INSERT INTO users (username, password_hash, salt, public_key)
            VALUES (?, ?, ?, ?)
        """, (username, password_hash, salt, public_key))
        conn.commit()

    @staticmethod
    def get_user_by_username(conn, username):
        # Retrieves a user row by username
        cursor = conn.execute("""
            SELECT * FROM users WHERE username = ?
        """, (username,))
        return cursor.fetchone()
