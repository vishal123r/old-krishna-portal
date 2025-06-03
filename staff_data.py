# staff_data.py
from datetime import datetime
import sqlite3

DATABASE = 'crm.db'  # Database file

# Function to check if data has been already shown to another staff member today
def data_already_seen(staff_id, data_id):
    today = datetime.today().strftime('%Y-%m-%d')  # Get today's date in YYYY-MM-DD format
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Check if this data has already been viewed by another staff today
    cursor.execute('''SELECT * FROM staff_data_viewed 
                      WHERE staff_id != ? AND data_id = ? AND view_date = ?''', 
                   (staff_id, data_id, today))
    result = cursor.fetchone()
    conn.close()
    
    return result is not None  # If result exists, the data has already been seen

# Function to mark the data as viewed by the staff member
def mark_data_as_viewed(staff_id, data_id):
    today = datetime.today().strftime('%Y-%m-%d')  # Get today's date
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Insert a record indicating this data has been viewed by the staff member today
    cursor.execute('''INSERT INTO staff_data_viewed (staff_id, data_id, view_date) 
                      VALUES (?, ?, ?)''', (staff_id, data_id, today))
    
    conn.commit()
    conn.close()
