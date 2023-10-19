import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('window_activity.db')  # Replace 'your_database.db' with your database file name
cursor = conn.cursor()

# Step 1: Delete the first 300 rows
delete_query = "DELETE FROM log_entries WHERE rowid < 197;"
cursor.execute(delete_query)

# Commit the changes and close the database connection
conn.commit()
conn.close()
