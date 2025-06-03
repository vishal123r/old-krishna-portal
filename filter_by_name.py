from flask import Blueprint, request, render_template
import sqlite3

# Create a blueprint for filtering by name
filter_by_name_bp = Blueprint('filter_by_name', __name__)

@filter_by_name_bp.route('/filter_by_name', methods=['GET', 'POST'])
def filter_by_name():
    """Page to show entries and filter by name or bilty no."""
    entries = []
    unique_bilty_names = []
    searched_name = None
    selected_biltyno = None  # Variable to store selected Bilty No.

    # Connect to the database
    conn = sqlite3.connect('crm.db')
    conn.row_factory = sqlite3.Row  # Access columns by name
    cursor = conn.cursor()

    if request.method == 'POST':
        # Get the name entered in the form
        searched_name = request.form.get('name', '').strip()
        selected_biltyno = request.form.get('biltyno', '').strip()  # Get the selected Bilty No.

        # If a name is provided, filter entries based on name and non-numeric and non-"self" Bilty No.
        query = '''
            SELECT * FROM customers
            WHERE (LOWER(firmname) LIKE LOWER(?) OR LOWER(reference_name) LIKE LOWER(?))
              AND (biltyno IS NULL OR biltyno NOT LIKE '%self%' AND biltyno NOT GLOB '*[0-9]*')
        '''
        params = (f'%{searched_name}%', f'%{searched_name}%')

        if selected_biltyno:
            query += " AND LOWER(biltyno) = LOWER(?)"
            params += (selected_biltyno,)

        cursor.execute(query, params)

    else:
        # On GET request, fetch all entries excluding specific bilty numbers
        cursor.execute(''' 
            SELECT * FROM customers 
            WHERE biltyno IS NULL OR 
                  (biltyno NOT LIKE '%self%' AND biltyno NOT GLOB '*[0-9]*')
        ''')

    entries = cursor.fetchall()

    # Fetch unique bilty names (non-numeric, non-"self") and their counts
    cursor.execute('''
        SELECT LOWER(biltyno) AS biltyno_normalized, COUNT(*) AS count
        FROM customers
        WHERE biltyno IS NOT NULL AND
              biltyno NOT LIKE '%self%' AND
              biltyno NOT GLOB '*[0-9]*'
        GROUP BY biltyno_normalized
        ORDER BY count DESC
    ''')

    # Ensure that only unique Bilty No.s are passed
    seen_biltynos = set()
    for bilty in cursor.fetchall():
        if bilty['biltyno_normalized'] not in seen_biltynos:
            unique_bilty_names.append(bilty)
            seen_biltynos.add(bilty['biltyno_normalized'])

    conn.close()  # Close the database connection

    return render_template(
        'filter_by_name.html',
        entries=entries,
        unique_bilty_names=unique_bilty_names,
        searched_name=searched_name,
        selected_biltyno=selected_biltyno  # Pass the selected Bilty No. to the template
    )
