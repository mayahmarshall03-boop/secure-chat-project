# Mariyah Marshall senior project
import sqlite3

conn=sqlite3.connect('database.sqlite');
cur=conn.cursor();

#Users table
cur.execute("""DROP TABLE IF EXISTS users""")
cur.execute("""CREATE TABLE users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT, 
    username TEXT UNIQUE NOT NULL, 
    password_hash TEXT NOT NULL, 
    public_key TEXT NOT NULL, 
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP )""")
conn.commit();


#messages table
cur.execute("""DROP TABLE IF EXISTS messages""")
cur.execute("""CREATE TABLE messages (
        message_id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_id INTEGER NOT NULL,
        receiver_id INTEGER NOT NULL,
        encrypted_message TEXT NOT NULL,
        encrypted_key TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        delivered BOOLEAN DEFAULT 0,
        FOREIGN KEY (sender_id) REFERENCES users(user_id),
        FOREIGN KEY (receiver_id) REFERENCES users(user_id))""")
conn.commit();