from sched import scheduler
from shelve import DbfilenameShelf
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, send_from_directory, g, session, abort, send_file
import sqlite3
import os
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
import csv
import pandas as pd
import shutil
import re
from io import BytesIO
import traceback
from io import BytesIO
from db import get_db_connection  # Import the database connection from db.py
import db
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import random
from utils import hash_password
from database import database_bp
from main import run_processing
from flask_mail import Mail, Message
from database_helper import DatabaseHelper  # Import the DatabaseHelper class
from email_helper import EmailHelper        # Import the EmailHelper class
from db_utils import get_tables_info  # Import the function to get the tables' structure
import traceback
import calendar
from tina_page import tina_bp  # Import the tina_bp blueprint
from pooja_page import pooja_bp
from priti_page import priti_bp
from ruhi_page import ruhi_bp
from neha_page import neha_bp
from dev_page import dev_bp
from anjali_page import anjali_bp
from avni_page import avni_bp
from juhi_page import juhi_bp
from harish_page import harish_bp
from adjustment_entries import init_routes  # Import the function to initialize routes for adjustments
from file_upload import UploadHandler  # Import UploadHandler
from file_upload import UploadHandler  # Import UploadHandler
from flask_sqlalchemy import SQLAlchemy
from app import db
from daily_summary import daily_summary_bp  # Import the blueprint
import logging
from flask_caching import Cache
from celery import Celery
import cProfile
from fetch_and_display import CustomerService  # Import the CustomerService class
from bill_service import BillService  # Import the new BillService class
from transport import transport_bp  # Import the transport blueprint
from customer_summary import customer_summary_bp  # Import the blueprint
from werkzeug.security import generate_password_hash
from customer_score import get_customer_details_and_score
from zero_biltyno_page import zero_biltyno_bp  # Import the new page blueprint
from filter_by_name import filter_by_name_bp
from flask_caching import Cache
from transport_detail import transport_detail_bp  # Import your blueprint
from parent_child import parent_child_bp 
from expenses import expenses_bp  # Importing expenses Blueprint
import json
from datetime import datetime
import re
from datetime import timedelta
from collections import Counter
from commitments_bp import commitments_page
from commitments_bp import commitments_bp
import uuid
from chat import chatbot_response
from customer_analysis import analyze_customers  # Import the analyze_customers function
from backup_manager import BackupManager
from delivery_page import delivery_bp  # Make sure this matches the actual filename
from calling_page import calling_page
from payment_pending import payment_pending  # Import the Blueprint
from payment_today import payment_today_bp  # Ensure correct import
from calling import calling_bp  # Import the calling blueprint
from chatbot import chatbot_bp
from online_users import online_users, online_users_bp  # Import singleton and blueprint
from activity.activity import activity_bp, init_user_activity_table, mark_user_online, log_activity
from admin import admin_bp
from builder import builder_bp
from editor import editor_bp
import importlib
from crm_blueprint import crm_bp
# Import the correction blueprint
from payment_history import payment_history_bp
from pwa import pwa_bp
from popup import popup_bp


logging.basicConfig(level=logging.DEBUG)

def run_processing():
    # Any initialization or setup before starting the app
    print("Processing before app runs...")

def get_db_connection():
    if 'db' not in g:
        g.db = sqlite3.connect('crm.db')  # Ensure the correct database name is used
        g.db.row_factory = sqlite3.Row
    return g.db

app = Flask(__name__)
app.secret_key = 'c8d71002c1a6e5f4c4cf0aaa3d7ada7f'
# Set up the database URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///crm.db'  # Adjust to your database URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Optional, to disable modification tracking
app.config['CACHE_TYPE'] = 'simple'  # You can use more advanced caching like Redis, Memcached
app.config["SESSION_PERMANENT"] = True
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=7)  # 7 din tak session rahega

# Set the upload folder (ensure the path is correct for your environment)
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')  # Folder to store uploads
# Initialize CustomerService instance
customer_service = CustomerService()

@app.route('/show_customer_info')
def show_customer_info():
    """Route to show customer information."""
    column_titles, customer_info = customer_service.fetch_all_customer_data()
    return render_template('customer_data.html', column_titles=column_titles, customer_info=customer_info)

# Optionally, set the allowed file extensions
# Define allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Initialize the SQLAlchemy object
db = SQLAlchemy(app)

# Register the blueprint with your Flask app
app.register_blueprint(database_bp, url_prefix='/database')
# Register blueprint
app.register_blueprint(delivery_bp)
app.register_blueprint(tina_bp)
app.register_blueprint(pooja_bp)
app.register_blueprint(priti_bp)
app.register_blueprint(ruhi_bp)
app.register_blueprint(neha_bp)
app.register_blueprint(dev_bp)
app.register_blueprint(anjali_bp)
app.register_blueprint(avni_bp)
app.register_blueprint(juhi_bp)
app.register_blueprint(harish_bp)
# Register the blueprint with the app
app.register_blueprint(daily_summary_bp, url_prefix='/daily_summary')
# Register the transport blueprint with your Flask app
app.register_blueprint(transport_bp, url_prefix='/transport')
# Register the blueprint without a url_prefix
app.register_blueprint(customer_summary_bp)
# Register the new blueprint with your Flask app
app.register_blueprint(zero_biltyno_bp, url_prefix='/zero_biltyno')
# Register the blueprint
app.register_blueprint(filter_by_name_bp)
# Register the blueprint with a prefix
app.register_blueprint(transport_detail_bp, url_prefix='/transport')
app.register_blueprint(parent_child_bp)
# Register the expenses blueprint
app.register_blueprint(expenses_bp)
app.register_blueprint(commitments_bp)
app.register_blueprint(calling_page)
app.register_blueprint(payment_pending)
# Register the blueprint for the payments page
# Register the blueprint
app.register_blueprint(payment_today_bp)
app.register_blueprint(calling_bp, url_prefix='/calling')
app.register_blueprint(chatbot_bp)
# Register blueprint for online users page
app.register_blueprint(online_users_bp)
# Blueprint register karo
app.register_blueprint(activity_bp)
# Admin blueprint ko register kar rahe hain
app.register_blueprint(admin_bp)
# Table create karne ka function app start me call karo
init_user_activity_table()
app.register_blueprint(builder_bp)
app.register_blueprint(editor_bp)
app.register_blueprint(crm_bp, url_prefix='/crm')
# Register the blueprint
app.register_blueprint(payment_history_bp)
app.register_blueprint(pwa_bp)
app.register_blueprint(popup_bp)

DYNAMIC_PATH = 'dynamic_pages'

# Ensure dynamic_pages is treated as a package
if not os.path.exists(os.path.join(DYNAMIC_PATH, '__init__.py')):
    with open(os.path.join(DYNAMIC_PATH, '__init__.py'), 'w'):
        pass  # create empty __init__.py file if not present

for filename in os.listdir(DYNAMIC_PATH):
    if filename.endswith('.py') and not filename.startswith('__'):
        module_name = filename[:-3]  # Remove .py extension
        try:
            # Import the module from dynamic_pages
            module = importlib.import_module(f'{DYNAMIC_PATH}.{module_name}')
            blueprint = getattr(module, f"{module_name}_bp")
            app.register_blueprint(blueprint)
            print(f"✅ Registered blueprint: {module_name}")
        except Exception as e:
            print(f"❌ Failed to register {module_name}: {e}")



# ✅ Initialize Backup System
backup_manager = BackupManager()

# ✅ Perform Backup & Restore
backup_manager.backup_database()  # Creates a backup
backup_manager.restore_database()  # Restores if crm.db is missing

# Initialize routes from the adjustment_entries.py file
init_routes(app)


# Create a connection to the crm.db database
conn = sqlite3.connect('crm.db')
cursor = conn.cursor()

# Create the transport_services table with columns prefixed by 'Transport'
cursor.execute('''
CREATE TABLE IF NOT EXISTS transport_services (
    transport_id INTEGER PRIMARY KEY AUTOINCREMENT,
    transport_name TEXT NOT NULL,
    transport_mobile_no TEXT NOT NULL,
    transport_city TEXT NOT NULL,
    transport_district TEXT NOT NULL,
    transport_state TEXT NOT NULL
)
''')

# Commit the changes and close the connection
conn.commit()
conn.close()


import sqlite3

conn = sqlite3.connect('crm.db')
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS call_preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    do_not_call BOOLEAN DEFAULT 0,
    call_date TEXT,
    notes TEXT,
    assigned_staff TEXT,
    region TEXT,
    status TEXT DEFAULT 'pending',
    FOREIGN KEY(customer_id) REFERENCES customers(id)
)
''')

conn.commit()
conn.close()

print("✅ Table 'call_preferences' created successfully.")


@app.teardown_appcontext
def close_connection(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def add_columns_if_not_exists():
    # Example for SQLAlchemy
    if not db.engine.dialect.has_column(db.engine, 'your_table_name', 'pincode'):
        # Add the pincode column
        pass  # Replace with your column addition code

def create_customers_table(cursor):
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT,
            address TEXT
        )
    ''')

        # Create additional_mobiles table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS additional_mobiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            mobile_number TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers (id)
        )
    ''')


def create_additional_mobiles_table(cursor):
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS additional_mobiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            mobile TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers (id)
        )
    ''')


def create_database(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    create_customers_table(cursor)
    create_additional_mobiles_table(cursor)
    conn.commit()
    conn.close()

def create_transport_table(cursor):
    cursor.execute('''CREATE TABLE IF NOT EXISTS transport (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        billno TEXT NOT NULL,
        gate_pass_no TEXT NOT NULL,
        transport_name TEXT NOT NULL,
        warehouse_location TEXT NOT NULL,
        driver_name TEXT,
        vehicle_number TEXT NOT NULL,
        warehouse_contact_number TEXT,
        delivery_date TEXT,
        contact_number TEXT
    )''')

def add_columns_to_transport():
    conn = sqlite3.connect('crm.db')
    cursor = conn.cursor()

    try:
        # Add billno column
        cursor.execute('ALTER TABLE transport ADD COLUMN billno TEXT NOT NULL')
        # Add gate_pass_no column
        cursor.execute('ALTER TABLE transport ADD COLUMN gate_pass_no TEXT NOT NULL')

        conn.commit()

    except sqlite3.DatabaseError as e:
        print(f"Error: {e}")
    finally:
        conn.close()

add_columns_to_transport()

def create_products_table(cursor):
    cursor.execute('''CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        transport_id INTEGER NOT NULL,
        product_name TEXT NOT NULL,
        variety TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        FOREIGN KEY (transport_id) REFERENCES transport (id)
    )''')

def create_sub_entries_table(cursor):
    cursor.execute('''CREATE TABLE IF NOT EXISTS sub_entries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        main_id INTEGER,
        sub_name TEXT NOT NULL,
        sub_amount REAL NOT NULL,
        FOREIGN KEY (main_id) REFERENCES customers(id) ON DELETE CASCADE
    )''')

def init_db():
    db_path = 'crm.db'

    # Create a new database if it doesn't exist
    if not os.path.exists(db_path):
        print("Database file does not exist. Creating new database...")
        create_database(db_path)

    try:
        conn = sqlite3.connect(db_path, check_same_thread=False)
        cursor = conn.cursor()

        # Create necessary tables if they do not exist
        create_tables_if_not_exists(cursor)

        # Create the sub_entries table if it doesn't exist
        create_sub_entries_table(cursor)

        conn.commit()
        print("Database tables are valid.")
        
    except sqlite3.DatabaseError as e:
        print(f"Database error: {e}")
        if os.path.exists(db_path):
            os.remove(db_path)  # Remove the corrupted database
            print("Corrupted database file removed. Reinitializing...")
        create_database(db_path)  # Re-create the database
        
    finally:
        conn.close()


def create_tables_if_not_exists(cursor):
    # Check and create 'customers' table if it doesn't exist
    cursor.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="customers";')
    result = cursor.fetchone()
    if result is None:
        print("Customers table does not exist, creating table...")
        create_customers_table(cursor)

    # Check for 'additional_mobiles' table and create it if it doesn't exist
    cursor.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="additional_mobiles";')
    result = cursor.fetchone()
    if result is None:
        print("Additional mobiles table does not exist, creating table...")
        create_additional_mobiles_table(cursor)

    # Check for 'users' table and create it if it doesn't exist
    cursor.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="users";')
    result = cursor.fetchone()
    if result is None:
        print("Users table does not exist, creating table...")
        create_users_table(cursor)

    # Check for 'transport' table and create it if it doesn't exist
    cursor.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="transport";')
    result = cursor.fetchone()
    if result is None:
        print("Transport table does not exist, creating table...")
        create_transport_table(cursor)

def create_customers_table(cursor):
    cursor.execute('''CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        amount REAL NOT NULL,
    )''')

def create_additional_mobiles_table(cursor):
    cursor.execute('''CREATE TABLE IF NOT EXISTS additional_mobiles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        mobile_number TEXT NOT NULL,
        FOREIGN KEY (customer_id) REFERENCES customers(id)
    )''')

def create_users_table(cursor):
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        password TEXT NOT NULL
    )''')

def create_transport_table(cursor):
    cursor.execute('''CREATE TABLE IF NOT EXISTS transport (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vehicle_name TEXT NOT NULL,
        transport_cost REAL NOT NULL
    )''')

def create_database(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    create_tables_if_not_exists(cursor)
    conn.commit()
    conn.close()


def add_bilty_image_column():
    try:
        conn = sqlite3.connect('crm.db')
        cursor = conn.cursor()
        cursor.execute('ALTER TABLE customers ADD COLUMN bilty_image TEXT')
        conn.commit()
        print("bilty_image column added successfully.")
    except sqlite3.DatabaseError as e:
        print(f"Error adding bilty_image column: {e}")
    finally:
        conn.close()

add_bilty_image_column()

import sqlite3

def add_category_column():
    conn = sqlite3.connect('crm.db')
    cursor = conn.cursor()

    # Check if the column already exists
    cursor.execute("PRAGMA table_info(customers)")
    columns = [col[1] for col in cursor.fetchall()]

    if "category" not in columns:
        cursor.execute("ALTER TABLE customers ADD COLUMN category TEXT")
        conn.commit()
        print("Category column added successfully.")
    else:
        print("Category column already exists.")

    conn.close()

add_category_column()


def add_reference_name_column(cursor):
    try:
        cursor.execute('ALTER TABLE customers ADD COLUMN reference_name TEXT')
    except sqlite3.OperationalError:
        # Column already exists, do nothing
        pass

def add_column_if_not_exists(cursor):
    try:
        cursor.execute('ALTER TABLE customers ADD COLUMN additional_mobile TEXT')
    except sqlite3.OperationalError:
        # Column already exists, do nothing
        pass

def create_transport_table(cursor):
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transport (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transport_name TEXT NOT NULL,
            warehouse_location TEXT NOT NULL,
            driver_name TEXT NOT NULL,
            vehicle_number TEXT NOT NULL,
            contact_number TEXT NOT NULL,
            delivery_date TEXT NOT NULL
        )
    ''')

def create_tables(cursor):
    # Create customers table
    cursor.execute('''CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        khccode TEXT NOT NULL,
        billno TEXT NOT NULL,
        biltyno TEXT NOT NULL,
        date TEXT NOT NULL,
        firmname TEXT NOT NULL,
        city TEXT NOT NULL,
        mobile TEXT NOT NULL,
        amount REAL NOT NULL,
        receive_amount REAL NOT NULL,
        delivery TEXT,
        payment_status TEXT NOT NULL,
        payment_received_date TEXT,
        transport_name TEXT,
        transport_number TEXT,
        bill_image TEXT,
        bilty_image TEXT,
        pincode TEXT NOT NULL DEFAULT "",
        state TEXT NOT NULL DEFAULT "",
        name TEXT,
        status TEXT,
        additional_mobile TEXT,  -- Add this line
        reference_name TEXT  -- Add reference_name column here
        ALTER TABLE customers ADD COLUMN offer_discount DECIMAL(10, 2) DEFAULT 0;
    )''')

    # Create payment_history table
    cursor.execute('''CREATE TABLE IF NOT EXISTS payment_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        date TEXT,
        amount REAL,
        FOREIGN KEY (customer_id) REFERENCES customers(id)
    )
    ''')

    # Create bills table
    cursor.execute('''CREATE TABLE IF NOT EXISTS bills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        amount REAL NOT NULL
    )
    ''')
 
init_db()

def initialize_database():
    conn = sqlite3.connect('crm.db')
    cursor = conn.cursor()
    create_tables(cursor)
    conn.commit()
    conn.close()


def update_delivery_status():
    try:
        # Connect to the database
        conn = sqlite3.connect('crm.db')
        cursor = conn.cursor()
        
        # Update the delivery column where it is None
        cursor.execute('''
            UPDATE customers
            SET delivery = 'No'
            WHERE delivery IS NULL
        ''')
        
        # Commit the changes
        conn.commit()
        print("Delivery status updated from None to 'No' successfully.")
    
    except sqlite3.DatabaseError as e:
        print(f"Error updating delivery status: {e}")
    
    finally:
        # Close the connection
        conn.close()

# Call the function to update the delivery status
update_delivery_status()

def update_payment_status_to_custom_format():
    try:
        # Connect to the database
        conn = sqlite3.connect('crm.db')
        cursor = conn.cursor()

        # Update the 'payment_status' column with custom formatting
        cursor.execute('''
            UPDATE customers
            SET payment_status = CASE 
                WHEN payment_status = 'pending' THEN 'Pending'
                WHEN payment_status = 'paid' THEN 'Paid'
                WHEN payment_status = 'cancel' THEN 'Cancel'
                ELSE payment_status
            END
        ''')

        # Commit the changes to the database
        conn.commit()
        print("payment_status values updated with custom format.")

    except sqlite3.DatabaseError as e:
        print(f"Error updating payment_status: {e}")
    finally:
        # Close the connection
        conn.close()

# Call the function to update all rows
update_payment_status_to_custom_format()

# Ensure that future entries are stored in the custom format
def insert_payment_status_custom_format(customer_id, status):
    try:
        # Convert the status to the custom format
        if status.lower() == 'pending':
            status = 'Pending'
        elif status.lower() == 'paid':
            status = 'Paid'
        elif status.lower() == 'cancel':
            status = 'Cancel'
        else:
            status = status.capitalize()  # Keep the first letter capitalized

        # Connect to the database
        conn = sqlite3.connect('crm.db')
        cursor = conn.cursor()

        # Update the payment status for the customer (use placeholders for safety)
        cursor.execute('''
            UPDATE customers
            SET payment_status = ?
            WHERE id = ?
        ''', (status, customer_id))

        # Commit the changes to the database
        conn.commit()
        print(f"Payment status for customer {customer_id} updated to {status}.")

    except sqlite3.DatabaseError as e:
        print(f"Error inserting payment_status: {e}")
    finally:
        # Close the connection
        conn.close()

# Test with a customer ID (replace with an actual customer ID from your table)
# Example: Update payment status for customer with ID = 1
insert_payment_status_custom_format(1, 'PENDING')


# Make sure to add the custom date format filter globally
def custom_date_format(value):
    if isinstance(value, datetime):
        return value.strftime('%d/%m/%Y')
    return value

app.jinja_env.filters['custom_date_format'] = custom_date_format

import sqlite3

@app.route('/view_customer_details')
def view_customer_details():
    """Route to view customer details from crm.db, ordered by latest date."""
    
    # Establish a connection to the database using your helper function
    conn = get_db_connection()
    
    # Fetch all customer data, ordered by date in descending order
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customers ORDER BY date DESC")  # Customize query if needed
    customers = cursor.fetchall()
    
    # Dynamically retrieve column names
    column_titles = [description[0] for description in cursor.description]
    
    # Close the connection
    conn.close()

    # Pass data to the template and render
    return render_template('customer_info_display.html', column_titles=column_titles, customer_info=customers)

def update_commitment_type():
    try:
        # Connect to the database
        conn = sqlite3.connect('crm.db')
        cursor = conn.cursor()

        # Update the 'commitment_type' column with custom formatting
        cursor.execute('''
            UPDATE customer_commitments
            SET commitment_type = CASE 
                WHEN commitment_type = 'payment' THEN 'Payment Due'
                WHEN commitment_type = 'delivery' THEN 'Scheduled for Delivery'
                WHEN commitment_type = 'order' THEN 'Order Confirmed'
                ELSE commitment_type
            END
        ''')

        # Commit the changes
        conn.commit()
        print("Commitment type values updated successfully.")
    
    except sqlite3.DatabaseError as e:
        print(f"Error updating commitment type: {e}")
    
    finally:
        # Close the connection
        conn.close()

# Call the function to update commitment types
update_commitment_type()


def update_billno_to_uppercase():
    # Connect to the SQLite database
    conn = sqlite3.connect('crm.db')
    cursor = conn.cursor()
    
    try:
        # Fetch all rows from the customers table
        cursor.execute('SELECT id, billno FROM customers')
        rows = cursor.fetchall()

        # Loop through each row and update billno to uppercase if it contains any lowercase letter
        for row in rows:
            billno = row[1]  # Get the billno from the row (index 1 as SELECT id, billno)
            
            if billno and any(c.islower() for c in billno):  # Check if billno contains any lowercase letter
                # Convert the billno to uppercase
                formatted_billno = billno.upper()
                cursor.execute('UPDATE customers SET billno = ? WHERE id = ?', (formatted_billno, row[0]))  # row[0] is the id

        # Commit changes to the database
        conn.commit()
        print("All billno values with lowercase letters have been updated to uppercase.")
    
    except sqlite3.DatabaseError as e:
        print(f"Error while updating billno values: {e}")
    
    finally:
        conn.close()

# Call the function to update billno column
update_billno_to_uppercase()

