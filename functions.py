import pandas as pd


# def get_current_session_number():
#     # Query the maximum session_number in the database
#     max_session_number = session.query(func.max(LogEntry.session_number)).scalar()
#     return max_session_number + 1 if max_session_number is not None else 1

# Define global event counters
#### KEYBOARD / MOUSE LOGGING FUNCTIONS
# Function to reset event counters

# Function to extract website URL
# def extract_current_url():
#     """Extracts the current URL using Selenium."""
#     try:
#         # Get the current URL
#         current_url = driver.current_url
#         return current_url
#     except Exception as e:
#         print(f"Error extracting current URL: {str(e)}")