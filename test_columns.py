from sqlalchemy import create_engine, MetaData, Table

# Connect to the database
engine = create_engine('sqlite:///window_activity.db')

# Create a metadata instance
metadata = MetaData()

# Reflect the table
log_entries = Table('log_entries', metadata, autoload_with=engine)

# Print the column names and types
print("Columns in the 'log_entries' table:")
for column in log_entries.columns:
    print(f"{column.name}: {column.type}")
