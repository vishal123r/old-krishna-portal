from flask import Blueprint, render_template, request, jsonify
import sqlite3
from datetime import datetime, timedelta

payment_today_bp = Blueprint('payment_today', __name__)

@payment_today_bp.route('/payment_today')
def payment_today():
    conn = sqlite3.connect('crm.db')
    cursor = conn.cursor()

    # Aaj ki date YYYY-MM-DD format me
    today = datetime.today().strftime('%Y-%m-%d')

    # Last day ki date calculate karo
    last_day = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')

    # payment_history table se sabhi entries latest date ke hisab se
    cursor.execute("""SELECT id, customer_id, amount, date 
                      FROM payment_history 
                      ORDER BY date DESC""")
    all_payment_history_sorted = cursor.fetchall()

    # Aaj ka total amount aur count
    cursor.execute("SELECT SUM(amount), COUNT(*) FROM payment_history WHERE date = ?", (today,))
    today_total_amount, today_count = cursor.fetchone()

    # Kal ka total amount aur count
    cursor.execute("SELECT SUM(amount), COUNT(*) FROM payment_history WHERE date = ?", (last_day,))
    last_day_total_amount, last_day_count = cursor.fetchone()

    conn.close()

    return render_template(
        'payment_today.html',
        all_payment_history_sorted=all_payment_history_sorted,
        today=today,
        today_total_amount=today_total_amount or 0,
        today_count=today_count or 0,
        last_day_total_amount=last_day_total_amount or 0,
        last_day_count=last_day_count or 0
    )

# Route to update payment record
@payment_today_bp.route('/update_payment', methods=['POST'])
def update_payment():
    data = request.get_json()
    payment_id = data['id']
    new_amount = data['amount']
    new_date = data['date']

    conn = sqlite3.connect('crm.db')
    cursor = conn.cursor()

    # Update payment record
    cursor.execute("""
        UPDATE payment_history
        SET amount = ?, date = ?
        WHERE id = ?
    """, (new_amount, new_date, payment_id))

    conn.commit()
    conn.close()

    return jsonify({'success': True})
