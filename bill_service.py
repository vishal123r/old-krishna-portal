import sqlite3

class BillService:
    def __init__(self, db_path='crm.db'):
        self.db_path = db_path

    def get_bill_entries(self, start=1, end=100):
        """Fetch bill entries from the database between the given range."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        query = '''SELECT id, billno, amount, date FROM customers WHERE id BETWEEN ? AND ?'''
        cursor.execute(query, (start, end))
        bill_entries = cursor.fetchall()
        conn.close()
        return bill_entries

    def get_bill_by_id(self, bill_id):
        """Fetch a specific bill entry by ID."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        query = '''SELECT * FROM customers WHERE id = ?'''
        cursor.execute(query, (bill_id,))
        bill_details = cursor.fetchone()
        conn.close()
        return bill_details
