# import sqlite3
from collections import defaultdict
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from sqlalchemy import create_engine, func, text
from functions import *
from datetime import datetime, timedelta
import random

# Create the database engine
engine = create_engine('sqlite:///window_activity.db')

def plot_activity(query, output, data_grain=60, tick_grain=120):
    rows = get_data_from_query(query)

    timestamps = [datetime.strptime(row.timestamp.split('.')[0], '%Y-%m-%d %H:%M:%S') for row in rows]
    keyboard_counts = [row.keyboard_count for row in rows]
    click_counts = [row.click_count for row in rows]

    start_time = min(timestamps)
    end_time = max(timestamps)

    ticks = [start_time + i * timedelta(minutes=data_grain) for i in range(int((end_time - start_time).total_seconds() / (data_grain * 60)) + 1)]

    all_keyboard_counts = np.zeros(len(ticks))
    all_click_counts = np.zeros(len(ticks))

    for i, tick in enumerate(ticks):
        relevant_indices = [j for j, t in enumerate(timestamps) if tick <= t < tick + timedelta(minutes=data_grain)]
        all_keyboard_counts[i] = sum(keyboard_counts[j] for j in relevant_indices)
        all_click_counts[i] = sum(click_counts[j] for j in relevant_indices)

    if (end_time - start_time) > timedelta(days=1):
        formatted_ticks = [timestamp.strftime('%Y-%m-%d %H:%M') for timestamp in ticks]
    else:
        formatted_ticks = [timestamp.strftime('%H:%M') for timestamp in ticks]

    plt.figure(figsize=(12, 6))

    index = np.arange(len(ticks))
    plt.bar(index, all_keyboard_counts, label='Keyboard Count')
    plt.bar(index, all_click_counts, bottom=all_keyboard_counts, label='Click Count')

    plt.xlabel('Time of Day')
    plt.ylabel('Count')
    plt.title('Keyboard / Mouse Activity')

    labeled_tick_count = max(1, int(tick_grain / data_grain))
    tick_positions = index[::labeled_tick_count]
    tick_labels = formatted_ticks[::labeled_tick_count]
    plt.xticks(ticks=tick_positions, labels=tick_labels)

    plt.legend()
    # ... (the code below stays the same)

    filename = f"images/{output}.png"
    plt.savefig(filename)  # Save the figure with the provided output name

    plt.close()

def get_data_from_2_col_query(query):
    rows = get_data_from_query(query)
    return pd.DataFrame(rows, columns=["window_category", "timestamps"])

def create_horizontal_bar_chart(df, category, axis):
    if df is None:
        return
    
    # Sort the DataFrame by timestamps in ascending order for a better visual representation in a horizontal bar chart
    df = df.sort_values(by=axis, ascending=True)
    
    
    # Create a list of colors
    colors = ['b' if title != 'Other' else 'r' for title in df[category]]
    
    plt.figure(figsize=(12, 6))
    
    # Create a horizontal bar chart with color based on the category
    plt.barh(df[category], df[axis], color=colors)
    
    # Wrap the text for each label so it doesn't overlap
    wrapped_labels = [wrap_text(label) for label in df[category]]
    plt.yticks(range(len(wrapped_labels)), wrapped_labels)
    
    # Annotate the bars with the exact value in minutes
    for i, val in enumerate(df[axis]):
        plt.text(val, i, f"{val:.2f}", va='center')
    
    plt.xlabel(axis)
    plt.ylabel(category)
    plt.title(f"Horizontal Bar Chart of {category} by {axis}")
    
    plt.savefig(f'images/hbc_{category}_{axis}.png')
    plt.close()

# Run the code (assuming get_data_from_query() is a function that you've defined elsewhere)

# Define the SQL query to fetch data from the table

# all is now in 6-hour blocks
trailing_all = """with trailing_view as(
SELECT 
datetime((strftime('%s', le.timestamp) / 21600) * 21600, 'unixepoch') as rounded_timestamp, sum(le.keyboard_events) AS keyboard_count, sum(le.mouse_events) AS click_count
FROM log_entries2 le
GROUP BY rounded_timestamp
)
SELECT rounded_timestamp AS timestamp, keyboard_count, click_count
FROM trailing_view;
"""

