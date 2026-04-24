# MessageModel handles all database operations for the messages table

class MessageModel:
    @staticmethod
    # @staticmethod means this method doesn't need an object or class data, so you call it directly on the class.

    def insert_message(db, sender_id, receiver_id, encrypted_message,
                       encrypted_key_receiver, encrypted_key_sender,
                       client_timestamp):
        # FIX: get the actual SQLite connection
        conn = db

        conn.execute("""
            INSERT INTO messages (
                    sender_id, 
                    receiver_id, 
                    encrypted_message, 
                    encrypted_key,          -- now treated as encrypted_key_receiver
                    encrypted_key_sender,   -- NEW COLUMN
                    client_timestamp
                    )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
                sender_id, 
                receiver_id, 
                encrypted_message, 
                encrypted_key_receiver,     # NEW NAME
                encrypted_key_sender,       # NEW ARG 
                client_timestamp
            ))
        conn.commit()

    @staticmethod
    def get_messages_between(db, user1, user2):
        cursor = db.cursor()
        cursor.execute("""
            SELECT
                message_id,
                sender_id,
                receiver_id,
                encrypted_message,
                encrypted_key,          -- receiver key
                timestamp,
                delivered,
                client_timestamp,
                encrypted_key_sender    -- NEW COLUMN
            FROM messages
            WHERE (sender_id = ? AND receiver_id = ?)
            OR (sender_id = ? AND receiver_id = ?)
            ORDER BY timestamp ASC
        """, (user1, user2, user2, user1))
        return cursor.fetchall()

    @staticmethod
    def get_messages_for_user(db, user_id):
        # Retrieves all messages sent TO a specific user
        conn = db
        cursor = conn.execute("""
            SELECT 
                message_id, 
                sender_id, 
                encrypted_message, 
                encrypted_key,          -- receiver key
                timestamp, 
                delivered,
                encrypted_key_sender    -- NEW COLUMN (optional)
            FROM messages
            WHERE receiver_id = ?
            ORDER BY timestamp ASC
        """, (user_id,))
        return cursor.fetchall()
