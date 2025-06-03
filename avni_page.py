from flask import Blueprint, render_template, request, redirect, url_for, session
import sqlite3
from datetime import datetime
from flask import Blueprint, render_template, session, flash, redirect, url_for

# Create a Blueprint for the avni page
avni_bp = Blueprint('avni_bp', __name__)

# Helper function to get a database connection
def get_db_connection():
    conn = sqlite3.connect('crm.db')  # Ensure the correct path to your database
    conn.row_factory = sqlite3.Row  # This allows access to rows as dictionaries
    return conn


@avni_bp.route('/avni_page')
def avni_page():
    # Check if the user has permission to view this page
    if 'avni' not in session['permissions'] and 'admin' not in session['permissions']:
        flash('You do not have permission to access this page. Logging you out.', 'danger')
        session.pop('username', None)  # Log the user out
        return redirect(url_for('login'))  # Redirect to login page

    try:
        # Get a database connection
        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch records where the reference_name is 'avni', case-insensitive
        cursor.execute('SELECT * FROM customers WHERE LOWER(reference_name) = "avni" ORDER BY id DESC')
        customers = cursor.fetchall()

        # Initialize the dictionary to store additional mobile numbers
        additional_mobiles = {}

        # Fetch additional mobile numbers for each customer
        cursor.execute('SELECT customer_id, mobile_number FROM additional_mobiles')
        for row in cursor.fetchall():
            customer_id = row['customer_id']
            mobile_number = row['mobile_number']
            if customer_id not in additional_mobiles:
                additional_mobiles[customer_id] = []
            additional_mobiles[customer_id].append(mobile_number)

        # Calculate total amount and the number of customers
        total_amount = sum(
            float(customer['amount']) if customer['amount'] else 0 for customer in customers
        )  # Convert 'amount' to float, default to 0 if it's None or invalid
        total_customers = len(customers)

        # Close the database connection
        conn.close()

        # Render the template and pass the customer data, total amount, total customers, and additional mobiles
        return render_template('avni/avni.html', customers=customers, total_amount=total_amount, total_customers=total_customers, additional_mobiles=additional_mobiles)

    except sqlite3.DatabaseError as e:
        print(f"Database error: {e}")
        return "An error occurred while fetching data."

@avni_bp.route('/avni/edit/<int:customer_id>', methods=['GET', 'POST'])
def avni_edit_page(customer_id):
    if 'avni' not in session['permissions'] and 'admin' not in session['permissions']:
        flash('You do not have permission to access this page. Logging you out.', 'danger')
        session.pop('username', None)  # Log the user out
        return redirect(url_for('login'))  # Redirect to login page

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # If the method is GET, fetch the customer details based on the ID
        if request.method == 'GET':
            cursor.execute('SELECT * FROM customers WHERE id = ?', (customer_id,))
            customer = cursor.fetchone()

            if not customer:
                conn.close()
                return f"Customer with ID {customer_id} not found."

            # Convert the sqlite3.Row object to a dictionary to allow modification
            customer_dict = dict(customer)

            # Format delivery_date for display (DD/MM/YYYY) for the input field
            if customer_dict['delivery_date']:
                try:
                    formatted_delivery_date = datetime.strptime(customer_dict['delivery_date'], '%Y-%m-%d').strftime('%d/%m/%Y')
                    customer_dict['delivery_date'] = formatted_delivery_date
                except ValueError:
                    customer_dict['delivery_date'] = ''  # In case of an invalid date format

            return render_template('avni/avni_edit.html', customer=customer_dict)

        # If the method is POST, update the customer details in the database
        if request.method == 'POST':
            # Process the date field for saving in the database
            date_str = request.form['date']
            try:
                formatted_date = datetime.strptime(date_str, '%d/%m/%Y').strftime('%Y-%m-%d')
            except ValueError:
                return "Invalid date format. Please use DD/MM/YYYY."

            # Similarly for delivery_date
            delivery_date_str = request.form['delivery_date']
            formatted_delivery_date = ''
            if delivery_date_str:
                try:
                    formatted_delivery_date = datetime.strptime(delivery_date_str, '%d/%m/%Y').strftime('%Y-%m-%d')
                except ValueError:
                    return "Invalid delivery date format. Please use DD/MM/YYYY."

            # Collect the updated form data
            updated_data = {
                'khccode': request.form['khccode'],
                'billno': request.form['billno'],
                'biltyno': request.form['biltyno'],
                'date': formatted_date,
                'firmname': request.form['firmname'],
                'city': request.form['city'],
                'state': request.form['state'],
                'mobile': request.form['mobile'],
                'amount': request.form['amount'],
                'reference_name': request.form['reference_name'],
                'delivery': request.form['delivery'],
                'delivery_date': formatted_delivery_date,
                'order_status': request.form['order_status']  # Add this line
            }

            # Update the customer data in the database
            cursor.execute('''UPDATE customers
                            SET khccode = ?, billno = ?, biltyno = ?, date = ?, firmname = ?, city = ?, state = ?,
                                mobile = ?, amount = ?, reference_name = ?, delivery = ?, delivery_date = ?, order_status = ? 
                            WHERE id = ?''', 
                        (updated_data['khccode'], updated_data['billno'], updated_data['biltyno'], updated_data['date'],
                            updated_data['firmname'], updated_data['city'], updated_data['state'], updated_data['mobile'],
                            updated_data['amount'], updated_data['reference_name'], updated_data['delivery'], 
                            updated_data['delivery_date'], updated_data['order_status'], customer_id))

            conn.commit()
            conn.close()

            # Get the referrer from the form (hidden input)
            referrer = request.form.get('referrer')

            # Redirect back to the same page the user was on, or to a default page
            if referrer:
                return redirect(referrer)  # Redirect to the page the user came from
            else:
                return redirect(url_for('avni_bp.avni_delivery_page'))  # Fallback to a default page (adjust as needed)

    except sqlite3.DatabaseError as e:
        print(f"Database error: {e}")
        conn.close()  # Ensure the connection is closed in case of an error
        return f"An error occurred while fetching or updating data: {e}"

