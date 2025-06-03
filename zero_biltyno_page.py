from flask import Blueprint, render_template
import sqlite3

# Create a blueprint for zero_biltyno_page
zero_biltyno_bp = Blueprint('zero_biltyno', __name__)

@zero_biltyno_bp.route('/')  # The route should be the root of the blueprint
def show_zero_biltyno_page():
    """Route to show customers with biltyno 0.00 or various zero formats."""
    # Connect to the database
    try:
        with sqlite3.connect('crm.db') as conn:
            conn.row_factory = sqlite3.Row  # This allows us to access columns by name
            cursor = conn.cursor()

            # Query to get customer data from the 'customers' table where biltyno is in any zero format
            cursor.execute('''SELECT * FROM customers WHERE biltyno IS NULL OR
                              biltyno = 0 OR
                              biltyno = 0.00 OR
                              biltyno = "0" OR
                              biltyno = "00" OR
                              biltyno = "000" OR
                              biltyno = "0000" OR
                              biltyno = "00000" OR
                              biltyno = "000000";''')
            customers = cursor.fetchall()

    except sqlite3.Error as e:
        customers = []
        print(f"Error while accessing database: {e}")

    # Return the template with the customer data
    return render_template('zero_biltyno_page.html', customers=customers)