def add_pincode_column():
    try:
        conn = sqlite3.connect('crm.db')
        cursor = conn.cursor()
        cursor.execute('ALTER TABLE customers ADD COLUMN pincode TEXT NOT NULL DEFAULT ""')
        conn.commit()
    except sqlite3.DatabaseError as e:
        print(f"Database error while adding pincode column: {e}")
    finally:
        conn.close()

add_pincode_column()

def add_adjustment_column(cursor):
    try:
        cursor.execute('ALTER TABLE customers ADD COLUMN adjustment_done INTEGER DEFAULT 0')
    except sqlite3.OperationalError:
        # Column already exists, do nothing
        pass

# Add this during initialization
conn = sqlite3.connect('crm.db')
cursor = conn.cursor()
add_adjustment_column(cursor)
conn.commit()
conn.close()

def add_order_status_column():
    try:
        conn = sqlite3.connect('crm.db')
        cursor = conn.cursor()
        cursor.execute('ALTER TABLE customers ADD COLUMN order_status TEXT NOT NULL DEFAULT "blank"')
        conn.commit()
    except sqlite3.DatabaseError as e:
        print(f"Error adding order_status column: {e}")
    finally:
        conn.close()

# Call this function when initializing or upgrading the database
add_order_status_column()

def find_column_usage(db, column_name):
    cursor = db.cursor()

    # Get all table names in the database
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    column_usage = {}

    for table_name in tables:
        table_name = table_name[0]

        # Check if the column exists in the table
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        
        for column in columns:
            if column[1] == column_name:
                if table_name not in column_usage:
                    column_usage[table_name] = []
                column_usage[table_name].append(column[1])  # column name

    return column_usage

@app.route('/find-column-usage/<column_name>')
def find_column_usage_route(column_name):
    db_connection = get_db_connection()  # Get the database connection
    usage = find_column_usage(db_connection, column_name)
    return jsonify(usage)

def search_for_column_usage(column_name):
    sql = f"SELECT name FROM sqlite_master WHERE type='table' AND name IN (SELECT name FROM sqlite_master WHERE sql LIKE '%{column_name}%');"
    cursor.execute(sql)
    tables_using_column = cursor.fetchall()
    return tables_using_column


@app.route('/database-structure')
def database_structure():
    db_connection = get_db_connection()  # Get the actual connection
    tables_info = get_tables_info(db_connection)  # Pass the connection to get_tables_info
    return render_template('database_structure.html', tables_info=tables_info)

def get_tables_info(db):
    cursor = db.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    tables_info = {}

    for table_name in tables:
        table_name = table_name[0]
        # Get columns for each table
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = [column[1] for column in cursor.fetchall()]
        tables_info[table_name] = columns

    return tables_info

# Flask-Mail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'krishnahomecare27@gmail.com'  # Your Gmail address
app.config['MAIL_PASSWORD'] = 'rxfw xlrf jrgr houp'  # Your Gmail password or app password
app.config['MAIL_DEFAULT_SENDER'] = 'krishnahomecare27@gmail.com'  # Your Gmail address
mail = Mail(app)

# Database Helper Class (using SQLite)
class DatabaseHelper:
    def __init__(self, db_name):
        self.db_name = db_name

    def get_connection(self):
        return sqlite3.connect(self.db_name)

    def fetch_weekly_entries(self, start_date, end_date):
        query = '''
            SELECT khccode, billno, biltyno, firmname, city, mobile, additional_mobile, amount, date
            FROM customers
            WHERE date BETWEEN ? AND ?
            ORDER BY date DESC
        '''
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, (start_date, end_date))
        rows = cursor.fetchall()
        conn.close()
        return rows


class EmailHelper:
    def __init__(self, app, mail):
        self.app = app
        self.mail = mail

    def send_email(self, subject, recipients, body, attachment=None):
        # Make sure recipients is a list
        if isinstance(recipients, str):  # If recipients is a string, convert it to a list
            recipients = [recipients]

        msg = Message(subject, recipients=recipients, body=body)
        msg.sender = 'krishnahomecare27@gmail.com'  # Your Gmail address

        if attachment:
            msg.attach("weekly_entries.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", attachment)

        try:
            self.mail.send(msg)
            print("Email sent successfully!")
            return "Email sent successfully!"  # Return success message
        except Exception as e:
            print(f"Error sending email: {e}")
            return f"Error sending email: {e}"  # Return error message
    
    def create_excel_report(self, rows):
        columns = [
            "KHC Code", "Bill No", "Bilty No", "Firm Name", "City", 
            "Mobile No", "Amount", "Extra Column"
        ]
        
        # Prepare formatted rows
        formatted_rows = []
        for row in rows:
            mobile_combined = f"{row[5]} / {row[6]}" if row[6] else row[5]
            formatted_date = datetime.strptime(row[8], "%Y-%m-%d").strftime("%d/%m/%Y")
            formatted_rows.append([row[0], row[1], row[2], row[3], row[4], mobile_combined, row[7], ""])

        # Convert data to pandas DataFrame
        df = pd.DataFrame(formatted_rows, columns=columns)

        # Capitalize all text in the DataFrame
        df = df.applymap(lambda x: x.upper() if isinstance(x, str) else x)

        # Save to BytesIO object (in-memory file)
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Weekly Entries')

        output.seek(0)

        print("Excel Report Created Successfully!")  # Debug message

        return output


# Initialize helpers
db_helper = DatabaseHelper('crm.db')  # Pass the correct database name
email_helper = EmailHelper(app, mail)

from datetime import datetime, timedelta

