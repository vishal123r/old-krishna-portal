import sqlite3

# Create a connection to the SQLite database (this will create the db file if it doesn't exist)
conn = sqlite3.connect('transport.db')

# Create a cursor object to execute SQL commands
cursor = conn.cursor()

# Create the transport_services table if it doesn't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS transport_services (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    cities TEXT,
    districts TEXT,
    states TEXT,
    UNIQUE(name)  -- Ensure name is unique to prevent duplicates
)
''')

# Function to check if a transport service exists
def check_if_service_exists(service_name):
    cursor.execute("SELECT 1 FROM transport_services WHERE name = ?", (service_name,))
    return cursor.fetchone() is not None

# Sample data
transport_services = [
    ('Sri Transport', 'A trusted transport company', 'City1, City2', 'District1, District2', 'State1, State2'),
    ('ABC Transport', 'Fast and reliable service', 'City3, City4', 'District3, District4', 'State3, State4')
]

# Insert sample data if not already present
for service in transport_services:
    name, description, cities, districts, states = service
    if not check_if_service_exists(name):  # Check if the service already exists
        cursor.execute('''
        INSERT INTO transport_services (name, description, cities, districts, states)
        VALUES (?, ?, ?, ?, ?)
        ''', (name, description, cities, districts, states))
    else:
        print(f"Service '{name}' already exists in the database.")

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Database and table created successfully! Data insertion is handled safely.")