@avni_bp.route('/avni/delivery', methods=['GET'])
def avni_delivery_page():
    if 'avni' not in session['permissions'] and 'admin' not in session['permissions']:
        flash('You do not have permission to access this page. Logging you out.', 'danger')
        session.pop('username', None)  # Log the user out
        return redirect(url_for('login'))  # Redirect to login page

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get the search query from the request arguments
        search_query = request.args.get('search', '')

        # Modify the SQL query based on the search term
        if search_query:
            cursor.execute(''' 
                SELECT * FROM customers 
                WHERE LOWER(reference_name) = "avni" 
                AND LOWER(delivery) LIKE "%no%" 
                AND LOWER(payment_status) != "cancel"  -- Exclude canceled orders
                AND (LOWER(firmname) LIKE ? OR LOWER(city) LIKE ? OR LOWER(state) LIKE ?)
                ORDER BY id DESC
            ''', ('%' + search_query.lower() + '%', '%' + search_query.lower() + '%', '%' + search_query.lower() + '%'))
        else:
            cursor.execute(''' 
                SELECT * FROM customers 
                WHERE LOWER(reference_name) = "avni" 
                AND LOWER(delivery) LIKE "%no%" 
                AND LOWER(payment_status) != "cancel"  -- Exclude canceled orders
                ORDER BY id DESC
            ''')

        customers = cursor.fetchall()

        # Initialize the dictionary to store additional mobile numbers
        additional_mobiles = {}

        # Fetch additional mobile numbers for each customer
        cursor.execute('SELECT customer_id, mobile_number FROM additional_mobiles')
        for row in cursor.fetchall():
            customer_id = row['customer_id']
            mobile_number = row['mobile_number']
            if customer_id not in additional_mobiles:
                additional_mobiles[customer_id] = []
            additional_mobiles[customer_id].append(mobile_number)

        # Calculate total amount and total customers
        total_amount = sum(
            float(customer['amount']) if customer['amount'] else 0 for customer in customers
        )
        total_customers = len(customers)

        conn.close()

        # Render the template with the filtered customers, totals, and additional mobiles
        return render_template('avni/avni_delivery.html', customers=customers, total_amount=total_amount, total_customers=total_customers, additional_mobiles=additional_mobiles)

    except sqlite3.DatabaseError as e:
        print(f"Database error: {e}")
        return f"An error occurred while fetching data: {e}"

