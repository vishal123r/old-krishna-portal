from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import sqlite3
from datetime import datetime

# Create the Blueprint with url_prefix set to '/general_expenses'
expenses_bp = Blueprint('expenses', __name__, template_folder='templates/general_expenses', url_prefix='/general_expenses')

DB_PATH = 'crm.db'

# Ensure session is enabled in app.py
def init_app(app):
    app.secret_key = "your_secret_key"  # Required for session

# Create expenses table if not exists
def create_table():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS expenses (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        amount REAL,
                        category TEXT,
                        date TEXT)''')
    conn.commit()
    conn.close()

def convert_date_format(date_str):
    try:
        # Check if the date is valid using the strptime method
        date_obj = datetime.strptime(date_str, '%d/%m/%Y')
        # Additional validation for impossible dates can be done here
        return date_obj.strftime('%Y-%m-%d')  # Convert to yyyy-mm-dd format for storage
    except ValueError:
        return None


# Route to display & add expenses
@expenses_bp.route('', methods=['GET', 'POST'])
def expenses():
    create_table()  # Ensure table exists
    if 'admin' not in session.get('permissions', []):
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('login'))

    if request.method == 'POST':
        amount = request.form['amount']
        category = request.form['category']
        date = request.form['date']

        # Convert the date from dd/mm/yyyy to yyyy-mm-dd format
        formatted_date = convert_date_format(date)

        if formatted_date:
            # Store in database
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO expenses (amount, category, date) VALUES (?, ?, ?)", (amount, category, formatted_date))
            conn.commit()
            conn.close()
            return redirect(url_for('expenses.expenses'))
        else:
            return "Invalid date format, please use dd/mm/yyyy", 400

    # Fetch all expenses from database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM expenses ORDER BY date DESC")
    db_expenses = cursor.fetchall()

    # Fetch all distinct categories for the expense list
    cursor.execute("SELECT DISTINCT category FROM expenses")
    categories = cursor.fetchall()

    # Calculate summary
    daily, weekly, monthly, yearly = calculate_expense_summary()

    # Calculate the total of all expenses
    cursor.execute("SELECT SUM(amount) FROM expenses")
    total_expenses = cursor.fetchone()[0] or 0
    conn.close()

    return render_template("general_expenses.html", expenses=db_expenses, categories=categories, daily=daily, weekly=weekly, monthly=monthly, yearly=yearly, total_expenses=total_expenses)

# Function to calculate expense summary
def calculate_expense_summary():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT SUM(amount) FROM expenses WHERE date = date('now')")
    daily = cursor.fetchone()[0] or 0

    cursor.execute("SELECT SUM(amount) FROM expenses WHERE date >= date('now', '-6 days')")
    weekly = cursor.fetchone()[0] or 0

    cursor.execute("SELECT SUM(amount) FROM expenses WHERE date >= date('now', 'start of month')")
    monthly = cursor.fetchone()[0] or 0

    cursor.execute("SELECT SUM(amount) FROM expenses WHERE date >= date('now', 'start of year')")
    yearly = cursor.fetchone()[0] or 0

    conn.close()
    return daily, weekly, monthly, yearly

# Route to handle deletion of expense
@expenses_bp.route('/delete_expense/<int:expense_id>', methods=['GET'])
def delete_expense(expense_id):
    if 'admin' not in session.get('permissions', []):
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('login'))

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()
    conn.close()

    return redirect(url_for('expenses.expenses'))

# Route to display expenses by category and their total
@expenses_bp.route('/category_summary', methods=['GET'])
def category_summary():
    if 'admin' not in session.get('permissions', []):
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('login'))

    # Fetch expenses grouped by category and calculate the total for each category
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT category, SUM(amount)
        FROM expenses
        GROUP BY category
    """)
    category_totals = cursor.fetchall()  # List of tuples (category, total_amount)
    conn.close()

    return render_template("category_summary.html", category_totals=category_totals)


