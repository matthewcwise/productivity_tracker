from sqlalchemy import create_engine, text
from utils import clean_window_title, determine_application, process_row

# Connect to the existing database
engine = create_engine('sqlite:///window_activity.db')

def update_log_entries():
    with engine.connect() as conn:
        trans = conn.begin()  # Start a transaction
        # try:
        result = conn.execute(text("""
            SELECT id, window_title, COALESCE(keyboard_events, 0) AS keyboard_events, 
                    COALESCE(mouse_events, 0) AS mouse_events 
            FROM log_entries order by timestamp
        """))
        rows = result.fetchall()
        previous_project = None
        previous_window_title = None
        category = None
        log_type = None

        focus_score = 0
        flow_score = 0

        for row in rows:
            log_id = row[0]
            window_title = row[1]
            keyboard_events = row[2]
            mouse_events = row[3]
            
            window_title, application, domain, detail, project, focus_score, flow_score = process_row(window_title, previous_project, previous_window_title, keyboard_events, mouse_events, focus_score, flow_score)
            
            active = 1 if keyboard_events + mouse_events > 0 else 0

            # Perform the update
            conn.execute(text("""
                UPDATE log_entries
                SET type = :type, 
                    category = :category, 
                    project_name = :project, 
                    active = :active, 
                    application = :application,
                    domain = :domain, 
                    detail = :detail,
                    flow_score = :flow_score,
                    focus_score = :focus_score
                WHERE id = :id
            """), {
                "type": log_type,
                "category": category,
                "project": project,
                "active": active,
                "application": application,
                "detail": detail,
                "domain": domain,
                "flow_score": flow_score,  # Pass flow_score
                "focus_score": focus_score,  # Pass focus_score
                "id": log_id
            })

            # Update previous values for the next iteration
            previous_project = project
            previous_window_title = window_title


        trans.commit()  # Commit the transaction
        # except Exception as e:
        #     trans.rollback()  # Roll back the transaction on error
        #     print(f"Error during update: {e}")

    print("Log entries updated successfully.")

if __name__ == "__main__":
    update_log_entries()
