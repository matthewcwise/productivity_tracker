import re
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

from dbCreate import LogEntry  # Import the LogEntry class from your database definition file

# Create the database engine
engine = create_engine('sqlite:///window_activity.db')

# Define the declarative base
Base = declarative_base()

# Define the WindowCategory table structure
class WindowCategory(Base):
    __tablename__ = 'window_categories'
    id = Column(Integer, primary_key=True, autoincrement=True)
    window_title = Column(String)
    window_url = Column(String)
    window_url_base = Column(String)
    window_category = Column(String)

# Create a session to interact with the database
Session = sessionmaker(bind=engine)
session = Session()

# Query the top 5 rows from the log_entries table
activity_category = session.query(LogEntry.window_title, LogEntry.window_url_base).distinct().all()

def categorize_window_title(window_title):
    for category in categories:
        if re.search(category['regex'], window_title, re.IGNORECASE):
            return category['name']
    return 'Other'  # Default category

categories = [
    {'name': 'Games', 'regex': r'(game|steam|gaming|MTGA|solitaire)', 'priority': 4},
    {'name': 'Homework', 'regex': r'(HW1|HW2|HW3|homework|CS236|Ed Discussion|study|lecture)', 'priority': 3},
    {'name': 'Coding', 'regex': r'(VS Code)', 'priority': 2},
    {'name': 'Productivity', 'regex': r'(mail)', 'priority': 1},
    {'name': 'Other', 'regex': r'.*', 'priority': 0},  # Default category
]

# Populate the WindowCategory table with distinct window titles and their categories
for title in activity_category:
    window_title = title[0]
    window_category = categorize_window_title(window_title)
    
    # Create a new WindowCategory entry
    new_category = WindowCategory(window_title=window_title, window_category=window_category)
    
    # Add the new entry to the session
    session.add(new_category)

# Commit the changes to the database
session.commit()

# Close the session
session.close()