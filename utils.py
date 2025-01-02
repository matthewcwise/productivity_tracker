import sqlite3
import pandas as pd

########################
###  Logging Functions
########################

# DATA CLEANUP

def clean_window_title(window_title):
    """Clean up the window title."""
    if window_title and window_title.startswith("\u25CF "):
        window_title = window_title[2:].strip()
    return window_title

def determine_application(window_title):
    if window_title.endswith(" - Google Chrome"):
        # print("Window Title Ends with Google Chrome, ", window_title)
        return "Google Chrome"
    elif window_title.endswith("- Visual Studio Code"):
        return "Visual Studio Code"
    elif window_title in ["Portal - Direct3D 9", "Windows PowerShell"]:
        return window_title
    elif "-" in window_title:
        parts = [part.strip() for part in window_title.split("-")]
        return parts[-1]
    else:
        return window_title
    
def vs_code_breakdown(window_title):
    abbreviated = window_title.split(" - Visual Studio Code")[0].strip()
    folder = abbreviated.split("-")[1].strip()
    file = abbreviated.split("-")[0].strip()
    
    return folder, file

def chrome_breakdown(window_title):
    abbreviated = window_title.split(" - Google Chrome")[0].strip()
    folder = None
    file = None

    try:
        
        if abbreviated.startswith("Amazon.com"):
            folder = "Amazon.com"
            file = abbreviated.split(":")[1].strip()

        elif abbreviated.startswith("Google Calendar"):
            folder = "Google Calendar"
            file = abbreviated.split("Calendar -")[1].strip()

        elif abbreviated.endswith("LinkedIn"):
            folder = "LinkedIn"
            file = abbreviated.split("| LinkedIn")[0].strip()
            
        elif abbreviated.endswith("YouTube"):
            folder = "YouTube"
            file = abbreviated.split("- YouTube")[0].strip()
            
        elif abbreviated.endswith("Messenger"):
            folder = "Facebook Messenger"
            file = abbreviated.split("| Messenger")[0].strip()
            
        elif abbreviated.endswith("- Slack"):
            folder = "Slack"
            file = abbreviated.split("- Slack")[0].strip()

        elif abbreviated.endswith("- Search"):
            folder = "Search"
            file = abbreviated.split("- Search")[0].strip()

        elif abbreviated.endswith("- Wikipedia"):
            folder = "Wikipedia"
            file = abbreviated.split("- Wikipedia")[0].strip()

        elif abbreviated.endswith("- Google Sheets"):
            folder = "Google Sheets"
            file = abbreviated.split("- Google Sheets")[0].strip()

        elif abbreviated == "Your Orders":
            folder = "Amazon.com"
            file = "Your Orders"

        else:
            folder = abbreviated
            file = None

        # if primary_window_str in ["Messenger"]:
        #     log_type = "messaging"
        #     category = "communication"
        #     project = "communication"
        
        # elif primary_window_str in ["Database Productivity Tracking Improvements"]:
        #     project = 'prod'
        #     log_type = 'coding'
        #     category = 'Personal Coding'
        
        # elif primary_window_str in ["Track which conferences are winning the 2024"] or secondary in ["Stream the Game Live"]:

        #     project = 'NCAAF'
        #     log_type = 'football'
        #     category = 'diversion'
        
        return folder, file
    except:
        return None, None

def assign_container_detail(window_title, application):
    try:
        if application == "Visual Studio Code":
            return vs_code_breakdown(window_title)
        elif application == "Google Chrome":
            return chrome_breakdown(window_title)
        else:
            return None, None
    except:
        return None, None

    

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
