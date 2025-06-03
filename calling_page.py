from flask import Blueprint, render_template, request, redirect
import sqlite3
from datetime import datetime

calling_page = Blueprint('calling_page', __name__)

@calling_page.route('/calling-dashboard', methods=['GET', 'POST'])
def calling_dashboard():
    conn = sqlite3.connect('crm.db')
    c = conn.cursor()

    if request.method == 'POST':
        customer_id = request.form['customer_id']
        do_not_call = int('do_not_call' in request.form)
        call_date = request.form.get('call_date')
        notes = request.form.get('notes')
        staff = request.form.get('assigned_staff')
        region = request.form.get('region')

        c.execute('''
            INSERT INTO call_preferences (customer_id, do_not_call, call_date, notes, assigned_staff, region)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (customer_id, do_not_call, call_date, notes, staff, region))
        conn.commit()
        return redirect('/calling-dashboard')

    # Filter: upcoming calls, or skip do_not_call
    c.execute('''
        SELECT cp.id, c.firmname, c.mobile, cp.call_date, cp.do_not_call, cp.notes, cp.assigned_staff, cp.region
        FROM call_preferences cp
        JOIN customers c ON cp.customer_id = c.id
        WHERE (cp.do_not_call = 0 AND (cp.call_date IS NULL OR cp.call_date <= ?))
        ORDER BY cp.call_date
    ''', (datetime.now().strftime("%Y-%m-%d"),))

    calls = c.fetchall()
    conn.close()
    return render_template('calling_dashboard.html', calls=calls)
