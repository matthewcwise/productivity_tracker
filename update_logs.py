from sqlalchemy import create_engine, text

# Connect to the existing database
engine = create_engine('sqlite:///window_activity.db')

def clean_window_title(window_title):
    """Clean up the window title."""
    if window_title and window_title.startswith("\u25CF "):
        window_title = window_title[2:].strip()
    return window_title

def determine_application(window_title):
    if window_title.endswith(" - Google Chrome"):
        return "Google Chrome"
    if window_title in ["Portal - Direct3D 9", "Windows PowerShell"]:
        return window_title
    elif "-" in window_title:
        parts = [part.strip() for part in window_title.split("-")]
        return parts[-1]
    else:
        return window_title

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
                
                active = 1 if keyboard_events + mouse_events > 0 else 0

                # Extract details from window_title
                details = extract_window_details(window_title)
                category, project, log_type = determine_category_and_project(window_title, details["application"])
                if details["application"] == "Google Chrome":
                    category, project, log_type = determine_chrome_details(details["primary_detail"], details["secondary_detail"], window_title, category, project, log_type)

                # Debugging output
                # print(f"Updating: ID={log_id}, type={log_type}, category={category}, "
                    #   f"project={project}, active={active}, application={details['application']}, "
                    #   f"primary_detail={details['primary_detail']}, secondary_detail={details['secondary_detail']}")

                # Perform the update
                conn.execute(text("""
                    UPDATE log_entries
                    SET type = :type, category = :category, project_name = :project, 
                        active = :active, application = :application,
                        primary_window_str = :primary_window_str, secondary = :secondary
                    WHERE id = :id
                """), {
                    "type": log_type,
                    "category": category,
                    "project": project,
                    "active": active,
                    "application": details["application"],
                    "primary_window_str": details["primary_detail"],
                    "secondary": details["secondary_detail"],
                    "id": log_id
                })

            trans.commit()  # Commit the transaction
        except Exception as e:
            trans.rollback()  # Roll back the transaction on error
            print(f"Error during update: {e}")

    print("Log entries updated successfully.")

if __name__ == "__main__":
    update_log_entries()
