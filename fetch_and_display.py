import sqlite3

class CustomerService:
    def __init__(self, db_path='crm.db'):
        self.db_path = db_path

    def fetch_all_customer_data(self):
        """Sabhi customer data ko descending order mein fetch karo."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Customers table se data fetch karo, order by id descending
        cursor.execute("SELECT id, name, date FROM customers ORDER BY id DESC LIMIT 5")  # Top 5 records

        # Data ko fetch karo
        customer_data = cursor.fetchall()

        # Columns ke naam ko fetch karo
        column_titles = [description[0] for description in cursor.description]

        # Database mein date ka format dekhne ke liye print karo
        if customer_data:
            print("Sample date format from database entries:")
            for row in customer_data:
                print(f"ID: {row[0]}, Name: {row[1]}, Date: {row[2]}")

        conn.close()  # Connection close karo

        return column_titles, customer_data
