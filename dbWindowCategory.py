import re
from sqlalchemy import create_engine, Column, Integer, String, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base  # Import declarative_base from the orm module

from dbCreate import LogEntry  # Make sure to import LogEntry from your dbCreate file

# Create the database engine
engine = create_engine('sqlite:///window_activity.db')

# Define the declarative base
Base = declarative_base()

# Define the WindowCategory table structure
class WindowCategory(Base):
    __tablename__ = 'window_categories'
    id = Column(Integer, primary_key=True, autoincrement=True)
    window_title = Column(String)
    window_url_base = Column(String)
    window_category = Column(String)
    row_count = Column(Integer)  # Add a column for the row count

# Create the table if it doesn't exist
Base.metadata.create_all(engine)

# Create a session to interact with the database
Session = sessionmaker(bind=engine)
session = Session()

categories = [
    {'name': 'Games', 'regex': r'(game|steam|gaming|MTGA|solitaire)', 'priority': 4},
    {'name': 'Homework', 'regex': r'(HW1|HW2|HW3|homework|CS236|Ed Discussion|study|lecture)', 'priority': 3},
    {'name': 'Coding', 'regex': r'(Visual Studio Code | Windows Powershell | .db |.py )', 'priority': 2},
    {'name': 'Productivity', 'regex': r'(mail)', 'priority': 1},
    {'name': 'Other', 'regex': r'.*', 'priority': 0},  # Default category
]

# Query the top 5 rows from the log_entries table
# activity_category = session.query(LogEntry.window_title, LogEntry.window_url_base).distinct().all()

activity_category = session.query(LogEntry.window_title, LogEntry.window_url_base) \
    .filter(LogEntry.window_title.isnot(None), LogEntry.window_title != '') \
    .distinct() \
    .all()

def categorize_window_title(window_title):
    for category in categories:
        if re.search(category['regex'], window_title, re.IGNORECASE):
            return category['name']
    return 'Other'  # Default category

# Function to get the count of rows for a given window_title and window_url_base
def get_row_count(window_title, window_url_base):
    return session.query(func.count(LogEntry.id)) \
        .filter(
            LogEntry.window_title == window_title,
            LogEntry.window_url_base == window_url_base
        ) \
        .scalar()

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