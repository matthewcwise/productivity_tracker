from sqlalchemy import create_engine, Column, Integer, String, func
from sqlalchemy import or_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
from dbCreate import LogEntry2, WindowCategory  # Make sure to import LogEntry from your dbCreate file
from functions import *

import re

# Create the database engine
engine = create_engine('sqlite:///window_activity.db')

# Define the declarative base
Base = declarative_base()


# Create the table if it doesn't exist
Base.metadata.create_all(engine)

# Create a session to interact with the database
Session = sessionmaker(bind=engine)
session = Session()

# Delete all rows from the window_categories table
session.query(WindowCategory).delete()
session.commit()

categories = [
    {'name': 'Games', 'regex': r'(game|steam|gaming|MTGA|solitaire)', 'priority': 10},
    {'name': 'RPA', 'regex': r'(HBS|HBR|flow chart tools|pdf text extraction|Disruptive Innovation|Christensen|Rose Park)', 'priority': 5},
    {'name': 'School', 'regex': r'(vae|QueueStatus|HW1|HW2|HW3|overleaf|logits|temperature scal|homework|softmax|Latex|CS236|Gradescope|AI Project|Ed Discussion|study|lecture)', 'priority': 5},
    {'name': 'Coding', 'regex': r'(nltk|root@family|SQLite|optimize code|hugging face|hugging_face|huggingface|Jupyter|Python|Visual Studio Code|Windows Powershell|.db|.py)', 'priority': 4},
    {'name': 'Communication', 'regex': r'(1:1 note|zoom|inbox|mail|messenger|outlook)', 'priority': 3},
    {'name': 'Gospel', 'regex': r'(priesthood|LDS|Book of Mormon|scripture|spirit)', 'priority': 3},
    {'name': 'Productivity', 'regex': r'(calendar|productivity dash|mouse activity vis|productivity app|ChatGPT)', 'priority': 2},
    {'name': 'Job Hunt', 'regex': r'(resume)', 'priority': 1},
    {'name': 'Finances', 'regex': r'(Mint|Ally|MACU|Wells Fargo|Chase)', 'priority': 1},
    {'name': 'None', 'regex': r'(Windows Default Lock Screen)', 'priority': 1},
    {'name': 'Documents', 'regex': r'(google docs)', 'priority': 2},
    {'name': 'Video', 'regex': r'(YouTube)', 'priority': 1},
    {'name': 'Other', 'regex': r'.*', 'priority': 0},  # Default category
]

# Function to get the count of rows for a given window_title and window_url_base
def get_row_count(window_title, window_url_base):
    return session.query(func.count(LogEntry2.id)) \
        .filter(
            LogEntry2.window_title == window_title,
            LogEntry2.window_url_base == window_url_base,
            or_(LogEntry2.keyboard_events != 0, LogEntry2.mouse_events != 0)  # new line to filter out unwanted rows
        ) \
        .scalar()

def categorize_window_title(window_title):
    for category in categories:
        if re.search(category['regex'], window_title, re.IGNORECASE):
            return category['name']
    return 'Other'  # Default category

# Query the active rows from the log_entries table
activity_category = session.query(LogEntry2.window_title, LogEntry2.window_url_base) \
    .filter(LogEntry2.window_title.isnot(None), LogEntry2.window_title != '') \
    .filter((LogEntry2.keyboard_events != 0) | (LogEntry2.mouse_events != 0)) \
    .distinct() \
    .all()

# Populate the WindowCategory table with distinct window titles and their categories
for title, url_base in activity_category:
    window_title = title
    window_category = categorize_window_title(window_title)
    
    # Get the row count using the get_row_count function
    row_count = get_row_count(window_title, url_base)
    
    # Create a new WindowCategory entry
    new_category = WindowCategory(
        window_title=window_title, 
        window_url_base=url_base, 
        window_category=window_category, 
        row_count=row_count
    )
    
    # Add the new entry to the session
    session.add(new_category)

# Commit the changes to the database
session.commit()

# Close the session
session.close()