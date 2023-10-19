from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base

# Create the database engine (it creates a SQLite database file named 'window_activity.db')
engine = create_engine('sqlite:///window_activity.db')

# Create a declarative base for defining the table
Base = declarative_base()

# Define the LogEntry table structure
class LogEntry(Base):
    """Represents a log entry in the database."""
    __tablename__ = 'log_entries'
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime)
    window_title = Column(String)
    window_url = Column(String)
    window_url_base = Column(String)
    keyboard_events = Column(Integer)
    mouse_events = Column(Integer)

# Create the table in the database
Base.metadata.create_all(engine)