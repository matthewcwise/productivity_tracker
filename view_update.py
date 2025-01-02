from sqlalchemy import text, create_engine

# Create database connection
engine = create_engine('sqlite:///window_activity.db')

def create_views():
    with engine.connect() as conn:
        # Drop the view if it exists
        conn.execute(text("DROP VIEW IF EXISTS chrome_window_titles;"))
        
        # Create the view
        conn.execute(text("""
            CREATE VIEW chrome_window_titles AS
            SELECT 
                window_title,
                project_name,
                type,
                category,
                secondary, primary_window_str,
                COUNT(*) AS usage_count
            FROM log_entries
            where (keyboard_events > 0 or mouse_events > 0)
            and application = 'Google Chrome'
            GROUP BY window_title, application, project_name, type, category, secondary, primary_window_str
            ORDER BY count(*) DESC;
        """))

        print("Views created successfully.")

if __name__ == "__main__":
    create_views()
