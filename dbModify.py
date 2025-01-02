from sqlalchemy import create_engine, MetaData, Table, Column, String, text

# Connect to the existing database
engine = create_engine('sqlite:///window_activity.db')

# Create metadata instance
metadata = MetaData()

# Reflect the log_entries table
log_entries = Table('log_entries', metadata, autoload_with=engine)

# Add the new column if it doesn't already exist
if not hasattr(log_entries.c, 'primary_window_str'):
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE log_entries ADD COLUMN primary_window_str STRING;"))

print("Column 'primary_window_str' added successfully.")