trailing_yesterday = """with trailing_view as(
SELECT datetime((strftime('%s', le.timestamp) / 3600) * 3600, 'unixepoch') as rounded_timestamp, sum(le.keyboard_events) AS keyboard_count, sum(le.mouse_events) AS click_count
FROM log_entries2 le

--WHERE date = (select max(date) from log_entries2 le2)-1

WHERE  le.timestamp >= datetime('now', '-1 day', 'start of day', '-7 hours') -- Start of yesterday
AND le.timestamp < datetime('now', 'start of day', '-7 hours') -- Start of today
GROUP BY rounded_timestamp
)
SELECT  rounded_timestamp AS timestamp, keyboard_count, click_count
FROM trailing_view;
"""

trailing_today = """with trailing_view as(
SELECT datetime((strftime('%s', le.timestamp) / 600) * 600, 'unixepoch') as rounded_timestamp, sum(le.keyboard_events) AS keyboard_count, sum(le.mouse_events) AS click_count
FROM log_entries2 le
WHERE date = (select max(date) from log_entries2 le2)
GROUP BY rounded_timestamp
)
SELECT rounded_timestamp AS timestamp, keyboard_count, click_count FROM trailing_view;
"""

trailing_90 = """with trailing_view as(
SELECT datetime((strftime('%s', le.timestamp) / 60) * 60, 'unixepoch') as rounded_timestamp, sum(le.keyboard_events) AS keyboard_count,sum(le.mouse_events) AS click_count
FROM log_entries2 le
WHERE le.timestamp >= datetime('now', '-10 hours')
GROUP BY rounded_timestamp
)
SELECT rounded_timestamp AS timestamp, keyboard_count, click_count
FROM trailing_view;
"""

trailing_today_category = """WITH RankedWindows AS (
SELECT window_title, count(timestamp) as timestamps, sum(keyboard_events) AS keyboard_count, sum(mouse_events) AS click_count, ROW_NUMBER() OVER (ORDER BY count(timestamp) DESC) AS rn
FROM log_entries2 le
WHERE le.timestamp >= datetime('now', 'start of day', '-7 hours') -- Start of today
GROUP BY window_title
HAVING sum(keyboard_events) > 0 OR sum(mouse_events) > 0
)
SELECT CASE WHEN rn <= 5 THEN window_title ELSE 'Other' END AS grouped_window_title, SUM(timestamps)/2 AS timestamps, SUM(keyboard_count) AS keyboard_count, SUM(click_count) AS click_count
FROM RankedWindows
GROUP BY grouped_window_title
ORDER BY grouped_window_title;
"""

category_query = """
    SELECT
        window_category,
        sum(row_count) as timestamps
    FROM
        window_categories
    GROUP BY 1
    ORDER BY 2 DESC
"""

