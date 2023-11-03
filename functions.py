import sqlite3
import pandas as pd



########################
###  Logging Functions
########################
# Initialize the event counters
key_count = 0
mouse_count = 0

# Keyboard event handler
def on_press(key):
    global key_count
    key_count += 1
    print("key count:",key_count)

# Mouse event handlers
def on_click(x, y, button, pressed):
    global mouse_count
    mouse_count += 1
    print("mouse_count:",mouse_count)

def on_scroll(x, y, dx, dy):
    global mouse_count
    mouse_count += 1
    print("mouse_count:",mouse_count)

# Reset event counters
def reset_event_counters():
    global mouse_count, key_count
    mouse_count = 0
    key_count = 0
    print("key count:",key_count)
    print("mouse_count:",mouse_count)


# def get_current_session_number():
#     # Query the maximum session_number in the database
#     max_session_number = session.query(func.max(LogEntry.session_number)).scalar()
#     return max_session_number + 1 if max_session_number is not None else 1

# Define global event counters
#### KEYBOARD / MOUSE LOGGING FUNCTIONS
# Function to reset event counters

# Function to extract website URL
# def extract_current_url():
#     """Extracts the current URL using Selenium."""
#     try:
#         # Get the current URL
#         current_url = driver.current_url
#         return current_url
#     except Exception as e:
#         print(f"Error extracting current URL: {str(e)}")

# from sqlalchemy import create_engine, MetaData, Table

# def sqliteDropTable(table, engine='sqlite:///window_activity.db')
#     # Create a database engine
#     engine = create_engine(engine)

#     # Create a metadata object
#     metadata = MetaData()

#     # Define the table you want to drop
#     your_table = Table(table, metadata, autoload_with=engine)

#     # Drop the table
#     your_table.drop(engine)



# # Function to delete rows from SQL table
# import sqlite3

# # Connect to the SQLite database
# conn = sqlite3.connect('window_activity.db')  # Replace 'your_database.db' with your database file name
# cursor = conn.cursor()

# # Step 1: Delete the first 300 rows
# delete_query = "DELETE FROM log_entries WHERE rowid < 197;"
# cursor.execute(delete_query)

# # Commit the changes and close the database connection
# conn.commit()
from sqlalchemy import text
from sqlalchemy import create_engine, text

def wrap_text(text, limit=20):
    """
    Wrap text to ensure that it fits within a specified width when plotted.
    """
    import textwrap
    return textwrap.fill(text, limit)


def get_data_from_query(query, engine = create_engine('sqlite:///window_activity.db')):
    with engine.connect() as connection:
        result = connection.execute(text(query))
        rows = result.fetchall()
    
    if not rows:
        print(f"No data found for the query: {query}")
        return None

    return rows

def create_or_replace_view(view_name, query, db_path='sqlite:///window_activity.db'):
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(db_path)

        cursor = conn.cursor()
        
        # Drop the view if it already exists
        cursor.execute(f"DROP VIEW IF EXISTS {view_name};")
        
        # Create the view
        cursor.execute(f"CREATE VIEW {view_name} AS {query};")
        
        # Commit the transaction
        conn.commit()
        
        print(f"View {view_name} created (or replaced) successfully.")
        
    except sqlite3.Error as e:
        print(f"Error: {e}")
    finally:
        # Close the database connection
        if conn:
            conn.close()

##########################################
## Window Category Work
##########################################
