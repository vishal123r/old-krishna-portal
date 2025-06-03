from flask import Blueprint, render_template, g
import sqlite3
from datetime import datetime

# Create the blueprint for daily summary
daily_summary_bp = Blueprint('daily_summary_bp', __name__)

def get_db_connection():
    """Establish and return a connection to the database"""
    if 'db' not in g:
        g.db = sqlite3.connect('crm.db')  # Connect to the CRM database
        g.db.row_factory = sqlite3.Row  # This allows us to access columns by name
    return g.db

# Updated route for daily summary
@daily_summary_bp.route('/daily_summary', methods=['GET'])
def daily_summary():
    today = datetime.today().strftime('%Y-%m-%d')  # Get today's date in 'YYYY-MM-DD' format
    conn = get_db_connection()  # Get DB connection
    cursor = conn.cursor()

    # Query for the number of customers who placed orders today
    cursor.execute('''SELECT COUNT(*) FROM customers WHERE DATE(date) = ?''', (today,))
    customer_count = cursor.fetchone()[0]

    # Query for the total payment received today
    cursor.execute('''SELECT SUM(receive_amount) FROM customers WHERE DATE(date) = ?''', (today,))
    total_payment = cursor.fetchone()[0] or 0.0  # Default to 0.0 if no payment

    # Query for deliveries marked as "YES" and their payment received
    cursor.execute('''SELECT COUNT(*), SUM(receive_amount) FROM customers WHERE delivery = "YES" AND DATE(date) = ?''', (today,))
    deliveries_count, total_delivery_payment = cursor.fetchone()

    # Query for today's customer details with their payment status and delivery details
    cursor.execute('''SELECT id, name, amount, receive_amount, delivery, payment_received_date, delivery_date
                      FROM customers WHERE DATE(date) = ?''', (today,))
    customers = cursor.fetchall()

    conn.close()  # Close the connection to the database

    # Ensure default values for payments
    total_payment = round(total_payment if total_payment is not None else 0.0, 2)
    total_delivery_payment = round(total_delivery_payment if total_delivery_payment is not None else 0.0, 2)

    # Render the daily summary page with customer data
    return render_template('daily_summary.html', 
                           customer_count=customer_count, 
                           total_payment=total_payment, 
                           deliveries_count=deliveries_count, 
                           total_delivery_payment=total_delivery_payment, 
                           customers=customers)
