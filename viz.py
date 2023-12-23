# import sqlite3
import numpy as np
import matplotlib.pyplot as plt
import sqlite3

from collections import defaultdict
import pandas as pd
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
    hour as rounded_timestamp, sum(le.keyboard_events) AS keyboard_count, sum(le.mouse_events) AS click_count
FROM LogEntryAgg le
GROUP BY rounded_timestamp
)
SELECT rounded_timestamp AS timestamp, keyboard_count, click_count
FROM trailing_view;
"""

trailing_yesterday = """with trailing_view as(
SELECT datetime((strftime('%s', le.timestamp) / 3600) * 3600, 'unixepoch') as rounded_timestamp, sum(le.keyboard_events) AS keyboard_count, sum(le.mouse_events) AS click_count
FROM LogEntryAgg le

--WHERE date = (select max(date) from LogEntryAgg le2)-1

WHERE  le.timestamp >= datetime('now', '-1 day', 'start of day', '-7 hours') -- Start of yesterday
AND le.timestamp < datetime('now', 'start of day', '-7 hours') -- Start of today
GROUP BY rounded_timestamp
)
SELECT  rounded_timestamp AS timestamp, keyboard_count, click_count
FROM trailing_view;
"""

trailing_today = """with trailing_view as(
SELECT datetime((strftime('%s', le.timestamp) / 600) * 600, 'unixepoch') as rounded_timestamp, sum(le.keyboard_events) AS keyboard_count, sum(le.mouse_events) AS click_count
FROM LogEntryAgg le
WHERE date = (select max(date) from LogEntryAgg le2)
GROUP BY rounded_timestamp
)
SELECT rounded_timestamp AS timestamp, keyboard_count, click_count FROM trailing_view;
"""

trailing_90 = """with trailing_view as(
SELECT datetime((strftime('%s', le.timestamp) / 60) * 60, 'unixepoch') as rounded_timestamp, sum(le.keyboard_events) AS keyboard_count,sum(le.mouse_events) AS click_count
FROM LogEntryAgg le
WHERE le.timestamp >= datetime('now', '-10 hours')
GROUP BY rounded_timestamp
)
SELECT rounded_timestamp AS timestamp, keyboard_count, click_count
FROM trailing_view;
"""

trailing_today_category = """WITH RankedWindows AS (
SELECT window_title, count(timestamp) as timestamps, sum(keyboard_events) AS keyboard_count, sum(mouse_events) AS click_count, ROW_NUMBER() OVER (ORDER BY count(timestamp) DESC) AS rn
FROM LogEntryAgg le
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
            LogEntryAgg le
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
            log_entries3 le
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

try:
    recent_activity_categories()
except:
    pass

################################################################
################################################################
# Generate Charts
################################################################
################################################################

try:
    plot_activity(trailing_yesterday, 'trailing_yesterday', 60, 120)
except:
    pass
try:
    plot_activity(trailing_today, 'trailing_today', 60, 120)
except:
    pass
# plot_activity(trailing_90, 'trailing_90', 1, 30)

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
        LogEntryAgg le
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
        LogEntryAgg le
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



programming_productivity = """WITH log2 AS (
    SELECT 
        hour,
        keyboard_events,
        mouse_events
    FROM 
        LogEntryAgg le
    INNER JOIN 
        window_categories wc ON le.window_title = wc.window_title
        AND wc.window_category IN ('Coding', 'RPA', 'School')
    WHERE 
        (le.keyboard_events + le.mouse_events) > 0
        and (le.keyboard_events + le.mouse_events) < 150
),
log1 AS (
    SELECT 
        hour,
        keyboard_events,
        mouse_events
    FROM 
        log_entries le
    INNER JOIN 
        window_categories wc ON le.window_title = wc.window_title
        AND wc.window_category IN ('Coding', 'RPA', 'School')
    WHERE 
        (le.keyboard_events + le.mouse_events) > 0
        and (le.keyboard_events + le.mouse_events) < 150
)

SELECT
    log2.hour,
    (SUM(log2.keyboard_events) + SUM(log1.keyboard_events)) / (COUNT(log2.hour) + COUNT(log1.hour)) AS keyboard_events,
    (SUM(log2.mouse_events) + SUM(log1.mouse_events)) / (COUNT(log2.hour) + COUNT(log1.hour)) AS mouse_events

FROM log2

LEFT JOIN log1 ON log2.hour = log1.hour
GROUP BY log2.hour
ORDER BY log2.hour;

"""


import numpy as np
import matplotlib.pyplot as plt

plt.figure(figsize=(12, 6))

# Assuming get_data_from_query is defined and returns the appropriate data
rows = get_data_from_query(programming_productivity)

# Initialize counts for each hour to zero
keyboard_events = [0] * 24

# Populate the events counts if data exists for that hour
for row in rows:
    hour_index = row[0]  # Assuming the hour is the first element in the row
    keyboard_events[hour_index] = row[1] or 0  # Replace None with 0

# Determine the top 5 and bottom 5 hours by keyboard_events
sorted_indices = np.argsort(keyboard_events)
# Filter out indices with zero counts for the bottom 5
sorted_indices_with_data = [index for index in sorted_indices if keyboard_events[index] > 0]

top_5_indices = sorted_indices_with_data[-5:]
# Ensure that we only consider non-zero data for the bottom 5
bottom_5_indices = sorted_indices_with_data[:5] if len(sorted_indices_with_data) > 5 else []

# Create a list for the colors of the bars
colors = ['blue' if i not in top_5_indices and i not in bottom_5_indices else 'green' if i in top_5_indices else 'red' for i in range(24)]

# Define the bar width
bar_width = 0.8

# Set the positions of the bars (0 through 23)
indices = np.arange(24)

# Plotting the keyboard events with color coding
plt.bar(indices, keyboard_events, bar_width, label='Keyboard Events', color=colors)

# Adding labels and title
plt.xlabel('Hour of Day')
plt.ylabel('Events Count')
plt.title('Programming/School Keyboard Events by Hour')

# Adding the legend
plt.legend()

# Setting the tick labels to show each hour (0 through 23)
plt.xticks(indices, [i for i in range(24)])

# Saving the plot
plt.savefig('images/programming_productivity.png')

# Close the plot figure
plt.close()


plt.figure(figsize=(12, 6))

# Assuming get_data_from_query is defined and returns the appropriate data
rows = get_data_from_query(trailing_all)

# Initialize counts for each hour to zero
keyboard_events = [0] * 24
mouse_events = [0] * 24

# Populate the events counts if data exists for that hour
for row in rows:
    hour_index = row[0]  # Assuming the hour is the first element in the row
    keyboard_events[hour_index] = row[1] or 0  # Replace None with 0
    mouse_events[hour_index] = row[2] or 0  # Replace None with 0

# Define the bar width
bar_width = 0.8

# Set the positions of the bars (0 through 23)
indices = np.arange(24)

# Plotting the keyboard events
plt.bar(indices, keyboard_events, bar_width, label='Keyboard Events', color='blue')

# Plotting the mouse events on top of the keyboard events
plt.bar(indices, mouse_events, bar_width, label='Mouse Events', color='orange', bottom=keyboard_events)

# Adding labels and title
plt.xlabel('Hour of Day')
plt.ylabel('Events Count')
plt.title('Programming/School Keyboard and Mouse Events by Hour')

# Adding the legend
plt.legend()

# Setting the tick labels to show each hour (0 through 23)
plt.xticks(indices, [i for i in range(24)])

# Saving the plot
plt.savefig('images/trailing_all_vAlt.png')

# Close the plot figure
plt.close()



plt.figure(figsize=(12, 6))

# Initialize counts for each hour to zero
keyboard_events = [0] * 24

# Populate the events counts if data exists for that hour
for row in rows:
    hour_index = row[0]  # Assuming the hour is the first element in the row
    keyboard_events[hour_index] = row[1] or 0  # Replace None with 0

# Determine the top 5 and bottom 5 hours by keyboard_events
sorted_indices = np.argsort(keyboard_events)
# Filter out indices with zero counts for the bottom 5
sorted_indices_with_data = [index for index in sorted_indices if keyboard_events[index] > 0]

top_5_indices = sorted_indices_with_data[-5:]
# Ensure that we only consider non-zero data for the bottom 5
bottom_5_indices = sorted_indices_with_data[:5] if len(sorted_indices_with_data) > 5 else []

# Create a list for the colors of the bars
colors = ['blue' if i not in top_5_indices and i not in bottom_5_indices else 'green' if i in top_5_indices else 'red' for i in range(24)]

# Define the bar width
bar_width = 0.8

# Set the positions of the bars (0 through 23)
indices = np.arange(24)

# Plotting the keyboard events with color coding
plt.bar(indices, keyboard_events, bar_width, label='Keyboard Events', color=colors)

# Adding labels and title
plt.xlabel('Hour of Day')
plt.ylabel('Events Count')
plt.title('Programming/School Keyboard Events by Hour')

# Adding the legend
plt.legend()

# Setting the tick labels to show each hour (0 through 23)
plt.xticks(indices, [i for i in range(24)])

# Saving the plot
plt.savefig('images/trailing_all.png')

# Close the plot figure
plt.close()



from matplotlib.patches import Rectangle
import matplotlib as mpl

# Create a colormap with a set_bad color
cmap_val = mpl.cm.get_cmap("hot_r").copy()
cmap_val.set_bad(color='lightgray')
  
heatmap = """SELECT
    strftime('%w', timestamp) AS weekday,
    hour as rounded_timestamp,
    1.0*count(timestamp)/2 AS active
    
FROM LogEntryAgg le
where keyboard_events+mouse_events > 0
GROUP BY weekday, hour;
"""

import numpy as np
import matplotlib.pyplot as plt
import sqlite3

# Fetch all rows from the query
rows = get_data_from_query(heatmap)
# Initialize a 2D array to store the data
activity_data = np.full((7, 24), np.nan)

# Populate the activity_data array
for row in rows:
    weekday, hour, keyboard_events = int(row[0]), int(row[1]), int(row[2])
    activity_data[weekday, hour] = keyboard_events

# Close the database connection
conn.close()

# Creating the heatmap
plt.figure(figsize=(12, 6))
im = plt.imshow(activity_data, cmap=cmap_val, interpolation='nearest')

# Adding labels and title
plt.xlabel('Hour of Day')
plt.ylabel('Day of Week')
plt.title('Activity Heatmap by Day and Hour')

# Adjusting the ticks to show days and hours
days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
hours = [str(i) for i in range(24)]
plt.xticks(np.arange(24), hours)
plt.yticks(np.arange(7), days)

# Add the rectangles
bottom_left_corner = (9 - 0.5, 1 - 0.5)  # Shifted by 0.5
width = 7 - 1  # Ending x-coordinate - starting x-coordinate
height = 6 - 1  # Ending y-coordinate - starting y-coordinate
rect = Rectangle(bottom_left_corner, width, height, linewidth=2, edgecolor='blue', facecolor='none')
plt.gca().add_patch(rect)

# Second rectangle - if needed, adjust the coordinates as necessary
# rect2 = Rectangle(other_corner, other_width, other_height, linewidth=2, edgecolor='blue', facecolor='none')
# plt.gca().add_patch(rect2)

# Create a horizontal colorbar at the bottom
cbar = plt.colorbar(im, orientation='horizontal', pad=0.1, shrink=0.75)
cbar.set_label('Active Minutes')

# Adjust layout to prevent overlap
plt.tight_layout()

# Saving the plot
plt.savefig('images/heatmap.png')

plt.close()


programming_productivity_heatmap = """SELECT 
        strftime('%w', timestamp) AS weekday,
        hour,
        SUM(keyboard_events) / COUNT(keyboard_events) AS keyboard_events,
        count(timestamp) as timestamps

    FROM 
        LogEntryAgg le
    INNER JOIN 
        window_categories wc ON le.window_title = wc.window_title
        AND wc.window_category IN ('Coding', 'RPA', 'School')
    WHERE 
        (le.keyboard_events + le.mouse_events) > 0
        and (le.keyboard_events + le.mouse_events) < 150
    group by 1, 2
    having count(timestamp) > 60;"""


productive_ratio = """
    SELECT 
        strftime('%w', timestamp) AS weekday,
        hour,
        1.0* sum(case when wc.window_category IN ('Coding', 'RPA', 'School') then 1 else 0 end)/count(timestamp) as productive_ratio,
        count(timestamp) as timestamp_count
    FROM
        LogEntryAgg le
    left JOIN 
        window_categories wc ON le.window_title = wc.window_title
        
    where le.keyboard_events + le.mouse_events > 0 and (le.keyboard_events + le.mouse_events) < 150
        group by 1, 2
        having timestamp_count > 60
        ;
"""

import numpy as np
import matplotlib.pyplot as plt
import sqlite3

# Fetch all rows from the query
rows = get_data_from_query(programming_productivity_heatmap)
# Initialize a 2D array to store the data
activity_data = np.full((7, 24), np.nan)

# Populate the activity_data array
for row in rows:
    weekday, hour, active = int(row[0]), int(row[1]), int(row[2])
    activity_data[weekday, hour] = active

# Close the database connection
conn.close()

# Creating the heatmap
plt.figure(figsize=(12, 6))
im = plt.imshow(activity_data, cmap=cmap_val, interpolation='nearest')

# Adding labels and title
plt.xlabel('Hour of Day')
plt.ylabel('Day of Week')
plt.title('Productivity Heatmap by Day and Hour')

# Adjusting the ticks to show days and hours
days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
hours = [str(i) for i in range(24)]
plt.xticks(np.arange(24), hours)
plt.yticks(np.arange(7), days)

# Add the rectangle
bottom_left_corner = (9 - 0.5, 1 - 0.5)  # Shifted by 0.5
width = 7 - 1  # Ending x-coordinate - starting x-coordinate
height = 6 - 1  # Ending y-coordinate - starting y-coordinate
rect = Rectangle(bottom_left_corner, width, height, linewidth=2, edgecolor='blue', facecolor='none')
plt.gca().add_patch(rect)

# Create a horizontal colorbar at the bottom
cbar = plt.colorbar(im, orientation='horizontal', pad=0.1, shrink=0.75)
cbar.set_label('Activity Level')

# Adjust layout to prevent overlap
plt.tight_layout()

# Saving the plot
plt.savefig('images/heatmap_productivity.png')

plt.close()


useful_timestamps = """SELECT 
    -- Adjust the date to the start of the week, which is Monday
    CASE 
        WHEN strftime('%w', timestamp) = '0' THEN date(timestamp, 'weekday 1') -- If it's Sunday, move to next day (Monday)
        ELSE date(timestamp, 'weekday 1', '-7 days') -- Otherwise, move to the Monday of the current week
    END AS week_start,
    1.0 * COUNT(timestamp) / 2 / 60 as active_hours
FROM 
    LogEntryAgg le
INNER JOIN 
    window_categories wc ON le.window_title = wc.window_title
    AND wc.window_category IN ('Coding', 'RPA', 'School')
WHERE 
    (le.keyboard_events + le.mouse_events) > 0
    and (le.keyboard_events + le.mouse_events) < 150
GROUP BY
    week_start
ORDER BY
    week_start;
    """

# Get the data from the database
rows = get_data_from_query(useful_timestamps)

# Separate the week starts and active hours
week_starts, active_hours = zip(*rows)

# Create the bar chart
plt.figure(figsize=(12, 6))
plt.bar(range(len(active_hours)), active_hours, color='skyblue')

# Adding labels and title
plt.xlabel('Week Starting Date')
plt.ylabel('Active Hours')
plt.title('Active Hours by Week Start Date')

# Adjust the x-axis ticks to show the start dates of the weeks
plt.xticks(range(len(active_hours)), week_starts)

# Saving the plot
plt.savefig('images/active_hours_by_week_start.png')
# Display the plot
plt.close()


# Fetch all rows from the query
rows = get_data_from_query(productive_ratio)



# Initialize a 2D array to store the data
activity_data = np.full((7, 24), np.nan)

# Populate the activity_data array
for row in rows:
    weekday, hour, ratio = int(row[0]), int(row[1]), float(row[2])  # Ensure ratio is a float
    activity_data[weekday, hour] = ratio

# Creating the heatmap
plt.figure(figsize=(12, 6))
im = plt.imshow(activity_data, cmap=cmap_val, interpolation='nearest')

# Adding labels and title
plt.xlabel('Hour of Day')
plt.ylabel('Day of Week')
plt.title('Productive Ratio by Day and Hour')

# Adjusting the ticks to show days and hours
days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
hours = [str(i) for i in range(24)]
plt.xticks(np.arange(24), hours)
plt.yticks(np.arange(7), days)

# Add the rectangle
bottom_left_corner = (9 - 0.5, 1 - 0.5)  # Shifted by 0.5
width = 7 - 1  # Ending x-coordinate - starting x-coordinate
height = 6 - 1  # Ending y-coordinate - starting y-coordinate
rect = Rectangle(bottom_left_corner, width, height, linewidth=2, edgecolor='blue', facecolor='none')
plt.gca().add_patch(rect)

# Create a horizontal colorbar at the bottom
cbar = plt.colorbar(im, orientation='horizontal', pad=0.1, shrink=0.75)
cbar.set_label('Productivity Ratio')

# Adjust layout to prevent overlap
plt.tight_layout()

# Saving the plot and showing it
plt.savefig('images/heatmap_productive_ratio.png')
plt.close()
