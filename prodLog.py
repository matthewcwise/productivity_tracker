import time
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from urllib.parse import urlparse
import pygetwindow as gw
from pynput import mouse, keyboard
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from dbCreate import LogEntry
import argparse

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Productivity Tracker")
parser.add_argument('--time_interval', type=int, default=30,
                    help='Time interval in seconds')
parser.add_argument('--print_log_interval', type=float,
                    default=5, help='Interval between printed logs in minutes')
args = parser.parse_args()

# Use command-line arguments
time_interval = args.time_interval
print_log_interval = args.print_log_interval

# Interval between printed logs (in logged rows)
log_interval_calc = (print_log_interval * 60 +
                     time_interval - 1) // time_interval

print(f"Productivity Tracker Started: {
      pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Time Interval: {time_interval} seconds")
print(f"Print Log Interval: {print_log_interval} minutes")

verbose = True

key_count = 0
mouse_count = 0

# Create a SQLite database engine that will manage the local database file 'window_activity.db'.
engine = create_engine('sqlite:///window_activity.db')

# Function to extract abbreviated URL


def get_abbreviated_url(url):
    try:
        parsed_url = urlparse(url)
        return parsed_url.netloc
    except Exception as e:
        print(f"Error parsing URL: {e}")
        return None

# Keyboard event handler


def on_press(key, verbose=False):
    global key_count
    key_count += 1
    if verbose:
        print("key count:", key_count)

# Mouse event handlers


def on_click(x, y, button, pressed, verbose=False):
    global mouse_count
    mouse_count += 1
    if verbose:
        print("mouse_count:", mouse_count, verbose=False)


def on_scroll(x, y, dx, dy, verbose=False):
    global mouse_count
    mouse_count += 1
    if verbose:
        print("mouse_count:", mouse_count)

# Reset event counters


def reset_event_counters(verbose=False):
    global mouse_count, key_count
    mouse_count = 0
    key_count = 0
    if verbose:
        print("key count:", key_count)
        print("mouse_count:", mouse_count)


# Collect mouse/keyboard events in a non-blocking fashion:
keyboard_listener = keyboard.Listener(on_press=on_press)
keyboard_listener.start()

mouse_listener = mouse.Listener(on_click=on_click, on_scroll=on_scroll)
mouse_listener.start()

# Create a session to interact with the database
session = Session(engine)

log_count = 0

# Setup Selenium to use Chrome DevTools Protocol
chrome_options = Options()
chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
# Path to chromedriver
service = Service(
    'C:/Users/matt/OneDrive/Documents/chromedriver-win64/chromedriver.exe')

driver = webdriver.Chrome(service=service, options=chrome_options)


def get_active_tab_url():
    try:
        # Get the current active window handle
        original_handle = driver.current_window_handle
        active_tab = driver.current_url
        return active_tab
    except Exception as e:
        print(f"Error getting active tab URL: {e}")
        return None


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

        # Extract URL if the active window is a Chrome window
        url = None
        url_abbrev = None
        if 'Google Chrome' in window_title:
            url = get_active_tab_url()
            url_abbrev = get_abbreviated_url(url)

        # Create a new LogEntry and insert it into the database
        new_log_entry = LogEntry(
            timestamp=current_time,
            date=current_time.strftime('%Y-%m-%d'),
            hour=current_time.hour,
            minute=current_time.minute,
            url=url,
            url_abbrev=url_abbrev,
            window_url_base=url_abbrev,
            window_title=window_title,
            keyboard_events=key_count,
            mouse_events=mouse_count
        )
        session.add(new_log_entry)
        session.commit()

        if log_count % log_interval_calc == 0:
            print(f"Latest Row ({log_count}):", current_time.strftime('%Y-%m-%d %H:%M:%S'),
                  window_title,
                  url,  # Print URL if available
                  url_abbrev,  # Print abbreviated URL if available
                  key_count,
                  mouse_count)

        log_count += 1

except KeyboardInterrupt:  # Graceful exit on Ctrl+C
    # Clean up and exit
    session.close()  # Close the database session
    mouse_listener.stop()
    keyboard_listener.stop()
    driver.quit()  # Close the Selenium driver
    print("Logging stopped by user.")
except Exception as e:
    print(f"An unexpected error occurred: {str(e)}")
    driver.quit()  # Close the Selenium driver
