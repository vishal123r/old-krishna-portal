import sqlite3
from flask import Blueprint, render_template, request
from datetime import datetime

payment_history_bp = Blueprint('payment_history', __name__, template_folder='templates')

def format_date(date_str):
    dt = datetime.strptime(date_str, '%Y-%m-%d')
    return dt.strftime('%d/%m/%Y')

@payment_history_bp.route('/payment-history', methods=['GET', 'POST'])
def payment_history():
    selected_date = None
    payments = []
    total_amount = 0  # total amount variable

    if request.method == 'POST':
        selected_date = request.form.get('date')

        conn = sqlite3.connect('crm.db')
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        query = """
            SELECT c.KHCCode, c.BillNo, c.BiltyNo, ph.date as payment_date, c.FirmName, c.City, c.State, c.Mobile, c.Reference_Name,
                   ph.amount
            FROM payment_history ph
            JOIN customers c ON ph.customer_id = c.id
            WHERE ph.date = ?
        """
        cur.execute(query, (selected_date,))
        rows = cur.fetchall()

        for row in rows:
            payments.append({
                'KHCCode': row['KHCCode'],
                'BillNo': row['BillNo'],
                'BiltyNo': row['BiltyNo'],
                'payment_date': format_date(row['payment_date']),
                'FirmName': row['FirmName'],
                'City': row['City'],
                'State': row['State'],
                'Mobile': row['Mobile'],
                'Reference_Name': row['Reference_Name'],
                'amount': row['amount'],
            })
            total_amount += row['amount']  # add to total

        conn.close()

    return render_template('payment_history.html', payments=payments, selected_date=selected_date, total_amount=total_amount)
