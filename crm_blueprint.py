from flask import Blueprint, render_template, request
import sqlite3

crm_bp = Blueprint('crm', __name__, url_prefix='/crm')

def get_db_connection():
    conn = sqlite3.connect('crm.db')
    conn.row_factory = sqlite3.Row  # Access by column name
    return conn

@crm_bp.route('/search', methods=['GET', 'POST'])
def search():
    results = None
    searched_reference_name = None
    total_due = 0.0
    total_amount = 0.0
    total_received_amount = 0.0

    if request.method == 'POST':
        amounts = request.form.get('amounts')
        reference_name = request.form.get('reference_name')

        if amounts and reference_name:
            amount_list = []
            for a in amounts.split(','):
                a = a.strip()
                try:
                    amount_list.append(float(a))
                except ValueError:
                    continue

            if amount_list:
                placeholders = ','.join('?' for _ in amount_list)
                query = f"""
                    SELECT 
                        c.id,
                        c.khccode,
                        c.billno,
                        c.date,
                        c.firmname,
                        c.state,
                        c.city,
                        c.mobile,
                        c.amount,
                        COALESCE(SUM(p.amount), 0) AS total_received,
                        (c.amount - COALESCE(SUM(p.amount), 0)) AS due_amount,
                        c.reference_name
                    FROM customers c
                    LEFT JOIN payment_history p ON c.id = p.customer_id
                    WHERE c.amount IN ({placeholders})
                    AND LOWER(c.reference_name) = LOWER(?)
                    GROUP BY c.id, c.khccode, c.billno, c.date, c.firmname, c.state, c.city, c.mobile, c.amount, c.reference_name
                    ORDER BY c.mobile, c.amount
                """
                params = amount_list + [reference_name.lower()]

                conn = get_db_connection()
                results = conn.execute(query, params).fetchall()
                conn.close()
                searched_reference_name = reference_name

    if results:
        for row in results:
            try:
                total_due += float(row['due_amount'])
                total_amount += float(row['amount'])
                total_received_amount += float(row['total_received'])
            except (ValueError, TypeError):
                pass

    return render_template(
        'search.html',
        results=results,
        searched_reference_name=searched_reference_name,
        total_due=total_due,
        total_amount=total_amount,
        total_received_amount=total_received_amount
    )
