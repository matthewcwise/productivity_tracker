import pygetwindow as gw
import time
import pandas as pd
import os
import regex as re
from functions import *
import matplotlib.pyplot as plt
import numpy as np

# Function to extract app name
def extract_app_name(title):
    # Define a list of keywords in the desired order of priority
    keywords = [
        'Overleaf',
        'Gmail',
        'Khan Academy',
        'Search',
        'Google Sheets',
        'Prime Video',
        'Ed Discussion',
        'Solitaire',
        'TurboTax',
        'Google Calendar',
        'Visual Studio Code',
        'Wikipedia',
        'Command Line'
    ]
    try:
        # Iterate through the keywords and try to find a match in the title
        for keyword in keywords:
            match = re.search(rf'\b{re.escape(keyword)}\b', title, re.IGNORECASE)
            if match:
                return keyword.strip()

        # If no keyword is found, return 'unknown'
        return 'unknown'
    except:
        return 'unknown'

# Function to categorize window titles
def categorize_title(title):
    for category, keywords in categories.items():
        if any(keyword in title for keyword in keywords):
            return category
    return 'Other'  # Default category

# Function to extract website URL
def extract_website_url(title):
    if 'Browsers' in title:  # Check if the category is related to browsers
        match = re.search(r'https?://([^\s/$.?#].[^\s]*)', title)
        return match.group(0).strip() if match else 'unknown'
    return 'unknown'

# Function to save logs
def save_logs(log_df):
    log_df.to_csv(log_filename, index=False)
    print("Logs saved.")

def plot_dynamic_chart(df):
    # Extract the last 60 rows
    last_60 = df.tail(60)

    # Count occurrences for each 'app_name'
    title_counts = last_60['app_name'].value_counts()

    # Map categories to colors
    unique_categories = last_60['category'].unique()
    color_map = plt.cm.get_cmap('Set1', len(unique_categories))
    category_to_color = {cat: color_map(i) for i, cat in enumerate(unique_categories)}

    # Create a dictionary mapping app names to their most recent category
    app_to_category = {row['app_name']: row['category'] for _, row in last_60.iterrows()}

    # Get the corresponding color for each 'app_name' based on its category
    colors = [category_to_color[app_to_category[title]] for title in title_counts.index]

    # Draw horizontal bar chart
    plt.clf()  # Clear the current figure
    title_counts.plot(kind='barh', color=colors, alpha=0.7)
    plt.title("app_name count (Last 60 Entries)")
    plt.ylabel("app_name")
    plt.xlabel("count")
    plt.tight_layout()

    plt.draw()  # Redraw the figure
    plt.pause(0.1)  # Allow plot to update

print(f"Logging begun: {pd.Timestamp.now()}")

# File name
log_filename = 'window_activity_log.csv'

# Initialize DataFrame
columns=['window_title', 'app_name', 'timestamp', 'category']

if os.path.exists(log_filename):
    # Load existing logs if file exists
    log_df = pd.read_csv(log_filename)
else:
    # Create new DataFrame if no logs exist
    log_df = pd.DataFrame(columns=columns)

# Define a dictionary of categories and keywords that identify them
categories = {
    'Games': ['Minecraft', 'Among Us', 'Steam', 'Solitaire'],  # Example game titles
    'Coding': ['Studio Code', 'python'],
    'School': ['Overleaf', 'Khan Academy', 'Ed Discussion'],
    'Productivity': ['Gmail', 'Command Line'],
    'Browsers' : ['Chrome', 'Firefox', 'Edge'],
    'Video': ['Prime Video', 'YouTube'],
    # Add more categories as needed...
}

# Initialize matplotlib interactive mode
plt.ion()
plot_dynamic_chart(log_df)

# Time tracking loop
try:
    while True:
        active_window = gw.getActiveWindow()
        current_time = pd.Timestamp.now()
        
        # Categorizing
        try:
            category = categorize_title(active_window.title)
        except:
            category = 'unknown'

        # Logging
        log_df = log_df.append({
            'window_title': active_window.title,
            'app_name': extract_app_name(active_window.title),
            'timestamp': current_time,
            'category': category
        }, ignore_index=True)

        # Save logs every 10 entries (5 minutes)
        if len(log_df) % 10 == 0:
            save_logs(log_df)

        # Print latest log every 30 minutes, show dynamic chart
        if len(log_df) % 60 == 0:
            print(f"Latest log:\n 'window_title': {active_window.title}\n 'timestamp': {current_time}\n 'category': {category}")
            plot_dynamic_chart(log_df)

        # Pause for 30 seconds
        time.sleep(30)

except KeyboardInterrupt:  # Graceful exit on Ctrl+C
    save_logs(log_df)
    print("Logging stopped by user.")
