import matplotlib.pyplot as plt
from flask import Flask, render_template, send_file
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from create_db import LogEntry  # Assuming create_db contains LogEntry definition
import pandas as pd
import io

app = Flask(__name__)

# Database setup
engine = create_engine('sqlite:///window_activity.db')
session = Session(engine)

@app.route('/')
def index():
    # Fetch data from the database (e.g., data from the last 30 minutes)
    # Modify the query to suit your specific data selection criteria
    query = session.query(LogEntry.timestamp, LogEntry.keyboard_events, LogEntry.mouse_events) \
                   .filter(LogEntry.timestamp >= pd.Timestamp.now() - pd.Timedelta(minutes=30)) \
                   .all()

    # Process the data as needed for visualization
    timestamps = [row.timestamp for row in query]
    keyboard_events = [row.keyboard_events for row in query]
    mouse_events = [row.mouse_events for row in query]

    # Create visualizations (example plots using Matplotlib)
    plt.figure(figsize=(12, 6))

    # Plot keyboard events over time (example)
    plt.subplot(2, 1, 1)
    plt.plot(timestamps, keyboard_events, label='Keyboard Events')
    plt.xlabel('Time')
    plt.ylabel('Keyboard Events')
    plt.title('Keyboard Events Over Time')
    plt.grid(True)
    plt.legend()

    # Plot mouse events over time (example)
    plt.subplot(2, 1, 2)
    plt.plot(timestamps, mouse_events, label='Mouse Events', color='orange')
    plt.xlabel('Time')
    plt.ylabel('Mouse Events')
    plt.title('Mouse Events Over Time')
    plt.grid(True)
    plt.legend()

    # Save the plots to a temporary file
    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png')
    img_buf.seek(0)

    # Generate HTML page with embedded plots
    return render_template('index.html', img_data=img_buf.getvalue())

if __name__ == '__main__':
    app.run(debug=True)
