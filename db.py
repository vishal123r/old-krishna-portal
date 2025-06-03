# db.py
import sqlite3

def get_db_connection():
    conn = sqlite3.connect('crm.db')
    conn.row_factory = sqlite3.Row  # This makes SQLite results accessible by column name
    return conn
