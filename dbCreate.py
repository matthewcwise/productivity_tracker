#####################################################################
#####################################################################
#####################################################################
#####################################################################
#######                                                       #######
#######                                                       #######
#######         Create Databases, Declare Achitecture         #######
#######                                                       #######
#######                                                       #######
#####################################################################
#####################################################################
#####################################################################



from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base

# Create a SQLite database engine that will manage the local database file 'window_activity.db'.
engine = create_engine('sqlite:///window_activity.db')

# Define a declarative base class from which all mapped classes should inherit.
Base = declarative_base()

# Define the 'LogEntry' table structure using SQLAlchemy ORM modeling.
class LogEntry(Base):
    __tablename__ = 'log_entries'  # Specifies the name of the table in the database

    # Define the columns of the table:
    id = Column(Integer, primary_key=True)  # Primary key column, uniquely identifies each record
    timestamp = Column(DateTime)  # Records the date and time of the log entry
    date = Column(String)  # Records the date as a string
    hour = Column(Integer)  # Records the hour of the log entry
    minute = Column(Integer)  # Records the minute of the log entry
    window_url = Column(String)  # URL of the window being logged
    window_url_base = Column(String)  # Base URL of the window, possibly for easier categorization
    window_title = Column(String)  # Title of the window
    keyboard_events = Column(Integer)  # Number of keyboard events during the logged time
    mouse_events = Column(Integer)  # Number of mouse events during the logged time

class LogEntryAgg(Base):
    __tablename__ = 'LogEntryAgg'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime)
    date = Column(String)
    hour = Column(Integer)
    minute = Column(Integer)
    window_url = Column(String)
    window_url_base = Column(String)
    window_title = Column(String)
    keyboard_events = Column(Integer)
    mouse_events = Column(Integer)

# Define the 'WindowCategory' table structure.
class WindowCategory(Base):
    __tablename__ = 'window_categories'  # Table name in the database

    # Define the columns of the table:
    id = Column(Integer, primary_key=True, autoincrement=True)  # Auto-incremented primary key
    window_title = Column(String)  # Title of the window for categorization
    window_url_base = Column(String)  # Base URL for categorization
    window_category = Column(String)  # Categorical label assigned to the window
    row_count = Column(Integer)  # Potential count of rows, possibly indicating the number of occurrences

# Apply the defined table structures to the connected database.
Base.metadata.create_all(engine)