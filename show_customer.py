# show_customer.py
from flask import render_template
from staff_data import data_already_seen, mark_data_as_viewed
from customer_service import CustomerService

customer_service = CustomerService()

def show_customer_data_for_staff(staff_id):
    column_titles, customer_info = customer_service.fetch_all_customer_data()

    data_to_show = []

    for customer in customer_info:
        data_id = customer[0]  # Assuming the first column is the ID of the customer
        
        # Check if this data has already been shown today
        if not data_already_seen(staff_id, data_id):
            data_to_show.append(customer)
            # Mark the data as viewed for this staff member
            mark_data_as_viewed(staff_id, data_id)

    return render_template('customer_data.html', column_titles=column_titles, customer_info=data_to_show)
