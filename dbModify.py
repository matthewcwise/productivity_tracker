from sqlalchemy import create_engine, MetaData, Table, Column, String, text

# Connect to the existing database
engine = create_engine('sqlite:///window_activity.db')

# Create metadata instance
metadata = MetaData()

# Reflect the log_entries table
log_entries = Table('log_entries', metadata, autoload_with=engine)

# Add the new column if it doesn't already exist
if not hasattr(log_entries.c, 'flow_score'):
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE log_entries ADD COLUMN flow_score STRING;"))

print("Column 'flow_score' added successfully.")

# from sqlalchemy import create_engine, MetaData, Table, text

# # Connect to the existing database
# engine = create_engine('sqlite:///window_activity.db')

# # Create metadata instance
# metadata = MetaData()

# # Reflect the log_entries table
# log_entries = Table('log_entries', metadata, autoload_with=engine)

# # Rename the "secondary" column to "domain" and "primary_window" column to "detail"
# with engine.connect() as conn:
#     # Rename "secondary" to "domain"
#     conn.execute(text("ALTER TABLE log_entries RENAME COLUMN secondary TO domain;"))
#     # Rename "primary_window" to "detail"
#     conn.execute(text("ALTER TABLE log_entries RENAME COLUMN primary_window_str TO detail;"))

# print("Columns renamed successfully.")
