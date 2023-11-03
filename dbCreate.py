from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base

# Create the database engine (it creates a SQLite database file named 'window_activity.db')
engine = create_engine('sqlite:///window_activity.db')

# Create a declarative base for defining the table
Base = declarative_base()

# Define the LogEntry table structure
class LogEntry(Base):
    __tablename__ = 'log_entries'

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
    # Add your new columns here
# Define the LogEntry table structure

class LogEntry2(Base):
    __tablename__ = 'log_entries2'

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
    # Add your new columns here

# Define the WindowCategory table structure
class WindowCategory(Base):
    __tablename__ = 'window_categories'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    window_title = Column(String)
    window_url_base = Column(String)
    window_category = Column(String)
    row_count = Column(Integer)

# Create the table in the database
Base.metadata.create_all(engine)