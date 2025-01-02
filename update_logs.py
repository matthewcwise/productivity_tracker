from sqlalchemy import create_engine, text
from utils import clean_window_title, determine_application, assign_container_detail

# Connect to the existing database
engine = create_engine('sqlite:///window_activity.db')


def extract_window_details(window_title):
    """Extract details from the window title."""
    # Remove leading "● " if present
    window_title = clean_window_title(window_title)

    application = determine_application(window_title)
    
    return {
        "primary_detail": window_title, 
        "secondary_detail": None,
        "application": window_title,
        "log_type": None
    }

def determine_category_and_project(window_title, application):
    """Determine the category and project based on the window title."""
    category = "unknown"
    project = None
    log_type = None

    if application in ["Visual Studio Code", "Windows PowerShell"]:
        log_type = "coding"

    elif application in ["Spotify Premium"]:
        log_type = "music"

    elif application in ["StarCraft II"]:
        log_type = "game"

    if window_title and "- Visual Studio Code" in window_title:
        project = window_title.split("-")[1].strip()
        if project.startswith("."):
            project = project[1:].strip()  # Remove leading dot
        category = "Work" if project == "tai_ai_api" else "Personal Coding"

    return category, project, log_type

def determine_chrome_details(primary_window_str, secondary, window_title, category, project, log_type):
    """Determine the category and project based on the window title."""

    if window_title.startswith("Amazon.com"):
        category = "shopping"
        project = "shopping"
        log_type = "shopping"

    if primary_window_str in ["Google Calendar"]:
        log_type = "calendar"
        category = "calendar"
        project = "calendar"

    if primary_window_str in ["Messenger"]:
        log_type = "messaging"
        category = "communication"
        project = "communication"
    
    elif primary_window_str in ["Database Productivity Tracking Improvements"]:
        project = 'prod'
        log_type = 'coding'
        category = 'Personal Coding'
    
    elif primary_window_str in ["Track which conferences are winning the 2024"] or secondary in ["Stream the Game Live"]:

        project = 'NCAAF'
        log_type = 'football'
        category = 'diversion'
    
        
    return category, project, log_type

def update_log_entries():
    with engine.connect() as conn:
        trans = conn.begin()  # Start a transaction
        try:
            result = conn.execute(text("""
                SELECT id, window_title, COALESCE(keyboard_events, 0) AS keyboard_events, 
                       COALESCE(mouse_events, 0) AS mouse_events 
                FROM log_entries
            """))
            rows = result.fetchall()

            for row in rows:
                log_id = row[0]
                window_title = row[1]
                keyboard_events = row[2]
                mouse_events = row[3]
                
                window_title = clean_window_title(window_title)
                application = determine_application(window_title)
                domain, detail = assign_container_detail(window_title, application)
                project = "Unknown"
                category = "Unknown"
                log_type = "Unknown"
                
                active = 1 if keyboard_events + mouse_events > 0 else 0

                # Perform the update
                conn.execute(text("""
                    UPDATE log_entries
                    SET type = :type, category = :category, project_name = :project, 
                        active = :active, application = :application,
                        domain = :domain, detail = :detail
                    WHERE id = :id
                """), {
                    "type": log_type,
                    "category": category,
                    "project": project,
                    "active": active,
                    "application": application,
                    "detail": detail,
                    "domain": domain,
                    "id": log_id
                })

            trans.commit()  # Commit the transaction
        except Exception as e:
            trans.rollback()  # Roll back the transaction on error
            print(f"Error during update: {e}")

    print("Log entries updated successfully.")

if __name__ == "__main__":
    update_log_entries()