with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT 
            datetime((strftime('%s', le.timestamp) / 600) * 600, 'unixepoch') as rounded_timestamp,
            wc.window_category,
            COUNT(*) as cnt
        FROM 
            log_entries2 le
        JOIN 
            window_categories wc ON le.window_title = wc.window_title
        WHERE 
            (le.keyboard_events + le.mouse_events) > 0
            and 
            le.timestamp >= datetime('now', '-24 hours')
        GROUP BY 
            rounded_timestamp, wc.window_category
        ORDER BY 
            rounded_timestamp ASC, cnt DESC
    """))
def recent_activity_categories():
    def get_data_from_query_int(query, engine = create_engine('sqlite:///window_activity.db')):
        with engine.connect() as connection:
            result = connection.execute(text(query))
            rows = result.fetchall()
        
        if not rows:
            print(f"No data found for the query: {query}")
            return None

        return rows


    new_query = """
        SELECT 
            datetime((strftime('%s', le.timestamp) / 600) * 600, 'unixepoch') as rounded_timestamp,
            wc.window_category,
            COUNT(*) as cnt
        FROM 
            log_entries2 le
        JOIN 
            window_categories wc ON le.window_title = wc.window_title
        WHERE 
            (le.keyboard_events + le.mouse_events) > 0
            and le.timestamp >= datetime('now', '-12 hours')
        GROUP BY 
            rounded_timestamp, wc.window_category
        ORDER BY 
            rounded_timestamp ASC, cnt DESC
    """

    aggregated_data = get_data_from_query_int(new_query)
    windows = defaultdict(list)

    for row in aggregated_data:
        rounded_timestamp, category, cnt = row
        windows[rounded_timestamp].append({'category': category, 'cnt': cnt})

    dominant_categories = {}

    for rounded_timestamp, categories in windows.items():
        dominant = max(categories, key=lambda x: x['cnt'])
        dominant_categories[rounded_timestamp] = dominant
        
    for rounded_timestamp, dominant in dominant_categories.items():
        dominant_count = dominant['cnt']
        other_count = sum(cat['cnt'] for cat in windows[rounded_timestamp] if cat['category'] != dominant['category'])
        # print(f"For the 10-min window starting at {rounded_timestamp}, the dominant category is {dominant['category']} with {dominant_count} timestamps, and other categories have {other_count} timestamps.")

    # Preparing data for plotting
    timestamps = list(dominant_categories.keys())
    dominant_counts = [dominant_categories[t]['cnt'] for t in timestamps]
    other_counts = [
        sum(cat['cnt'] for cat in windows[t] if cat['category'] != dominant_categories[t]['category'])
        for t in timestamps
    ]

    unique_categories = set(dominant_categories[t]['category'] for t in timestamps)

    # 5. Generate colors and map them to categories
    # Pre-defined colors for certain categories
    predefined_colors = {
        'Games': 'tab:purple',
        'RPA': 'tab:orange',
        'AI': 'tab:blue',
        'Coding': 'aquamarine',
        'School': 'tab:red',  # Cardinal Red
        'Productivity': 'yellow',
        'Communication': 'pink',
        'Planning': 'tab:brown',
        'Gospel':'tab:olive',
        'Finances': 'tab:cyan',
        'Other': 'green', 
    }

    # Generate random colors for the rest
    all_colors = list(mcolors.CSS4_COLORS.values())
    random.shuffle(all_colors)  # Shuffle to get random colors
    remaining_categories = [cat for cat in unique_categories if cat not in predefined_colors]
    num_remaining_colors = len(remaining_categories)
    remaining_colors = all_colors[:num_remaining_colors]

    # Combine predefined and random colors
    category_colors = {**predefined_colors, **dict(zip(remaining_categories, remaining_colors))}

    # 6. Continue with your plotting logic
    # e.g., using dominant_colors in your plt.bar() function
    dominant_colors = [category_colors[dominant_categories[t]['category']] for t in timestamps]

    # Plotting
    plt.figure(figsize=(10, 6))

    plt.bar(timestamps, dominant_counts, color=dominant_colors, label='Dominant Category')
    plt.bar(timestamps, other_counts, color='black', bottom=dominant_counts, label='Other Categories')

    # Add labels and title
    plt.xlabel('Time')
    plt.ylabel('Number of Timestamps')
    plt.title('Activity Categories Over Time')

    # Limit number of ticks on the x-axis
    if len(timestamps) > 0:
        plt.xticks([timestamps[0], timestamps[len(timestamps)//2], timestamps[-1]])

    plt.savefig(f'images/activity_focus.png')
    plt.close()
recent_activity_categories()

################################################################
################################################################
# Generate Charts
################################################################
################################################################
plot_activity(trailing_all, 'trailing_all', 240, 2880)  # Plot using trailing_all query
plot_activity(trailing_yesterday, 'trailing_yesterday', 60, 120)
plot_activity(trailing_today, 'trailing_today', 60, 120)
plot_activity(trailing_90, 'trailing_90', 1, 30)

category_results = get_data_from_2_col_query(category_query)
create_horizontal_bar_chart(category_results, "window_category", "timestamps")

rows = get_data_from_query(trailing_today_category)
query_results = pd.DataFrame(rows, columns=["window_title", "timestamps", "keyboard_count", "click_count"])
create_horizontal_bar_chart(query_results, "window_title", "timestamps")

category_activity = """
WITH logs AS (
    SELECT 
        timestamp,
        keyboard_events,
        mouse_events,
        keyboard_events + mouse_events AS events_logged,
        wc.window_category,
        ROW_NUMBER() OVER (ORDER BY wc.window_category DESC) AS rn
    FROM 
        log_entries2 le
    LEFT JOIN 
        window_categories wc ON le.window_title = wc.window_title
    WHERE 
        (le.keyboard_events + le.mouse_events) > 0
    ORDER BY 
        timestamp, events_logged DESC
)
SELECT 
    window_category,
    COUNT(*) AS total_rows,
    AVG(keyboard_events) AS avg_keyboard_events,
    AVG(mouse_events) AS avg_mouse_events,
    AVG(events_logged) AS avg_events_logged,
    -- Median, p25, p75, p80, p90 calculations will need to be done using subqueries
    (SELECT keyboard_events FROM logs AS sub WHERE sub.window_category = logs.window_category ORDER BY keyboard_events LIMIT 1 OFFSET (COUNT(*) / 2)) AS median_keyboard_events,
    (SELECT keyboard_events FROM logs AS sub WHERE sub.window_category = logs.window_category ORDER BY keyboard_events LIMIT 1 OFFSET (COUNT(*) * 0.25)) AS p25_keyboard_events,
    (SELECT keyboard_events FROM logs AS sub WHERE sub.window_category = logs.window_category ORDER BY keyboard_events LIMIT 1 OFFSET (COUNT(*) * 0.75)) AS p75_keyboard_events,
    (SELECT keyboard_events FROM logs AS sub WHERE sub.window_category = logs.window_category ORDER BY keyboard_events LIMIT 1 OFFSET (COUNT(*) * 0.8)) AS p80_keyboard_events,
    (SELECT keyboard_events FROM logs AS sub WHERE sub.window_category = logs.window_category ORDER BY keyboard_events LIMIT 1 OFFSET (COUNT(*) * 0.9)) AS p90_keyboard_events
