import re
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
    if window_title == "Figure 1":
        return "Visual Studio Code"
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
    if window_title == "Figure 1":
        return "prod", "Figure 1"
    abbreviated = window_title.split(" - Visual Studio Code")[0].strip()
    folder = abbreviated.split("-")[1].strip()
    file = abbreviated.split("-")[0].strip()
    return folder, file


chat_gpt_conversations = {
    "Session Tracking Logic":"prod",
    "Rename Columns in DB":"prod",
                          }

enders = [" - Google Chrome",
          "- Visual Studio Code",
          "| LinkedIn",
          "- Slack",
          "- Search",
          "- Wikipedia",
          "- Google Sheets",
          "- Google Docs",
          "| ESPN",
          "- Watch ESPN",
          "- YouTube"
          "NCAA.com"]            
beginners = ["Amazon.com",
             "Meet - ",
             "Google Calendar - ",
             "TherapyAI - Calendar - ",
             "- YouTube",
             "Messenger",
             "Slack", "Search", "Wikipedia", "Google Sheets", "ESPN", "Your Orders"]

def chrome_breakdown(window_title):
    abbreviated = window_title.split(" - Google Chrome")[0].strip()
    domain = abbreviated
    detail = None
    # try:
    #     # This is the list of ChatGPT conversations
        
    if abbreviated in chat_gpt_conversations:
        domain = "ChatGPT"
        detail = abbreviated
        return domain, detail
    elif abbreviated.endswith("Messenger"):
        domain = "FacebookMessenger"
        detail = abbreviated.split("| Messenger")[0].strip()
        return domain, detail
    for beginner in beginners:
        if abbreviated.startswith(beginner):
            # domain = beginner
            domain = re.sub(r'[ \|\:\;\-]', '', beginner)
            detail = abbreviated.split(beginner)[1].strip()
            return domain, detail
    for end in enders:
        if abbreviated.endswith(end):
            # domain = abbreviated.split(end)[0].strip()
            domain = re.sub(r'[ \|\:\;\-]', '', end)
            detail = abbreviated.split(end)[0].strip()
            return domain, detail
    return domain, detail


        # elif abbreviated.startswith("Amazon.com"):
        #     domain = "Amazon.com"
        #     detail = abbreviated.split(":")[1].strip()

        # elif abbreviated.startswith("Google Calendar"):
        #     domain = "Google Calendar"
        #     detail = abbreviated.split("Calendar -")[1].strip()

        # elif abbreviated.endswith("LinkedIn"):
        #     domain = "LinkedIn"
        #     detail = abbreviated.split("| LinkedIn")[0].strip()
            
        # elif abbreviated.endswith("YouTube"):
        #     domain = "YouTube"
        #     detail = abbreviated.split("- YouTube")[0].strip()
            
            
        # elif abbreviated.endswith("- Slack"):
        #     domain = "Slack"
        #     detail = abbreviated.split("- Slack")[0].strip()

        # elif abbreviated.endswith("- Search"):
        #     domain = "Search"
        #     detail = abbreviated.split("- Search")[0].strip()

        # elif abbreviated.endswith("- Wikipedia"):
        #     domain = "Wikipedia"
        #     detail = abbreviated.split("- Wikipedia")[0].strip()

        # elif abbreviated.endswith("- Google Sheets"):
        #     domain = "Google Sheets"
        #     detail = abbreviated.split("- Google Sheets")[0].strip()

        # elif abbreviated.endswith("ESPN"):
        #     domain = "ESPN"
        #     detail = abbreviated.split("| ESPN")[0].strip()
        #     detail = detail.split("- Watch ESPN")[0].strip()
            
        # elif abbreviated == "Your Orders":
        #     domain = "Amazon.com"
        #     detail = "Your Orders"

        # else:
        #     domain = abbreviated
        #     detail = None
        

    # except:
    #     return None, None



def assign_container_detail(window_title, application):
    # try:
    if application == "Visual Studio Code":
        return vs_code_breakdown(window_title)
    elif application == "Google Chrome":
        return chrome_breakdown(window_title)
    else:
        return None, None
    # except:
    #     return None, None


def determine_project(application, container, detail, previous_project):
    if application == "Visual Studio Code":
        return container
    
    if application == "WhatsApp":
        return "Communication"
    
    # if application in ["pgAdmin 4", "Calculator", "Task Switching"]:
    #     return previous_project
    
    if detail in ["Matt/Thomas 1:1 (recurring)", "Notes - Matt/Thomas 1:1 (recurring)"]:
        return "Matt/Thomas 1:1"
    
    elif application == "Google Chrome":
        if container == "ChatGPT":
            if detail in chat_gpt_conversations:
                return chat_gpt_conversations[detail]
            else:
                return previous_project
        else:
            return container
    else:
        return application

