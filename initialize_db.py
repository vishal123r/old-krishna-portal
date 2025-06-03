import sqlite3

def create_tables(cursor):
    # Create customers table
    cursor.execute('''CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        khccode TEXT NOT NULL,
        billno TEXT NOT NULL,
        biltyno TEXT NOT NULL,
        date TEXT NOT NULL,
        firmname TEXT NOT NULL,
        city TEXT NOT NULL,
        mobile TEXT NOT NULL,
        amount REAL NOT NULL,
        receive_amount REAL NOT NULL,
        delivery TEXT,
        payment_status TEXT NOT NULL,
        payment_received_date TEXT,
        transport_name TEXT,
        transport_number TEXT,
        bill_image TEXT,
        bilty_image TEXT,
        pincode TEXT NOT NULL DEFAULT "",
        state TEXT NOT NULL DEFAULT "",
        name TEXT,
        status TEXT
    )''')

    # Create payment_history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payment_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            date TEXT,
            amount REAL,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        )
    ''')

    # Create bills table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL
        )
    ''')

def initialize_database():
    conn = sqlite3.connect('crm.db')
    cursor = conn.cursor()
    create_tables(cursor)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    initialize_database()
