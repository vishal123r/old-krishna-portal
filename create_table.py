import sqlite3

def drop_and_create_table():
    try:
        # Connect to the database
        conn = sqlite3.connect('crm.db')
        cursor = conn.cursor()

        # Drop the table if it exists
        cursor.execute('DROP TABLE IF EXISTS customer_commitments')

        # Create the customer_commitments table with the correct structure
        cursor.execute(''' 
            CREATE TABLE IF NOT EXISTS customer_commitments (
                commitment_id INTEGER PRIMARY KEY,
                commitment_date DATE,
                commitment_type TEXT,
                new_commitment_type TEXT,  -- This will store custom commitment types if 'Add New' is chosen
                information TEXT,          -- This will store any additional information about the commitment
                note TEXT                  -- This will store any notes regarding the commitment
            );
        ''')

        # Commit changes
        conn.commit()
        print("customer_commitments table recreated successfully.")

    except sqlite3.DatabaseError as e:
        print(f"Error creating customer_commitments table: {e}")

    finally:
        # Close the connection
        conn.close()

# Call the function to drop and create the table
drop_and_create_table()
