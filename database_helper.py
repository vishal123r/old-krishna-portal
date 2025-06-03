import sqlite3

class DatabaseHelper:
    def __init__(self, db_name):
        self.db_name = db_name

    def get_connection(self):
        conn = sqlite3.connect(self.db_name)
        return conn

    def fetch_weekly_entries(self, start_date, end_date):
        query = '''
            SELECT khccode, billno, biltyno, firmname, city, mobile, additional_mobile, amount, date
            FROM customers
            WHERE date BETWEEN ? AND ? 
            ORDER BY date DESC
        '''
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, (start_date, end_date))
        rows = cursor.fetchall()
        conn.close()
        return rows