FROM logs
GROUP BY window_category;
"""


import sqlite3
import matplotlib.pyplot as plt
import numpy as np

# Connect to SQLite database
conn = sqlite3.connect('window_activity.db')

# Your SQL query string (modified to include p75_mouse_events)
sql_query = """
WITH logs AS (
    SELECT 
        timestamp,
        keyboard_events,
        mouse_events,
        keyboard_events + mouse_events AS events_logged,
        wc.window_category,
        ROW_NUMBER() OVER (ORDER BY wc.window_category DESC) AS rn
    FROM 
        log_entries2 le
    LEFT JOIN 
        window_categories wc ON le.window_title = wc.window_title
    WHERE 
        (le.keyboard_events + le.mouse_events) > 0
    ORDER BY 
        timestamp, events_logged DESC
)
SELECT 
    window_category,
    COUNT(timestamp) AS total_rows,
    AVG(keyboard_events) AS avg_keyboard_events,
    AVG(mouse_events) AS avg_mouse_events,
    AVG(events_logged) AS avg_events_logged
    -- Median, p25, p75, p80, p90 calculations will need to be done using subqueries
FROM logs
GROUP BY window_category;
"""

# Fetch data
cursor = conn.execute(sql_query)
data = cursor.fetchall()

# Sort by 'total_rows' and get top 5 categories
data = sorted(data, key=lambda x: x[1], reverse=True)[:5]
categories = [x[0] for x in data]
total_rows = [x[1] for x in data]
avg_keyboard_events = [x[2] for x in data]
avg_mouse_events = [x[3] for x in data]  # Assume p75_mouse_events is the 8th column in your SQL output

# Prepare data for stacked bar chart
index = np.arange(len(categories))
bar_width = 0.35

# Create stacked bar chart
plt.figure(figsize=(12, 6))
bar1 = plt.bar(index, avg_keyboard_events, bar_width, label='avg_keyboard_events')
bar2 = plt.bar(index, avg_mouse_events, bar_width, bottom=avg_keyboard_events, label='avg_mouse_events')

# Add some details
plt.xlabel('Categories')
plt.ylabel('Event Counts')
plt.title('Top 5 Categories by Total Rows and Avg Event Counts')
plt.xticks(index, categories, rotation=30)
plt.legend()

# Show the chart
plt.tight_layout()
plt.savefig(f'images/category_productive.png')
plt.close
# Close the database connection
conn.close()
    # (SELECT keyboard_events FROM logs AS sub WHERE sub.window_category = logs.window_category ORDER BY keyboard_events LIMIT 1 OFFSET (COUNT(*) / 2)) AS median_keyboard_events,
    # (SELECT keyboard_events FROM logs AS sub WHERE sub.window_category = logs.window_category ORDER BY keyboard_events LIMIT 1 OFFSET (COUNT(*) * 0.25)) AS p25_keyboard_events,
    # (SELECT keyboard_events FROM logs AS sub WHERE sub.window_category = logs.window_category ORDER BY keyboard_events LIMIT 1 OFFSET (COUNT(*) * 0.75)) AS p75_keyboard_events,
    # (SELECT keyboard_events FROM logs AS sub WHERE sub.window_category = logs.window_category ORDER BY keyboard_events LIMIT 1 OFFSET (COUNT(*) * 0.8)) AS p80_keyboard_events,
    # (SELECT keyboard_events FROM logs AS sub WHERE sub.window_category = logs.window_category ORDER BY keyboard_events LIMIT 1 OFFSET (COUNT(*) * 0.9)) AS p90_keyboard_events
