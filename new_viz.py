from sqlalchemy import create_engine, text
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Step 1: Connect to the database using SQLAlchemy
engine = create_engine('sqlite:///window_activity.db')

# Step 2: Query the required data
query = text("""
SELECT timestamp, focus_score, flow_score, keyboard_events, mouse_events, project_name
FROM log_entries
WHERE DATE(DATETIME(timestamp, '-9 hours')) = DATE(DATETIME('now', '-9 hours'))  -- Adjust to Los Angeles timezone
""")
with engine.connect() as conn:
    result = conn.execute(query)
    # Convert query result to a pandas DataFrame
    data = pd.DataFrame(result.fetchall(), columns=result.keys())

# Step 3: Convert timestamp to datetime
data['timestamp'] = pd.to_datetime(data['timestamp'])

# Step 4: Calculate a trailing average of 10 for focus and flow scores
data['focus_score_avg'] = data['focus_score'].rolling(window=10).mean()
data['flow_score_avg'] = data['flow_score'].rolling(window=10).mean()

# Step 5: Group by hour and count rows where focus_score > 0.7, then divide by 2 to get "minutes"
data['hour'] = data['timestamp'].dt.floor('H')  # Round down to the hour
focus_counts = data[data['focus_score'] > 0.7].groupby('hour').size() / 2  # Convert count to "minutes"

# Step 6: Calculate average focus score per hour when keyboard_events + mouse_events > 0
filtered_data = data[data['keyboard_events'] + data['mouse_events'] > 0]
average_focus = filtered_data.groupby('hour')['focus_score'].mean()

# Step 7: Calculate total activity per hour
total_activity = filtered_data.groupby('hour')[['keyboard_events', 'mouse_events']].sum().sum(axis=1)

# Step 8: Calculate focus time per project
focus_data = data[data['focus_score'] > 0.7]
focus_time_per_project = focus_data.groupby('project_name').size() / 2  # Each row is 30 seconds

# Step 9: Categorize into top 5 projects and "Other"
top_projects = focus_time_per_project.nlargest(5)
other_focus_time = focus_time_per_project.loc[~focus_time_per_project.index.isin(top_projects.index)].sum()
top_projects_with_other = pd.concat([top_projects, pd.Series(other_focus_time, index=['Other'])])

# Step 10: Create a 2x2 plot layout
fig, axs = plt.subplots(2, 2, figsize=(16, 12))

# Plot 1: Line chart (Focus and Flow Scores)
axs[0, 0].plot(data['timestamp'], data['focus_score_avg'], label="Focus Score (Trailing Avg)", linewidth=2)
axs[0, 0].plot(data['timestamp'], data['flow_score_avg'], label="Flow Score (Trailing Avg)", linewidth=2)
for hour in data['hour'].unique():
    axs[0, 0].axvline(hour, color='gray', linestyle='--', linewidth=0.5, alpha=0.7)
axs[0, 0].xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
axs[0, 0].set_title('Focus and Flow Scores Over Time (Trailing Average)', fontsize=14)
axs[0, 0].set_xlabel('Time (Hour)', fontsize=12)
axs[0, 0].set_ylabel('Scores', fontsize=12)
axs[0, 0].legend(title="Legend", loc='upper left')

# Plot 2: Bar chart (Focus counts per hour in minutes)
axs[0, 1].bar(focus_counts.index, focus_counts.values, width=0.03, align='center', color='skyblue', edgecolor='black')
axs[0, 1].xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
axs[0, 1].xaxis.set_major_locator(mdates.HourLocator())
axs[0, 1].set_title('Minutes with Focus Score > 0.7 per Hour', fontsize=14)
axs[0, 1].set_xlabel('Time (Hour)', fontsize=12)
axs[0, 1].set_ylabel('Minutes', fontsize=12)

# Plot 3: Bar chart (Total activity per hour with focus score line)
ax2 = axs[1, 0].twinx()  # Create a twin y-axis for the second y-axis
bars = axs[1, 0].bar(total_activity.index, total_activity.values, width=0.03, align='center', color='blue', edgecolor='black', label="Total Activity")
line, = ax2.plot(average_focus.index, average_focus.values, label="Average Focus Score", color='orange', marker='o', linewidth=2)
axs[1, 0].xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
axs[1, 0].xaxis.set_major_locator(mdates.HourLocator())
axs[1, 0].set_title('Total Activity and Average Focus Score per Hour', fontsize=14)
axs[1, 0].set_xlabel('Time (Hour)', fontsize=12)
axs[1, 0].set_ylabel('Total Activity (Keyboard + Mouse)', fontsize=12)
ax2.set_ylabel('Average Focus Score', fontsize=12)
handles, labels = [], []
for ax in [axs[1, 0], ax2]:
    h, l = ax.get_legend_handles_labels()
    handles.extend(h)
    labels.extend(l)
axs[1, 0].legend(handles, labels, title="Metrics", loc='upper left')

# Plot 4: Stacked bar chart (Focus time by project)
top_projects_with_other.plot(kind='bar', ax=axs[1, 1], color=['orange', 'blue', 'green', 'purple', 'red', 'gray'], legend=False)
axs[1, 1].set_title('Total Focus Time by Project (Top 5 + Other)', fontsize=14)
axs[1, 1].set_xlabel('Projects', fontsize=12)
axs[1, 1].set_ylabel('Total Focus Time (Minutes)', fontsize=12)
axs[1, 1].legend(title="Projects", loc='upper left', labels=top_projects_with_other.index)

# Adjust layout and save
plt.tight_layout()
plt.savefig('focus_scores_with_activity_and_projects_chart_2x2.png')