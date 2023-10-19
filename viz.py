import matplotlib.pyplot as plt
from sqlalchemy import create_engine, text
from datetime import datetime, timedelta

# Create the database engine
engine = create_engine('sqlite:///window_activity.db')

# Define the SQL query to fetch data from the table
query = """

with trailing_view as(

SELECT 
    le.timestamp, 
    sum(le2.keyboard_events) AS keyboard_count,
    sum(le2.mouse_events) AS click_count
FROM
    log_entries le

LEFT JOIN
    log_entries le2 ON le.id - le2.id BETWEEN 0 AND 29

LEFT JOIN
    window_categories wc
ON
    le.window_title = wc.window_title
    AND le.window_url_base = wc.window_url_base

GROUP BY
    le.timestamp, wc.window_category

)
SELECT 
    timestamp, 
    keyboard_count,
    click_count
FROM
    trailing_view;
"""

# Execute the SQL query to fetch data
with engine.connect() as connection:
    result = connection.execute(text(query))
    rows = result.fetchall()

# Separate data for the two lines
timestamps = [datetime.strptime(row.timestamp.split('.')[0], '%Y-%m-%d %H:%M:%S') for row in rows]
keyboard_counts = [row.keyboard_count for row in rows]
click_counts = [row.click_count for row in rows]

# Calculate the start and end times
start_time = min(timestamps)
end_time = max(timestamps)

# Align the start_time to the nearest hour or half-hour
start_time -= timedelta(minutes=start_time.minute % 30, seconds=start_time.second)

# Set the desired interval for the x-axis ticks (30 minutes)
tick_interval = timedelta(minutes=30)

# Generate a list of timestamps at 30-minute intervals
ticks = [start_time + timedelta(seconds=i * 30) for i in range(int((end_time - start_time).total_seconds() / 30) + 1)]

# Format the ticks to display time in HH:MM format
formatted_ticks = [timestamp.strftime('%H:%M') for timestamp in ticks]

# Create stacked line charts
plt.figure(figsize=(10, 6))
plt.stackplot(timestamps, keyboard_counts, click_counts, labels=['Keyboard Count', 'Click Count'], alpha=0.5)
plt.xlabel('Time of Day')
plt.ylabel('Count')
plt.title('Keyboard / Mouse Activity')
plt.legend(loc='upper left')

plt.xticks(
    ticks=ticks[::60],  # Choose every 2nd tick to reduce density
    labels=formatted_ticks[::60],  # Use formatted ticks
    # rotation=45
)

plt.show()