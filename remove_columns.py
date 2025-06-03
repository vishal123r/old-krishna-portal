import sqlite3
import os

# Source database file
source_db_name = "crm.db"

# Backup database file
backup_db_name = "crm_backup.db"

# Connect to the source database
conn = sqlite3.connect(source_db_name)
cursor = conn.cursor()

# Connect to the backup database (it will create the backup if it doesn't exist)
backup_conn = sqlite3.connect(backup_db_name)
backup_cursor = backup_conn.cursor()

# Get the list of all tables in the source database, skipping internal tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name != 'sqlite_sequence';")
tables = cursor.fetchall()

# Copy each table from the source database to the backup database
for table in tables:
    table_name = table[0]

    # Get the schema of the table (this includes column names and types)
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = cursor.fetchall()

    # Create the same table in the backup database
    column_definitions = ", ".join([f"{col[1]} {col[2]}" for col in columns])
    backup_cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({column_definitions})")

    # Copy data from the source table to the backup table
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()

    # Insert data into the backup table using INSERT OR REPLACE to handle unique constraint issues
    for row in rows:
        placeholders = ", ".join(["?" for _ in row])
        backup_cursor.execute(f"INSERT OR REPLACE INTO {table_name} VALUES ({placeholders})", row)

# Commit and close both connections
backup_conn.commit()
backup_conn.close()
conn.close()

print(f"✅ Backup of {source_db_name} structure and data saved in {backup_db_name}")
