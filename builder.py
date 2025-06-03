import os
import re
import sqlite3
from flask import Blueprint, render_template, request, abort

builder_bp = Blueprint('builder', __name__)

DYNAMIC_PAGE_PATH = 'dynamic_pages'  # Folder for generated Python blueprint files
TEMPLATE_PATH = 'templates'          # Folder for HTML templates

def get_tables(database):
    """Return list of table names in the SQLite database."""
    try:
        conn = sqlite3.connect(database)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        return tables
    except Exception:
        return []

def get_columns(database, table):
    """Return list of column names for the specified table."""
    try:
        conn = sqlite3.connect(database)
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [row[1] for row in cursor.fetchall()]
        conn.close()
        return columns
    except Exception:
        return []

@builder_bp.route('/create-page', methods=['GET', 'POST'])
def create_page():
    # List all .db files in current directory
    databases = [f for f in os.listdir() if f.endswith('.db')]
    selected_db = request.form.get('database') or request.args.get('database')
    selected_table = request.form.get('table') or request.args.get('table')
    columns = get_columns(selected_db, selected_table) if selected_db and selected_table else []

    if request.method == 'POST' and 'columns' in request.form:
        page_name = request.form['page_name'].strip().replace(" ", "_")
        db = request.form['database']
        table = request.form['table']
        cols = request.form.getlist('columns')

        # Validate page_name
        if not page_name:
            return "❌ Page name cannot be empty."

        if not re.match(r'^\w+$', page_name):
            return "❌ Invalid page name. Use only letters, numbers, and underscores."

        # Make sure directories exist
        os.makedirs(DYNAMIC_PAGE_PATH, exist_ok=True)
        os.makedirs(TEMPLATE_PATH, exist_ok=True)

        # Create Python blueprint code
        page_code = f"""from flask import Blueprint, render_template
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

        # Create HTML template code
        html_code = f"""{{% extends 'base.html' %}}
{{% block content %}}
<h2>{{{{ columns|length }}}} Records Found</h2>
<table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse; width: 100%;">
  <thead>
    <tr>
      {{% for col in columns %}}
      <th>{{{{ col.replace('_', ' ').title() }}}}</th>
      {{% endfor %}}
    </tr>
  </thead>
  <tbody>
    {{% if data %}}
      {{% for row in data %}}
      <tr>
        {{% for item in row %}}
        <td>{{{{ item }}}}</td>
        {{% endfor %}}
      </tr>
      {{% endfor %}}
    {{% else %}}
      <tr><td colspan="{{{{ columns|length }}}}">No records found.</td></tr>
    {{% endif %}}
  </tbody>
</table>
{{% endblock %}}
"""

        # Save blueprint Python file
        with open(os.path.join(DYNAMIC_PAGE_PATH, f"{page_name}.py"), 'w', encoding='utf-8') as f:
            f.write(page_code)

        # Save template HTML file
        with open(os.path.join(TEMPLATE_PATH, f"{page_name}.html"), 'w', encoding='utf-8') as f:
            f.write(html_code)

        return f"""
<div style='
    margin: 30px auto;
    max-width: 600px;
    padding: 20px 30px;
    border-radius: 12px;
    background-color: #e6ffed;
    color: #155724;
    border: 1px solid #c3e6cb;
    font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    text-align: center;
'>
    <h2 style='margin-bottom: 10px;'>✅ Page Created!</h2>
    <p style='font-size: 18px;'>Page <strong style="color: #007bff;">'{page_name}'</strong> is now live.</p>
    <a href='/{page_name}' style='
        display: inline-block;
        margin-top: 12px;
        padding: 10px 20px;
        background-color: #007bff;
        color: white;
        text-decoration: none;
        border-radius: 6px;
        font-weight: bold;
    '>🔗 Visit /{page_name}</a>
</div>
"""


    # If GET request or form incomplete, show form
    tables = get_tables(selected_db) if selected_db else []
    return render_template('create_page.html',
                           databases=databases,
                           tables=tables,
                           columns=columns,
                           selected_db=selected_db,
                           selected_table=selected_table)
