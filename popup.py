from flask import Blueprint, render_template, request
import sqlite3

popup_bp = Blueprint('popup_bp', __name__)

def get_db_connection():
    conn = sqlite3.connect('crm.db')
    conn.row_factory = sqlite3.Row
    return conn

@popup_bp.route('/popup/<staff_name>')
def show_popup(staff_name):
    conn = get_db_connection()
    data = conn.execute('SELECT * FROM popup_data WHERE staff_name = ?', (staff_name,)).fetchone()
    conn.close()
    return render_template('popup.html', data=data)

@popup_bp.route('/manage_popup', methods=['GET', 'POST'])
def manage_popup():
    conn = get_db_connection()

    # fetch all unique reference names from customers
    references = conn.execute('SELECT DISTINCT reference_name FROM customers WHERE reference_name IS NOT NULL').fetchall()

    if request.method == 'POST':
        staff_name = request.form['staff_name']
        message = request.form['message']
        conn.execute(
            'INSERT OR REPLACE INTO popup_data (staff_name, message) VALUES (?, ?)',
            (staff_name, message)
        )
        conn.commit()

    data = conn.execute('SELECT * FROM popup_data').fetchall()
    conn.close()
    return render_template('manage_popup.html', data=data, references=references)