@avni_bp.route('/avni/dashboard', methods=['GET'])
def avni_dashboard():
    if 'avni' not in session['permissions'] and 'admin' not in session['permissions']:
        flash('You do not have permission to access this page. Logging you out.', 'danger')
        session.pop('username', None)  # Log the user out
        return redirect(url_for('login'))  # Redirect to login page

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get today's date in YYYY-MM-DD format for comparison
        today_date = datetime.today().strftime('%Y-%m-%d')

        # Fetch the 5 most recent customers where delivery is 'yes' and the delivery_date is today (Excluding canceled)
        cursor.execute(''' 
            SELECT * FROM customers 
            WHERE LOWER(reference_name) = "avni" 
            AND LOWER(delivery) = "yes" 
            AND delivery_date = ? 
            AND payment_status != "Cancel"
            ORDER BY delivery_date DESC LIMIT 5
        ''', (today_date,))
        recent_changes = cursor.fetchall()

        # Convert sqlite3.Row to a dictionary for easier modification
        recent_changes = [dict(customer) for customer in recent_changes]

        # Convert the date fields to the desired format (DD/MM/YYYY)
        for customer in recent_changes:
            if customer['date']:
                try:
                    customer['date'] = datetime.strptime(customer['date'], '%Y-%m-%d').strftime('%d/%m/%Y')
                except ValueError:
                    customer['date'] = 'Invalid Date'

            if customer['delivery_date']:
                try:
                    customer['delivery_date'] = datetime.strptime(customer['delivery_date'], '%Y-%m-%d').strftime('%d/%m/%Y')
                except ValueError:
                    customer['delivery_date'] = 'Invalid Date'

        # Fetch general statistics where delivery is 'yes' (including canceled orders for totals)
        cursor.execute('SELECT COUNT(*) FROM customers WHERE LOWER(reference_name) = "avni" AND LOWER(delivery) = "yes"')
        total_customers = cursor.fetchone()[0]

        cursor.execute('SELECT SUM(amount) FROM customers WHERE LOWER(reference_name) = "avni" AND LOWER(delivery) = "yes"')
        total_amount = cursor.fetchone()[0] or 0

        cursor.execute('SELECT COUNT(*) FROM customers WHERE LOWER(reference_name) = "avni" AND LOWER(delivery) = "no"')
        total_no_delivery = cursor.fetchone()[0]

        # Fetch total amount for "no" deliveries (including canceled orders for totals)
        cursor.execute('SELECT SUM(amount) FROM customers WHERE LOWER(reference_name) = "avni" AND LOWER(delivery) = "no"')
        total_no_delivery_amount = cursor.fetchone()[0] or 0

        # Fetch the same for canceled deliveries (to include in total)
        cursor.execute('SELECT COUNT(*) FROM customers WHERE LOWER(reference_name) = "avni" AND payment_status = "Cancel"')
        total_cancelled = cursor.fetchone()[0]

        cursor.execute('SELECT SUM(amount) FROM customers WHERE LOWER(reference_name) = "avni" AND payment_status = "Cancel"')
        total_cancelled_amount = cursor.fetchone()[0] or 0

        conn.close()

        # Render the dashboard template with the statistics and recent changes
        return render_template('avni/avni_dashboard.html',
                               recent_changes=recent_changes,
                               total_customers=total_customers,
                               total_amount=total_amount,
                               total_no_delivery=total_no_delivery,
                               total_no_delivery_amount=total_no_delivery_amount,
                               total_cancelled=total_cancelled,
                               total_cancelled_amount=total_cancelled_amount)

    except sqlite3.DatabaseError as e:
        print(f"Database error: {e}")
        return f"An error occurred while fetching data: {e}"
    except Exception as e:
        print(f"Unexpected error: {e}")
        return f"An unexpected error occurred: {e}"

