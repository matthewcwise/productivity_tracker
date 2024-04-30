import time
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from dbCreate import LogEntry
# from functions import *

import pygetwindow as gw
from pynput import mouse, keyboard

# Time interval in seconds
time_interval = 30
# Interval between printed logs (in minutes)
print_log_interval = 5

# Interval between printed logs (in logged rows)
log_interval_calc = (print_log_interval * 60 + time_interval - 1) // time_interval

print(f"Productivity Tracker Started: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")

verbose = True

key_count = 0
mouse_count = 0

# Keyboard event handler
def on_press(key, verbose = False):
    global key_count
    key_count += 1
    if verbose:
        print("key count:",key_count)

# Mouse event handlers
def on_click(x, y, button, pressed, verbose = False):
    global mouse_count
    mouse_count += 1
    if verbose:
        print("mouse_count:",mouse_count, verbose = False)

def on_scroll(x, y, dx, dy, verbose = False):
    global mouse_count
    mouse_count += 1
    if verbose:
        print("mouse_count:",mouse_count)

# Reset event counters
def reset_event_counters(verbose = False):
    global mouse_count, key_count
    mouse_count = 0
    key_count = 0
    if verbose:
        print("key count:",key_count)
        print("mouse_count:",mouse_count)

# Collect mouse/keyboard events in a non-blocking fashion:
keyboard_listener = keyboard.Listener(on_press=on_press)
keyboard_listener.start()

mouse_listener = mouse.Listener(on_click=on_click,on_scroll=on_scroll)
mouse_listener.start()

# Create a session to interact with the database
engine = create_engine('sqlite:///window_activity.db')
session = Session(engine)

log_count = 0

try:
    while True:
        reset_event_counters()

        # Collect events over a 30-second interval
        time.sleep(time_interval)
        active_window = gw.getActiveWindow()
        current_time = pd.Timestamp.now()
        try:
            window_title = active_window.title
        except:
            window_title = ''

        # Create a new LogEntry and insert it into the database
        new_log_entry = LogEntry(
            timestamp=current_time,
            date=current_time.strftime('%Y-%m-%d'),
            hour=current_time.hour,  # New column
            minute=current_time.minute,  # New column
            window_title=window_title,
            keyboard_events=key_count,
            mouse_events=mouse_count
        )
        session.add(new_log_entry)
        session.commit()

        if log_count % (log_interval_calc) == 0:
            print(f"Latest Row ({log_count}):", current_time.strftime('%Y-%m-%d %H:%M:%S'),
                window_title,
                key_count,
                mouse_count)
            

        log_count +=1

except KeyboardInterrupt:  # Graceful exit on Ctrl+C
    # Clean up and exit
    session.close()  # Close the database session
    mouse_listener.stop()
    keyboard_listener.stop()
    print("Logging stopped by user.")
except Exception as e:
    print(f"An unexpected error occurred: {str(e)}")