import os
import re
import ast
import sqlite3
from flask import (
    Blueprint, render_template, request, abort, redirect, url_for
)

editor_bp = Blueprint('editor', __name__, template_folder='templates')

DYNAMIC_PAGE_PATH = 'dynamic_pages'
TEMPLATE_PATH = 'templates'
DB_FILE = 'crm.db'

PROTECTED_PAGES = {'payment_paid', 'home', 'login'}  # pages you don't want to allow editing/deleting


def get_existing_pages(exclude_pages=None):
    exclude_pages = set(exclude_pages or [])
    pages = set()

    if os.path.exists(DYNAMIC_PAGE_PATH):
        py_files = {f[:-3] for f in os.listdir(DYNAMIC_PAGE_PATH) if f.endswith('.py')}
        pages.update(py_files)

    if os.path.exists(TEMPLATE_PATH):
        html_files = {f[:-5] for f in os.listdir(TEMPLATE_PATH) if f.endswith('.html')}
        pages.update(html_files)

    # Remove protected and excluded pages (case-insensitive)
    filtered_pages = [
        p for p in pages
        if p.lower() not in {pg.lower() for pg in exclude_pages}
    ]
    return sorted(filtered_pages)


@editor_bp.route('/edit-pages', methods=['GET', 'POST'])
def edit_pages():
    pages = get_existing_pages(exclude_pages=PROTECTED_PAGES)
    
    # Extra filter in case something slips through:
    pages = [p for p in pages if p.lower() not in {pg.lower() for pg in PROTECTED_PAGES}]

    selected_page = request.args.get('page') or request.form.get('page')
    message = None
    message_type = 'info'

    if request.method == 'POST':
        # Handle delete request
        if 'delete_page' in request.form:
            page_to_delete = request.form['delete_page']
            if page_to_delete in PROTECTED_PAGES:
                message = f"⚠️ Page '{page_to_delete}' is protected and cannot be deleted."
                message_type = 'error'
            elif page_to_delete not in pages:
                message = f"⚠️ Page '{page_to_delete}' not found or already deleted."
                message_type = 'error'
            else:
                try:
                    os.remove(os.path.join(TEMPLATE_PATH, f"{page_to_delete}.html"))
                    os.remove(os.path.join(DYNAMIC_PAGE_PATH, f"{page_to_delete}.py"))
                    message = f"🗑️ Page '{page_to_delete}' deleted successfully."
                    message_type = 'success'
                    return redirect(url_for('editor.edit_pages'))
                except Exception as e:
                    message = f"Error deleting page '{page_to_delete}': {e}"
                    message_type = 'error'

        # Handle saving edits to HTML
        elif 'page' in request.form and 'html' in request.form:
            page_to_save = request.form['page']
            if page_to_save in PROTECTED_PAGES:
                message = f"⚠️ Page '{page_to_save}' is protected and cannot be edited."
                message_type = 'error'
            else:
                html_content = request.form['html']
                try:
                    with open(os.path.join(TEMPLATE_PATH, f"{page_to_save}.html"), 'w', encoding='utf-8') as f:
                        f.write(html_content)
                    message = f"✅ Page '{page_to_save}.html' saved successfully."
                    message_type = 'success'
                    # Redirect to prevent form resubmission
                    return redirect(url_for('editor.edit_pages', page=page_to_save))
                except Exception as e:
                    message = f"Error saving page '{page_to_save}': {e}"
                    message_type = 'error'

    # Load HTML content for the selected page to edit
    html_content = ""
    if selected_page:
        if selected_page in PROTECTED_PAGES:
            message = f"⚠️ Editing not allowed for protected page '{selected_page}'."
            message_type = 'error'
        elif selected_page in pages:
            try:
                with open(os.path.join(TEMPLATE_PATH, f"{selected_page}.html"), 'r', encoding='utf-8') as f:
                    html_content = f.read()
            except Exception as e:
                message = f"Could not load content for '{selected_page}': {e}"
                message_type = 'error'
        else:
            message = f"Page '{selected_page}' not found."
            message_type = 'error'

    return render_template(
        'edit_pages.html',
        pages=pages,
        selected_page=selected_page,
        html_content=html_content,
        message=message,
        message_type=message_type,
        protected_pages=PROTECTED_PAGES
    )


@editor_bp.route('/preview/<page>', methods=['GET', 'POST'])
def preview_page(page):
    """Preview page with data from DB based on dynamic columns."""
    pages = get_existing_pages()
    if page not in pages and page not in PROTECTED_PAGES:
        return abort(404, description="Page not found")

    template_file = os.path.join(TEMPLATE_PATH, f"{page}.html")

    try:
        with open(template_file, 'r', encoding='utf-8') as f:
            template_content = f.read()
    except FileNotFoundError:
        return abort(404, description="Template file not found")

    # Extract current column list from the template (if present)
    match = re.search(r'(\{%\s*set\s+columns\s*=\s*)(\[.*?\])(\s*%\})', template_content, re.DOTALL)
    if match:
        try:
            current_columns = ast.literal_eval(match.group(2))
            if not isinstance(current_columns, list):
                current_columns = []
        except Exception:
            current_columns = []
    else:
        current_columns = []

    # Handle POST to update columns dynamically
    if request.method == 'POST':
        selected_columns = request.form.getlist('selected_columns')
        selected_columns = list(dict.fromkeys(selected_columns))  # remove duplicates
        new_columns_str = f"{{% set columns = {selected_columns} %}}"

        if match:
            new_template_content = template_content[:match.start()] + new_columns_str + template_content[match.end():]
        else:
            # Insert column set at the beginning if not present
            new_template_content = new_columns_str + '\n' + template_content

        # Save updated template
        with open(template_file, 'w', encoding='utf-8') as f:
            f.write(new_template_content)

        return redirect(url_for('editor.preview_page', page=page))

    # Determine table name for the page, default is same as page name
    page_table_map = {
        'payment_paid': 'customers',  # example mapping
        # add other custom mappings here if needed
    }
    table = page_table_map.get(page, page)

    # Connect to DB and get all columns for table
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Check if table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
    if cursor.fetchone() is None:
        conn.close()
        # Render template with empty data if table not found
        return render_template(f"{page}.html", data=[], columns=[], all_columns=[])

    cursor.execute(f"PRAGMA table_info({table})")
    all_columns = [row[1] for row in cursor.fetchall()]

    # If no columns set in template, default to all columns
    used_columns = current_columns if current_columns else all_columns

    # Fetch rows with selected columns
    # Protect against SQL injection by allowing only columns from all_columns
    safe_columns = [col for col in used_columns if col in all_columns]
    if not safe_columns:
        safe_columns = all_columns  # fallback to all columns if none safe

    query = f"SELECT {', '.join(safe_columns)} FROM {table}"
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()

    return render_template(
        f"{page}.html",
        data=rows,
        columns=safe_columns,
        all_columns=all_columns,
    )
