from sqlalchemy import inspect

def get_tables_info(db):
    # Use db.engine to access the underlying SQLAlchemy engine
    inspector = inspect(db.engine)
    
    # Get all table names
    tables = inspector.get_table_names()
    
    tables_info = {}

    for table_name in tables:
        # Get columns for each table
        columns = [column['name'] for column in inspector.get_columns(table_name)]
        tables_info[table_name] = columns

    return tables_info
