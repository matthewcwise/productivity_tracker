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
    # Primary key column, uniquely identifies each record
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime)  # Records the date and time of the log entry
    date = Column(String)  # Records the date as a string
    hour = Column(Integer)  # Records the hour of the log entry
    minute = Column(Integer)  # Records the minute of the log entry
    url = Column(String)  # URL of the window being logged
    url_abbrev = Column(String)  # Abbreviated URL of the window
    # Base URL of the window, possibly for easier categorization
    window_url_base = Column(String)
    window_title = Column(String)  # Title of the window
    # Number of keyboard events during the logged time
    keyboard_events = Column(Integer)
    # Number of mouse events during the logged time
    mouse_events = Column(Integer)

# Define the 'LogEntryAgg' table structure using SQLAlchemy ORM modeling.


class LogEntryAgg(Base):
    __tablename__ = 'log_entries_agg'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime)
    date = Column(String)
    hour = Column(Integer)
    minute = Column(Integer)
    url = Column(String)
    url_abbrev = Column(String)
    window_url_base = Column(String)
    window_title = Column(String)
    keyboard_events = Column(Integer)
    mouse_events = Column(Integer)

# Define the 'WindowCategory' table structure.


class WindowCategory(Base):
    __tablename__ = 'window_categories'  # Table name in the database

    # Define the columns of the table:
    # Auto-incremented primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    window_title = Column(String)  # Title of the window for categorization
    window_url_base = Column(String)  # Base URL for categorization
    # Categorical label assigned to the window
    window_category = Column(String)
    # Potential count of rows, possibly indicating the number of occurrences
    row_count = Column(Integer)


# Apply the defined table structures to the connected database.
Base.metadata.create_all(engine)

print("Tables created successfully.")
