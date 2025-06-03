import sqlite3
from flask import Blueprint, render_template, request, redirect, url_for
from collections import defaultdict

# Create the blueprint for transport details
transport_detail_bp = Blueprint('transport_detail_bp', __name__)

@transport_detail_bp.route('/transport_detail', methods=['GET', 'POST'])
def transport_detail():
    conn = sqlite3.connect('crm.db')
    cursor = conn.cursor()

    # Fetch all the transport services data from the customers table, grouped by city
    cursor.execute('''
        SELECT transport_name, transport_number, city 
        FROM customers
        WHERE city IS NOT NULL
    ''')
    transport_services = cursor.fetchall()

    # Close the database connection
    conn.close()

    # Group the transport services by city
    grouped_transport_services = defaultdict(list)

    # Filter out the "None" values and remove duplicates
    for service in transport_services:
        transport_name, transport_number, city = service
        if transport_name and transport_number and transport_name != "None" and transport_number != "None":
            if (transport_name, transport_number) not in grouped_transport_services[city]:
                grouped_transport_services[city].append((transport_name, transport_number))

    # Render the transport_detail.html page and pass the data to the template
    return render_template('transport/transport_detail.html', grouped_transport_services=grouped_transport_services)

