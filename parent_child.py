from flask import Flask, Blueprint, render_template, request, redirect, url_for, flash
import sqlite3
from db import get_db_connection  

# Create a Blueprint
parent_child_bp = Blueprint('parent_child', __name__)

# Route to show main entries and filter by Bill No.
@parent_child_bp.route('/parent_child', methods=['GET', 'POST'])
def show_main_entries():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch all distinct Bill Nos. for dropdown
        cursor.execute("SELECT DISTINCT billno FROM customers")
        bill_numbers = cursor.fetchall()

        # If the form is submitted (POST), filter entries based on selected Bill No.
        billno = request.form.get('bill_no')  # Selected Bill No.
        if billno:
            # Fetch entries based on selected Bill No.
            cursor.execute("SELECT * FROM customers WHERE billno = ?", (billno,))
            main_entries = cursor.fetchall()
        else:
            main_entries = []  # No Bill No. selected, so no entries are displayed
        
        return render_template('parent_child.html', main_entries=main_entries, bill_numbers=bill_numbers)
    
    except Exception as e:
        flash(f"Database Error: {str(e)}", "danger")
        return render_template('parent_child.html', main_entries=[])
    
    finally:
        cursor.close()
        conn.close()

@parent_child_bp.route('/view_entry/<int:entry_id>', methods=['GET'])
def view_entry(entry_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch sub-entries for the given entry_id
        cursor.execute("SELECT * FROM sub_entries WHERE entry_id = ?", (entry_id,))
        sub_entries = cursor.fetchall()

        return render_template('view_entry.html', sub_entries=sub_entries)

    except Exception as e:
        flash(f"Database Error: {str(e)}", "danger")
        return redirect(url_for('parent_child.show_main_entries'))

    finally:
        cursor.close()
        conn.close()

# Route to add a new main entry
@parent_child_bp.route('/add_main_entry', methods=['POST'])
def add_main_entry():
    if request.method == 'POST':
        name = request.form.get('name')
        amount = request.form.get('amount')
        
        if not name or not amount:
            flash("Name and Amount are required!", "danger")
            return redirect(url_for('parent_child.show_main_entries'))

        # Validate amount as a valid number
        try:
            amount = float(amount)
        except ValueError:
            flash("Amount must be a valid number!", "danger")
            return redirect(url_for('parent_child.show_main_entries'))

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO customers (name, amount) VALUES (?, ?)", (name, amount))
            conn.commit()
            flash("Main entry added successfully!", "success")
        except Exception as e:
            flash(f"Database Error: {str(e)}", "danger")
        finally:
            cursor.close()
            conn.close()

    return redirect(url_for('parent_child.show_main_entries'))
