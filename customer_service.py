# customer_service.py
import sqlite3

class CustomerService:
    def fetch_all_customer_data(self):
        conn = sqlite3.connect('crm.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, email, phone, address FROM customers')
        customer_info = cursor.fetchall()
        column_titles = ['ID', 'Name', 'Email', 'Phone', 'Address']  # Customize this based on your table
        conn.close()
        return column_titles, customer_info
