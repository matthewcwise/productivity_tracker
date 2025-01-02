from sqlalchemy import (
    create_engine, Column, Integer, String, DateTime, ForeignKey, Enum, Index
)
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

# Create a SQLite database engine
engine = create_engine('sqlite:///window_activity.db')

# Define the declarative base
Base = declarative_base()

# Define predefined categories
from enum import Enum as PyEnum
class ActivityCategory(PyEnum):
    PRODUCTIVE = "Work"
    DISTRACTED = "Personal"

# Define the LogEntry table
class LogEntry(Base):
    __tablename__ = 'log_entries'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=func.now())
    application = Column(String)
    domain = Column(String)
    detail = Column(String)
    flow_score = Column(Integer)
    focus_score = Column(Integer)
    window_url = Column(String)
    window_url_base = Column(String)
    window_title = Column(String)
    keyboard_events = Column(Integer, default=0)
    mouse_events = Column(Integer, default=0)
    category_id = Column(Integer, ForeignKey('window_categories.id'))
    session_num = Column(Integer)  # New column for session tracking
    user = Column(String)  # New column for user tracking

    # Relationships
    category = relationship("WindowCategory", back_populates="entries")

# Define the WindowCategory table
class WindowCategory(Base):
    __tablename__ = 'window_categories'

    id = Column(Integer, primary_key=True, autoincrement=True)
    window_title = Column(String)
    window_url_base = Column(String)
    window_category = Column(Enum(ActivityCategory))
    
    # Relationships
    entries = relationship("LogEntry", back_populates="category")

# Create indexes for performance
Index('idx_window_url_base', LogEntry.window_url_base)
Index('idx_timestamp', LogEntry.timestamp)

# Create the tables
Base.metadata.create_all(engine)
