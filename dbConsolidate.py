from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from dbCreate import LogEntry, LogEntry2, LogEntry3
from dbCreate import LogEntryAgg

engine = create_engine('sqlite:///window_activity.db')

# Create a Session
Session = sessionmaker(bind=engine)
session = Session()

# Counter for added entries
added_entries, skipped_entries = 0, 0

for table in [LogEntry, LogEntry2, LogEntry3]:    
    # Query all rows from LogEntry table
    log_entries = session.query(table).all()

    # Iterate through each log entry
    for entry in log_entries:
        # Check if a duplicate entry exists in LogEntryAgg
        exists = session.query(LogEntryAgg).filter(
            LogEntryAgg.timestamp == entry.timestamp,
            LogEntryAgg.window_url == entry.window_url,
            LogEntryAgg.window_title == entry.window_title
            # Add any other fields you deem necessary for the duplication check
        ).scalar() is not None

        # If it doesn't exist, create and add new entry
        if not exists:
            new_entry = LogEntryAgg(
                timestamp=entry.timestamp,
                date=entry.date,
                hour=entry.hour,
                minute=entry.minute,
                window_url=entry.window_url,
                window_url_base=entry.window_url_base,
                window_title=entry.window_title,
                keyboard_events=entry.keyboard_events,
                mouse_events=entry.mouse_events
            )
            session.add(new_entry)
            added_entries += 1
        else:
            skipped_entries +=1

# Commit the session to save the changes
session.commit()

# Print the number of entries added
print(f"{added_entries} entries added, {skipped_entries} entries skipped")

# Close the session
session.close()
