import threading
import time
import pandas as pd
from sqlalchemy import create_engine
from utils import clean_window_title, determine_application, assign_container_detail
from sqlalchemy.orm import Session
from dbCreate import LogEntry
import pygetwindow as gw
from pynput import mouse, keyboard

# We track
# - the window title
# - the application
# - This is broken down into:
#   - Domain (Chrome)/Folder (VS Code)
#   - Webpage (Chrome)/File (VS Code)
# - the number of mouse events

# Time interval in seconds
time_interval = 30
print_log_interval = 5

log_interval_calc = (print_log_interval * 60 + time_interval - 1) // time_interval
print(f"Productivity Tracker Started: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")

verbose = True
stop_flag = False  # Flag to stop the user input thread
key_count = 0
mouse_count = 0

# Initialize the event counters
key_count = 0
mouse_count = 0


# Event counters
def on_press(key, verbose=False):
    global key_count
    key_count += 1

def on_click(x, y, button, pressed, verbose=False):
    global mouse_count
    mouse_count += 1

def on_scroll(x, y, dx, dy, verbose=False):
def on_scroll(x, y, dx, dy, verbose=False):
    global mouse_count
    mouse_count += 1

def reset_event_counters(verbose=False):
    global mouse_count, key_count
    mouse_count = 0
    key_count = 0


current_user = "Matt"


# Separate thread for user input
def user_input_handler():
    global current_user, stop_flag
    while not stop_flag:
        user_input = input(f"""Enter your name (or press Enter to keep the current user ({current_user})): """).strip()
        if user_input:
            change_time = pd.Timestamp.now()
            current_user = user_input
            print(f"User switched to: {current_user} at {change_time}\n")

# Start the user input thread
input_thread = threading.Thread(target=user_input_handler, daemon=True)
input_thread.start()

# Set up mouse and keyboard listeners
keyboard_listener = keyboard.Listener(on_press=on_press)
keyboard_listener.start()

mouse_listener = mouse.Listener(on_click=on_click, on_scroll=on_scroll)
mouse_listener.start()

# Create a session to interact with the database
session = Session(engine)

log_count = 0
# Initialize flow_score and previous_window_title
flow_score = 0
previous_window_title = None

try:
    while True:
        reset_event_counters()

        # Collect events over a time interval
        time.sleep(time_interval)
        active_window = gw.getActiveWindow()
        current_time = pd.Timestamp.now()

        try:
            window_title = active_window.title
        except:
            window_title = ''
        
        window_title = clean_window_title(window_title)
        application = determine_application(window_title)
        container, detail = assign_container_detail(window_title, application)

        # Update flow_score
        if window_title == previous_window_title:
            flow_score += 1
        else:
            flow_score = 0  # Reset flow_score if the window_title changes

        # Update previous_window_title for next iteration
        previous_window_title = window_title

        # Create a new LogEntry and insert it into the database
        new_log_entry = LogEntry(
            timestamp=current_time,
            window_title=window_title,
            application=application,
            domain=container,
            detail=detail,
            keyboard_events=key_count,
            mouse_events=mouse_count,
            user=current_user,  # Add user to the log entry
            flow_score=flow_score  # Include flow_score in the log entry
        )

        session.add(new_log_entry)
        session.commit()

        if log_count % log_interval_calc == 0:
        if log_count % log_interval_calc == 0:
            print(f"Latest Row ({log_count}):", current_time.strftime('%Y-%m-%d %H:%M:%S'),
                  window_title, key_count, mouse_count, flow_score, current_user)

        log_count += 1

except KeyboardInterrupt:  # Graceful exit on Ctrl+C
    stop_flag = True  # Stop the input thread
    session.close()  # Close the database session
    mouse_listener.stop()
    keyboard_listener.stop()
    print("Logging stopped by user.")
except Exception as e:
    print(f"An unexpected error occurred: {str(e)}")
