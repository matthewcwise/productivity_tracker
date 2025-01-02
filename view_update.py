# from sqlalchemy import text, create_engine

# # Create database connection
# engine = create_engine('sqlite:///window_activity.db')

# def create_views():
#     with engine.connect() as conn:
#         # Drop the view if it exists
#         conn.execute(text("DROP VIEW IF EXISTS chrome_window_titles;"))
        
#         # Create the view
#         conn.execute(text("""
#             CREATE VIEW chrome_window_titles AS
#             SELECT 
#                 window_title,
#                 project_name,
#                 type,
#                 category,
#                 secondary, primary_window_str,
#                 COUNT(*) AS usage_count
#             FROM log_entries
#             where (keyboard_events > 0 or mouse_events > 0)
#             and application = 'Google Chrome'
#             GROUP BY window_title, application, project_name, type, category, secondary, primary_window_str
#             ORDER BY count(*) DESC;
#         """))

#         print("Views created successfully.")

# if __name__ == "__main__":
#     create_views()
from sqlalchemy import text, create_engine

# Create database connection
engine = create_engine('sqlite:///window_activity.db')

def create_views():
    with engine.connect() as conn:
        # Drop the view if it exists
        conn.execute(text("DROP VIEW IF EXISTS log_entries_today;"))
        
        # Create the view for the current calendar date
        conn.execute(text("""
            CREATE VIEW log_entries_today AS
            SELECT 
                id, timestamp, keyboard_events, mouse_events, application, domain, detail, project_name, user, focus_score, flow_score, window_title
            FROM log_entries
            WHERE DATE(DATETIME(timestamp, '-9 hours')) = DATE(DATETIME('now', '-9 hours'))  -- Adjust to Los Angeles timezone
            
ORDER BY id ASC;
        """))

        print("Views created successfully.")

if __name__ == "__main__":
    create_views()

# WHERE DATE(timestamp) = DATE('now')  -- Filter for current calendar date

from sqlalchemy import text, create_engine

# Create database connection
engine = create_engine('sqlite:///window_activity.db')

def create_views():
    with engine.connect() as conn:
        # Drop the view if it exists
        conn.execute(text("DROP VIEW IF EXISTS summary_today;"))
        
        # Create the view for the current calendar date
        conn.execute(text("""
            CREATE VIEW summary_today AS
            SELECT 
    project_name,
    COUNT(*) / 2 AS active_minutes,
    (SUM(keyboard_events) / COUNT(*)) / 2 AS keyboard_events, 
    (SUM(mouse_events) / COUNT(*)) / 2 AS mouse_events, 
    max(focus_score) AS max_focus_score,
    MAX(flow_score) AS max_flow_score
FROM log_entries_today
WHERE (keyboard_events > 0 OR mouse_events > 0)
GROUP BY project_name
ORDER BY active_minutes DESC;       -- Then by active minutes for each row

        """))

        print("Views created successfully.")

if __name__ == "__main__":
    create_views()

# WHERE DATE(timestamp) = DATE('now')  -- Filter for current calendar date

#             SELECT 
#     application,
#     project_name,
#     domain,
#     detail, 
#     COUNT(*) / 2 AS active_minutes,
#     (SUM(keyboard_events) / COUNT(*)) / 2 AS keyboard_events, 
#     (SUM(mouse_events) / COUNT(*)) / 2 AS mouse_events, 
#     MAX(flow_score) AS max_flow_score,
#     SUM(COUNT(*) / 2) OVER (PARTITION BY project_name) AS total_active_minutes -- Total active minutes per project
# FROM log_entries_today
# WHERE (keyboard_events > 0 OR mouse_events > 0)
# GROUP BY application, 
#          project_name,
#          domain,
#          detail
# ORDER BY total_active_minutes DESC, -- Order by total active minutes across applications
#          active_minutes DESC;       -- Then by active minutes for each row
