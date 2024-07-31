import re
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, func, or_
# Ensure this imports the correct models
from dbCreateTables import LogEntryAgg, WindowCategory, LogEntry

# Create the database engine
engine = create_engine('sqlite:///window_activity.db')

# Create a Session
Session = sessionmaker(bind=engine)
session = Session()

# Counter for added entries
added_entries, skipped_entries = 0, 0

# Process log entries
log_entries = session.query(LogEntry).all()
for entry in log_entries:
    exists = session.query(LogEntryAgg).filter(
        LogEntryAgg.timestamp == entry.timestamp,
        LogEntryAgg.url == entry.url,
        LogEntryAgg.window_title == entry.window_title
    ).scalar() is not None

    if not exists:
        new_entry = LogEntryAgg(
            timestamp=entry.timestamp,
            date=entry.date,
            hour=entry.hour,
            minute=entry.minute,
            url=entry.url,
            url_abbrev=entry.url_abbrev,
            window_url_base=entry.window_url_base,
            window_title=entry.window_title,
            keyboard_events=entry.keyboard_events,
            mouse_events=entry.mouse_events
        )
        session.add(new_entry)
        added_entries += 1
    else:
        skipped_entries += 1

# Commit the session to save the changes
session.commit()

# Print the number of entries added
print(f"{added_entries} entries added, {skipped_entries} entries skipped")

# Close the session
session.close()

# Create a new session
session = Session()

# Delete all rows from the window_categories table
session.query(WindowCategory).delete()
session.commit()

categories = [
    {'name': 'Productivity',
        'regex': r'(calendar|productivity dash|mouse activity vis|productivity app|ChatGPT)', 'priority': 2},
    {'name': 'None', 'regex': r'(Windows Default Lock Screen)', 'priority': 1},
    {'name': 'Documents', 'regex': r'(google docs)', 'priority': 2},
    {'name': 'Video', 'regex': r'(YouTube)', 'priority': 1},
    {'name': 'Other', 'regex': r'.*', 'priority': 0},  # Default category
]


def get_row_count(window_title, window_url_base):
    return session.query(func.count(LogEntryAgg.id)).filter(
        LogEntryAgg.window_title == window_title,
        LogEntryAgg.window_url_base == window_url_base,
        or_(LogEntryAgg.keyboard_events != 0, LogEntryAgg.mouse_events != 0)
    ).scalar()


def categorize_window_title(window_title):
    for category in categories:
        if re.search(category['regex'], window_title, re.IGNORECASE):
            return category['name']
    return 'Other'  # Default category


# Query the active rows from the log_entries_agg table
activity_category = session.query(LogEntryAgg.window_title, LogEntryAgg.window_url_base).filter(
    LogEntryAgg.window_title.isnot(None), LogEntryAgg.window_title != '',
    (LogEntryAgg.keyboard_events != 0) | (LogEntryAgg.mouse_events != 0)
).distinct().all()

# Populate the WindowCategory table with distinct window titles and their categories
for title, url_base in activity_category:
    window_title = title
    window_category = categorize_window_title(window_title)
    row_count = get_row_count(window_title, url_base)
    new_category = WindowCategory(
        window_title=window_title,
        window_url_base=url_base,
        window_category=window_category,
        row_count=row_count
    )
    session.add(new_category)

# Commit the changes to the database
session.commit()

# Close the session
session.close()

print("Window categories populated successfully.")