@avni_bp.route('/avni/payment_due', methods=['GET'])
def payment_due():
    if 'avni' not in session['permissions'] and 'admin' not in session['permissions']:
        flash('You do not have permission to access this page. Logging you out.', 'danger')
        session.pop('username', None)  # Log the user out
        return redirect(url_for('login'))  # Redirect to login page

    try:
        # Get a database connection using your utility function
        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch customers where reference_name = 'avni', delivery = 'yes', and payment_status = 'pending'
        cursor.execute('''
            SELECT * FROM customers
            WHERE LOWER(reference_name) = "avni"
            AND LOWER(delivery) = "yes"
            AND LOWER(payment_status) = "pending"
            ORDER BY date DESC
        ''')
        pending_payments = cursor.fetchall()

        # Convert sqlite3.Row to a dictionary for easier modification
        pending_payments = [dict(customer) for customer in pending_payments]

        # Initialize total values
        total_customers = len(pending_payments)
        total_amount_due = 0.0
        total_received_amount = 0.0
        total_adjusted_due = 0.0

        # Initialize the dictionary to store additional mobile numbers
        additional_mobiles = {}

        # Fetch additional mobile numbers for each customer
        cursor.execute('SELECT customer_id, mobile_number FROM additional_mobiles')
        for row in cursor.fetchall():
            customer_id = row['customer_id']
            mobile_number = row['mobile_number']
            if customer_id not in additional_mobiles:
                additional_mobiles[customer_id] = []
            additional_mobiles[customer_id].append(mobile_number)

        # Calculate the total amount due and total received amount
        for customer in pending_payments:
            # Fetch total received amount for each customer from payment_history
            cursor.execute('SELECT SUM(amount) FROM payment_history WHERE customer_id = ?', (customer['id'],))
            received_amount = cursor.fetchone()[0] or 0.0
            customer['total_received_amount'] = received_amount  # Add to the customer data

            # Calculate due amount (Amount - Received Amount)
            due_amount = customer['amount'] - received_amount
            customer['due_amount'] = due_amount  # Add due amount to the customer data

            # Adjust due amount with offer discount (if any)
            adjusted_due = due_amount - (customer.get('offer_discount', 0) or 0.0)
            customer['adjusted_due'] = adjusted_due  # Add adjusted due amount to the customer data

            # Update total values
            total_amount_due += customer['amount']
            total_received_amount += received_amount
            total_adjusted_due += adjusted_due

            # Format the date field to DD/MM/YYYY
            if customer.get('date'):
                try:
                    customer['date'] = datetime.strptime(customer['date'], '%Y-%m-%d').strftime('%d/%m/%Y')
                except ValueError:
                    customer['date'] = 'Invalid Date'

        # Close the database connection
        conn.close()

        # Render the payment due template with the pending payments data and additional mobiles
        return render_template('avni/payment_due.html', 
                               pending_payments=pending_payments,
                               total_customers=total_customers,
                               total_amount_due=total_amount_due,
                               total_received_amount=total_received_amount,
                               total_adjusted_due=total_adjusted_due,
                               additional_mobiles=additional_mobiles)

    except sqlite3.DatabaseError as e:
        print(f"Database error: {e}")
        return f"An error occurred while fetching data: {e}"
    except Exception as e:
        print(f"Unexpected error: {e}")
        return f"An unexpected error occurred: {e}"
    
from collections import defaultdict
from datetime import datetime

@avni_bp.route('/avni/scheme', methods=['GET', 'POST'])
def avni_scheme_page():
    if 'avni' not in session.get('permissions', []) and 'admin' not in session.get('permissions', []):
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('login'))

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Define the date range for the filter
        start_date = '2025-01-01'
        end_date = '2026-01-01'

        # Query to count orders grouped by amount for avni, filtering by date range
        cursor.execute(''' 
            SELECT amount, COUNT(*) AS count
            FROM customers
            WHERE LOWER(reference_name) = 'avni'
            AND date BETWEEN ? AND ?
            GROUP BY amount
        ''', (start_date, end_date))

        schemes = cursor.fetchall()
        conn.close()

        # Initialize counts for all schemes
        scheme_counts = defaultdict(int)

        # Process fetched data and count based on amounts
        for scheme in schemes:
            amount = scheme[0]
            count = scheme[1]
            scheme_counts[amount] += count  # Grouping based on amounts dynamically

        # Calculate total schemes and total amount dynamically
        total_schemes = sum(scheme_counts.values())  # Total orders count
        total_amount = sum(amount * count for amount, count in scheme_counts.items())  # Total scheme value

        # Expected schemes for comparison (static, could be dynamic if needed)
        expected_schemes = {amount: 150 for amount in scheme_counts}  # Replace with dynamic if necessary

        # Render the template with updated data
        return render_template(
            'avni/scheme.html',
            scheme_counts=scheme_counts,
            total_schemes=total_schemes,
            total_amount=total_amount,
            current_user="avni",
            expected_schemes=expected_schemes
        )

    except sqlite3.DatabaseError as e:
        print(f"Database error: {e}")
        return "An error occurred while fetching scheme data."
    except Exception as e:
        print(f"Unexpected error: {e}")
        return "An unexpected error occurred."


@avni_bp.route('/avni/canceled', methods=['GET'])
def avni_canceled_page():
    if 'avni' not in session.get('permissions', []) and 'admin' not in session.get('permissions', []):
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('login'))

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Query to get the canceled orders for avni, sorted by date (most recent first)
        cursor.execute('''
            SELECT id, khccode, billno, biltyno, date, firmname, city, state, mobile, amount, reference_name
            FROM customers
            WHERE LOWER(reference_name) = 'avni'
            AND LOWER(payment_status) = 'cancel'
            ORDER BY date DESC  -- Sort by date in descending order (most recent first)
        ''')

        canceled_orders = cursor.fetchall()
        conn.close()

        # Render the canceled orders page template with the canceled orders data
        return render_template('avni/avni_canceled_page.html', canceled_orders=canceled_orders)

    except Exception as e:
        flash(f"An error occurred: {e}", 'danger')
        return redirect(url_for('home'))
