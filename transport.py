from flask import Blueprint, render_template, request, redirect, url_for, flash, g
import sqlite3
from datetime import datetime

# Define the blueprint for the transport module
transport_bp = Blueprint('transport', __name__, template_folder='templates/transport')

# Function to get the database connection
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect('crm.db')
        g.db.row_factory = sqlite3.Row  # This enables dictionary access to the result rows
    return g.db

# Function to fetch all transport entries from the database
def get_all_transport_entries():
    db = get_db()  # Get the db connection
    # Query to fetch all transport entries
    return db.execute('SELECT * FROM transport').fetchall()

@transport_bp.route('/add', methods=['GET', 'POST'])
def add_transport():
    if request.method == 'POST':
        billno = request.form['billno']
        gate_pass_no = request.form['gate_pass_no']
        transport_name = request.form['transport_name']
        warehouse_location = request.form['warehouse_location']
        driver_name = request.form['driver_name']
        vehicle_number = request.form['vehicle_number']
        warehouse_contact_number = request.form['warehouse_contact_number']
        driver_contact_number = request.form['driver_contact_number']
        delivery_date = request.form['delivery_date']

        # Convert the delivery_date from dd/mm/yyyy to yyyy-mm-dd format
        try:
            formatted_date = datetime.strptime(delivery_date, '%d/%m/%Y').strftime('%Y-%m-%d')
        except ValueError:
            # If the date format is incorrect, raise an error and show a custom message
            flash('Invalid date format. Please use dd/mm/yyyy.', 'error')
            return redirect(url_for('transport.add_transport'))

        try:
            # Connect to the database with a timeout of 5 seconds
            conn = sqlite3.connect('crm.db', timeout=5)
            cursor = conn.cursor()

            # Insert data into transport table
            cursor.execute('''INSERT INTO transport (billno, gate_pass_no, transport_name, warehouse_location, driver_name, vehicle_number, warehouse_contact_number, driver_contact_number, delivery_date)
                              VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                            (billno, gate_pass_no, transport_name, warehouse_location, driver_name, vehicle_number, warehouse_contact_number, driver_contact_number, formatted_date))

            transport_id = cursor.lastrowid  # Get the ID of the newly inserted transport entry

            # Insert products for this transport entry
            product_names = request.form.getlist('product_name[]')
            varieties = request.form.getlist('variety[]')
            quantities = request.form.getlist('quantity[]')

            for product_name, variety, quantity in zip(product_names, varieties, quantities):
                cursor.execute('''INSERT INTO products (transport_id, product_name, variety, quantity)
                                VALUES (?, ?, ?, ?)''',
                                (transport_id, product_name, variety, quantity))

            conn.commit()
            conn.close()

            flash('Transport entry added successfully along with products!', 'success')
            return redirect(url_for('transport.show_transport'))
        
        except sqlite3.DatabaseError as e:
            flash(f'Error: {e}', 'error')
            return redirect(url_for('transport.add_transport'))

    return render_template('transport/add_transport.html')

@transport_bp.route('/show')
def show_transport():
    transport_entries = get_all_transport_entries()

    # Convert each transport entry to a dictionary for mutability
    transport_entries_dict = []
    for transport in transport_entries:
        transport_dict = dict(transport)  # Convert sqlite3.Row to dict
        transport_dict['products'] = get_db().execute(
            'SELECT * FROM products WHERE transport_id = ?', (transport['id'],)
        ).fetchall()
        transport_entries_dict.append(transport_dict)

    return render_template('transport/show_transport.html', transport_entries=transport_entries_dict)

@transport_bp.route('/view/<int:transport_id>', methods=['GET'])
def view_transport(transport_id):
    db = get_db()  # Now you have access to the db object
    
    # Query to fetch transport details based on transport_id
    transport_entry = db.execute(
        'SELECT * FROM transport WHERE id = ?', (transport_id,)
    ).fetchone()
    
    # Query to fetch the products related to the transport entry
    products = db.execute(
        'SELECT * FROM products WHERE transport_id = ?', (transport_id,)
    ).fetchall()

    if not transport_entry:
        return "Transport entry not found.", 404

    return render_template(
        'transport/view_transport.html',
        transport_entry=transport_entry,
        products=products
    )

@transport_bp.route('/delete/<int:transport_id>', methods=['POST'])
def delete_transport(transport_id):
    try:
        # Connect to the database
        conn = sqlite3.connect('crm.db')
        cursor = conn.cursor()

        # Delete associated products first (to avoid foreign key constraint issues)
        cursor.execute('DELETE FROM products WHERE transport_id = ?', (transport_id,))

        # Now delete the transport entry itself
        cursor.execute('DELETE FROM transport WHERE id = ?', (transport_id,))

        conn.commit()
        conn.close()

        flash('Transport entry and associated products deleted successfully!', 'success')
    except sqlite3.DatabaseError as e:
        flash(f'Error: {e}', 'error')

    return redirect(url_for('transport.show_transport'))

@transport_bp.route('/dashboard')
def dashboard():
    db = get_db()  # Get the database connection

    # Query to fetch all transport entries
    transport_entries = db.execute('SELECT * FROM transport').fetchall()

    # Prepare a dictionary to hold the transport name and total quantity per product
    transport_dashboard_data = []

    for transport in transport_entries:
        transport_id = transport['id']
        transport_name = transport['transport_name']

        # Query to fetch products linked to the transport entry
        products = db.execute(
            'SELECT product_name, SUM(quantity) as total_quantity FROM products WHERE transport_id = ? GROUP BY product_name',
            (transport_id,)
        ).fetchall()

        # Add transport and products data to the dashboard list
        product_data = {product['product_name']: product['total_quantity'] for product in products}

        transport_dashboard_data.append({
            'transport_name': transport_name,
            'products': product_data
        })

    return render_template('transport/dashboard.html', transport_dashboard_data=transport_dashboard_data)
