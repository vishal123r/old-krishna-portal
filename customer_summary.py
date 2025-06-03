from flask import Blueprint, render_template, request
from db import get_db_connection

# Blueprint setup without a url_prefix
customer_summary_bp = Blueprint('customer_summary', __name__)

@customer_summary_bp.route('/customer_summary')
def customer_summary():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Query for state-level summary
    cursor.execute('''
        SELECT state, COUNT(id) as total_customers, SUM(amount) as total_amount
        FROM customers
        GROUP BY state
    ''')
    states = cursor.fetchall()
    conn.close()
    
    return render_template('customer_summary.html', states=states)

@customer_summary_bp.route('/city_summary/<state>', methods=['GET'])
def city_summary(state):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Query for city-level summary
    cursor.execute('''
        SELECT city, COUNT(id) as total_customers, SUM(amount) as total_amount
        FROM customers
        WHERE state = ?
        GROUP BY city
    ''', (state,))
    cities = cursor.fetchall()
    conn.close()

    return render_template('city_summary.html', cities=cities, state=state)
