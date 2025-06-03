import os
import sqlite3
import logging
import shutil

class BackupManager:
    def __init__(self, source_db="crm.db", backup_folder="data", backup_db="chat.db"):
        self.source_db = source_db  # Original Database
        self.backup_folder = backup_folder  # Folder to Store Backup
        self.backup_db = os.path.join(backup_folder, backup_db)  # Backup Database Path

        # ✅ Ensure Backup Folder Exists
        os.makedirs(self.backup_folder, exist_ok=True)

        # ✅ Logging Setup
        logging.basicConfig(level=logging.DEBUG)

    def backup_database(self):
        """ Copies all data & structure from crm.db to chat.db """
        if not os.path.exists(self.source_db):
            logging.warning("⚠ `crm.db` NOT FOUND! Backup skipped.")
            return

        try:
            source_conn = sqlite3.connect(self.source_db)
            dest_conn = sqlite3.connect(self.backup_db)
            source_cursor = source_conn.cursor()
            dest_cursor = dest_conn.cursor()
            
            # Get all tables from crm.db
            source_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = source_cursor.fetchall()
            
            for table_name in tables:
                table = table_name[0]
                
                # Get the table creation SQL
                source_cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table}';")
                create_table_sql = source_cursor.fetchone()[0]
                
                # Create table in chat.db
                dest_cursor.execute(f"DROP TABLE IF EXISTS {table};")  # Remove old table
                dest_cursor.execute(create_table_sql)
                
                # Copy all data
                source_cursor.execute(f"SELECT * FROM {table};")
                rows = source_cursor.fetchall()
                columns = [desc[0] for desc in source_cursor.description]
                placeholders = ",".join(["?" for _ in columns])
                
                dest_cursor.executemany(f"INSERT INTO {table} VALUES ({placeholders})", rows)
            
            # Commit and close connections
            dest_conn.commit()
            source_conn.close()
            dest_conn.close()
            logging.info("✅ Backup completed successfully!")

        except Exception as e:
            logging.error(f"❌ Error in database backup: {e}")

    def restore_database(self):
        """ Restores crm.db from chat.db if deleted """
        if os.path.exists(self.source_db):
            logging.info("✅ `crm.db` exists. No need to restore.")
            return

        if not os.path.exists(self.backup_db):
            logging.error("❌ No backup found! Restore failed.")
            return

        try:
            shutil.copy(self.backup_db, self.source_db)
            logging.info("✅ `crm.db` restored successfully from `chat.db`!")

        except Exception as e:
            logging.error(f"❌ Error restoring database: {e}")
