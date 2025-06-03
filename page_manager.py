import os
from flask import Blueprint, render_template, request, redirect, url_for, flash

manage_pages_bp = Blueprint('manage_pages', __name__, template_folder='templates')

TEMPLATE_PATH = 'templates'
PROTECTED_PAGES = {'home', 'login', 'payment_paid'}

def get_pages():
    if not os.path.exists(TEMPLATE_PATH):
        os.makedirs(TEMPLATE_PATH)
    pages = [f[:-5] for f in os.listdir(TEMPLATE_PATH) if f.endswith('.html')]
    return sorted(pages)

@manage_pages_bp.route('/manage-pages', methods=['GET', 'POST'])
def manage_pages():
    pages = get_pages()

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'create':
            new_page = request.form.get('new_page_name', '').strip()
            content = request.form.get('new_page_content', '').strip()
            if not new_page:
                flash("Page name cannot be empty!", "error")
            elif new_page.lower() in {p.lower() for p in pages}:
                flash("Page already exists!", "error")
            else:
                filename = os.path.join(TEMPLATE_PATH, f"{new_page}.html")
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                flash(f"Page '{new_page}' created successfully.", "success")
                return redirect(url_for('manage_pages.manage_pages'))

        elif action == 'save':
            page = request.form.get('page_to_edit')
            if page in PROTECTED_PAGES:
                flash(f"'{page}' is protected and cannot be edited.", "error")
            else:
                content = request.form.get('page_content', '')
                filename = os.path.join(TEMPLATE_PATH, f"{page}.html")
                try:
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(content)
                    flash(f"Page '{page}' saved successfully.", "success")
                    return redirect(url_for('manage_pages.manage_pages', selected=page))
                except Exception as e:
                    flash(f"Error saving page: {e}", "error")

        elif action == 'delete':
            page = request.form.get('page_to_delete')
            if page in PROTECTED_PAGES:
                flash(f"'{page}' is protected and cannot be deleted.", "error")
            else:
                filename = os.path.join(TEMPLATE_PATH, f"{page}.html")
                if os.path.exists(filename):
                    os.remove(filename)
                    flash(f"Page '{page}' deleted successfully.", "success")
                    return redirect(url_for('manage_pages.manage_pages'))
                else:
                    flash("Page not found.", "error")

    selected_page = request.args.get('selected')
    page_content = ''
    if selected_page:
        try:
            with open(os.path.join(TEMPLATE_PATH, f"{selected_page}.html"), 'r', encoding='utf-8') as f:
                page_content = f.read()
        except Exception as e:
            flash(f"Could not load page content: {e}", "error")

    return render_template('manage_pages.html',
                           pages=pages,
                           selected_page=selected_page,
                           page_content=page_content,
                           protected_pages=PROTECTED_PAGES)