@app.route('/weekly_entries', methods=['GET'])
def weekly_entries():
    # Get the selected week start date from the request, default to current week
    today = datetime.today()
    selected_date = request.args.get('week_start_date', default=today.strftime('%Y-%m-%d'))

    # Ensure the start date is Monday
    selected_date = datetime.strptime(selected_date, '%Y-%m-%d')
    start_date = selected_date - timedelta(days=selected_date.weekday())  # Adjust to Monday
    end_date = start_date + timedelta(days=6)  # Sunday

    try:
        # Query database to get entries for the week
        conn = get_db_connection()
        entries = conn.execute(
            'SELECT * FROM customers WHERE date BETWEEN ? AND ?',
            (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
        ).fetchall()

        # Convert each Row to dictionary and format date
        entries = [
            {**dict(entry), 'date': datetime.strptime(entry['date'], '%Y-%m-%d').strftime('%d/%m/%Y')}
            for entry in entries
        ]
        
        # Calculate total amount for the week
        total_amount = sum(entry['amount'] for entry in entries)

        # Get past weeks (Monday as start date)
        past_weeks = [
            (today - timedelta(weeks=i)).strftime('%Y-%m-%d')
            for i in range(5)  # Fetch the past 5 weeks
        ]

        conn.close()

    except sqlite3.Error as e:
        flash(f"Error fetching data from the database: {e}", category='error')
        return render_template('error.html')

    return render_template(
        'weekly_entries.html',
        start_date=start_date.strftime('%d/%m/%Y'),
        end_date=end_date.strftime('%d/%m/%Y'),
        total_amount=total_amount,
        entries=entries,
        selected_week=start_date.strftime('%Y-%m-%d'),
        past_weeks=past_weeks
    )

@app.route('/export_weekly_entries', methods=['GET'])
def export_weekly_entries():
    # Get the selected week start date from the form (if provided)
    week_start_date = request.args.get('week_start_date')

    # If no week is selected, default to the most recent Monday
    if not week_start_date:
        week_start_date = datetime.today().strftime('%Y-%m-%d')

    # Calculate the start and end of the selected week
    start_of_week = datetime.strptime(week_start_date, '%Y-%m-%d')
    end_of_week = start_of_week + timedelta(days=6)  # Sunday

    # Format dates for SQL query (YYYY-MM-DD)
    start_date = start_of_week.strftime('%Y-%m-%d')
    end_date = end_of_week.strftime('%Y-%m-%d')

    # Fetch weekly entries from the database for the selected week
    rows = db_helper.fetch_weekly_entries(start_date, end_date)

    # Prepare rows with the "State" column before "City"
    formatted_rows = []
    for row in rows:
        mobile_combined = f"{row[5]} / {row[6]}" if row[6] else row[5]
        formatted_date = datetime.strptime(row[8], "%Y-%m-%d").strftime("%d/%m/%Y")
        
        # Ensure the 'State' (column index 9) is inserted before 'City' (assuming 'City' is column index 4 or another appropriate index)
        formatted_rows.append([
            row[0],  # KHC Code
            row[1],  # Bill No
            row[2],  # Bilty No
            formatted_date,  # Date
            row[3],  # Firm Name
            row[9],  # State (added here before City)
            row[4],  # City
            mobile_combined,  # Mobile No
            row[7],  # Amount
            ""  # Extra Column
        ])

    # Create the Excel report with the updated row data
    output = email_helper.create_excel_report(formatted_rows)

    # Try sending the email and handle errors
    email_send_status = email_helper.send_email(
        subject="Weekly Entries Report",
        recipients=["rkvyas555555@gmail.com", "vishalvyas121212@gmail.com", "vikasvyas2250@gmail.com"],
        body="Hello, Please find the weekly entries report attached.",
        attachment=output.read()
    )

    if "Error" in email_send_status:
        flash(f"Failed to send weekly entries report. Error: {email_send_status}", 'error')
    else:
        flash("Weekly entries report sent successfully!", 'success')

    # Redirect back to the weekly entries page
    return redirect(url_for('weekly_entries', start_date=start_date, end_date=end_date))

@app.route('/download_excel_report', methods=['GET'])
def download_excel_report():
    # Get the selected week start date from the form (if provided)
    week_start_date = request.args.get('week_start_date')

    # If no week is selected, default to the most recent Monday
    if not week_start_date:
        week_start_date = datetime.today().strftime('%Y-%m-%d')

    # Calculate the start and end of the selected week
    start_of_week = datetime.strptime(week_start_date, '%Y-%m-%d')
    end_of_week = start_of_week + timedelta(days=6)  # Sunday

    # Format dates for SQL query (YYYY-MM-DD)
    start_date = start_of_week.strftime('%Y-%m-%d')
    end_date = end_of_week.strftime('%Y-%m-%d')

    # Fetch weekly entries from the database for the selected week
    rows = db_helper.fetch_weekly_entries(start_date, end_date)

    # Create the Excel report
    output = email_helper.create_excel_report(rows)

    # Reset the position to the start of the in-memory file
    output.seek(0)

    # Send the generated Excel file for download
    return send_file(output, 
                     as_attachment=True, 
                     download_name="weekly_entries.xlsx",  # Use download_name instead of attachment_filename
                     mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

users = {'krishnahomecare': 'Vikas@123'}  # Updated dummy user data for login

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('Please log in to access this page.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def home():
    if 'username' in session:
        # Fetch user accessible pages
        username = session['username']
        conn = sqlite3.connect('auto.db')
        cursor = conn.cursor()
        cursor.execute('SELECT accessible_pages FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()

        if user:
            accessible_pages = user[0].split(',') if user[0] else []

            if accessible_pages:
                # Map user roles to specific Blueprint and endpoint
                role_to_endpoint = {
                    'anjali': 'anjali_bp.anjali_page',
                    'pooja': 'pooja_bp.pooja_page',
                    'avni': 'avni_bp.avni_page',
                    'juhi': 'juhi_bp.juhi_page',
                    'dev': 'dev_bp.dev_page',
                    'tina': 'tina_bp.tina_page',
                    'priti': 'priti_bp.priti_page',
                    'ruhi': 'ruhi_bp.ruhi_page',
                    'neha': 'neha_bp.neha_page',
                    'harish': 'harish_bp.harish_page',
                    'delivery': 'delivery_bp.customers_with_buttons',
                    'payment_pending': 'payment_pending.payment_pending'

                }

                # Check each accessible page and redirect to the first matching endpoint
                for role in accessible_pages:
                    endpoint = role_to_endpoint.get(role.lower())
                    if endpoint:
                        return redirect(url_for(endpoint))

        return redirect(url_for('index'))  # Fallback to index if no valid pages found

    return redirect(url_for('login'))  # Redirect to login if not logged in

@app.route('/some_route')
@login_required
def some_route():
    # Assume 'username' is stored in the session after login
    username = session['username']
    conn = sqlite3.connect('auto.db')
    cursor = conn.cursor()
    cursor.execute('SELECT accessible_pages FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()

    user_permissions = user[0].split(',') if user else []
    return render_template('your_template.html', user_permissions=user_permissions)

from datetime import datetime

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        # Hardcoded admin
        if username == 'krishnahomecare' and password == 'Vikas@123':
            login_time = datetime.now().replace(microsecond=0)
            session['username'] = username
            session['permissions'] = ['admin']
            session['login_time'] = login_time.strftime("%Y-%m-%d %H:%M:%S")
            online_users.add_user(username, login_time)
            flash('Admin login successful!', 'success')
            return redirect(url_for('index'))

        # DB user check
        try:
            conn = sqlite3.connect('auto.db')
            cursor = conn.cursor()
            cursor.execute(
                'SELECT accessible_pages, reference_name FROM users WHERE username = ? AND password = ?',
                (username, password)
            )
            user = cursor.fetchone()

            if user:
                accessible_pages = user[0].split(',') if user[0] else []
                reference_name = user[1] if len(user) > 1 else None

                login_time = datetime.now().replace(microsecond=0)

                session['username'] = username
                session['reference_name'] = reference_name
                session['permissions'] = accessible_pages
                session['login_time'] = login_time.strftime("%Y-%m-%d %H:%M:%S")

                online_users.add_user(username, login_time)

                page_redirects = {
                    'anjali': 'anjali_bp.anjali_page',
                    'pooja': 'pooja_bp.pooja_page',
                    'avni': 'avni_bp.avni_page',
                    'juhi': 'juhi_bp.juhi_page',
                    'dev': 'dev_bp.dev_page',
                    'tina': 'tina_bp.tina_page',
                    'priti': 'priti_bp.priti_page',
                    'ruhi': 'ruhi_bp.ruhi_page',
                    'neha': 'neha_bp.neha_page',
                    'harish': 'harish_bp.harish_page',
                    'delivery': 'delivery_bp.customers_with_buttons',
                    'payment_pending': 'payment_pending.payment_pending_page',
                }

                for page in accessible_pages:
                    page_key = page.strip().lower()
                    if page_key in page_redirects:
                        return redirect(url_for(page_redirects[page_key]))

                flash('No valid accessible pages found for this user!', 'warning')
                return redirect(url_for('index'))

            else:
                flash('Invalid username or password!', 'danger')

        except sqlite3.DatabaseError as e:
            print(f"Database error: {e}")
            flash('A database error occurred. Please try again later.', 'danger')

        finally:
            conn.close()

    return render_template('login.html')

@app.route('/logout')
def logout():
    username = session.get('username')
    login_time_str = session.get('login_time')

    if username and login_time_str:
        online_users.remove_user(username, login_time_str)
    else:
        print("Logout: Missing username or login_time in session.")

    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))

def seconds_to_human(seconds):
    seconds = int(seconds)
    if seconds < 60:
        return f"{seconds} seconds ago"
    elif seconds < 3600:
        mins = seconds // 60
        return f"{mins} minute{'s' if mins > 1 else ''} ago"
    elif seconds < 86400:
        hours = seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    else:
        days = seconds // 86400
        return f"{days} day{'s' if days > 1 else ''} ago"

app.jinja_env.filters['seconds_to_human'] = seconds_to_human

def get_customer_data(reference_name):
    try:
        # Get a database connection
        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch customers where the reference_name matches (case-insensitive)
        cursor.execute('SELECT * FROM customers WHERE LOWER(reference_name) = ? ORDER BY id DESC', (reference_name.lower(),))
        customers = cursor.fetchall()

        # Calculate total amount and total number of customers
        total_amount = sum(
            float(customer['amount']) if customer['amount'] else 0 for customer in customers
        )  # Convert 'amount' to float, default to 0 if it's None or invalid
        total_customers = len(customers)

        # Close the database connection
        conn.close()

        return customers, total_amount, total_customers

    except sqlite3.DatabaseError as e:
        print(f"Database error: {e}")
        return None, 0, 0


@app.route('/edit_user')
def edit_user_page():
    # Render the edit user page if the user has permission
    return render_template('edit_user.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        new_password = request.form['password']

        try:
            conn = sqlite3.connect('auto.db')  # Connect to your database
            cursor = conn.cursor()

            # Check if the username already exists
            cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
            existing_user = cursor.fetchone()

            if existing_user:
                flash('Username already exists!', 'danger')
            else:
                # Hash the password before saving it
                hashed_password = generate_password_hash(new_password)
                # Insert the new user into the database
                cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', 
                               (username, hashed_password))
                conn.commit()
                flash('Registration successful! You can now log in.', 'success')
                return redirect(url_for('login'))

        except sqlite3.DatabaseError as e:
            print(f"Database error: {e}")
            flash('An error occurred. Please try again.', 'danger')
        finally:
            conn.close()

    return render_template('register.html')


def create_database():
    # Connect to the SQLite database (it will create the database file if it doesn't exist)
    conn = sqlite3.connect('auto.db')
    cursor = conn.cursor()

    # Create a new table for users with permissions if it does not already exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            accessible_pages TEXT DEFAULT ''
        )
    ''')

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

# Call this function to create the database and table if they don't exist
create_database()

def check_table_structure():
    conn = sqlite3.connect('auto.db')
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(users)")
    columns = cursor.fetchall()
    for column in columns:
        print(column)

    conn.close()

check_table_structure()

@app.route('/users')
@login_required  # Ensure that this page is only accessible if the user is logged in
def users():
    try:
        conn = sqlite3.connect('auto.db')  # Connect to your database
        cursor = conn.cursor()

        # Fetch all users from the database including password and accessible pages
        cursor.execute('SELECT username, password, accessible_pages FROM users')
        all_users = cursor.fetchall()

        # Debugging: Print the fetched data
        print(all_users)  # Check the format of the data being returned

    except sqlite3.DatabaseError as e:
        print(f"Database error: {e}")
        all_users = []
    finally:
        conn.close()

    return render_template('users.html', all_users=all_users)

@app.route('/delete_user/<username>', methods=['POST'])
@login_required
def delete_user(username):
    try:
        conn = sqlite3.connect('auto.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM users WHERE username = ?', (username,))
        conn.commit()
        flash('User deleted successfully!', 'success')
    except sqlite3.DatabaseError as e:
        print(f"Database error: {e}")
        flash('An error occurred while deleting the user.', 'danger')
    finally:
        conn.close()
    
    return redirect(url_for('users'))

def get_user_data(username):
    conn = sqlite3.connect('auto.db')
    cursor = conn.cursor()
    cursor.execute('SELECT username, password, accessible_pages FROM users WHERE username = ?', (username,))
    user_data = cursor.fetchone()
    conn.close()
    return user_data

@app.route('/edit_user/<username>', methods=['GET', 'POST'])
@login_required
def edit_user(username):
    # Fetch current user data
    user_data = get_user_data(username)

    # Check if user data exists
    if not user_data:
        flash("This user does not exist. Please go back to the users list.")
        return redirect(url_for('users'))  # Redirect to users list if user not found

    if request.method == 'POST':
        # Get new data from the form
        new_username = request.form['username']
        new_password = request.form['password']
        accessible_pages = request.form.getlist('accessible_pages')  # Get selected pages
        
        # Connect to the database to update user data
        conn = sqlite3.connect('auto.db')
        
        # Update user information in the database
        if new_username != username:  # If username is changing
            conn.execute(
                "UPDATE users SET username = ?, password = ?, accessible_pages = ? WHERE username = ?", 
                (new_username, new_password, ','.join(accessible_pages), username)
            )
        else:
            # Update only the password and accessible pages
            conn.execute(
                "UPDATE users SET password = ?, accessible_pages = ? WHERE username = ?", 
                (new_password, ','.join(accessible_pages), username)
            )
        
        conn.commit()
        conn.close()
        
        flash("User updated successfully!")  # Success message
        return redirect(url_for('users'))  # Redirect to users list

    # Prepare accessible pages for the form
    accessible_pages_list = user_data[2].split(',') if user_data[2] else []
    
    # Return the edit user form with current user data
    return render_template('edit_user.html', user_data=[user_data[0], user_data[1], accessible_pages_list])

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

def get_crm_connection():
    return sqlite3.connect('crm.db')

def get_auto_connection():
    return sqlite3.connect('auto.db')

# Function to update the user's password in the database
def update_user_password(old_username, new_username, new_password):
    try:
        conn = sqlite3.connect('auto.db')
        cursor = conn.cursor()
        
        # Update user information in the database
        cursor.execute(
            "UPDATE users SET username = ?, password = ? WHERE username = ?", 
            (new_username, new_password, old_username)
        )
        conn.commit()
        flash("User updated successfully!")  # Success message

    except sqlite3.DatabaseError as e:
        print(f"Database error: {e}")
        flash('An error occurred while updating the user.', 'danger')
    finally:
        conn.close()

    if 'username' not in session:
        flash('Please log in to access this page.', 'danger')  # Flash message for unauthenticated access
        return redirect(url_for('login'))  # Redirect to login page

def update_user_password(username, old_password, new_password):
    # Update password logic here
    print("User updated successfully!")  # Debugging message


# Register a custom Jinja filter for date formatting
@app.template_filter('format_date')
def format_date(date, format_string='%d/%m/%Y'):  # Default format string
    if isinstance(date, str):
        date = datetime.strptime(date, '%Y-%m-%d')  # Convert string to datetime if needed
    return date.strftime(format_string)  # Return the formatted date

@app.route('/index', methods=['GET', 'POST'])
def index():
    if 'username' not in session:
        flash('Please log in to access this page.', 'danger')
        return redirect(url_for('login'))

    try:
        # Get the last 5 weeks for selection
        weeks = get_last_weeks()

        # Format weeks' start and end dates in DD/MM/YYYY
        for week in weeks:
            week['start'] = datetime.strptime(week['start'], '%Y-%m-%d').strftime('%d/%m/%Y')
            week['end'] = datetime.strptime(week['end'], '%Y-%m-%d').strftime('%d/%m/%Y')
            week['display'] = f"{week['start']} to {week['end']}"

        # Get the selected week from the form, default to None if not set
        selected_week = request.form.get('week', None)

        weekly_entries = []
        total_order_amount = 0  # Initialize the total amount for orders
        total_payment_received = 0  # Initialize the total payments received
        formatted_start_date = ""
        formatted_end_date = ""

        if selected_week:
            # Split the selected week into start and end dates
            start_date_str, end_date_str = selected_week.split(' to ')

            try:
                start_date = datetime.strptime(start_date_str, '%d/%m/%Y')
                end_date = datetime.strptime(end_date_str, '%d/%m/%Y')

                # Format the dates in DD/MM/YYYY format
                formatted_start_date = start_date.strftime('%d/%m/%Y')
                formatted_end_date = end_date.strftime('%d/%m/%Y')

            except ValueError as e:
                flash('Invalid date format. Please ensure the date is in DD/MM/YYYY format.', 'danger')
                return redirect(url_for('index'))

            try:
                # Get the weekly entries
                weekly_entries = get_weekly_entries_for_week(start_date, end_date)

                # Convert sqlite3.Row to dictionary and format date
                # Convert sqlite3.Row to dictionary and format date
                weekly_entries = [dict(entry) for entry in weekly_entries]  # Convert each entry to a dictionary

                for entry in weekly_entries:
                    try:
                        entry['date'] = datetime.strptime(entry['date'], '%Y-%m-%d').strftime('%d/%m/%Y')
                    except ValueError as e:
                        entry['date'] = 'Invalid Date'  # If the date is invalid, set it to 'Invalid Date'

                # Sort entries in descending order of date
                weekly_entries.sort(key=lambda x: datetime.strptime(x['date'], '%d/%m/%Y') if x['date'] != 'Invalid Date' else datetime.min, reverse=True)

                # Calculate the total order amount for this week
                total_order_amount = sum(float(entry['amount']) for entry in weekly_entries if entry.get('amount'))

                # Fetch the total payments received for this week
                conn = get_db_connection()
                cursor = conn.cursor()

                cursor.execute('''
                    SELECT SUM(ph.amount)
                    FROM payment_history ph
                    JOIN customers c ON ph.customer_id = c.id
                    WHERE DATE(ph.date) BETWEEN ? AND ?
                ''', (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
                
                total_payment_received = cursor.fetchone()[0]
                total_payment_received = float(total_payment_received) if total_payment_received else 0
                conn.close()

            except Exception as e:
                flash(f"Error fetching or processing entries: {str(e)}", 'danger')
                return redirect(url_for('index'))

        return render_template('index.html', weeks=weeks, weekly_entries=weekly_entries, selected_week=selected_week,
                               total_order_amount=total_order_amount, total_payment_received=total_payment_received,
                               formatted_start_date=formatted_start_date, formatted_end_date=formatted_end_date)

    except Exception as e:
        # Catch any other unexpected errors
        flash(f"An error occurred: {str(e)}", 'danger')
        return render_template('index.html', weeks=[], weekly_entries=[], selected_week=None, total_order_amount=0, total_payment_received=0)

def get_total_payment_for_week(start_date, end_date):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch total payment amount for the given week
    cursor.execute('''
        SELECT SUM(ph.amount)
        FROM payment_history ph
        WHERE ph.date BETWEEN ? AND ?
    ''', (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))

    total_payment = cursor.fetchone()[0]
    conn.close()

    return total_payment if total_payment else 0

# Function to get the last 5 weeks
def get_last_weeks():
    today = datetime.today()
    weeks = []
    
    for i in range(5):  # To get the last 5 weeks (change to 4 for last 4 weeks)
        start_of_week = today - timedelta(days=today.weekday()) - timedelta(weeks=i)
        end_of_week = start_of_week + timedelta(days=6)  # End of the week is 6 days after start
        
        # Format the week range (e.g., '2024-11-24 to 2024-11-30')
        weeks.append({
            'start': start_of_week.strftime('%Y-%m-%d'),
            'end': end_of_week.strftime('%Y-%m-%d'),
            'display': f"{start_of_week.strftime('%Y-%m-%d')} to {end_of_week.strftime('%Y-%m-%d')}"
        })
    
    return weeks

from datetime import timedelta

# Function to fetch weekly data for the selected week
def get_weekly_entries_for_week(start_date, end_date):
    conn = sqlite3.connect('crm.db')
    conn.row_factory = sqlite3.Row  # To return results as Row objects
    cursor = conn.cursor()

    # Adjust end_date to include the entire day (until the last second of the day)
    end_date = end_date + timedelta(days=1) - timedelta(seconds=1)

    # Ensure that the query checks for the whole day range, including any time part
    cursor.execute('''SELECT * FROM customers WHERE date BETWEEN ? AND ?''', 
                   (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
    weekly_entries = cursor.fetchall()
    conn.close()
    return weekly_entries

# Function to get the weeks of a month (not used in the current code but kept for reference)
def get_weeks_of_month(month_start):
    # Get the total days in the month
    _, last_day = calendar.monthrange(month_start.year, month_start.month)

    # Create weekly date ranges for the month
    weeks = []
    for i in range(0, last_day, 7):
        start_date = month_start.replace(day=i + 1)
        end_date = min(month_start.replace(day=i + 7), month_start.replace(day=last_day))
        weeks.append((start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
    
    return weeks
from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime, timedelta
import sqlite3
import calendar

def add_last_download_date_column():
    try:
        conn = sqlite3.connect('crm.db')  # Use your actual database name
        cursor = conn.cursor()

        # Add the last_download_date column if it doesn't exist
        cursor.execute("ALTER TABLE users ADD COLUMN last_download_date DATE")

        conn.commit()
        print("Column 'last_download_date' added successfully!")
    except sqlite3.DatabaseError as e:
        print(f"Error adding column: {e}")
    finally:
        if conn:
            conn.close()

# Call this function once to add the column
add_last_download_date_column()

def trigger_download():
    # This function triggers the download, similar to your export_weekly_entries logic
    # You can reuse the export_weekly_entries code here, or if using Celery or another task queue,
    # you can schedule the download task to run in the background.
    # For simplicity, I'm calling it directly.

    # Call the download logic here
    export_weekly_entries()

from datetime import datetime

def format_result_as_html(result):
    # existing HTML table code...
    return f"""
    <table> ... </table>
    <br>
    <button onclick="history.back()" style="margin-top: 15px; padding: 10px 16px; background-color: #f0f0f0; border: 1px solid #ccc; border-radius: 6px; cursor: pointer; font-size: 14px;">
      ⬅️ Back
    </button>
    """

@app.route('/customers')
def customers():
    if 'username' not in session:
        flash('Please log in to access this page.', 'danger')
        return redirect(url_for('login'))

    search_query = request.args.get('search', '')
    current_year = datetime.now().year
    selected_year = request.args.get('year', str(current_year))
    page = int(request.args.get('page', 1))
    per_page = 50  # Ek page me 50 rows dikhenge
    offset = (page - 1) * per_page

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Distinct years fetch karna
        cursor.execute('SELECT DISTINCT strftime("%Y", date) AS year FROM customers ORDER BY year DESC')
        years = [row['year'] for row in cursor.fetchall()]

        # Customers query with search, year filter, limit, offset
        query = '''
            SELECT * FROM customers
            WHERE (khccode LIKE ? OR firmname LIKE ? OR pincode LIKE ?)
        '''
        params = ['%' + search_query + '%', '%' + search_query + '%', '%' + search_query + '%']

        if selected_year != 'all':
            query += ' AND strftime("%Y", date) = ?'
            params.append(selected_year)

        query += ' ORDER BY datetime(date) DESC LIMIT ? OFFSET ?'
        params.extend([per_page, offset])

        cursor.execute(query, params)
        customers_data = cursor.fetchall()
        customers_list = [dict(row) for row in customers_data]

        # Additional mobile numbers fetch karna
        additional_mobiles = {}
        cursor.execute('SELECT customer_id, mobile_number FROM additional_mobiles')
        for row in cursor.fetchall():
            customer_id = row['customer_id']
            mobile_number = row['mobile_number']
            additional_mobiles.setdefault(customer_id, []).append(mobile_number)

        # Totals initialize
        total_amount = 0.0
        total_received_amount = 0.0
        total_due = 0.0
        total_cancelled = 0.0

        for row in customers_list:
            amount = float(row.get('amount', 0.0))
            status = row.get('payment_status', '').strip().lower()
            customer_id = row['id']
            primary_mobile = row.get('mobile', '').strip()

            cursor.execute('SELECT SUM(amount) FROM payment_history WHERE customer_id = ?', (customer_id,))
            customer_received_amount = cursor.fetchone()[0] or 0.0
            row['total_received_amount'] = customer_received_amount

            due_amount = amount - customer_received_amount

            if status == 'cancel':
                total_cancelled += amount
                row['due_amount'] = 0.0
            else:
                total_amount += amount
                total_received_amount += customer_received_amount
                row['due_amount'] = due_amount
                total_due += due_amount

            # Update khccode for all customers with same mobile or additional mobiles
            cursor.execute(''' 
                UPDATE customers 
                SET khccode = ? 
                WHERE mobile = ? OR id = ? OR id IN (
                    SELECT customer_id FROM additional_mobiles WHERE mobile_number = ? 
                )
            ''', (row['khccode'], primary_mobile, customer_id, primary_mobile))

        conn.commit()

        # Overall totals for filtered customers (without limit)
        if selected_year != 'all':
            cursor.execute(''' 
                SELECT SUM(amount) as total_amount,
                       SUM(CASE WHEN payment_status != 'Cancel' THEN amount ELSE 0 END) as total_due,
                       SUM(CASE WHEN payment_status != 'Cancel' THEN (
                           SELECT SUM(amount) FROM payment_history WHERE customer_id = customers.id
                       ) ELSE 0 END) as total_received_amount,
                       SUM(CASE WHEN payment_status = 'Cancel' THEN amount ELSE 0 END) as total_cancelled
                FROM customers
                WHERE (khccode LIKE ? OR firmname LIKE ? OR pincode LIKE ?)
                  AND strftime("%Y", date) = ?
            ''', ('%' + search_query + '%', '%' + search_query + '%', '%' + search_query + '%', selected_year))
        else:
            cursor.execute(''' 
                SELECT SUM(amount) as total_amount,
                       SUM(CASE WHEN payment_status != 'Cancel' THEN amount ELSE 0 END) as total_due,
                       SUM(CASE WHEN payment_status != 'Cancel' THEN (
                           SELECT SUM(amount) FROM payment_history WHERE customer_id = customers.id
                       ) ELSE 0 END) as total_received_amount,
                       SUM(CASE WHEN payment_status = 'Cancel' THEN amount ELSE 0 END) as total_cancelled
                FROM customers
                WHERE khccode LIKE ? OR firmname LIKE ? OR pincode LIKE ?
            ''', ('%' + search_query + '%', '%' + search_query + '%', '%' + search_query + '%'))

        overall_totals = cursor.fetchone()
        total_amount = overall_totals['total_amount'] or 0.0
        total_received_amount = overall_totals['total_received_amount'] or 0.0
        total_cancelled = overall_totals['total_cancelled'] or 0.0
        total_due = total_amount - total_received_amount

        # Category summary
        cursor.execute("SELECT Category, COUNT(*) as total FROM customers GROUP BY Category")
        category_data = cursor.fetchall()

        # Total customers count for pagination
        count_query = '''
            SELECT COUNT(*) as total_count FROM customers
            WHERE (khccode LIKE ? OR firmname LIKE ? OR pincode LIKE ?)
        '''
        count_params = ['%' + search_query + '%', '%' + search_query + '%', '%' + search_query + '%']
        if selected_year != 'all':
            count_query += ' AND strftime("%Y", date) = ?'
            count_params.append(selected_year)
        cursor.execute(count_query, count_params)
        total_customers_count = cursor.fetchone()['total_count']

        total_pages = (total_customers_count + per_page - 1) // per_page  # total pages calculate

    except sqlite3.DatabaseError as e:
        print(f"Database error: {e}")
        customers_list = []
        years = []
        category_data = []
        total_amount = total_received_amount = total_due = total_cancelled = 0.0
        total_pages = 1
        page = 1

    finally:
        conn.close()

    return render_template(
        'customers.html',
        show_extra_buttons=True,
        customers=customers_list,
        years=years,
        total_amount=total_amount,
        total_received_amount=total_received_amount,
        total_due=total_due,
        total_cancelled=total_cancelled,
        search_query=search_query,
        additional_mobiles=additional_mobiles,
        selected_year=selected_year,
        category_data=category_data,
        page=page,
        total_pages=total_pages
    )

def get_categories():
    conn = sqlite3.connect('crm.db')  # Aapka database
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT category FROM customers")  # "customers" table se unique categories
    categories = cursor.fetchall()
    conn.close()
    return categories

def get_firms_by_category(category):
    conn = sqlite3.connect('crm.db')  # ya aapke db ka naam
    cursor = conn.cursor()
    cursor.execute("SELECT id, category, firmname FROM customers WHERE category=?", (category,))
    firms = cursor.fetchall()
    conn.close()
    return firms

@app.route('/categories', methods=['GET', 'POST'])
def show_categories():
    categories = get_categories()  # Make sure this function is defined above or imported
    firms = []
    selected_category = None

    if request.method == 'POST':
        selected_category = request.form.get('category')
        firms = get_firms_by_category(selected_category)

    return render_template('categories.html', categories=categories, firms=firms, selected_category=selected_category)

@app.route('/duplicate-khccodes')
def duplicate_khccodes():
    if 'username' not in session:
        flash('Please log in to access this page.', 'danger')
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Query to find customers with the same mobile number but different khccode
        query = '''
            SELECT c1.id, c1.khccode, c1.mobile, c1.firmname, c1.city, c1.state, c1.amount, c1.payment_status
            FROM customers c1
            WHERE EXISTS (
                SELECT 1 FROM customers c2
                WHERE c2.mobile = c1.mobile AND c2.khccode != c1.khccode
            )
            ORDER BY c1.mobile, c1.khccode
        '''
        cursor.execute(query)
        customers_data = cursor.fetchall()

        # Convert the result into a list of dictionaries using column names
        column_names = [description[0] for description in cursor.description]
        customers_list = [dict(zip(column_names, row)) for row in customers_data]

        # Automatically correct the duplicate KHC codes
        for customer in customers_list:
            # Find all customers with the same mobile number
            mobile = customer['mobile']
            cursor.execute(''' 
                SELECT id, khccode FROM customers WHERE mobile = ? 
            ''', (mobile,))
            duplicate_entries = cursor.fetchall()

            # Check if there are duplicates with different KHC codes
            khccodes = set(entry[1] for entry in duplicate_entries)  # Getting only the KHC codes
            if len(khccodes) > 1:
                # Automatically assign the same KHC code to all duplicate entries
                # Choose to update to the first KHC code (or any other logic you prefer)
                new_khccode = duplicate_entries[0][1]

                # Update all duplicate entries to the same KHC code
                cursor.executemany(''' 
                    UPDATE customers 
                    SET khccode = ? 
                    WHERE id = ? 
                ''', [(new_khccode, entry[0]) for entry in duplicate_entries])

                # Commit the changes to the database
                conn.commit()

        flash('Duplicate KHC codes have been corrected successfully.', 'success')

    except sqlite3.DatabaseError as e:
        conn.rollback()
        print(f"Database error: {e}")
        flash('An error occurred while correcting duplicate KHC codes. Please try again.', 'danger')
        customers_list = []

    finally:
        conn.close()  # Close the connection

    # Render the template and pass the customers list
    return render_template(
        'duplicate_khccodes.html',
        customers=customers_list
    )

# Configure Celery to use Redis
def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)
    return celery

app.config.update(
    CELERY_BROKER_URL='redis://localhost:6379/0',  # Redis broker URL
    CELERY_RESULT_BACKEND='redis://localhost:6379/0',  # Redis backend
)

# Create Celery instance
celery = make_celery(app)

# Celery task to update KHC codes automatically
@celery.task(bind=True)
def update_khc_codes(self):
    conn = sqlite3.connect('your_database.db')
    cursor = conn.cursor()
    try:
        # Query to find customers with the same mobile number but different khccode
        query = '''
            SELECT c1.id, c1.khccode, c1.mobile
            FROM customers c1
            WHERE EXISTS (
                SELECT 1 FROM customers c2
                WHERE c2.mobile = c1.mobile AND c2.khccode != c1.khccode
            )
        '''
        cursor.execute(query)
        customers_data = cursor.fetchall()

        # Correct the duplicate KHC codes
        for customer in customers_data:
            mobile = customer[2]
            cursor.execute('''
                SELECT id, khccode FROM customers WHERE mobile = ?
            ''', (mobile,))
            duplicate_entries = cursor.fetchall()

            # If multiple KHC codes are found, update them
            if len(set(entry[1] for entry in duplicate_entries)) > 1:
                new_khccode = duplicate_entries[0][1]  # Take the first KHC code
                cursor.executemany('''
                    UPDATE customers
                    SET khccode = ?
                    WHERE id = ?
                ''', [(new_khccode, entry[0]) for entry in duplicate_entries])
                conn.commit()

    except sqlite3.DatabaseError as e:
        print(f"Database error: {e}")
    finally:
        conn.close()

# Endpoint to manually trigger the task (for testing)
@app.route('/trigger-update')
def trigger_update():
    update_khc_codes.apply_async()  # Trigger background task
    flash('KHC codes update task started.', 'success')
    return redirect(url_for('index'))

@app.route('/update_adjustment_status', methods=['POST'])
def update_adjustment_status():
    data = request.get_json()
    customer_id = data.get('customer_id')

    # Update the database to set adjustment_done = 1 (or 0 for uncheck)
    conn = get_db_connection()
    conn.execute('UPDATE customers SET adjustment_done = ? WHERE id = ?', 
                 (1 if data['adjustment_done'] else 0, customer_id))
    conn.commit()
    conn.close()

    return jsonify({'status': 'success'}), 200

# Custom filter to format date
@app.template_filter('format_date')
def format_date(date_string):
    try:
        # Assuming the date is in 'yyyy-mm-dd' format
        date_object = datetime.strptime(date_string, '%Y-%m-%d')
        return date_object.strftime('%d/%m/%Y')  # Format to dd/mm/yyyy
    except ValueError:
        return date_string  # Return original if format is unexpected

from datetime import datetime
from flask import render_template, flash, redirect, url_for, session, request
import sqlite3
import traceback

@app.route('/add_customer', methods=['GET', 'POST'])
def add_customer():
    if 'username' not in session:
        flash('Please log in to access this page.', 'danger')
        return redirect(url_for('login'))

    customer = {}

    if request.method == 'POST':
        khc_code = request.form['khccode']
        bill_no = request.form['billno']
        bilty_no = request.form['biltyno']
        date_str = request.form.get('date', datetime.now().strftime('%d/%m/%Y')).replace('-', '/')

        try:
            date = datetime.strptime(date_str, '%d/%m/%Y').strftime('%Y-%m-%d')
        except ValueError:
            flash('Invalid date format. Please use DD/MM/YYYY.', 'error')
            return render_template('add_customer.html', current_date=datetime.now().strftime('%d/%m/%Y'), customer=customer)

        name = request.form.get('name', '')
        firm_name = request.form['firmname']
        state = request.form['state']
        city = request.form['city']
        category = request.form.get('category', '')
        district = request.form['district']
        tehsil = request.form['tehsil']

        pincode_input = request.form['pincode']
        if not pincode_input:
            flash('Pincode is required.', 'error')
            return render_template('add_customer.html', current_date=datetime.now().strftime('%d/%m/%Y'), customer=customer)

        try:
            pincode = int(pincode_input)
        except ValueError:
            flash('Invalid pincode. Please enter a number.', 'error')
            return render_template('add_customer.html', current_date=datetime.now().strftime('%d/%m/%Y'), customer=customer)

        mobile = request.form['mobile']
        amount = float(request.form['amount'])
        reference_name = request.form['reference_name']
        receive_amount = float(request.form.get('receive_amount', '0'))
        payment_status = request.form.get('payment_status', 'Pending')
        additional_mobiles = request.form.getlist('additional_mobile[]')

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            sql_command = '''
                INSERT INTO customers 
                (khccode, billno, biltyno, date, name, firmname, state, city, pincode, mobile, amount, reference_name, receive_amount, payment_status, category, district, tehsil)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''

            cursor.execute(sql_command,
                (khc_code, bill_no, bilty_no, date, name, firm_name, state, city, pincode, mobile, amount,
                 reference_name, receive_amount, payment_status, category, district, tehsil))

            customer_id = cursor.lastrowid

            for add_mobile in additional_mobiles:
                if add_mobile:
                    cursor.execute('''
                        INSERT INTO additional_mobiles (customer_id, mobile_number)
                        VALUES (?, ?)
                    ''', (customer_id, add_mobile))

            conn.commit()
            flash('Customer added successfully!', 'success')

        except sqlite3.DatabaseError as e:
            print(f"Database error while adding customer: {e}")
            print(traceback.format_exc())
            flash('Error occurred while adding customer.', 'error')

        finally:
            conn.close()

        return redirect(url_for('customers'))

    current_date = datetime.now().strftime('%d/%m/%Y')
    return render_template('add_customer.html', current_date=current_date, customer=customer)


@app.route('/get_customer_details')
def get_customer_details():
    mobile = request.args.get('mobile')
    if not mobile:
        return jsonify({"error": "Mobile number is required."}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM customers WHERE mobile = ?", (mobile,))
        customer = cursor.fetchone()
        conn.close()

        if customer:
            # Assuming the database columns map to these keys
            return jsonify({
                "exists": True,
                "khc_code": customer["khccode"],
                "name": customer["name"],
                "firm_name": customer["firmname"],
                "state": customer["state"],
                "city": customer["city"],
                "pincode": customer["pincode"],
                "amount": customer["amount"],
                "reference_name": customer["reference_name"],
            })
        else:
            return jsonify({"exists": False})

    except sqlite3.DatabaseError as e:
        print(f"Error fetching customer details: {e}")
        return jsonify({"error": "Database error occurred."}), 500

@app.route('/get_khc_code', methods=['GET'])
def get_khc_code():
    mobile = request.args.get('mobile')
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check for KHC code associated with the provided mobile number
    cursor.execute('SELECT khccode FROM customers WHERE mobile = ?', (mobile,))
    row = cursor.fetchone()

    if row:
        return jsonify({'khc_code': row[0]})  # Return the KHC code if found
    else:
        # If not found, you can handle creating a new KHC code
        return jsonify({'khc_code': None})  # Return None if no KHC code exists for that mobile

@app.route('/save_khc_code', methods=['POST'])
def save_khc_code():
    data = request.json
    mobile = data['mobile']
    additional_mobiles = data.get('additional_mobile', [])  # List of additional mobile numbers
    khc_code = data['khc_code']

    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if the primary mobile number already has a KHC code
    cursor.execute('SELECT khccode FROM customers WHERE mobile = ?', (mobile,))
    row = cursor.fetchone()

    if row and row[0]:  # If the KHC code already exists
        khc_code = row[0]  # Use the existing KHC code
    else:
        # Insert or update the primary mobile number with the new KHC code
        cursor.execute('''
            INSERT INTO customers (mobile, khccode) 
            VALUES (?, ?) 
            ON CONFLICT(mobile) DO UPDATE SET khccode = ?
        ''', (mobile, khc_code, khc_code))

    # Save additional mobile numbers with the same KHC code
    for additional_mobile in additional_mobiles:
        cursor.execute('''
            INSERT INTO customers (mobile, khccode) 
            VALUES (?, ?) 
            ON CONFLICT(mobile) DO UPDATE SET khccode = ?
        ''', (additional_mobile, khc_code, khc_code))

    conn.commit()
    conn.close()

    return jsonify({'success': True, 'message': 'KHC codes saved for all mobile numbers.'})

@app.route('/view_customer/<int:customer_id>')
def view_customer(customer_id):
    if 'username' not in session:
        flash('Please log in to access this page.', 'danger')
        return redirect(url_for('login'))

    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        # Fetch the customer details
        cursor.execute('SELECT * FROM customers WHERE id = ?', (customer_id,))
        customer = cursor.fetchone()

        if not customer:
            abort(404, description="Customer not found")

        customer = dict(customer)

        # Make sure 'billno' exists before using it
        bill_no = customer.get('billno')

        # Ensure 'delivery' has a default value
        customer['delivery'] = customer.get('delivery', 'NO')

        # Additional mobile numbers
        additional_mobiles_str = customer.get('additional_mobile', '')
        additional_mobiles = additional_mobiles_str.split(',') if additional_mobiles_str else []

        # Payment history
        cursor.execute('SELECT date, amount FROM payment_history WHERE customer_id = ?', (customer_id,))
        payment_history = cursor.fetchall()

        total_received_amount = sum(row['amount'] for row in payment_history) if payment_history else 0.0
        offer_discount = customer.get('offer_discount', 0.0)
        final_amount = customer.get('amount', 0.0) - offer_discount
        due_amount = final_amount - total_received_amount

        # Update payment status logic
        if customer.get('adjustment_done'):
            customer['payment_status'] = 'Adjustment'
        elif due_amount <= 0 and customer['payment_status'] not in ('Paid', 'Cancel'):
            cursor.execute('UPDATE customers SET payment_status = ? WHERE id = ?', ('Paid', customer_id))
            conn.commit()
            customer['payment_status'] = 'Paid'
        if customer.get('payment_status') in [None, 'None', ''] or customer['delivery'] == 'NO':
            customer['payment_status'] = 'Unknown'

        # Fetch adjustments related to the customer (both bill_from and bill_to)
        formatted_adjustments = []
        from_customers = {}  # To store payment status for 'bill_from'
        to_customers = {}    # To store payment status for 'bill_to'

        if bill_no:
            cursor.execute('''
                SELECT * FROM adjustments
                WHERE bill_from = ? OR bill_to = ?
            ''', (bill_no, bill_no))
            adjustments = cursor.fetchall()

            for adj in adjustments:
                # For bill_from
                if adj['bill_from'] not in from_customers:
                    cursor.execute('SELECT payment_status FROM customers WHERE billno = ?', (adj['bill_from'],))
                    row = cursor.fetchone()
                    from_customers[adj['bill_from']] = dict(row) if row else {}

                # For bill_to
                if adj['bill_to'] not in to_customers:
                    cursor.execute('SELECT payment_status FROM customers WHERE billno = ?', (adj['bill_to'],))
                    row = cursor.fetchone()
                    to_customers[adj['bill_to']] = dict(row) if row else {}

                # Now, after fetching, you can safely get payment statuses
                from_payment_status = from_customers.get(adj['bill_from'], {}).get('payment_status', 'Not Available')
                to_payment_status = to_customers.get(adj['bill_to'], {}).get('payment_status', 'Not Available')
                
                # Format adjustment details
                description = ""
                if adj['bill_from'] == bill_no:
                    description = f"₹{adj['adjustment_amount']} given to Bill No {adj['bill_to']}"
                    payment_status = to_payment_status  # For 'bill_from', show 'payment_status' of 'bill_to'
                elif adj['bill_to'] == bill_no:
                    description = f"₹{adj['adjustment_amount']} received from Bill No {adj['bill_from']}"
                    payment_status = from_payment_status  # For 'bill_to', show 'payment_status' of 'bill_from'

                formatted_adjustments.append({
                    'date': adj['date'],
                    'bill_from': adj['bill_from'],
                    'bill_to': adj['bill_to'],
                    'amount': adj['amount'],
                    'adjustment_amount': adj['adjustment_amount'],
                    'payment_status': payment_status,  # Add payment status to each adjustment
                    'description': description
                })

        # Inside your render_template call, pass 'formatted_adjustments' as usual
        return render_template(
            'view_customer.html',
            customer=customer,
            additional_mobiles=additional_mobiles,
            payment_history=payment_history,
            total_received_amount=total_received_amount,
            due_amount=due_amount,
            offer_discount=offer_discount,
            final_amount=final_amount,
            adjustments=formatted_adjustments,
            adjustments_message=None,  # If no adjustments, you can set this to None
            from_customers=from_customers,
            to_customers=to_customers
        )

    finally:
        conn.close()

def get_additional_mobiles(customer_id):
    conn = sqlite3.connect('crm.db')
    cursor = conn.cursor()
    
    # Adjust column name based on the actual schema
    cursor.execute("SELECT mobile_number FROM additional_mobiles WHERE customer_id = ?", (customer_id,))
    additional_mobiles = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    return additional_mobiles
    
    # Query to fetch additional mobile numbers based on customer_id
    cursor.execute("SELECT additional_mobile FROM additional_mobiles WHERE customer_id = ?", (customer_id,))
    additional_mobiles = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    return additional_mobiles

def add_state_column():
    try:
        conn = sqlite3.connect('crm.db')
        cursor = conn.cursor()
        cursor.execute('ALTER TABLE customers ADD COLUMN state TEXT NOT NULL DEFAULT ""')
        conn.commit()
    except sqlite3.DatabaseError as e:
        print(f"Database error while adding state column: {e}")
    finally:
        conn.close()

add_state_column()

def get_customer_by_id(customer_id):
    try:
        conn = sqlite3.connect('crm.db')
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(customers)")
        columns = [column[1] for column in cursor.fetchall()]
        
        cursor.execute("SELECT * FROM customers WHERE id = ?", (customer_id,))
        row = cursor.fetchone()
        if row:
            customer = dict(zip(columns, row))
            return customer
        return None
    except sqlite3.DatabaseError as e:
        print(f"Database error: {e}")
        return None
    finally:
        conn.close()
        
from datetime import datetime

@app.route('/edit_customer/<int:customer_id>', methods=['GET', 'POST'])
def edit_customer(customer_id):
    # Check if the user is logged in
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()

    # Fetch the current customer before both GET and POST operations
    current_customer = conn.execute('SELECT * FROM customers WHERE id = ?', (customer_id,)).fetchone()
    if not current_customer:
        conn.close()
        abort(404, description="Customer not found")

    # Fetch distinct categories (excluding empty and 'Manual')
    raw_categories = conn.execute(
        "SELECT DISTINCT category FROM customers WHERE category IS NOT NULL AND TRIM(category) != '' AND category != 'Manual'"
    ).fetchall()
    category_list = [row['category'] for row in raw_categories]

    if request.method == 'POST':
        # Fetch form data
        cancel_order = request.form.get('cancel_order')
        payment_status = 'Cancel' if cancel_order else 'Pending'
        adjustment_done = 1 if request.form.get('adjustment_done') else 0

        khc_code = request.form.get('khccode')
        name = request.form.get('name')
        billno = request.form.get('billno')
        biltyno = request.form.get('biltyno')
        date = request.form.get('date')
        firmname = request.form.get('firmname')
        reference_name = request.form.get('reference_name')
        state = request.form.get('state')
        city = request.form.get('city')
        pincode = request.form.get('pincode')
        mobile = request.form.get('mobile')
        amount = float(request.form.get('amount'))
        delivery = request.form.get('delivery')
        transport_name = request.form.get('transport_name')
        transport_number = request.form.get('transport_number')
        additional_mobiles = request.form.getlist('additional_mobile')
        additional_mobiles_str = ','.join(additional_mobiles)
        district = request.form.get('district')
        tehsil = request.form.get('tehsil')
        offer_discount = float(request.form.get('offer_discount', 0))
        order_status = request.form.get('order_status', 'Pending')
        category = request.form.get('category')

        # Handle manual category input
        if category == 'Manual':
            category = request.form.get('manualCategory', '').strip()
            if not category:
                flash('Please provide a custom category.', 'error')
                return render_template(
                    'edit_customer.html',
                    customer=current_customer,
                    additional_mobiles=additional_mobiles,
                    formatted_date=date,
                    categories=category_list
                )

        # Format the date
        try:
            formatted_date = datetime.strptime(date, '%d/%m/%Y').strftime('%Y-%m-%d')
        except ValueError:
            formatted_date = date

        # Update the customer
        conn.execute('''UPDATE customers SET 
                       khccode = ?, name = ?, billno = ?, biltyno = ?, date = ?, firmname = ?, reference_name = ?, 
                       state = ?, city = ?, pincode = ?, mobile = ?, additional_mobile = ?, 
                       amount = ?, delivery = ?, transport_name = ?, transport_number = ?, 
                       payment_status = ?, offer_discount = ?, delivery_date = ?, order_status = ?, 
                       adjustment_done = ?, category = ?, district = ?, tehsil = ? 
                       WHERE id = ?''',
                     (khc_code, name, billno, biltyno, formatted_date, firmname, reference_name, state,
                      city, pincode, mobile, additional_mobiles_str, amount,
                      delivery, transport_name, transport_number, payment_status, offer_discount,
                      request.form.get('delivery_date'), order_status, adjustment_done, category, district, tehsil, customer_id))

        # Update additional mobiles
        conn.execute("DELETE FROM additional_mobiles WHERE customer_id = ?", (customer_id,))
        for mobile_number in additional_mobiles:
            if mobile_number:
                conn.execute("INSERT INTO additional_mobiles (customer_id, mobile_number) VALUES (?, ?)",
                             (customer_id, mobile_number))

        conn.commit()
        conn.close()
        return redirect(url_for('view_customer', customer_id=customer_id))

    # GET request handling
    # Fetch additional mobiles and extract only the mobile numbers
    additional_mobiles = conn.execute("SELECT mobile_number FROM additional_mobiles WHERE customer_id = ?", (customer_id,)).fetchall()
    additional_mobiles_list = [mobile['mobile_number'] for mobile in additional_mobiles]  # Extract the mobile numbers into a list
    conn.close()

    try:
        formatted_date = datetime.strptime(current_customer['date'], '%Y-%m-%d').strftime('%Y-%m-%d')
    except ValueError:
        formatted_date = current_customer['date']

    return render_template(
        'edit_customer.html',
        customer=current_customer,
        additional_mobiles_list=additional_mobiles_list,  # Pass additional mobiles list
        formatted_date=formatted_date,
        categories=category_list
    )

@app.route('/update_checked_customers', methods=['POST'])
def update_checked_customers():
    conn = get_db_connection()
    
    # Get the list of selected customer IDs (those with checked checkboxes)
    selected_customer_ids = request.form.getlist('customer_ids')
    
    # First, update the selected customers (those with checked checkboxes)
    if selected_customer_ids:
        for customer_id in selected_customer_ids:
            conn.execute('UPDATE customers SET adjustment_done = 1 WHERE id = ?', (customer_id,))
    
    # For customers that are unchecked, set adjustment_done to 0
    # Get the customer IDs for all customers that have adjustment_done set to 1
    all_customer_ids = [customer['id'] for customer in conn.execute('SELECT id FROM customers WHERE adjustment_done = 1').fetchall()]
    unchecked_customer_ids = [str(customer['id']) for customer in conn.execute('SELECT id FROM customers').fetchall() if str(customer['id']) not in selected_customer_ids]
    
    if unchecked_customer_ids:
        for customer_id in unchecked_customer_ids:
            conn.execute('UPDATE customers SET adjustment_done = 0 WHERE id = ?', (customer_id,))
    
    conn.commit()
    conn.close()

    # Redirect to show_checked_customers to display updated list
    return redirect(url_for('show_checked_customers'))

@app.route('/show_checked_customers', methods=['GET'])
def show_checked_customers():
    conn = get_db_connection()
    # Fetch customers with adjustment_done = 1
    customers = conn.execute('SELECT * FROM customers WHERE adjustment_done = 1').fetchall()
    conn.close()

    # Render the page with customers who are marked as checked
    return render_template('show_checked_customers.html', customers=customers)

@app.route('/mark_multiple_checked', methods=['GET', 'POST'])
def mark_multiple_checked():
    conn = get_db_connection()

    if request.method == 'GET':
        # Fetch all customers to display in the form
        customers = conn.execute('SELECT * FROM customers').fetchall()
        conn.close()
        return render_template('mark_multiple_checked.html', customers=customers)

    if request.method == 'POST':
        # Get the list of selected customer IDs from the request (AJAX or form submission)
        selected_customers = request.form.getlist('customer_ids')

        # Update `adjustment_done` for selected customers
        for customer_id in selected_customers:
            conn.execute('UPDATE customers SET adjustment_done = 1 WHERE id = ?', (customer_id,))
        conn.commit()

        conn.close()

        # Redirect to the same page to show the updated status
        return redirect(url_for('mark_multiple_checked'))

@app.route('/update_adjustment_done', methods=['POST'])
def update_adjustment_done():
    # Get customer ID and new state (checked or unchecked)
    customer_id = request.form['customer_id']
    adjustment_done = request.form['adjustment_done'] == 'true'  # 'true' if checked, 'false' if unchecked

    # Update the `adjustment_done` field in the database
    conn = get_db_connection()
    conn.execute('UPDATE customers SET adjustment_done = ? WHERE id = ?', (1 if adjustment_done else 0, customer_id))
    conn.commit()
    conn.close()

    return '', 204  # Return empty response with 204 No Content status

@app.route('/mark_checked/<int:customer_id>', methods=['POST'])
def mark_checked(customer_id):
    conn = get_db_connection()
    # Fetch the current checked status (1 or 0)
    customer = conn.execute('SELECT * FROM customers WHERE id = ?', (customer_id,)).fetchone()

    if customer:
        # Toggle the adjustment_done status (0 to 1, or 1 to 0)
        new_status = 0 if customer['adjustment_done'] == 1 else 1
        conn.execute('UPDATE customers SET adjustment_done = ? WHERE id = ?', (new_status, customer_id))
        conn.commit()

    conn.close()
    return redirect(url_for('show_checked_customers'))

@app.template_filter('format_date')
def format_date(value, format='%d/%m/%Y'):
    if value:
        try:
            # Check if the date is already in yyyy-mm-dd format
            return datetime.strptime(value, '%Y-%m-%d').strftime(format)
        except ValueError:
            # If the date is not in the expected format, handle it
            try:
                return datetime.strptime(value, '%d/%m/%Y').strftime(format)
            except ValueError:
                return value  # If parsing fails, return the original value
    return value

def add_offer_discount_column():
    conn = sqlite3.connect('crm.db')  # Replace with your actual database path
    cursor = conn.cursor()

    # Check if the column exists before trying to add it
    cursor.execute("PRAGMA table_info(customers);")
    columns = [column[1] for column in cursor.fetchall()]  # Extract column names

    if 'offer_discount' not in columns:
        try:
            cursor.execute('''ALTER TABLE customers ADD COLUMN offer_discount DECIMAL(10, 2) DEFAULT 0;''')
            conn.commit()
            print("Column 'offer_discount' added successfully.")
        except sqlite3.OperationalError as e:
            print(f"Error adding column: {e}")
    else:
        print("Column 'offer_discount' already exists.")
    conn.close()

# Call the function to add the column when the app starts
add_offer_discount_column()

@app.route('/generate_khc_code', methods=['GET'])
def generate_khc_code():
    # Example logic to generate a KHC code (replace with your own logic)
    generated_code = f"KHC-{random.randint(1000, 9999)}"
    return jsonify({"khc_code": generated_code})

def update_schema():
    conn = sqlite3.connect('crm.db')  # Replace with your actual database path
    cursor = conn.cursor()

    # Add 'status' column if it doesn't exist
    try:
        cursor.execute('''
            ALTER TABLE customers
            ADD COLUMN status TEXT
        ''')
        print("Column 'status' added successfully.")
    except sqlite3.OperationalError as e:
        print(f"Error: {e}")

    conn.commit()
    conn.close()

update_schema()

@app.route('/add_payment/<int:customer_id>', methods=['POST'])
def add_payment(customer_id):
    if 'username' not in session:
        flash('Please log in to access this page.', 'danger')  # Flash message for unauthenticated access
        return redirect(url_for('login'))  # Redirect to login page

    payment_date = request.form.get('payment_date')
    payment_amount = request.form.get('payment_amount')

    conn = get_db_connection()
    cursor = conn.cursor()

    # Add the new payment entry to the database
    cursor.execute('INSERT INTO payment_history (customer_id, date, amount) VALUES (?, ?, ?)', 
                   (customer_id, payment_date, payment_amount))
    conn.commit()
    conn.close()

    return redirect(url_for('view_customer', customer_id=customer_id))

@app.route('/import_data', methods=['GET', 'POST'])
def import_data():
    if 'username' not in session:
        flash('Please log in to access this page.', 'danger')  # Flash message for unauthenticated access
        return redirect(url_for('login'))  # Redirect to login page

    if request.method == 'POST':
        file = request.files['file']
        if file and file.filename.endswith(('.xls', '.xlsx')):
            # Ensure the directory exists
            upload_dir = 'static/uploads'
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)
            
            file_path = os.path.join(upload_dir, secure_filename(file.filename))
            file.save(file_path)

            try:
                # Read the Excel file
                df = pd.read_excel(file_path, engine='openpyxl')
                
                # Ensure the DataFrame has the required columns
                required_columns = [
                    'khccode', 'billno', 'biltyno', 'date', 'name', 'firmname',
                    'state', 'city', 'pincode', 'mobile', 'amount', 'receive_amount',
                    'delivery', 'payment_status', 'payment_received_date', 'transport_name',
                    'transport_number'
                ]
                
                # Check for missing columns
                missing_columns = [col for col in required_columns if col not in df.columns]
                if missing_columns:
                    raise ValueError(f'Missing columns: {", ".join(missing_columns)}')
                
                # Connect to the SQLite database
                conn = sqlite3.connect('crm.db')
                cursor = conn.cursor()
                
                # Insert data into the database
                for _, row in df.iterrows():
                    cursor.execute('''
                        INSERT INTO customers 
                        (khccode, billno, biltyno, date, name, firmname, state, city, pincode, mobile, amount, receive_amount, delivery, payment_status, payment_received_date, transport_name, transport_number) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        row.get('khccode', ''), row.get('billno', ''), row.get('biltyno', ''), row.get('date', ''), row.get('name', ''), 
                        row.get('firmname', ''), row.get('state', ''), row.get('city', ''), row.get('pincode', ''), row.get('mobile', ''), 
                        float(row.get('amount', 0)), float(row.get('receive_amount', 0)), row.get('delivery', ''), row.get('payment_status', ''), 
                        row.get('payment_received_date', None), row.get('transport_name', ''), row.get('transport_number', '')
                    ))
                conn.commit()
                conn.close()
                
                flash('Data imported successfully', 'success')
            except Exception as e:
                print(f"Error importing data: {e}")
                flash('An error occurred while importing data', 'error')
        
        return redirect(url_for('customers'))
    
    return render_template('import_data.html')

# Ensure the directory exists
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_all_data():
    """Fetch all tables from the database and combine them into a single DataFrame."""
    try:
        conn = sqlite3.connect('crm.db')
        cursor = conn.cursor()

        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]

        all_dataframes = []
        for table in tables:
            try:
                df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
                df.columns = [f"{table}_{col}" for col in df.columns]  # Prefix column names
                all_dataframes.append(df)
            except Exception as e:
                print(f"Error fetching data from table {table}: {e}")
                continue
        
        conn.close()
        return pd.concat(all_dataframes, axis=1) if all_dataframes else pd.DataFrame()
    except Exception as e:
        print(f"Database error: {e}")
        return pd.DataFrame()

@app.route('/export_data')
def export_data():
    if 'username' not in session:
        flash('Please log in to access this page.', 'danger')
        return redirect(url_for('login'))

    try:
        final_df = get_all_data()
        if final_df.empty:
            flash('No data found to export.', 'warning')
            return redirect(url_for('customers'))

        file_path = os.path.join(UPLOAD_FOLDER, 'database_export.xlsx')
        final_df.to_excel(file_path, index=False)
        flash('Data exported successfully', 'success')
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        flash(f"Error exporting data: {e}", 'danger')
        return redirect(url_for('customers'))

@app.route('/export_customers_to_excel')
def export_customers_to_excel():
    if 'username' not in session:
        flash('Please log in to access this page.', 'danger')
        return redirect(url_for('login'))

    try:
        conn = sqlite3.connect('crm.db')
        query = """
            SELECT id, khccode, billno, biltyno, date, firmname, city, mobile, amount,
                   receive_amount, delivery, payment_status, payment_received_date, transport_name,
                   transport_number, bill_image, state, pincode, name, adjustment, customer_adjustment,
                   status, adjustment_amount, additional_mobile, reference_name, offer_discount
            FROM customers;
        """
        df = pd.read_sql_query(query, conn)
        conn.close()

        if 'khccode' not in df.columns:
            flash("Error: 'khccode' column not found in the data.", 'danger')
            return redirect(url_for('customers'))

        df_duplicates = df[df['khccode'].map(df['khccode'].value_counts()) > 1]
        file_path = os.path.join(UPLOAD_FOLDER, "exported_customers_data.xlsx")
        df_duplicates.to_excel(file_path, index=False)

        flash('Customer data exported successfully.', 'success')
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        flash(f"Error exporting customer data: {e}", 'danger')
        return redirect(url_for('customers'))

@app.route('/download_file/<filename>')
def download_file(filename):
    if 'username' not in session:
        flash('Please log in to access this page.', 'danger')  # Flash message for unauthenticated access
        return redirect(url_for('login'))  # Redirect to login page

    try:
        directory = 'static/uploads'
        return send_from_directory(directory, filename, as_attachment=True)
    except Exception as e:
        flash(f"Error downloading file: {e}", 'error')
        return redirect(url_for('customers'))

@app.route('/show_tables')
def show_tables():
    if 'username' not in session:
        flash('Please log in to access this page.', 'danger')  # Flash message for unauthenticated access
        return redirect(url_for('login'))  # Redirect to login page

    try:
        # Connect to the SQLite database
        conn = sqlite3.connect('crm.db')
        cursor = conn.cursor()

        # Query to get the list of tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        # Collect table and column information
        table_info = {}
        for table in tables:
            table_name = table[0]
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            table_info[table_name] = [col[1] for col in columns]

        conn.close()

        # Render the template with table info
        return render_template('show_tables.html', table_info=table_info)

    except Exception as e:
        print(f"Error fetching table info: {e}")
        return "An error occurred while fetching table information."

@app.route('/delete_customer/<int:customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    if 'username' not in session:
        flash('Please log in to access this page.', 'danger')  # Flash message for unauthenticated access
        return redirect(url_for('login'))  # Redirect to login page

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('DELETE FROM customers WHERE id = ?', (customer_id,))
        if cursor.rowcount == 0:  # Check if any row was deleted
            return jsonify({'status': 'error', 'error': 'Customer not found'}), 404
        
        conn.commit()
        return jsonify({'status': 'success'})
    except sqlite3.Error as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500
    finally:
        conn.close()  # Ensure connection is closed

def create_backup():
    if 'username' not in session:
        flash('Please log in to access this page.', 'danger')  # Flash message for unauthenticated access
        return redirect(url_for('login'))  # Redirect to login page

    backup_folder = 'static/backups'
    
    if not os.path.exists(backup_folder):
        os.makedirs(backup_folder)
    
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    backup_file = os.path.join(backup_folder, f'crm_backup_{timestamp}.db')
    
    db_file = 'crm.db'
    
    try:
        with open(db_file, 'rb') as fsrc:
            with open(backup_file, 'wb') as fdst:
                fdst.write(fsrc.read())
        return backup_file
    except Exception as e:
        print(f"Error creating backup: {e}")
        return None


@app.route('/backup_data', methods=['POST'])
def backup_data():
    if 'username' not in session:
        flash('Please log in to access this page.', 'danger')  # Flash message for unauthenticated access
        return redirect(url_for('login'))  # Redirect to login page

    try:
        source_file = 'crm.db'  # Adjust this path
        backup_file = f'static/backups/crm_backup_{datetime.now().strftime("%Y%m%d%H%M%S")}.db'  # Adjust this path
        
        backup_folder = os.path.dirname(backup_file)
        if not os.path.exists(backup_folder):
            os.makedirs(backup_folder)
        
        shutil.copy(source_file, backup_file)
        
        return jsonify({'message': 'Backup successful!'})
    except Exception as e:
        print(e)
        return jsonify({'message': 'Backup failed.'}), 500

@app.route('/restore_database', methods=['POST'])
def restore_database():
    if 'username' not in session:
        flash('Please log in to access this page.', 'danger')  # Flash message for unauthenticated access
        return redirect(url_for('login'))  # Redirect to login page

    if 'file' not in request.files:
        flash('No file part', 'error')
        return redirect(url_for('home'))
    
    file = request.files['file']
    
    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(url_for('home'))
    
    if file and file.filename.endswith('.db'):
        backup_path = os.path.join('static/backups', secure_filename(file.filename))
        
        try:
            file.save(backup_path)
            
            db_path = 'crm.db'
            os.remove(db_path)  # Remove the old database
            shutil.copy(backup_path, db_path)  # Copy the backup as the new database
            
            flash('Database restored successfully', 'success')
            return redirect(url_for('home'))
        except Exception as e:
            print(f"Error restoring database: {e}")
            flash('An error occurred while restoring the database', 'error')
            return redirect(url_for('home'))
        
    flash('Invalid file format', 'error')
    return redirect(url_for('home'))

@app.route('/bill_adjustment')
def bill_adjustment():
    if 'username' not in session:
        flash('Please log in to access this page.', 'danger')  # Flash message for unauthenticated access
        return redirect(url_for('login'))  # Redirect to login page

    db = get_db_connection()
    try:
        bills = db.execute('SELECT DISTINCT billno FROM customers').fetchall()
        bills_list = [{'billno': row['billno']} for row in bills]
    except sqlite3.OperationalError as e:
        return f"Database error: {e}", 500
    finally:
        db.close()
    return render_template('bill_adjustment.html', bills=bills_list)

@app.route('/reverse_adjustment/<int:adjustment_id>', methods=['POST'])
def reverse_adjustment(adjustment_id):
    if 'username' not in session:
        flash('Please log in to access this page.', 'danger')
        return redirect(url_for('login'))

    db = get_db_connection()
    try:
        # Fetch the adjustment record from the database
        adjustment = db.execute('SELECT * FROM adjustments WHERE id = ?', (adjustment_id,)).fetchone()
        if adjustment:
            # Fetch original amounts for the customers involved in the adjustment
            from_bill = adjustment['bill_from']
            to_bill = adjustment['bill_to']
            adjustment_amount = adjustment['adjustment_amount']
            
            # Reverse the adjustment by updating the customers' amounts
            # Increase the "From Bill" amount by the adjustment amount
            db.execute('UPDATE customers SET amount = amount + ? WHERE billno = ?',
                       (adjustment_amount, from_bill))  # Restore amount to "From Bill"
            
            # Decrease the "To Bill" amount by the adjustment amount
            db.execute('UPDATE customers SET amount = amount - ? WHERE billno = ?',
                       (adjustment_amount, to_bill))  # Undo the adjustment from "To Bill"
            
            # Commit the changes to the customers' amounts
            db.commit()

            # Remove the adjustment record from the adjustments table
            db.execute('DELETE FROM adjustments WHERE id = ?', (adjustment_id,))
            db.commit()

            flash('Adjustment reversed successfully, amounts updated.', 'success')
        else:
            flash('Adjustment not found.', 'danger')
    except sqlite3.Error as e:
        flash(f'Database error: {e}', 'danger')
        db.rollback()
    finally:
        db.close()

    return redirect(url_for('bill_adjustment'))

from datetime import datetime

@app.route('/adjust_bills', methods=['POST'])
def adjust_bills():
    if 'username' not in session:
        flash('Please log in to access this page.', 'danger')
        return redirect(url_for('login'))

    data = request.get_json()
    from_bill_no = data['fromBillNo']
    to_bill_no = data['toBillNo']
    adjustment_amount = float(data['adjustmentAmount'])

    db = get_db_connection()
    try:
        # Retrieve current amounts for both bills
        from_bill = db.execute('SELECT amount FROM customers WHERE billno = ?', (from_bill_no,)).fetchone()
        to_bill = db.execute('SELECT amount FROM customers WHERE billno = ?', (to_bill_no,)).fetchone()
        
        if not from_bill or not to_bill:
            return jsonify({"error": "Invalid bill numbers"}), 400

        # Calculate the new amounts
        new_from_amount = from_bill['amount'] - adjustment_amount
        new_to_amount = to_bill['amount'] + adjustment_amount

        if new_from_amount < 0:
            return jsonify({"error": "Insufficient amount in the from bill"}), 400

        # Update the customers table
        db.execute('UPDATE customers SET amount = ? WHERE billno = ?', (new_from_amount, from_bill_no))
        db.execute('UPDATE customers SET amount = ? WHERE billno = ?', (new_to_amount, to_bill_no))

        # Save adjustment record in 'adjustments' table
        db.execute('''
            INSERT INTO adjustments (bill_from, bill_to, amount, date, description, adjustment_amount)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            from_bill_no,
            to_bill_no,
            from_bill['amount'],  # original amount of 'from' bill
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            f"₹{adjustment_amount} adjusted from {from_bill_no} to {to_bill_no}",
            adjustment_amount
        ))

        db.commit()

    except sqlite3.OperationalError as e:
        return jsonify({"error": f"Database error: {e}"}), 500
    finally:
        db.close()

    return jsonify({
        "adjustmentAmount": adjustment_amount,
        "newFromAmount": new_from_amount,
        "newToAmount": new_to_amount
    })

@app.route('/adjustment-records')
def adjustment_records():
    if 'username' not in session:
        flash('Please log in to view records.', 'danger')
        return redirect(url_for('login'))

    db = get_db_connection()
    try:
        records = db.execute('SELECT * FROM adjustments ORDER BY date DESC').fetchall()
    finally:
        db.close()

    return render_template('adjustment_records.html', records=records)


@app.route('/pricelist')
def pricelist():
    return render_template('pricelist.html')

import sqlite3
from datetime import datetime, timedelta

def fetch_sales_data():
    conn = sqlite3.connect('crm.db')
    cursor = conn.cursor()

    # Fetch the start and end date for the entire range (first and last date of the dataset)
    cursor.execute("SELECT MIN(date), MAX(date) FROM customers")
    start_date, end_date = cursor.fetchone()

    # Handle case where no start or end date was found
    if start_date is None or end_date is None:
        print("Error: No valid start or end date found in the database.")
        conn.close()
        return None, None, None, None, None, None

    # Fetch yearly sales data
    cursor.execute("""
        SELECT strftime('%Y', date) AS year, 
               SUM(amount) AS total_sales
        FROM customers 
        GROUP BY year
    """)
    yearly_sales = cursor.fetchall()

    # Fetch monthly sales data
    cursor.execute("SELECT strftime('%Y-%m', date) AS month, SUM(amount) AS total_sales FROM customers GROUP BY month")
    monthly_sales = cursor.fetchall()

    # Fetch weekly sales data
    cursor.execute("""
        SELECT strftime('%Y-%W', date) AS week, SUM(amount) AS total_sales
        FROM customers GROUP BY week
    """)
    weekly_sales = cursor.fetchall()

    # Ensure weekly_sales is always a list, even if no data is found
    if weekly_sales is None:
        weekly_sales = []

    conn.close()

    return yearly_sales, monthly_sales, weekly_sales

@app.route('/report')
def report():
    if 'username' not in session:
        flash('Please log in to access this page.', 'danger')  # Flash message for unauthenticated access
        return redirect(url_for('login'))  # Redirect to login page

    # Fetch sales data (yearly, monthly, weekly) using your function
    yearly_sales, monthly_sales, weekly_sales = fetch_sales_data()

    # Calculate growth percentage and amount growth for yearly sales
    yearly_sales_with_growth = []
    previous_year_sales = None
    for row in yearly_sales:
        year, total_sales = row
        growth_percentage = 0
        amount_growth = 0

        if previous_year_sales is not None:
            # Calculate the growth percentage and amount growth
            growth_percentage = round(((total_sales - previous_year_sales) / previous_year_sales) * 100, 2)
            amount_growth = total_sales - previous_year_sales

        yearly_sales_with_growth.append((year, total_sales, growth_percentage, amount_growth))

        # Set the previous year sales for the next iteration
        previous_year_sales = total_sales

    # Prepare week data from weekly sales
    week_data = {}
    for week_str, total_sales in weekly_sales:
        start_date, end_date = get_week_start_end(week_str)
        if start_date and end_date:
            week_data[week_str] = (start_date, end_date, total_sales)

    # Pass the result to the template
    return render_template('report.html',
                           yearly_sales=yearly_sales_with_growth,
                           monthly_sales=monthly_sales,
                           week_data=week_data)

def get_week_start_end(week_str):
    try:
        # Split the 'YYYY-Www' format into year and week number
        year, week = week_str.split('-')
        week = int(week)
        
        # Calculate the first day of the given week (Monday)
        d = datetime.strptime(f'{year}-W{week}-1', "%Y-W%U-%w")
        start_date = d.strftime('%Y-%m-%d')
        
        # Calculate the last day of the given week (Sunday)
        end_date = (d + timedelta(days=6)).strftime('%Y-%m-%d')
        
        return start_date, end_date
    except Exception as e:
        print(f"Error processing week {week_str}: {e}")
        return None, None  # Return None if there's an error


@app.route('/get_bill_amount/<bill_no>')
def get_bill_amount(bill_no):
    db = get_db_connection()
    try:
        bill = db.execute('SELECT amount FROM customers WHERE billno = ?', (bill_no,)).fetchone()
        amount = bill['amount'] if bill else 0
    except sqlite3.OperationalError as e:
        return jsonify({"amount": 0, "error": f"Database error: {e}"}), 500
    finally:
        db.close()
    return jsonify({'amount': amount})
 

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if 'username' not in session:
        flash('Please log in to access this page.', 'danger')  # Flash message for unauthenticated access
        return redirect(url_for('login'))  # Redirect to login page

    if request.method == 'POST':
        file = request.files['file']
        if file and (file.filename.endswith('.xls') or file.filename.endswith('.xlsx')):
            try:
                # Read the uploaded Excel file directly from memory
                file_data = BytesIO(file.read())
                df = pd.read_excel(file_data)

                # Fill missing values with an empty string or a default value
                df = df.fillna('')

                # Connect to the database
                conn = get_db_connection()
                cursor = conn.cursor()

                # Insert each row of data into the 'customers' table
                for _, row in df.iterrows():
                    cursor.execute(''' 
                        INSERT INTO customers (khccode, billno, biltyno, date, firmname, city, mobile, amount, receive_amount, delivery, 
                                              payment_status, payment_received_date, transport_name, transport_number, bill_image, 
                                              pincode, state, name, status, additional_mobile, reference_name, offer_discount)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (row['khccode'], row['billno'], row['biltyno'], row['date'], row['firmname'], row['city'], row['mobile'], row['amount'],
                          row['receive_amount'], row['delivery'], row['payment_status'], row['payment_received_date'], row['transport_name'],
                          row['transport_number'], row['bill_image'], row['pincode'], row['state'], row['name'], row['status'],
                          row['additional_mobile'], row['reference_name'], row['offer_discount']))

                conn.commit()
                conn.close()

                # Show a success message
                message = "File uploaded and data added to the database successfully!"
            except Exception as e:
                message = f"Error: {str(e)}"
        else:
            message = "Please upload a valid Excel file."

        # Redirect to avoid re-upload on page refresh
        return redirect(url_for('upload_file', message=message))

    # GET request: show the upload page with a success/error message if any
    return render_template('upload.html', message=request.args.get('message'))



@app.route('/delivery_status')
def delivery_status():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Query to fetch the necessary data, including the total_received_amount
    cursor.execute('''
        SELECT c.*, 
            GROUP_CONCAT(am.mobile_number) AS additional_mobiles,
            SUM(amount) AS total_received_amount,
            (c.amount - SUM(amount)) AS due_amount
        FROM customers c
        LEFT JOIN additional_mobiles am ON c.id = am.customer_id
        LEFT JOIN payments p ON c.id = p.customer_id
        WHERE (c.delivery IS NULL OR c.delivery = '' OR LOWER(c.delivery) IN ('no', 'none'))
        AND (c.payment_status != 'Cancel' OR c.payment_status IS NULL)  -- Exclude canceled entries and include unknown payment statuses
        GROUP BY c.id
    ''')

    customers = cursor.fetchall()

    # Calculate the total amount and number of entries
    total_amount = sum(customer['amount'] for customer in customers)
    total_entries = len(customers)

    conn.close()

    # Render the template with the calculated values
    return render_template('delivery/delivery_status.html', 
                           customers=customers,
                           total_amount=total_amount,
                           total_entries=total_entries)

@app.route('/delivery_dashboard')
def delivery_dashboard():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch pending deliveries (if needed for total pending amount/customers)
    cursor.execute('''
        SELECT SUM(amount) AS total_pending_amount, COUNT(*) AS total_pending_customers
        FROM customers c
        WHERE (c.delivery IS NULL OR c.delivery = '' OR LOWER(c.delivery) IN ('no', 'none'))
        AND (c.payment_status != 'Cancel' OR c.payment_status IS NULL)
    ''')

    pending_data = cursor.fetchone()
    total_pending_amount = pending_data['total_pending_amount']
    total_pending_customers = pending_data['total_pending_customers']

    # Fetch the latest delivery date
    cursor.execute('''
        SELECT MAX(delivery_date) AS latest_delivery_date
        FROM customers
        WHERE delivery = 'Yes'
    ''')

    latest_delivery_date = cursor.fetchone()['latest_delivery_date']

    # Fetch the deliveries only for the latest delivery date
    cursor.execute('''
        SELECT id, name, delivery_date, amount, delivery
        FROM customers
        WHERE delivery = 'Yes' AND delivery_date = ?
        ORDER BY delivery_date DESC
    ''', (latest_delivery_date,))

    latest_deliveries = cursor.fetchall()

    conn.close()

    # Render the template with the necessary data
    return render_template('delivery/delivery_dashboard.html', 
                           total_pending_amount=total_pending_amount,
                           total_pending_customers=total_pending_customers,
                           latest_delivery_date=latest_delivery_date,
                           latest_deliveries=latest_deliveries)


@app.route('/delivery/view/<int:customer_id>', methods=['GET'])
def delivery_view(customer_id):
    # Fetch the customer details from the database
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM customers WHERE id = ?', (customer_id,))
    customer = cursor.fetchone()

    if not customer:
        flash('Customer not found', 'error')
        return redirect(url_for('delivery_status'))  # Redirect to the delivery status page if customer not found

    conn.close()

    return render_template('delivery/delivery_view.html', customer=customer)

@app.route('/delivery/edit/<int:customer_id>', methods=['GET', 'POST'])
def delivery_edit(customer_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch the customer details
    cursor.execute('SELECT * FROM customers WHERE id = ?', (customer_id,))
    customer = cursor.fetchone()

    if not customer:
        flash('Customer not found', 'error')
        return redirect(url_for('delivery_status'))

    if request.method == 'POST':
        # Get form data
        delivery_status = request.form['delivery_status']
        delivery_date = request.form.get('delivery_date')  # Optional field
        cancel_order = 'cancel_order' in request.form

        # Update customer delivery status and delivery date
        cursor.execute('''
            UPDATE customers SET
            delivery = ?,
            delivery_date = ?,
            payment_status = ?
            WHERE id = ?
        ''', (delivery_status, delivery_date, 'Cancel' if cancel_order else 'Paid', customer_id))
        conn.commit()

        flash('Customer delivery status updated', 'success')
        return redirect(url_for('delivery_view', customer_id=customer_id))

    conn.close()
    return render_template('delivery/delivery_edit.html', customer=customer)

@app.route('/payment_status', methods=['GET'])
def payment_status():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Query to get customers
    cursor.execute('''SELECT c.id, c.khccode, c.billno, c.biltyno, c.date, c.firmname, c.state, c.city, c.mobile,
                            c.amount, c.receive_amount, (c.amount - c.receive_amount) AS due_amount, c.reference_name, 
                            c.offer_discount, COALESCE(SUM(ph.amount), 0) AS total_received
                    FROM customers c
                    LEFT JOIN payment_history ph ON c.id = ph.customer_id
                    WHERE LOWER(c.payment_status) = "pending" 
                    AND LOWER(c.payment_status) != "cancelled" 
                    AND LOWER(c.delivery) = "yes" 
                    GROUP BY c.id 
                    ORDER BY c.id DESC''')
    customers = cursor.fetchall()

    # Convert sqlite3.Row to dict for easier manipulation
    customers_dict = []
    for customer in customers:
        customer_dict = dict(customer)
        if 'offer_discount' not in customer_dict:
            customer_dict['offer_discount'] = 0  # Default to 0 if the field is missing
        customers_dict.append(customer_dict)

    # Pass the data to the template
    return render_template('payment/payment_status.html', customers=customers_dict)

@app.route('/payment_dashboard', methods=['GET'])
def payment_dashboard():
    total_pending_amount, total_pending_customers, latest_payments = calculate_pending_amount_and_customers(payment_status_filter="pending", delivery_status_filter="yes", latest=True)

    return render_template('payment/payment_dashboard.html', 
                           total_pending_amount=total_pending_amount,
                           total_pending_customers=total_pending_customers,
                           latest_payments=latest_payments)

def calculate_pending_amount_and_customers(payment_status_filter="pending", delivery_status_filter="yes"):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Build the query with dynamic filters for payment and delivery status using '?' placeholders for SQLite
    query = '''
        SELECT * FROM customers 
        WHERE LOWER(payment_status) = ? 
        AND LOWER(payment_status) != "cancelled" 
        AND LOWER(delivery) = ? 
        ORDER BY id DESC
    '''
    cursor.execute(query, (payment_status_filter, delivery_status_filter))  # Use tuple with parameters
    customers = cursor.fetchall()

    # Calculate the total pending amount and total pending customers
    total_pending_amount = sum(customer['amount'] - customer['receive_amount'] for customer in customers)
    total_pending_customers = len(customers)

    conn.close()

    return total_pending_amount, total_pending_customers, customers

@app.route('/payment_view')
def payment_view():
    customer_id = request.args.get('customer_id')  # Get the customer_id from the URL query parameter
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch the customer data for the given customer_id, calculating due_amount directly in SQL
    if customer_id:
        cursor.execute('''
            SELECT *, 
                   (amount - total_received - IFNULL(offer_discount, 0)) AS due_amount
            FROM customers 
            WHERE id = ?
        ''', (customer_id,))
        customer = cursor.fetchone()  # Fetch the specific customer
    else:
        # If no customer_id is provided, fetch all customers (fallback behavior)
        cursor.execute('''
            SELECT *, 
                   (amount - total_received - IFNULL(offer_discount, 0)) AS due_amount
            FROM customers
        ''')
        customer = cursor.fetchall()  # For all customers (you may adjust this as needed)

    conn.close()

    return render_template('payment/payment_view.html', customer=customer)

def add_total_received_column():
    try:
        conn = sqlite3.connect('crm.db')
        cursor = conn.cursor()
        cursor.execute('ALTER TABLE customers ADD COLUMN total_received REAL DEFAULT 0')
        conn.commit()
        print("Column 'total_received' added successfully.")
    except sqlite3.DatabaseError as e:
        print(f"Error adding 'total_received' column: {e}")
    finally:
        conn.close()

# Call this function to add the column
add_total_received_column()


@app.route('/data_upload', methods=['GET', 'POST'])
def data_upload_file():
    # Example: Replace with dynamic customer data as needed
    customer = {'state': 'selected'}  # Default state

    if request.method == 'POST':
        # Get the file from the form
        file = request.files.get('file')

        # Get the state from the form (we will use this as the name)
        state = request.form.get('state')

        # If all the required fields are present, save the file
        if file and state:
            # Use the state as the folder name
            folder_name = state  # Folder name format: State
            folder_path = os.path.join('data', folder_name)  # Folder path where file will be stored

            # Create the folder if it doesn't exist
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)

            # Check if the file is an Excel file
            if file.filename.endswith(('.xlsx', '.xls')):
                # Load the file into a DataFrame using Pandas
                try:
                    data = pd.read_excel(file)

                    # Required columns
                    required_columns = ['firm_name', 'city', 'mobile_no', 'additional_mobile_no']

                    # Check for missing columns and add them if necessary
                    for col in required_columns:
                        if col not in data.columns:
                            data[col] = None  # Add missing columns with empty values

                    # Save the updated DataFrame back to an Excel file
                    file_path = os.path.join(folder_path, file.filename)
                    data.to_excel(file_path, index=False)

                    flash(f'File successfully uploaded and validated. Saved to {file_path}')
                    return redirect(url_for('data_upload_file'))

                except Exception as e:
                    flash(f'Error processing the file: {e}')
                    return redirect(url_for('data_upload_file'))
            else:
                flash('Invalid file type. Please upload a valid Excel file.')
                return redirect(url_for('data_upload_file'))
        else:
            flash('Please provide a state and file.')
            return redirect(url_for('data_upload_file'))

    # Render the HTML form and pass the customer data (state)
    return render_template('data_upload.html', customer=customer)

@app.route('/add_document/<int:customer_id>', methods=['POST'])
def add_document(customer_id):
    # Fetch files from the form
    bill_file = request.files.get('bill_image')
    bilty_file = request.files.get('bilty_image')
    payment_file = request.files.get('payment_image')
    other_documents = request.files.getlist('other_documents')  # Get list of files for "Other Documents"

    # Fetch customer details to get the KHC code and billno
    customer = get_customer_by_id(customer_id)  # Replace with actual DB fetching logic
    khc_code = customer['khccode']  # Assuming customer has a 'khccode'
    billno = customer.get('billno', 'unknown')  # Assuming 'billno' is a field; default to 'unknown' if not present

    # Directory to save files
    upload_folder = os.path.join(app.config['UPLOAD_FOLDER'], khc_code)
    os.makedirs(upload_folder, exist_ok=True)  # Create directory if it doesn't exist

    # Function to save a file with appropriate prefix
    def save_file(file, prefix, index=None):
        if file and allowed_file(file.filename):
            # Get the file extension (image or pdf)
            file_ext = file.filename.rsplit('.', 1)[1].lower()
            # Construct filename using prefix and billno (no old file name)
            if index is not None:
                # Add number to filename if it's not the first file
                filename = f"{prefix}_{billno}_{index}.{file_ext}"
            else:
                filename = f"{prefix}_{billno}.{file_ext}"  # Use only billno if it's a single file
            filepath = os.path.join(upload_folder, filename)
            file.save(filepath)
            return filename  # Return the saved filename
        return None

    # Save files with appropriate prefixes
    bill_filename = None
    if bill_file:
        bill_filename = save_file(bill_file, "bill")
    
    bilty_filename = None
    if bilty_file:
        bilty_filename = save_file(bilty_file, "bilty")

    payment_filename = None
    if payment_file:
        payment_filename = save_file(payment_file, "payment")

    # Save "Other Documents" (Multiple Files)
    other_files = []
    for index, file in enumerate(other_documents, start=1):  # Starting index at 1 for numbering
        file_name = save_file(file, "other", index)
        if file_name:
            other_files.append(file_name)

    # Flash success message
    flash("Documents uploaded successfully!", "success")

    # Redirect to the customer documents view page
    return redirect(url_for('view_customer_documents', customer_id=customer_id))


# Route to view customer documents
@app.route('/view_customer_documents/<int:customer_id>')
def view_customer_documents(customer_id):
    customer = get_customer_by_id(customer_id)  # Fetch customer details
    khc_code = customer['khccode']
    
    # Extract mobile number or an alternative unique identifier
    mobile_number = customer.get('mobile_number', customer.get('name'))

    # Define the folder path where customer documents are stored
    folder_path = os.path.join(app.config['UPLOAD_FOLDER'], khc_code)
    document_files = {}

    if os.path.exists(folder_path):
        for file in os.listdir(folder_path):
            # Assuming the file format is something like 'bill_12345.pdf', extracting the Bill No
            bill_no = file.split('_')[1]  # Extract Bill No. from the filename
            
            # Initialize the dictionary for the bill number if it doesn't exist
            if bill_no not in document_files:
                document_files[bill_no] = {
                    'bill_images': [],
                    'bilty_images': [],
                    'payment_images': [],
                    'other_documents': []  # Added 'other_documents' to hold extra uploads
                }

            # Check file type and categorize based on prefix
            if file.startswith("bill_"):
                document_files[bill_no]['bill_images'].append(file)
            elif file.startswith("bilty_"):
                document_files[bill_no]['bilty_images'].append(file)
            elif file.startswith("payment_"):
                document_files[bill_no]['payment_images'].append(file)
            elif file.startswith("other_"):  # Handle 'other' documents
                document_files[bill_no]['other_documents'].append(file)

    # Render the template and pass the data (customer info and document files)
    return render_template(
        'view_customer_documents.html',
        customer=customer,
        image_files=document_files,  # Passing the variable here
        mobile_number=mobile_number
    )


# Route to serve static files (like PDFs, images) from the uploads folder
@app.route('/serve_file_static/<path:filename>')
def serve_file_static(filename):
    folder_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    return send_from_directory(os.path.dirname(folder_path), os.path.basename(folder_path))

# Initialize BillService instance
bill_service = BillService()
from urllib.parse import unquote

@app.route('/show_bills', methods=['GET'])
def show_bills():
    """
    Route to display bills based on prefix and numeric range filtering,
    with consistent formatting for the `BILL NO.` field and date.
    """
    start = request.args.get('start', default=1, type=int)  # Pagination start
    end = request.args.get('end', default=100, type=int)    # Pagination end
    prefix_filter = request.args.get('prefix', default='', type=str).upper()  # Convert prefix to uppercase
    num_start = request.args.get('num_start', default=None, type=int)  # Start of the numeric range
    num_end = request.args.get('num_end', default=None, type=int)      # End of the numeric range

    # Connect to the database
    conn = sqlite3.connect('crm.db')
    cursor = conn.cursor()

    # Build the SQL query dynamically
    query = '''
        SELECT khccode,
               REPLACE(UPPER(SUBSTR(billno, 1, LENGTH(?))), ' ', '') || '-' || 
               CAST(
                   REPLACE(REPLACE(SUBSTR(billno, LENGTH(?)+1), ' ', ''), '-', '') AS INTEGER
               ) AS formatted_billno,
               firmname, amount,
               strftime('%d/%m/%Y', date) AS formatted_date,  -- Format date as DD/MM/YYYY
               id
        FROM customers
        WHERE 1=1
    '''
    params = [prefix_filter, prefix_filter]

    # Filter by prefix (case-insensitive)
    if prefix_filter and prefix_filter != 'ALL':
        query += '''
            AND UPPER(SUBSTR(billno, 1, LENGTH(?))) = ?
        '''
        params.extend([prefix_filter, prefix_filter])

    # Filter by numeric range
    if num_start is not None and num_end is not None:
        query += '''
            AND CAST(
                REPLACE(REPLACE(
                    SUBSTR(billno, LENGTH(?)+1), ' ', ''
                ), '-', '') AS INTEGER
            ) BETWEEN ? AND ?
        '''
        params.extend([prefix_filter, num_start, num_end])

    # Add ordering and pagination
    query += ' ORDER BY formatted_billno LIMIT ? OFFSET ?'
    params.extend([end - start + 1, start - 1])

    cursor.execute(query, params)
    bill_entries = cursor.fetchall()

    # Predefined prefixes for the dropdown
    prefixes = ['ALL', 'KHC', 'KHCR', 'KT']

    # Close the database connection
    conn.close()

    # Render the template, passing the data
    return render_template('show_bills.html', 
                           bill_entries=bill_entries, 
                           start=start, 
                           end=end, 
                           prefix_filter=prefix_filter, 
                           num_start=num_start, 
                           num_end=num_end, 
                           prefixes=prefixes)

@app.route('/show_bill_details/<bill_id>')
def show_bill_details(bill_id):
    """Route to show detailed information for a specific bill."""
    bill_details = bill_service.get_bill_by_id(bill_id)
    if bill_details:
        return render_template('bill_details.html', bill_details=bill_details)
    else:
        return "Bill not found", 404


@app.route('/update_customer/<customer_id>', methods=['GET', 'POST'])
def update_customer(customer_id):
    # Fetch customer data by customer_id from the database
    customer_data = get_customer_by_id(customer_id)

    if not customer_data:
        return "Customer not found", 404  # Handle case if customer is not found

    # Render the update_customer.html template with customer data
    return render_template('update_customer.html', customer=customer_data)

@app.route('/save_customer_update/<customer_id>', methods=['POST'])
def save_customer_update(customer_id):
    # Fetch the updated data from the form
    updated_name = request.form['customer_name']
    
    # Update customer data in the database
    update_customer_in_db(customer_id, updated_name) # type: ignore

    # Redirect after updating
    return redirect(url_for('customer_list'))


@app.route('/missing_bill_numbers', methods=['GET'])
def find_missing_bill_numbers():
    """Route to find and display missing bill numbers with prefixes."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch all bill numbers from the database
        cursor.execute('SELECT DISTINCT billno FROM customers')  # Ensure unique bill numbers
        rows = cursor.fetchall()

        # Prepare to store bill numbers by prefix
        bill_data = {}
        for row in rows:
            bill = row['billno']
            if bill:
                match = re.match(r'([A-Z]+-\w+-?)(\d+)', bill)  # Match the format PREFIX-NUMBER
                if match:
                    prefix = match.group(1)
                    number = int(match.group(2))
                    if prefix not in bill_data:
                        bill_data[prefix] = []
                    bill_data[prefix].append(number)

        # Process each prefix group to find missing numbers
        results = {}
        for prefix, numbers in bill_data.items():
            sorted_numbers = sorted(set(numbers))  # Remove duplicates and sort
            full_range = set(range(sorted_numbers[0], sorted_numbers[-1] + 1))
            missing_numbers = sorted(full_range - set(sorted_numbers))
            results[prefix] = {
                "existing": [f"{prefix}{num}" for num in sorted_numbers],
                "missing": [f"{prefix}{num}" for num in missing_numbers]
            }

        # Render the results
        return render_template(
            'missing_bills.html',
            results=results
        )
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

from datetime import datetime
from flask import render_template, flash

@app.route('/show_customers_by_delivery_date')
def show_customers_by_delivery_date():
    """Route to show customers ordered by the latest delivery date with today's customers first."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # SQL query to fetch customers with a non-null delivery_date, ordered by the latest delivery date
    query = """
    SELECT id, name, mobile, delivery_date, khccode, billno, biltyno, date, firmname, 
           state, city, mobile, amount, reference_name
    FROM customers 
    WHERE delivery_date IS NOT NULL AND delivery_date != '' 
    ORDER BY STRFTIME('%Y-%m-%d', delivery_date) DESC
    """
    cursor.execute(query)
    customers = cursor.fetchall()

    # Convert the fetched data to a list of dictionaries and format delivery_date to dd/mm/yyyy
    customer_list = []
    today_customers = []  # To store customers with today's delivery date
    for customer in customers:
        # Format the delivery_date using your custom function
        formatted_date = parse_date_with_formats(customer['delivery_date'])
        
        # Convert the customer row to a dictionary and add the formatted delivery date
        customer_dict = dict(customer)
        customer_dict['formatted_delivery_date'] = formatted_date
        
        # Check if the formatted delivery date matches today's date
        if formatted_date:
            try:
                if datetime.strptime(formatted_date, '%d/%m/%Y').date() == datetime.now().date():
                    today_customers.append(customer_dict)  # Append the updated dictionary
            except ValueError:
                pass  # Ignore invalid formatted dates

        customer_list.append(customer_dict)

    # Sort the customer list by delivery date in descending order, placing None values at the end
    customer_list.sort(
        key=lambda x: datetime.strptime(x['formatted_delivery_date'], '%d/%m/%Y') 
        if x['formatted_delivery_date'] else datetime.min,
        reverse=True
    )

    # Get today's date as a string in 'dd/mm/yyyy' format
    current_date = datetime.now().strftime('%d/%m/%Y')

    # Count today's deliveries
    today_count = len(today_customers)

    # If no customers with a delivery date are found, display a message
    if not customer_list:
        flash('No customers found with a delivery date.', 'info')

    # Pass the customer data, today's customers count, and current date to the template
    return render_template(
        'customers_by_delivery_date.html', 
        customers=customer_list, 
        today_customers=today_customers,
        current_date=current_date,
        today_count=today_count  # Pass the count to template
    )

@app.template_filter('parse_date_with_formats')
def parse_date_with_formats(value, format='%d/%m/%Y'):
    if value:
        try:
            # Skip invalid dates like '00/00/00'
            if value in ['00/00/00', '00-00-00']:
                return None  # Return None for invalid dates

            # First, try parsing with '%Y-%m-%d'
            return datetime.strptime(value, '%Y-%m-%d').strftime(format)
        except ValueError:
            try:
                # Then, try parsing with '%d/%m/%Y'
                return datetime.strptime(value, '%d/%m/%Y').strftime(format)
            except ValueError:
                try:
                    # Finally, try parsing with '%d/%m/%y'
                    return datetime.strptime(value, '%d/%m/%y').strftime(format)
                except ValueError:
                    return None  # Return None if all parsing fails
    return None  # Return None for empty values

@app.route('/mark_payment_received', methods=['POST'])
def mark_payment_received():
    payment_id = request.form.get('payment_id')
    
    if not payment_id:
        flash("Invalid payment ID.", "error")
        return redirect(request.referrer)

    try:
        conn = get_db_connection()

        # Update the payment status in the `customers` table
        conn.execute(
            "UPDATE customers SET payment_status = 'paid' WHERE id = ?",
            (payment_id,)
        )
        conn.commit()

        conn.close()

        flash("Payment marked as paid successfully!", "success")

        # Get the user's role (assuming it's stored in session or user data)
        user_role = session.get('user_role')  # You might have a different way of getting the role
        
        if user_role:
            # Dynamically redirect to the correct role-based page
            return redirect(url_for(f'{user_role}_bp.payment_due'))  
        else:
            flash("User role not found.", "error")
            return redirect(request.referrer)

    except sqlite3.DatabaseError as e:
        print(f"Database error: {e}")
        flash("An error occurred while updating the payment status.", "error")
        return redirect(request.referrer)

    except Exception as e:
        print(f"Unexpected error: {e}")
        flash("An unexpected error occurred.", "error")
        return redirect(request.referrer)

@app.route('/paid_payments')
def view_paid_payments():
    conn = get_db_connection()

    # Fetch all paid payments from the `customers` table
    paid_payments = conn.execute(
        "SELECT * FROM customers WHERE payment_status = 'paid'"
    ).fetchall()
    conn.close()

    return render_template(
        'common/paid_payments.html',
        paid_payments=paid_payments
    )

@app.route('/correct_payment', methods=['POST'])
def correct_payment():
    payment_id = request.form.get('payment_id')

    if not payment_id:
        flash("Invalid payment ID.", "error")
        return redirect(url_for('view_paid_payments'))

    try:
        conn = get_db_connection()

        # Update the payment status to "paid"
        conn.execute(
            "UPDATE customers SET payment_status = 'paid' WHERE id = ?",
            (payment_id,)
        )
        conn.commit()
        conn.close()

        flash("Payment marked as correct and status set to paid!", "success")
        return redirect(url_for('view_paid_payments'))

    except sqlite3.DatabaseError as e:
        print(f"Database error: {e}")
        flash("An error occurred while marking the payment as correct.", "error")
        return redirect(url_for('view_paid_payments'))

    except Exception as e:
        print(f"Unexpected error: {e}")
        flash("An unexpected error occurred.", "error")
        return redirect(url_for('view_paid_payments'))


@app.route('/incorrect_payment', methods=['POST'])
def incorrect_payment():
    payment_id = request.form.get('payment_id')

    if not payment_id:
        flash("Invalid payment ID.", "error")
        return redirect(url_for('view_paid_payments'))

    try:
        conn = get_db_connection()

        # Fetch the payment to ensure it exists and check if it's marked as 'paid'
        payment = conn.execute(
            "SELECT * FROM customers WHERE id = ?",
            (payment_id,)
        ).fetchone()

        if not payment:
            flash("Payment not found.", "error")
            return redirect(url_for('view_paid_payments'))

        if payment['payment_status'] == 'paid':
            # If it's paid, mark it as incorrect and update the status to 'pending'
            conn.execute(
                "UPDATE customers SET payment_status = 'pending' WHERE id = ?",
                (payment_id,)
            )
            conn.commit()
            flash("Payment marked as incorrect and status reverted to pending!", "success")
        else:
            flash("The payment is already marked as incorrect or not paid.", "error")
        
        conn.close()
        return redirect(url_for('view_paid_payments'))

    except sqlite3.DatabaseError as e:
        print(f"Database error: {e}")
        flash("An error occurred while marking the payment as incorrect.", "error")
        return redirect(url_for('view_paid_payments'))

    except Exception as e:
        print(f"Unexpected error: {e}")
        flash("An unexpected error occurred.", "error")
        return redirect(url_for('view_paid_payments'))


@app.route('/manage_payments')
def manage_payments():
    conn = get_db_connection()

    # Fetch all paid payments from the `customers` table
    paid_payments = conn.execute(
        "SELECT * FROM customers WHERE payment_status = 'paid'"
    ).fetchall()

    # Fetch all incorrect (pending) payments from the `customers` table
    incorrect_payments = conn.execute(
        "SELECT * FROM customers WHERE payment_status = 'pending'"
    ).fetchall()
    
    conn.close()

    return render_template(
        'common/manage_payments.html',
        paid_payments=paid_payments,
        incorrect_payments=incorrect_payments
    )

@app.route('/toggle_payment_status', methods=['POST'])
def toggle_payment_status():
    payment_id = request.form.get('payment_id')

    if not payment_id:
        flash("Invalid payment ID.", "error")
        return redirect(url_for('manage_payments'))

    try:
        conn = get_db_connection()

        # Fetch the payment to ensure it exists and check the current status
        payment = conn.execute(
            "SELECT * FROM customers WHERE id = ?",
            (payment_id,)
        ).fetchone()

        if not payment:
            flash("Payment not found.", "error")
            return redirect(url_for('manage_payments'))

        if payment['payment_status'] == 'paid':
            # If it's paid, mark it as incorrect (set status to 'pending')
            conn.execute(
                "UPDATE customers SET payment_status = 'pending' WHERE id = ?",
                (payment_id,)
            )
            flash("Payment status reverted to pending.", "success")
        else:
            # If it's not paid, mark it as paid
            conn.execute(
                "UPDATE customers SET payment_status = 'paid' WHERE id = ?",
                (payment_id,)
            )
            flash("Payment status updated to paid.", "success")

        conn.commit()
        conn.close()

        return redirect(url_for('manage_payments'))

    except sqlite3.DatabaseError as e:
        print(f"Database error: {e}")
        flash("An error occurred while updating the payment status.", "error")
        return redirect(url_for('manage_payments'))

    except Exception as e:
        print(f"Unexpected error: {e}")
        flash("An unexpected error occurred.", "error")
        return redirect(url_for('manage_payments'))

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, render_template, flash, redirect, url_for, session
import random
import string
import sqlite3
import os
import csv
from datetime import datetime

# Global list to track regenerated entries
regenerated_entries_file = 'regenerated_entries_log.csv'

# Ensure the log file exists with appropriate headers
if not os.path.exists(regenerated_entries_file):
    with open(regenerated_entries_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['ID', 'Old KHC Code', 'New KHC Code', 'Mobile', 'Bill No', 'Firm Name', 'State', 'City', 'Amount', 'Timestamp'])

# Create a scheduler
scheduler = BackgroundScheduler()

def auto_check_for_duplicates():
    """Schedule a task to check for duplicates every hour."""
    with app.app_context():
        view_duplicates()

# Schedule the task to run at a specific interval (e.g., every hour)
scheduler.add_job(auto_check_for_duplicates, 'interval', hours=1)

# Start the scheduler
scheduler.start()

def generate_unique_khccode(cursor):
    """Helper function to generate a unique khccode."""
    existing_codes = set(row[0] for row in cursor.execute("SELECT khccode FROM customers").fetchall())
    while True:
        new_khccode = "KHC" + ''.join(random.choices(string.digits, k=4))
        if new_khccode not in existing_codes:
            return new_khccode

@app.route('/regenerate_entry/<int:entry_id>', methods=['POST'])
def regenerate_entry(entry_id):
    if 'username' not in session:
        flash('Please log in to access this page.', 'danger')
        return redirect(url_for('login'))

    try:
        conn = sqlite3.connect('crm.db')
        cursor = conn.cursor()

        # Fetch the current `khccode` and other data for the given entry
        cursor.execute("SELECT id, khccode, mobile, billno, firmname, state, city, amount FROM customers WHERE id = ?", (entry_id,))
        result = cursor.fetchone()
        if not result:
            flash(f"Entry with ID {entry_id} does not exist.", 'danger')
            return redirect(url_for('view_duplicates'))

        old_khccode = result[1]

        # Generate a new unique `khccode`
        new_khccode = generate_unique_khccode(cursor)

        # Update the database with the new `khccode`
        cursor.execute("UPDATE customers SET khccode = ? WHERE id = ?", (new_khccode, entry_id))
        conn.commit()

        # Append the regenerated entry to the CSV file
        with open(regenerated_entries_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([ 
                result[0],  # ID
                old_khccode,
                new_khccode,
                result[2],  # Mobile
                result[3],  # Bill No
                result[4],  # Firm Name
                result[5],  # State
                result[6],  # City
                result[7],  # Amount
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Timestamp
            ])

        flash(f"Successfully regenerated 'khccode' for entry ID {entry_id}: {old_khccode} → {new_khccode}", 'success')
    except Exception as e:
        flash(f"An error occurred while regenerating 'khccode': {e}", 'danger')
    finally:
        conn.close()

    return redirect(url_for('view_duplicates'))

@app.route('/view_duplicates')
def view_duplicates():
    """View all customer entries that might be duplicates."""
    try:
        conn = sqlite3.connect('crm.db')
        cursor = conn.cursor()

        # Example query to find duplicates based on `mobile` number
        cursor.execute("SELECT id, khccode, mobile, billno, firmname, state, city, amount FROM customers GROUP BY mobile HAVING COUNT(mobile) > 1")
        duplicates = cursor.fetchall()
        return render_template('view_duplicates.html', duplicates=duplicates)
    except Exception as e:
        flash(f"Error fetching duplicates: {e}", 'danger')
        return redirect(url_for('index'))
    finally:
        conn.close()



@app.route('/update_entry', methods=['POST'])
def update_entry():
    if 'username' not in session:
        flash('Please log in to access this page.', 'danger')
        return redirect(url_for('login'))

    try:
        conn = sqlite3.connect('crm.db')
        cursor = conn.cursor()

        # Get form data (assuming it's from a form submission)
        entry_id = request.form.get('entry_id')
        mobile_numbers = request.form.get('mobile').split('\n')  # Handle multiple mobile numbers
        firm_name = request.form.get('firm_name')
        amount = request.form.get('amount')
        reference_name = request.form.get('reference_name')

        # Check for any existing entry with the same mobile numbers
        cursor.execute("SELECT khccode FROM customers WHERE mobile IN (?)", (",".join(mobile_numbers),))
        existing_codes = cursor.fetchall()

        if existing_codes:
            # Reuse the first found khccode for all mobile numbers
            new_khccode = existing_codes[0][0]
        else:
            # Generate a new unique 'khccode' if no match is found
            new_khccode = generate_unique_khccode(cursor)

        # Update the database with the new `khccode` for the current entry
        cursor.execute("UPDATE customers SET khccode = ?, firmname = ?, amount = ?, reference_name = ? WHERE id = ?",
                       (new_khccode, firm_name, amount, reference_name, entry_id))
        conn.commit()

        flash(f"Entry updated successfully with KHC Code: {new_khccode}", 'success')

    except Exception as e:
        flash(f"An error occurred: {e}", 'danger')

    finally:
        conn.close()

    return redirect(url_for('view_duplicates'))

@app.route('/check_for_updates')
def check_for_updates():
    try:
        conn = sqlite3.connect('crm.db')
        cursor = conn.cursor()

        # Fetch all customers from the database
        cursor.execute("SELECT id, khccode, mobile, billno, firmname, state, city, amount FROM customers")
        rows = cursor.fetchall()

        updated = False  # Flag to track if any update has been made

        for row in rows:
            entry_id = row[0]
            old_khccode = row[1]

            # Check if this khccode has duplicates (based on your logic)
            cursor.execute(""" 
                SELECT COUNT(*) FROM customers 
                WHERE khccode = ? AND mobile != ?
            """, (old_khccode, row[2]))  # Ensure it's a duplicate by checking different mobile numbers
            duplicate_count = cursor.fetchone()[0]

            if duplicate_count > 0:
                # Generate a new unique khccode
                new_khccode = generate_unique_khccode(cursor)

                # Update the database with the new khccode
                cursor.execute("UPDATE customers SET khccode = ? WHERE id = ?", (new_khccode, entry_id))
                conn.commit()

                # Mark that the database has been updated
                updated = True

                # Log the change in the CSV file
                with open(regenerated_entries_file, mode='a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow([
                        entry_id,  # ID
                        old_khccode,
                        new_khccode,
                        row[2],  # Mobile
                        row[3],  # Bill No
                        row[4],  # Firm Name
                        row[5],  # State
                        row[6],  # City
                        row[7],  # Amount
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Timestamp
                    ])

        conn.close()

        if updated:
            return {'status': 'updated'}, 200  # If any update has been made
        else:
            return {'status': 'no_changes'}, 200  # No changes were made
    except Exception as e:
        return {'status': 'error', 'message': str(e)}, 500


@app.route('/customer_details_and_score/<int:customer_id>')
def customer_details(customer_id):
    # Assuming you have a function `get_customer_details_and_score`
    customer, score = get_customer_details_and_score(customer_id)

    if customer is None:
        flash("Customer not found.")
        return redirect(url_for('home'))  # Redirect to home or error page

    # Pass the customer details and score to the template
    return render_template('customer_details_and_score.html', customer=customer, score=score)

@app.route('/download_custom_excel_report')
def download_custom_excel_report():
    week_start_date = request.args.get('week_start_date')
    
    # Convert the week_start_date to a datetime object
    start_date = datetime.strptime(week_start_date, "%Y-%m-%d")
    
    # Calculate the end_date by adding 6 days to the start_date
    end_date = start_date + timedelta(days=6)
    
    # Fetch the data for the selected week
    entries = get_weekly_entries_for_week(start_date, end_date)
    
    # Convert sqlite3.Row objects to dictionaries
    entries = [dict(entry) for entry in entries]
    
    # Combine 'mobile' and 'additional_mobile' and format 'date'
    for entry in entries:
        mobile = entry.get('mobile', '')
        additional_mobile = entry.get('additional_mobile', '')
        entry['mobile'] = f"{mobile} / {additional_mobile}".strip(" /")
        
        if 'date' in entry and entry['date']:
            entry['date'] = datetime.strptime(entry['date'], "%Y-%m-%d").strftime("%m/%d/%Y")
        
        # Extract numeric part from 'billno'
        if 'billno' in entry and entry['billno']:
            entry['billno_numeric'] = int(''.join(filter(str.isdigit, entry['billno'])))
        else:
            entry['billno_numeric'] = float('inf')  # Assign high value if billno is missing or non-numeric
    
    # Sort entries by 'billno_numeric'
    entries = sorted(entries, key=lambda x: x['billno_numeric'])
    
    # Define the final column order and names
    selected_columns = [
        ('khccode', 'KHC Code'),
        ('billno', 'Bill No'),
        ('biltyno', 'Bilty No'),
        ('date', 'Date'),
        ('firmname', 'Firm Name'),
        ('state', 'State'),
        ('city', 'City'),
        ('mobile', 'Mobile No'),
        ('amount', 'Amount'),
        ('extra', 'Extra')
    ]
    
    # Reformat entries with the desired column order and names
    formatted_entries = [
        {display_name: entry.get(column_name, '') for column_name, display_name in selected_columns}
        for entry in entries
    ]
    
    # Create a DataFrame with the new column names and order
    df = pd.DataFrame(formatted_entries, columns=[display_name for _, display_name in selected_columns])
    
    # Create a new Excel file in memory
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Weekly Entries')
    
    output.seek(0)
    
    # Create a custom filename
    filename = f"Weekly_Entries_{start_date.strftime('%Y-%m-%d')}.xlsx"
    
    # Return the file for download
    return send_file(output, as_attachment=True, download_name=filename, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@app.route('/update_reference', methods=['GET', 'POST'])
def update_reference():
    if request.method == 'POST':
        # Get the selected bills and the new reference name
        selected_bills = request.form.getlist('billno')  # List of selected bill numbers
        new_reference = request.form['reference_name']
        
        # Update the reference name for selected bills in the database
        if selected_bills:
            conn = get_db_connection()
            cursor = conn.cursor()
            for billno in selected_bills:
                cursor.execute('''UPDATE customers 
                                  SET reference_name = ? 
                                  WHERE billno = ?''', (new_reference, billno))
            conn.commit()
            conn.close()
            return redirect(url_for('update_reference'))  # Redirect to refresh the page
    
    # Fetch all bills (or relevant data) to display in the form
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT billno FROM customers')
    bills = cursor.fetchall()
    conn.close()

    return render_template('update_reference.html', bills=bills)

@app.route('/search_bills', methods=['GET'])
def search_bills():
    query = request.args.get('query', '')  # Get the search query parameter
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # SQL query to search for bills based on the query string (using LIKE for partial matches)
    cursor.execute('SELECT DISTINCT billno FROM customers WHERE billno LIKE ?', ('%' + query + '%',))
    bills = cursor.fetchall()
    
    conn.close()

    # Return the matching bills as JSON
    return jsonify([bill['billno'] for bill in bills])


@app.route('/issues_dashboard')
def issues_dashboard():
    # Sample data; replace this with actual database query results.
    issues = [
        {"name": "Database Error", "description": "Cannot connect to the database.", "location": "Database Server", "timestamp": "2025-01-01 10:15:00"},
        {"name": "API Failure", "description": "Timeout in API response.", "location": "Backend Server", "timestamp": "2025-01-01 11:00:00"},
    ]
    return render_template('issues_dashboard.html', issues=issues)

# Sample issue-to-solution mapping
ISSUE_SOLUTIONS = {
    "Database Error": [
        "Verify the database connection settings in the application configuration file.",
        "Ensure the database file 'crm.db' exists in the correct directory and has appropriate read/write permissions.",
        "Test database connectivity manually using SQLite CLI or a GUI tool.",
        "Check logs for error messages and enable DEBUG mode in Flask to get detailed traces.",
        "Restart the application after verifying the configuration."
    ],
    "API Failure": [
        "Check the API endpoint URL and ensure it is reachable from the application server.",
        "Verify the API server is running and not experiencing downtime.",
        "Inspect API request parameters and ensure they match the API's requirements.",
        "Use tools like Postman or curl to manually test the API.",
        "Handle API timeouts in the application with appropriate retry mechanisms."
    ]
}

@app.route('/issue_solutions', methods=['POST'])
def get_solution():
    logging.info("POST request to /issue_solutions received")
    issue = request.json.get('issue')
    solution = ISSUE_SOLUTIONS.get(issue, ["Solution not found. Please report this issue."])
    return jsonify({"solution": solution})

@app.route('/grouped_bill_numbers')
def show_grouped_bill_numbers():
    conn = get_db_connection()
    cursor = conn.cursor()

    # SQL query to fetch bill numbers from the 'customers' table
    cursor.execute('SELECT billno FROM customers')
    bills = cursor.fetchall()

    # Group the bill numbers by firm name based on the prefix in the billno
    grouped_bills = {
        'KHC': [],
        'KHCR': [],
        'KT': []
    }

    # Populate the grouped bills dictionary
    for bill in bills:
        billno = bill[0]  # billno is the first value
        if billno.startswith('KHC-'):
            grouped_bills['KHC'].append(int(billno.split('-')[1]))
        elif billno.startswith('KHCR-'):
            grouped_bills['KHCR'].append(int(billno.split('-')[1]))
        elif billno.startswith('KT-'):
            grouped_bills['KT'].append(int(billno.split('-')[1]))

    # Define the valid range for KHC bills between 460 and 1910
    valid_khc_range = set(range(460, 1910 + 1))  # From KHC-460 to KHC-1910
    valid_khcr_range = set(range(1, 48)).union(set(range(1001, 2081)))
    valid_kt_range = set(range(1, 973 + 1))

    # Function to find missing bills based on a valid range
    def find_missing_bills(existing_bills, valid_range):
        existing_bills = sorted(existing_bills)
        missing_bills = sorted(valid_range - set(existing_bills))
        return missing_bills

    # Find missing bills for each firm
    missing_bills = {
        'KHC': find_missing_bills(grouped_bills['KHC'], valid_khc_range),
        'KHCR': find_missing_bills(grouped_bills['KHCR'], valid_khcr_range),
        'KT': find_missing_bills(grouped_bills['KT'], valid_kt_range)
    }

    # Update the grouped_bills to include both existing and missing bills
    for firm in grouped_bills:
        grouped_bills[firm] = {
            'existing': sorted(grouped_bills[firm]),
            'missing': missing_bills[firm]
        }

    # Count the missing bills for each firm
    missing_counts = {firm: len(data['missing']) for firm, data in grouped_bills.items()}

    # Grand total calculation
    grand_total_existing = sum(len(data['existing']) for data in grouped_bills.values())
    grand_total_missing = sum(missing_counts.values())
    grand_total_combined = grand_total_existing + grand_total_missing

    return render_template('grouped_bill_numbers.html', 
                           grouped_bills=grouped_bills, 
                           missing_counts=missing_counts,
                           grand_total_existing=grand_total_existing,
                           grand_total_missing=grand_total_missing,
                           grand_total_combined=grand_total_combined)

@app.route('/show_duplicate_billnos')
def show_duplicate_billnos():
    """Route to show records with duplicate billno."""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Query to find billnos that appear more than once
    cursor.execute('''
        SELECT billno, COUNT(*) as count 
        FROM customers 
        GROUP BY billno 
        HAVING count > 1
    ''')
    duplicate_billnos = cursor.fetchall()
    
    if duplicate_billnos:
        # For each duplicate billno, fetch the associated records
        all_duplicates = {}
        for billno, _ in duplicate_billnos:
            cursor.execute('''
                SELECT id, billno, name, date, khccode, mobile 
                FROM customers WHERE billno = ?
            ''', (billno,))
            all_duplicates[billno] = cursor.fetchall()
        
        conn.close()
        return render_template('show_duplicates.html', all_duplicates=all_duplicates)
    else:
        conn.close()
        # Directly display the message if no duplicates are found
        return render_template('show_duplicates.html', message="No duplicate Bill Nos found.")

def get_db_connection():
    if 'db_conn' not in g:
        g.db_conn = sqlite3.connect('crm.db')
        g.db_conn.row_factory = sqlite3.Row  # To return rows as dictionaries
    return g.db_conn

@app.teardown_appcontext
def close_db_connection(exception):
    db_conn = g.pop('db_conn', None)
    if db_conn is not None:
        db_conn.close()

# Path to the recent searches file
RECENT_SEARCHES_FILE = 'recent_searches.txt'

# Save search queries to the recent searches file
def save_recent_search(query):
    if os.path.exists(RECENT_SEARCHES_FILE):
        with open(RECENT_SEARCHES_FILE, 'r') as file:
            recent_searches = file.readlines()
    else:
        recent_searches = []

    # Remove duplicates and ensure query is unique
    recent_searches = list(set([line.strip() for line in recent_searches]))

    if query and query not in recent_searches:
        recent_searches.insert(0, query)

    with open(RECENT_SEARCHES_FILE, 'w') as file:
        for search in recent_searches:
            file.write(f"{search}\n")

# Get recent searches
def get_recent_searches():
    if os.path.exists(RECENT_SEARCHES_FILE):
        with open(RECENT_SEARCHES_FILE, 'r') as file:
            return [line.strip() for line in file.readlines()]
    return []

import re

def normalize_text(text):
    # Allow hyphens by excluding them from removal (commas and other punctuation are removed)
    text = re.sub(r'[^\w\s-]', '', text)
    return " ".join(text.split()).upper()

def create_normalized_field(row):
    # Combine fields that are relevant for search
    combined = f"{row['id']} {row['khccode']} {row['billno']} {row['name']} ..."
    return normalize_text(combined)

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '').strip()
    results = []
    message = ''

    if query:
        # Normalize query: keep hyphens but remove commas/other punctuation, then convert to upper-case.
        normalized_query = normalize_text(query)
        # Split into words, regardless of order.
        words = normalized_query.split()  # e.g. ["KHC-3164", "KORBA"]

        conn = get_db_connection()

        # List of fields to search; each field is normalized by removing commas and upper-casing.
        fields = [
            "REPLACE(UPPER(id), ',', '')",
            "REPLACE(UPPER(khccode), ',', '')",
            "REPLACE(UPPER(billno), ',', '')",
            "REPLACE(UPPER(biltyno), ',', '')",
            "REPLACE(UPPER(date), ',', '')",
            "REPLACE(UPPER(firmname), ',', '')",
            "REPLACE(UPPER(city), ',', '')",
            "REPLACE(UPPER(state), ',', '')",
            "REPLACE(UPPER(mobile), ',', '')",
            "REPLACE(UPPER(amount), ',', '')",
            "REPLACE(UPPER(receive_amount), ',', '')",
            "REPLACE(UPPER(payment_status), ',', '')",
            "REPLACE(UPPER(payment_received_date), ',', '')",
            "REPLACE(UPPER(transport_name), ',', '')",
            "REPLACE(UPPER(transport_number), ',', '')",
            "REPLACE(UPPER(bill_image), ',', '')",
            "REPLACE(UPPER(bilty_image), ',', '')",
            "REPLACE(UPPER(pincode), ',', '')",
            "REPLACE(UPPER(status), ',', '')",
            "REPLACE(UPPER(additional_mobile), ',', '')",
            "REPLACE(UPPER(reference_name), ',', '')",
            "REPLACE(UPPER(offer_discount), ',', '')",
            "REPLACE(UPPER(order_status), ',', '')",
            "REPLACE(UPPER(name), ',', '')"
        ]

        # Build WHERE clause: for each word, at least one field must match it.
        where_conditions = []
        where_params = []
        for word in words:
            conditions_for_word = []
            for field in fields:
                conditions_for_word.append(f"{field} LIKE ?")
                where_params.append(f"%{word}%")
            where_conditions.append("(" + " OR ".join(conditions_for_word) + ")")
        # All words must be present
        where_clause = " AND ".join(where_conditions)

        # Build scoring expression to rank results based on how many fields match each word.
        score_expressions = []
        score_params = []
        for word in words:
            for field in fields:
                score_expressions.append(f"(CASE WHEN {field} LIKE ? THEN 1 ELSE 0 END)")
                score_params.append(f"%{word}%")
        score_expr = " + ".join(score_expressions)

        # Final query: records must match all words regardless of order.
        dynamic_query = f"""
            SELECT *, ({score_expr}) as score 
            FROM customers 
            WHERE {where_clause}
            ORDER BY score DESC
        """
        # Combine parameters: first for score expressions, then for the WHERE clause.
        params = tuple(score_params + where_params)

        results = conn.execute(dynamic_query, params).fetchall()

        if results:
            message = f'Search Results for "{query}"'
        else:
            message = f'No results found for "{query}".'
    else:
        message = 'Please enter a search query.'

    return jsonify({
        'message': message,
        'results': [dict(row) for row in results]
    })

@app.route('/search_suggestions', methods=['GET'])
def search_suggestions():
    query = request.args.get('query', '').strip()
    normalized_query = normalize_text(query).upper()
    suggestions = []

    if query:
        # Save the original search query if desired
        save_recent_search(query)

        recent_searches = get_recent_searches()
        suggestions = [s for s in recent_searches if s.lower().startswith(query.lower())]

        conn = get_db_connection()

        columns = [
            'id', 'khccode', 'billno', 'biltyno', 'date', 'firmname', 'city', 'state', 'mobile', 
            'amount', 'receive_amount', 'payment_status', 'payment_received_date', 'transport_name',
            'transport_number', 'bill_image', 'bilty_image', 'pincode', 'status', 'additional_mobile', 
            'reference_name', 'offer_discount', 'order_status', 'name'
        ]
        
        for column in columns:
            column_suggestions = conn.execute(
                f"SELECT DISTINCT {column} FROM customers WHERE REPLACE(UPPER({column}), ',', '') LIKE ?", 
                (f"%{normalized_query}%",)
            ).fetchall()
            
            for suggestion in column_suggestions:
                suggestions.append(suggestion[0])
                
    return jsonify(suggestions=suggestions)

@app.route('/order_statistics')
def order_statistics():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Query to count total customer entries (including both new and repeat)
    total_entries_query = '''
        SELECT COUNT(*) AS total_entries
        FROM customers
        WHERE mobile NOT LIKE '0%' 
        AND mobile NOT LIKE '%000000%' 
        AND LENGTH(mobile) > 5
    '''
    cursor.execute(total_entries_query)
    total_entries = cursor.fetchone()[0]

    # Query to count distinct repeat customers (those who have placed more than one order)
    total_repeat_customers_query = '''
        SELECT COUNT(DISTINCT mobile) AS total_repeat_customers
        FROM customers
        WHERE mobile IN (
            SELECT mobile
            FROM customers
            GROUP BY mobile
            HAVING COUNT(mobile) > 1
        )
        AND mobile NOT LIKE '0%' 
        AND mobile NOT LIKE '%000000%' 
        AND LENGTH(mobile) > 5
    '''
    cursor.execute(total_repeat_customers_query)
    total_repeat_customers = cursor.fetchone()[0]

    # Query for repeat orders (customers with more than 1 order)
    repeat_query = '''
        SELECT COUNT(mobile) AS repeat_orders
        FROM customers
        WHERE mobile IN (
            SELECT mobile
            FROM customers
            GROUP BY mobile
            HAVING COUNT(mobile) > 1
        )
        AND mobile NOT LIKE '0%' 
        AND mobile NOT LIKE '%000000%' 
        AND LENGTH(mobile) > 5
    '''
    cursor.execute(repeat_query)
    repeat_orders = cursor.fetchone()[0]

    # Query for new orders (customers with exactly 1 order)
    new_query = '''
        SELECT COUNT(DISTINCT mobile) AS new_orders
        FROM customers
        WHERE mobile IN (
            SELECT mobile
            FROM customers
            GROUP BY mobile
            HAVING COUNT(mobile) = 1
        )
        AND mobile NOT LIKE '0%' 
        AND mobile NOT LIKE '%000000%' 
        AND LENGTH(mobile) > 5
    '''
    cursor.execute(new_query)
    new_orders = cursor.fetchone()[0]

    # Query to get count of customers grouped by appearance frequency and year
    appearance_query = '''
        SELECT strftime('%Y', date) AS year, frequency, COUNT(*) AS count_of_customers
        FROM (
            SELECT mobile, COUNT(mobile) AS frequency, MIN(date) AS date
            FROM customers
            WHERE mobile NOT LIKE '0%' 
            AND mobile NOT LIKE '%000000%' 
            AND LENGTH(mobile) > 5
            AND date IS NOT NULL
            AND date != ''
            GROUP BY mobile
        ) AS frequency_data
        GROUP BY year, frequency
        ORDER BY year, frequency
    '''
    cursor.execute(appearance_query)
    appearance_data = cursor.fetchall()

    # Consolidate data for all years and frequencies in a dictionary
    consolidated_data = {}
    for row in appearance_data:
        year = row[0]
        frequency = row[1]
        count_of_customers = row[2]
        if year not in consolidated_data:
            consolidated_data[year] = {}
        consolidated_data[year][frequency] = count_of_customers

    # Sort data by year and frequency
    appearance_data_sorted = []
    for year, frequencies in sorted(consolidated_data.items()):
        for frequency, count in sorted(frequencies.items()):
            appearance_data_sorted.append({
                "year": year,
                "frequency": frequency,
                "count_of_customers": count
            })

    conn.close()

    return render_template(
        'order_statistics.html',
        total_entries=total_entries,  # Total entries in the customers table
        repeat_orders=repeat_orders,
        total_repeat_customers=total_repeat_customers,  # Total repeat customers
        new_orders=new_orders,
        appearance_data=appearance_data_sorted
    )

@app.route('/bill_and_delivery', methods=['GET', 'POST'])
def bill_and_delivery():
    if 'selected_bills' not in session:
        session['selected_bills'] = []

    try:
        conn = sqlite3.connect('crm.db')
        cursor = conn.cursor()

        # Query all customers for dropdown
        cursor.execute('''
            SELECT khccode, billno, biltyno, date, firmname, city, state, mobile, amount, reference_name 
            FROM customers
        ''')
        customers = cursor.fetchall()

        if request.method == 'POST':
            if 'bill_no' in request.form:  # Select a new bill
                bill_no = request.form['bill_no']
                cursor.execute(''' 
                    SELECT khccode, billno, biltyno, date, firmname, city, state, mobile, amount, reference_name 
                    FROM customers WHERE billno = ?
                ''', (bill_no,))
                selected_bill = cursor.fetchone()

                # Add bill to session if not already added
                if selected_bill and selected_bill not in session['selected_bills']:
                    session['selected_bills'].append(selected_bill)

            elif 'remove_bill_no' in request.form:  # Remove a bill from session
                bill_no_to_remove = request.form['remove_bill_no']
                # Remove the selected bill from the session list
                session['selected_bills'] = [bill for bill in session['selected_bills'] if bill[1] != bill_no_to_remove]

            session.modified = True

    except sqlite3.Error as e:
        flash(f"An error occurred: {e}", "danger")
        customers, selected_bills = [], []
    finally:
        conn.close()

    # Fetch the selected bills from the session
    selected_bills = session['selected_bills']

    return render_template('bill_and_delivery.html', customers=customers, selected_bills=selected_bills)

@app.route('/view_bill/<bill_no>', methods=['GET', 'POST'])
def view_bill(bill_no):
    try:
        conn = sqlite3.connect('crm.db')
        cursor = conn.cursor()

        # Fetch all bills for the dropdown selection
        cursor.execute(''' 
            SELECT billno, firmname FROM customers
        ''')
        customers = cursor.fetchall()

        # Fetch the main bill details for the selected bill
        cursor.execute(''' 
            SELECT khccode, billno, biltyno, date, firmname, city, state, mobile, amount, reference_name
            FROM customers WHERE billno = ?
        ''', (bill_no,))
        main_bill_details = cursor.fetchone()

        # Initialize selected_bills in session if not already there
        if 'selected_bills' not in session:
            session['selected_bills'] = []

        # Add the main bill to the session if it's not already in the selected bills
        if main_bill_details:
            session['selected_bills'] = [main_bill_details]  # Only keep the selected bill in the session

        # Handle adding a new bill to the session
        if request.method == 'POST':
            selected_bill_no = request.form.get('bill_no')

            # Fetch the details for the newly selected bill
            cursor.execute('''
                SELECT khccode, billno, biltyno, date, firmname, city, state, mobile, amount, reference_name
                FROM customers WHERE billno = ?
            ''', (selected_bill_no,))
            new_bill_details = cursor.fetchone()

            # Replace the session with the new selected bill
            if new_bill_details:
                session['selected_bills'] = [new_bill_details]

        session.modified = True

    except sqlite3.Error as e:
        flash(f"An error occurred: {e}", "danger")
        main_bill_details = None
        customers = []
    finally:
        conn.close()

    # Render the page with only the selected bill
    return render_template('view_bill.html', main_bill_details=main_bill_details, customers=customers)

@app.route('/weekly_payments')
def weekly_payments():
    # Check if the user is logged in
    if 'username' not in session:
        flash('Please log in to access this page.', 'danger')
        return redirect(url_for('login'))

    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Fetch payment history with customer details
        cursor.execute('''
            SELECT ph.date, ph.amount, c.firmname, c.mobile
            FROM payment_history ph
            JOIN customers c ON ph.customer_id = c.id
        ''')
        payment_history = cursor.fetchall()

        # Initialize the data structure for weekly payments
        weekly_data = {}

        for payment in payment_history:
            # Validate the payment record length
            if len(payment) < 4:
                print(f"Skipping invalid entry: {payment}")
                continue

            try:
                # Parse the payment date
                payment_date = datetime.strptime(payment[0], '%Y-%m-%d')
            except ValueError:
                print(f"Skipping invalid date format: {payment[0]}")
                continue

            # Calculate the start and end of the week (Monday to Sunday)
            start_date = payment_date - timedelta(days=payment_date.weekday())
            end_date = start_date + timedelta(days=6)
            week_range = f"{start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}"

            # Identify the week uniquely by year and ISO week number
            payment_year = payment_date.year
            payment_week = payment_date.isocalendar()[1]

            # Add week data if not already present
            if (payment_year, payment_week) not in weekly_data:
                weekly_data[(payment_year, payment_week)] = {
                    'week_range': week_range,
                    'total_received': 0,  # Initialize weekly total
                    'customers': []
                }

            # Update weekly totals and customer details
            weekly_data[(payment_year, payment_week)]['total_received'] += payment[1]
            weekly_data[(payment_year, payment_week)]['customers'].append({
                'firm_name': payment[2] or 'N/A',
                'mobile_number': payment[3] or 'N/A'
            })

        # Sort the weekly data by the start date of the week (most recent first)
        sorted_weekly_data = sorted(
            weekly_data.values(),
            key=lambda x: datetime.strptime(x['week_range'].split(' - ')[0], '%d/%m/%Y'),
            reverse=True
        )

    except Exception as e:
        # Log and display error messages
        flash(f"Error processing weekly payments: {e}", 'danger')
        sorted_weekly_data = []
    finally:
        # Close the database connection
        conn.close()

    # Render the template with the processed data
    return render_template('weekly_payments.html', weekly_payments=sorted_weekly_data)
def get_all_amounts():
    conn = sqlite3.connect('crm.db')
    cursor = conn.cursor()

    # Fetch the 'amount' from the 'customers' table
    cursor.execute("SELECT amount FROM customers")
    amounts = cursor.fetchall()  # Fetching the amounts

    # Predefined ranges for amounts
    amount_ranges = {
        3504: (3501, 3509),
        4501: (4501, 4501),
        7008: (7001, 7009),
        14016: (14011, 14019),
        17500: (17501, 17509),
        19157: (19151, 19159)
    }

    amount_counts = {}
    other_amounts_count = 0

    # Count the occurrences of each amount
    for amount in amounts:
        amount_value = round(amount[0], 2)  # Round to handle float precision issues
        
        # Check if the amount falls into one of the predefined ranges
        matched = False
        for specific_amount, (lower, upper) in amount_ranges.items():
            if lower <= amount_value <= upper:
                if specific_amount in amount_counts:
                    amount_counts[specific_amount] += 1
                else:
                    amount_counts[specific_amount] = 1
                matched = True
                break
        
        # If it doesn't match any predefined amount range, count it as "Other"
        if not matched:
            other_amounts_count += 1

    conn.close()

    return amount_counts, other_amounts_count

@app.route('/total_scheme')
def total_scheme_page():
    amount_counts, other_amounts_count = get_all_amounts()  # Get the counts of amounts and other amounts
    return render_template('total_scheme.html', amount_counts=amount_counts, other_amounts_count=other_amounts_count)

@app.route('/invalid_mobile_numbers')
def invalid_mobile_numbers():
    """Route to show customers with invalid mobile numbers."""
    # Create a connection to the database
    conn = sqlite3.connect('crm.db')
    cursor = conn.cursor()

    # Query to fetch customers with mobile numbers that are not exactly 10 digits long
    cursor.execute('''
        SELECT * FROM customers
        WHERE LENGTH(mobile) != 10 AND mobile IS NOT NULL;
    ''')

    # Fetch all rows with invalid mobile numbers
    customers_with_invalid_mobile = cursor.fetchall()

    # Close the database connection
    conn.close()

    return render_template('invalid_mobile_numbers.html', customers=customers_with_invalid_mobile)

# 📌 Chat API
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "").strip()
    
    # Agar session_id pehle se hai toh wahi use hoga
    if "session_id" not in session:
        session["session_id"] = str(uuid.uuid4())

    # Chatbot ka response lena
    response = chatbot_response(user_message)
    
    return jsonify({
        "response": response,
        "session_id": session["session_id"]
    })



@app.route("/customer_analysis")
def customer_analysis():
    # Get the analyzed customer data
    customers = analyze_customers()

    # Count Categories
    genuine_count = sum(1 for c in customers if c['payment_category'] == 'Genuine')
    average_count = sum(1 for c in customers if c['payment_category'] == 'Average')
    risky_count = sum(1 for c in customers if c['payment_category'] == 'Risky')

    # Render the template with customer data and counts
    return render_template(
        "customer_analysis.html",
        customers=customers,
        genuine_count=genuine_count,
        average_count=average_count,
        risky_count=risky_count
    )

@app.route('/location-data', methods=['GET', 'POST'])
def location_data():
    conn = sqlite3.connect('crm.db')
    cursor = conn.cursor()

    if request.method == 'POST':  # Button press
        cursor.execute("UPDATE customers SET pincode = '343041' WHERE pincode IS NULL OR pincode = ''")
        conn.commit()

    cursor.execute("SELECT city, state, pincode FROM customers")
    rows = cursor.fetchall()
    conn.close()
    return render_template('location_data.html', data=rows)

@app.route('/add_reminder', methods=['POST'])
def add_reminder():
    billno = request.form['billno']
    note = request.form['note']
    reminder_date = request.form['reminder_date']

    # Fetch the customer_id using Bill No.
    conn = sqlite3.connect('crm.db')
    c = conn.cursor()
    c.execute("SELECT id FROM customers WHERE billno = ?", (billno,))
    customer_id = c.fetchone()[0]  # Get the customer_id from the Bill No.

    # Insert the reminder into the reminders table
    c.execute("INSERT INTO reminders (customer_id, note, reminder_date) VALUES (?, ?, ?)",
              (customer_id, note, reminder_date))
    conn.commit()
    conn.close()
    return redirect('/reminders')

@app.route('/reminders')
def reminders_page():
    try:
        conn = sqlite3.connect('crm.db')
        conn.row_factory = sqlite3.Row  # To get column names as keys
        c = conn.cursor()

        # Get reminders along with Bill No and Customer Name
        c.execute("""
            SELECT r.id, cu.billno, cu.name, r.note, r.reminder_date
            FROM reminders r
            JOIN customers cu ON r.customer_id = cu.id
            WHERE r.status = 'pending'
            ORDER BY r.reminder_date
        """)
        data = c.fetchall()

        # Get customers for dropdown (Bill No and Name)
        c.execute("SELECT billno, name FROM customers ORDER BY id DESC")
        customers = c.fetchall()

        # Debugging: Print customers data
        print(customers)

        conn.close()
        return render_template("reminders.html", data=data, customers=customers)
    except Exception as e:
        logging.error("Error occurred: %s", e)  # Log the error message
        return f"An error occurred: {e}", 500

import sqlite3

def create_table():
    # Database connection
    conn = sqlite3.connect('crm.db')
    cursor = conn.cursor()

    # Create table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS calling_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            firm_name TEXT NOT NULL,
            mobile_number TEXT NOT NULL,
            category TEXT NOT NULL,
            state TEXT NOT NULL,
            district TEXT NOT NULL,
            extra_columns TEXT
        )
    ''')

    # Commit and close
    conn.commit()
    conn.close()

create_table()

# Initialize maintenance mode flag
maintenance_mode = False

@app.route('/maintenance-admin')
def maintenance_admin_page():
    global maintenance_mode
    status_text = "<span class='status on'>ON</span>" if maintenance_mode else "<span class='status off'>OFF</span>"
    return f'''
    <html>
        <head>
            <title>Maintenance Control Panel</title>
            <style>
                body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
                h1 {{ color: #333; }}
                button {{ padding: 10px 20px; background-color: #4CAF50; color: white; border: none; cursor: pointer; }}
                button:hover {{ background-color: #45a049; }}
                p {{ font-size: 18px; }}
                .status {{ font-weight: bold; }}
                .status.on {{ color: #5cb85c; }}
                .status.off {{ color: #d9534f; }}
            </style>
        </head>
        <body>
            <h1>Maintenance Control Panel</h1>
            <form action="/toggle-maintenance" method="get">
                <button type="submit">Toggle Maintenance Mode</button>
            </form>
            <p>Maintenance Mode is: {status_text}</p>
        </body>
    </html>
    '''

@app.route('/toggle-maintenance')
def toggle_maintenance():
    global maintenance_mode
    maintenance_mode = not maintenance_mode
    return redirect(url_for('maintenance_admin_page'))

@app.before_request
def check_maintenance_mode():
    global maintenance_mode
    if maintenance_mode and request.endpoint not in ['maintenance_admin_page', 'maintenance_page', 'toggle_maintenance']:
        return redirect(url_for('maintenance_page'))

@app.route('/maintenance')
def maintenance_page():
    global maintenance_mode
    if not maintenance_mode:
        return redirect('/')
    return '''<html>
        <head>
            <title>Site Under Maintenance</title>
            <style>
                body { font-family: Arial, sans-serif; text-align: center; padding: 50px; background-color: #f9f9f9; }
                h1 { color: #d9534f; font-size: 36px; }
                p { font-size: 20px; color: #555; }
                .maintenance-icon { font-size: 100px; color: #d9534f; margin-bottom: 20px; }
            </style>
        </head>
        <body>
            <div class="maintenance-icon">🚧</div>
            <h1>Site Under Maintenance</h1>
            <p>We are currently performing scheduled maintenance. <br>Please check back soon. Thank you for your patience.</p>
        </body>
    </html>'''

import logging

ADMIN_PASSWORD = "krishna123"

def get_db_connection():
    import sqlite3
    conn = sqlite3.connect('crm.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/delete-entry', methods=['POST'])
def delete_entry():
    data = request.json
    password = data.get('password')
    entry_id = data.get('entry_id')

    if password != ADMIN_PASSWORD:
        return jsonify({'success': False, 'message': 'Wrong password'})

    if not entry_id:
        return jsonify({'success': False, 'message': 'Entry ID not provided'})

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Pehle try karo id se delete karna (integer banake)
        try:
            entry_id_int = int(entry_id)
            cursor.execute("DELETE FROM customers WHERE id = ?", (entry_id_int,))
            conn.commit()
        except ValueError:
            # Agar integer me convert nahi hua to ignore karo
            pass

        if cursor.rowcount == 0:
            # Phir try karo khccode se delete karna (string me)
            cursor.execute("DELETE FROM customers WHERE khccode = ?", (entry_id,))
            conn.commit()

        if cursor.rowcount == 0:
            return jsonify({'success': False, 'message': 'Deletion failed: Entry not found for given ID or KHCCODE'})

        return jsonify({'success': True, 'message': 'Entry deleted successfully'})

    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

    finally:
        conn.close()

@app.route('/recycle-bin')
def recycle_bin():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customers WHERE status = 0 ORDER BY date DESC")
    deleted_entries = cursor.fetchall()
    conn.close()
    # Aap HTML template ko render kar sakte ho jisme deleted_entries show hongi
    return render_template('recycle_bin.html', entries=deleted_entries)

@app.route('/restore-entry', methods=['POST'])
def restore_entry():
    entry_id = request.form.get('entry_id')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE customers SET status = 1 WHERE id = ?", (entry_id,))
    conn.commit()
    conn.close()
    return redirect('/recycle-bin')

@app.route('/permanent-delete-entry', methods=['POST'])
def permanent_delete_entry():
    entry_id = request.form.get('entry_id')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM customers WHERE id = ?", (entry_id,))
    conn.commit()
    conn.close()
    return redirect('/recycle-bin')

import os

import os

def get_file_structure(startpath):
    exclude_dirs = {
        '.vscode', '__pycache__', '.venv', 'venv',
        'chat', 'app/chat', 'app/chat/templates'
    }

    allowed_uploads = {'khc001', 'khc002', 'khc003'}

    structure = []

    for root, dirs, files in os.walk(startpath):
        rel_root = os.path.relpath(root, startpath).replace("\\", "/")

        # Rule 1: Skip excluded folders
        if any(rel_root == ex or rel_root.startswith(ex + '/') for ex in exclude_dirs):
            continue

        # Rule 2: Handle static/uploads/
        if rel_root == 'static/uploads':
            # Keep only allowed folders
            dirs[:] = [d for d in dirs if d in allowed_uploads]
            files[:] = []  # Don't show files in uploads root
        elif rel_root.startswith('static/uploads/'):
            # Only allow top-level khc001/002/003 folders
            folder_name = rel_root.split('/')[-1]
            if folder_name not in allowed_uploads:
                continue
            if rel_root.count('/') > 2:
                continue  # Skip any deeper folders inside khcXXX
            files[:] = []  # Don't show files inside khcXXX
            dirs[:] = []   # Don't allow going deeper

        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * level
        structure.append(f"{indent}{os.path.basename(root)}/")

        subindent = ' ' * 4 * (level + 1)
        for f in files:
            structure.append(f"{subindent}{f}")

        # Filter out excluded folders from traversal
        dirs[:] = [
            d for d in dirs
            if os.path.join(rel_root, d).replace("\\", "/") not in exclude_dirs
        ]

    return "\n".join(structure)

@app.route('/structure')
def structure():
    folder_path = '.'  # Change this to your desired path
    file_tree = get_file_structure(folder_path)
    return render_template('structure.html', file_tree=file_tree)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
