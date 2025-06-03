from flask import Blueprint, render_template, flash, redirect, url_for, request, session
import sqlite3

# Create a Blueprint for payment_pending routes
payment_pending = Blueprint('payment_pending', __name__)

# Function to fetch pending payment customers where delivery is 'yes'
def fetch_pending_customers(state_type):
    try:
        with sqlite3.connect('crm.db') as conn:
            conn.row_factory = sqlite3.Row  # So we can access columns by name
            cursor = conn.cursor()

            if state_type == 'rajasthan':
                query = """
                    SELECT id, khccode, firmname, billno, biltyno, amount, city, mobile, payment_status
                    FROM customers
                    WHERE LOWER(state) = 'rajasthan' AND LOWER(delivery) = 'yes' AND LOWER(payment_status) = 'pending'
                """
            else:
                query = """
                    SELECT id, khccode, firmname, billno, biltyno, amount, city, mobile, payment_status
                    FROM customers
                    WHERE LOWER(state) != 'rajasthan' AND LOWER(delivery) = 'yes' AND LOWER(payment_status) = 'pending'
                """

            cursor.execute(query)
            customers = cursor.fetchall()

    except sqlite3.Error as e:
        flash(f"Database error: {e}", "error")
        customers = []

    return customers

# Function to mark payment as received (paid)
def mark_payment_as_paid(customer_id):
    try:
        with sqlite3.connect('crm.db') as conn:
            cursor = conn.cursor()

            # Update payment_status to 'paid' for the given customer_id
            cursor.execute('''
                UPDATE customers
                SET payment_status = 'paid'
                WHERE id = ?
            ''', (customer_id,))

            conn.commit()

            flash("Payment marked as paid successfully!", "success")

    except sqlite3.Error as e:
        flash(f"Database error: {e}", "error")

# Route to display the main payment pending page
@payment_pending.route('/payment_pending')
def payment_pending_page():
    return render_template('payment_pending.html')

# Rajasthan Customers Route
@payment_pending.route('/rajasthan_entries')
def rajasthan_entries():
    customers = fetch_pending_customers('rajasthan')
    if not customers:
        flash("No pending payment customers for Rajasthan with delivery 'yes'.", "warning")
    return render_template('rajasthan_entries.html', customers=customers)

# Other States Customers Route
@payment_pending.route('/other_states_entries')
def other_states_entries():
    customers = fetch_pending_customers('other')
    if not customers:
        flash("No pending payment customers for other states with delivery 'yes'.", "warning")
    return render_template('other_states_entries.html', customers=customers)

# Route to mark a customer payment as paid for Rajasthan customers
@payment_pending.route('/mark_payment_paid/<int:customer_id>', methods=['POST'])
def mark_payment_paid(customer_id):
    mark_payment_as_paid(customer_id)  # Mark the payment as paid
    return redirect(request.referrer)  # Redirect back to the same page where the action was initiated

# Route to mark a customer payment as paid for other states customers
@payment_pending.route('/mark_payment_paid_other/<int:customer_id>', methods=['POST'])
def mark_payment_paid_other(customer_id):
    mark_payment_as_paid(customer_id)  # Mark the payment as paid
    return redirect(request.referrer)  # Redirect back to the same page where the action was initiated