def update_focus_flow(old_flow_score, old_focus_score, 
                      project, previous_project, 
                      window_title, previous_window_title,
                      keyboard_events, mouse_events,
                      alpha = 0.15,
                      max_events = 20
                      ):
    """Update the focus and flow scores.
    These increment when there is activity and the thing remains the same. They reset when there is a switch. They do not change when the the thing remains the same but there is no activity. We don't penalize inactivity here bc there could be valuable things going on, but we don't want to automatically count it as a flow/focus.    
    """
    events = keyboard_events + mouse_events
    # Update focus_score
    if project == previous_project:
        row_focus_score = min(events/max_events, 1)
    else:
        row_focus_score = 0
        
    if window_title == previous_window_title:
        row_flow_score = min(events/max_events, 1)
    else:
        row_flow_score = 0
        
    flow_score = alpha * row_flow_score + (1 - alpha) * old_flow_score
    focus_score = alpha * row_focus_score + (1 - alpha) * old_focus_score

    return round(focus_score, 3), round(flow_score, 3)


def process_row(window_title, previous_project, previous_window_title, keyboard_events, mouse_events, focus_score, flow_score):
    window_title = clean_window_title(window_title)
    application = determine_application(window_title)
    domain, detail = assign_container_detail(window_title, application)
    project = determine_project(application, domain, detail, previous_project)
    focus_score, flow_score = update_focus_flow(flow_score, focus_score, 
                      project, previous_project, 
                      window_title, previous_window_title,
                      keyboard_events, mouse_events
                      )
    return window_title, application, domain, detail, project, focus_score, flow_score

# def update_focus_flow(flow_score, focus_score, 
#                       project, previous_project, 
#                       window_title, previous_window_title,
#                       keyboard_events, mouse_events
#                       ):
#     """Update the focus and flow scores.
#     These increment when there is activity and the thing remains the same. They reset when there is a switch. They do not change when the the thing remains the same but there is no activity. We don't penalize inactivity here bc there could be valuable things going on, but we don't want to automatically count it as a flow/focus.    
#     """
#     # Update focus_score
#     if project == previous_project:
#         if keyboard_events + mouse_events > 0:
#             focus_score += 1
#     else:
#         focus_score = 0

#     # Update flow_score
#     if window_title == previous_window_title:
#         if keyboard_events + mouse_events > 0:
#             flow_score += 1
#     else:
#         flow_score = 0  # Reset

#     return focus_score, flow_score





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
# # conn.commit()
# from sqlalchemy import text
# from sqlalchemy import create_engine, text

# def wrap_text(text, limit=20):
#     """
#     Wrap text to ensure that it fits within a specified width when plotted.
#     """
#     import textwrap
#     return textwrap.fill(text, limit)


# def get_data_from_query(query, engine = create_engine('sqlite:///window_activity.db')):
#     with engine.connect() as connection:
#         result = connection.execute(text(query))
#         rows = result.fetchall()
    
#     if not rows:
#         print(f"No data found for the query: {query}")
#         return None

#     return rows

# def create_or_replace_view(view_name, query, db_path='sqlite:///window_activity.db'):
#     try:
#         # Connect to the SQLite database
#         conn = sqlite3.connect(db_path)

#         cursor = conn.cursor()
        
#         # Drop the view if it already exists
#         cursor.execute(f"DROP VIEW IF EXISTS {view_name};")
        
#         # Create the view
#         cursor.execute(f"CREATE VIEW {view_name} AS {query};")
        
#         # Commit the transaction
#         conn.commit()
        
#         print(f"View {view_name} created (or replaced) successfully.")
        
#     except sqlite3.Error as e:
#         print(f"Error: {e}")
#     finally:
#         # Close the database connection
#         if conn:
#             conn.close()

# ##########################################
# ## Window Category Work
# ##########################################



# def extract_window_details(window_title):
#     """Extract details from the window title."""
#     # Remove leading "● " if present
#     window_title = clean_window_title(window_title)

#     application = determine_application(window_title)
    
#     return {
#         "primary_detail": window_title, 
#         "secondary_detail": None,
#         "application": window_title,
#         "log_type": None
#     }

# def determine_category_and_project(window_title, application):
#     """Determine the category and project based on the window title."""
#     category = "unknown"
#     project = None
#     log_type = None

#     if application in ["Visual Studio Code", "Windows PowerShell"]:
#         log_type = "coding"

#     elif application in ["Spotify Premium"]:
#         log_type = "music"

#     elif application in ["StarCraft II"]:
#         log_type = "game"

#     if window_title and "- Visual Studio Code" in window_title:
#         project = window_title.split("-")[1].strip()
#         if project.startswith("."):
#             project = project[1:].strip()  # Remove leading dot
#         category = "Work" if project == "tai_ai_api" else "Personal Coding"

#     return category, project, log_type

# def determine_chrome_details(primary_window_str, secondary, window_title, category, project, log_type):
#     """Determine the category and project based on the window title."""

#     if window_title.startswith("Amazon.com"):
#         category = "shopping"
#         project = "shopping"
#         log_type = "shopping"

#     if primary_window_str in ["Google Calendar"]:
#         log_type = "calendar"
#         category = "calendar"
#         project = "calendar"

#     if primary_window_str in ["Messenger"]:
#         log_type = "messaging"
#         category = "communication"
#         project = "communication"
    
#     elif primary_window_str in ["Database Productivity Tracking Improvements"]:
#         project = 'prod'
#         log_type = 'coding'
#         category = 'Personal Coding'
    
#     elif primary_window_str in ["Track which conferences are winning the 2024"] or secondary in ["Stream the Game Live"]:

#         project = 'NCAAF'
#         log_type = 'football'
#         category = 'diversion'
    
        
#     return category, project, log_type
