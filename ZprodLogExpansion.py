from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from dbCreate import LogEntry  # assuming dbCreate.py has your LogEntry class with new columns
import pandas as pd
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from dbCreate import LogEntry

# Create the database engine (it creates a SQLite database file named 'window_activity.db')
engine = create_engine('sqlite:///window_activity.db')

# Create a declarative base for defining the table

session = Session(engine)

# with engine.connect() as conn:
#     conn.execute(text("ALTER TABLE log_entries ADD COLUMN date STRING"))
#     conn.execute(text("ALTER TABLE log_entries ADD COLUMN hour INTEGER"))
#     conn.execute(text("ALTER TABLE log_entries ADD COLUMN minute INTEGER"))
#     conn.execute(text("ALTER TABLE log_entries ADD COLUMN second INTEGER"))

# Query all rows to update
all_logs = session.query(LogEntry).all()

for log in all_logs:
    timestamp = pd.Timestamp(log.timestamp)
    log.date = timestamp.strftime('%Y-%m-%d')
    log.hour = timestamp.hour
    log.minute = timestamp.minute

# Commit the changes
session.commit()