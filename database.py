from flask import Blueprint, render_template, flash, redirect, url_for
import sqlite3
from flask import g

def get_db_connection():
    if 'db' not in g:
        g.db = sqlite3.connect('crm.db')
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db_connection(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

# Create a Blueprint for the database structure
database_bp = Blueprint('database', __name__)

@database_bp.route('/database-structure', methods=['GET'])
def database_structure():
    try:
        conn = sqlite3.connect('crm.db')
        cursor = conn.cursor()

        # Get the list of tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        tables_info = {}

        # Get column names for each table
        for table in tables:
            table_name = table[0]
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            tables_info[table_name] = [col[1] for col in columns]  # Extract column names

        conn.close()

        return render_template('database_structure.html', tables_info=tables_info)

    except Exception as e:
        flash(f"Error fetching database structure: {str(e)}", 'error')
        return redirect(url_for('index'))  # Redirect to the main page on error

