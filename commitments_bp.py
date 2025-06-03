from flask import Blueprint, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

# Register a custom Jinja2 filter
def custom_date_format(value):
    if isinstance(value, datetime):
        return value.strftime('%d/%m/%Y')
    return value

commitments_bp = Blueprint('commitments', __name__)

# Add the filter to the app's Jinja environment
@commitments_bp.app_context_processor
def inject_custom_filters():
    return {
        'custom_date_format': custom_date_format
    }

def get_commitments():
    try:
        # Connect to the database
        conn = sqlite3.connect('crm.db')
        cursor = conn.cursor()

        # Fetch all commitments from the database, ordered by commitment_date descending
        cursor.execute('''
            SELECT commitment_id, commitment_date, commitment_type, new_commitment_type, information, note 
            FROM customer_commitments
            ORDER BY commitment_date ASC        
        ''')
        commitments = cursor.fetchall()

        # Convert commitment_date from string to datetime object and format it as dd/mm/yyyy
        for i in range(len(commitments)):
            commitment_date_str = commitments[i][1]
            commitment_date = datetime.strptime(commitment_date_str, '%Y-%m-%d')  # Convert string to datetime
            commitments[i] = commitments[i][:1] + (commitment_date.strftime('%d/%m/%Y'),) + commitments[i][2:]

        # Close the connection
        conn.close()

        return commitments
    except sqlite3.DatabaseError as e:
        print(f"Error fetching commitments: {e}")
        return []

def delete_commitment(commitment_id):
    try:
        # Connect to the database
        conn = sqlite3.connect('crm.db')
        cursor = conn.cursor()

        # Delete the commitment with the given ID
        cursor.execute('DELETE FROM customer_commitments WHERE commitment_id = ?', (commitment_id,))

        # Commit changes
        conn.commit()
        conn.close()
        print(f"Commitment with ID {commitment_id} deleted successfully.")

    except sqlite3.DatabaseError as e:
        print(f"Error deleting commitment: {e}")

@commitments_bp.route('/commitments', methods=['GET'])
def commitments_page():
    commitments = get_commitments()
    return render_template('commitments.html', commitments=commitments)

@commitments_bp.route('/add_commitment', methods=['GET', 'POST'])
def add_commitment():
    if request.method == 'POST':
        try:
            # Get the form data
            commitment_date = request.form['commitment_date']
            commitment_type = request.form['commitment_type']

            # Check if a custom commitment type was entered
            if commitment_type == 'Add New':
                commitment_type = request.form['new_commitment_type']
            
            information = request.form['information']
            note = request.form['note']

            # Ensure 'information' and 'note' are optional (if empty, set to NULL)
            if not information:
                information = None
            if not note:
                note = None

            # Connect to the database
            conn = sqlite3.connect('crm.db')
            cursor = conn.cursor()

            # Insert new commitment into the database
            cursor.execute(''' 
                INSERT INTO customer_commitments (commitment_date, commitment_type, new_commitment_type, information, note)
                VALUES (?, ?, ?, ?, ?)
            ''', (commitment_date, commitment_type, commitment_type if commitment_type == 'Add New' else '', information, note))

            # Commit changes
            conn.commit()
            conn.close()

            # Redirect to the commitments page
            return redirect(url_for('commitments.commitments_page'))

        except sqlite3.DatabaseError as e:
            print(f"Error inserting commitment: {e}")
            return f"Error adding commitment: {e}"
    
    # Handle GET request (when accessing the page directly)
    return render_template('commitments.html', commitments=get_commitments())

@commitments_bp.route('/delete_commitment/<int:commitment_id>', methods=['POST'])
def delete_commitment_route(commitment_id):
    delete_commitment(commitment_id)
    return redirect(url_for('commitments.commitments_page'))
