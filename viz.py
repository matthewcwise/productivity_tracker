from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
import matplotlib.pyplot as plt
import pandas as pd

# Create a SQLite database engine that will manage the local database file 'window_activity.db'.
# engine = create_engine('sqlite:///window_activity.db')
engine = create_engine('sqlite:///window_activity.db', dialect='sqlite3')


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


# Create a session to interact with the database
Session = sessionmaker(bind=engine)
session = Session()

# Query the database to get the sum of keyboard and mouse events by hour
results = session.query(
    LogEntry.hour,
    (LogEntry.keyboard_events + LogEntry.mouse_events).label('activity')
).all()

# Close the session
session.close()

# Process the results into a DataFrame
df = pd.DataFrame(results, columns=['hour', 'activity'])

# Group by hour and sum the activities
activity_by_hour = df.groupby('hour').sum().reset_index()

# Plot the data using matplotlib
plt.figure(figsize=(10, 6))
plt.bar(activity_by_hour['hour'], activity_by_hour['activity'], color='blue')
plt.xlabel('Hour of the Day')
plt.ylabel('Activity (Sum of Keyboard and Mouse Events)')
plt.title('Activity by Hour')
plt.xticks(activity_by_hour['hour'])
plt.grid(True)
plt.show()
