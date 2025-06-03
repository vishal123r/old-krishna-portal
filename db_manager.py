import sqlite3
import logging
from datetime import datetime

DB_NAME = "crm.db"

def connect_db():
    """Establish connection with the database."""
    try:
        conn = sqlite3.connect(DB_NAME)
        logging.info("✅ Database connection successful.")
        return conn
    except Exception as e:
        logging.error(f"❌ Database connection error: {e}")
        return None

def get_orders_count_by_date(date):
    """Fetch orders count for a specific date."""
    try:
        conn = connect_db()
        if not conn:
            return "⚠️ Database connection failed."

        cursor = conn.cursor()
        logging.debug(f"Executing query: SELECT COUNT(*) FROM customers WHERE strftime('%Y-%m-%d', order_date) = '{date}'")
        cursor.execute("SELECT COUNT(*) FROM customers WHERE strftime('%Y-%m-%d', order_date) = ?", (date,))
        result = cursor.fetchone()
        
        if result:
            logging.debug(f"Query result: {result[0]} orders found for {date}")
        else:
            logging.warning(f"No orders found for {date}")
        
        conn.close()
        
        return result[0] if result else 0
    except Exception as e:
        logging.error(f"❌ Database error (get_orders_count_by_date): {e}")
        return "⚠️ Error fetching data."
