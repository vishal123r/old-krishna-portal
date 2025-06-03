from flask import Blueprint, render_template, request, redirect, url_for
import sqlite3

# Create blueprint for delivery routes
delivery_bp = Blueprint('delivery_bp', __name__)

# Route for customers with buttons
@delivery_bp.route('/customers-with-buttons')
def customers_with_buttons():
    return render_template('customers_with_buttons.html')

@delivery_bp.route('/customers-with-delivery')
def customers_with_delivery():
    conn = sqlite3.connect('crm.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM customers 
        WHERE delivery IS NOT NULL 
        AND TRIM(delivery) != '' 
        AND LOWER(delivery) NOT IN ('yes') 
        AND state != 'Rajasthan'
        AND payment_status != 'Cancel'
        ORDER BY CAST(SUBSTR(billno, INSTR(billno, '-') + 1) AS INTEGER)
    """)
    customers = cursor.fetchall()

    conn.close()
    return render_template('customers_with_delivery_filtered.html', customers=customers)

@delivery_bp.route('/customers-from-rajasthan')
def customers_from_rajasthan():
    conn = sqlite3.connect('crm.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM customers 
        WHERE delivery IS NOT NULL 
        AND TRIM(delivery) != '' 
        AND LOWER(delivery) NOT IN ('yes') 
        AND state = 'Rajasthan'
        AND payment_status != 'Cancel'
        ORDER BY 
            CASE 
                WHEN LOWER(billno) LIKE '%khcr%' THEN 0
                WHEN LOWER(billno) LIKE '%kt%' THEN 1
                ELSE 2
            END,
            CAST(SUBSTR(billno, INSTR(billno, '-') + 1) AS INTEGER)
    """)
    customers = cursor.fetchall()

    conn.close()
    return render_template('customers_from_rajasthan.html', customers=customers)

# Route for customers with a delivery number (excluding Rajasthan)
@delivery_bp.route('/customer-details/<int:customer_id>')
def customer_details(customer_id):
    # Connect to the database
    conn = sqlite3.connect('crm.db')
    conn.row_factory = sqlite3.Row  # This makes each row return a dictionary-like object
    cursor = conn.cursor()

    # Query to fetch a specific customer by ID
    cursor.execute("SELECT * FROM customers WHERE id = ?", (customer_id,))
    customer = cursor.fetchone()

    # Close the connection
    conn.close()

    if customer:
        # Pass the customer details to the template
        return render_template('customers_with_delivery_status.html', customer=customer)
    else:
        # If customer not found, show an error or redirect
        return "Customer not found", 404

@delivery_bp.route('/update-customer/<int:customer_id>', methods=['POST'])
def update_customer(customer_id):
    conn = sqlite3.connect('crm.db')
    cursor = conn.cursor()

    updated_data = {
        'khccode': request.form['khccode'],
        'billno': request.form['billno'],
        'biltyno': request.form['biltyno'],  # ✅ Only once here
        'date': request.form['date'],
        'name': request.form['name'],
        'firmname': request.form['firmname'],
        'state': request.form['state'],
        'district': request.form['district'],
        'tehsil': request.form['tehsil'],
        'city': request.form['city'],
        'pincode': request.form['pincode'],
        'mobile': request.form['mobile'],
        'amount': request.form['amount'],
        'delivery': request.form['delivery'],
        'category': request.form['category'],
        'payment_status': request.form['payment_status'],
        'additional_mobile': request.form['additional_mobile'],
        'reference_name': request.form['reference_name'],
        'offer_discount': request.form['offer_discount'],
        'delivery_date': request.form['delivery_date'],
        'transport_name': request.form['transport_name'],
        'transport_number': request.form['transport_number'],
        'order_status': request.form['order_status']
    }

    cursor.execute("""
        UPDATE customers
        SET khccode = ?, billno = ?, biltyno = ?, date = ?, name = ?, firmname = ?, state = ?, 
            district = ?, tehsil = ?, city = ?, pincode = ?, mobile = ?, amount = ?, delivery = ?, 
            category = ?, payment_status = ?, additional_mobile = ?, reference_name = ?, 
            offer_discount = ?, delivery_date = ?, transport_name = ?, transport_number = ?, order_status = ?
        WHERE id = ?
    """, (
        updated_data['khccode'], updated_data['billno'], updated_data['biltyno'], updated_data['date'],
        updated_data['name'], updated_data['firmname'], updated_data['state'], updated_data['district'],
        updated_data['tehsil'], updated_data['city'], updated_data['pincode'], updated_data['mobile'],
        updated_data['amount'], updated_data['delivery'], updated_data['category'], updated_data['payment_status'],
        updated_data['additional_mobile'], updated_data['reference_name'], updated_data['offer_discount'],
        updated_data['delivery_date'], updated_data['transport_name'], updated_data['transport_number'],
        updated_data['order_status'],
        customer_id
    ))

    conn.commit()
    conn.close()

    return redirect(url_for('delivery_bp.customer_details', customer_id=customer_id))

