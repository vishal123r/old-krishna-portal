import sqlite3
from db import get_db_connection
from datetime import datetime

def get_customer_details_and_score(customer_id):
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row  # Ensure the rows are returned as dictionaries
    cursor = conn.cursor()

    # Fetch customer details
    cursor.execute('SELECT * FROM customers WHERE id = ?', (customer_id,))
    customer = cursor.fetchone()

    # Fetch payment history for the customer
    cursor.execute('SELECT * FROM payment_history WHERE customer_id = ?', (customer_id,))
    payments = cursor.fetchall()

    # Initialize score
    score = 0

    # **1. Order Frequency (Using payment history count as a proxy for orders)**
    order_count = len(payments)  # Assume each payment is related to an order
    if order_count >= 10:  # 10 or more orders
        score += 30
    elif order_count >= 5:  # 5 to 9 orders
        score += 20
    else:  # Fewer than 5 orders
        score += 10

    # **2. Order Recency (Using payment history dates)**
    if payments:
        # Find the date of the most recent payment
        last_payment_date = datetime.strptime(payments[0]['payment_date'], '%Y-%m-%d')
        days_since_last_payment = (datetime.now() - last_payment_date).days
        if days_since_last_payment <= 30:  # Payment in the last month
            score += 20
        elif days_since_last_payment <= 90:  # Payment in the last 3 months
            score += 10
        else:
            score -= 10

    # **3. Payment Timeliness**
    on_time_payments = 0
    late_payments = 0

    for payment in payments:
        due_date = datetime.strptime(payment['due_date'], '%Y-%m-%d')
        payment_date = datetime.strptime(payment['payment_date'], '%Y-%m-%d')
        if payment_date <= due_date:  # Paid on time
            on_time_payments += 1
        else:  # Late payment
            late_payments += 1

    # **Bonus for on-time payments**
    if order_count > 0:  # Only check timeliness if there are payments
        if on_time_payments / len(payments) > 0.8:  # More than 80% on-time payments
            score += 25
        elif on_time_payments / len(payments) > 0.5:  # More than 50% on-time payments
            score += 15
        else:  # If more than 50% payments are late
            score -= 20

    # **Penalty for late payments**
    if late_payments > 3:
        score -= 15  # Penalize for more than 3 late payments

    # **4. Amount Paid**
    total_paid = sum(payment['amount'] for payment in payments)
    if total_paid > 10000:
        score += 30  # High spender
    elif total_paid > 5000:
        score += 20  # Moderate spender
    else:
        score += 10  # Low spender

    conn.close()

    return customer, score
