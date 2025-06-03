from flask import Blueprint, render_template, request
import sqlite3
import os

builder_bp = Blueprint('builder', __name__)
DYNAMIC_PAGE_PATH = 'dynamic_pages'
TEMPLATE_PATH = 'templates'

# ✅ Get table names from DB
def get_tables(database):
    if not database: return []
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [i[0] for i in cursor.fetchall()]
    conn.close()
    return tables

# ✅ Get column names from a table
def get_columns(database, table):
    if not database or not table: return []
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table});")
    columns = [i[1] for i in cursor.fetchall()]
    conn.close()
    return columns

@builder_bp.route('/create-page', methods=['GET', 'POST'])
def create_page():
    databases = [f for f in os.listdir() if f.endswith('.db')]

    selected_db = request.form.get('database') or request.args.get('database')
    selected_table = request.form.get('table') or request.args.get('table')

    tables = get_tables(selected_db) if selected_db else []
    columns = get_columns(selected_db, selected_table) if selected_db and selected_table else []

    if request.method == 'POST':
        db = request.form.get('database')
        table = request.form.get('table')
        cols = request.form.getlist('columns')
        page_name = request.form.get('page_name')

        if not all([db, table, cols, page_name]):
            return "❌ Missing form fields. Please fill everything."

        # ✅ Dynamic Python Page Code
        page_code = f"""
from flask import Blueprint, render_template
import sqlite3

{page_name}_bp = Blueprint('{page_name}', __name__)

@{page_name}_bp.route('/{page_name}')
def show():
    conn = sqlite3.connect('{db}')
    cursor = conn.cursor()
    cursor.execute("SELECT {', '.join(cols)} FROM {table}")
    rows = cursor.fetchall()
    conn.close()
    return render_template('{page_name}.html', data=rows, columns={cols})
"""

        os.makedirs(DYNAMIC_PAGE_PATH, exist_ok=True)
        with open(f'{DYNAMIC_PAGE_PATH}/{page_name}.py', 'w') as f:
            f.write(page_code)

        # ✅ Create corresponding HTML Template
        html_code = """{% extends 'base.html' %}
{% block content %}
<h2>{{ columns }}</h2>
<table border="1" cellpadding="5">
<tr>{% for col in columns %}<th>{{ col }}</th>{% endfor %}</tr>
{% for row in data %}
<tr>{% for item in row %}<td>{{ item }}</td>{% endfor %}</tr>
{% endfor %}
</table>
{% endblock %}
"""
        os.makedirs(TEMPLATE_PATH, exist_ok=True)
        with open(f'{TEMPLATE_PATH}/{page_name}.html', 'w') as f:
            f.write(html_code)

        return f"✅ Page '{page_name}' created. Access it at: <a href='/{page_name}'>/{page_name}</a> (Don't forget to import the blueprint!)"

    return render_template(
        'create_page.html',
        databases=databases,
        tables=tables,
        columns=columns,
        selected_db=selected_db,
        selected_table=selected_table
    )
