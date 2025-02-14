import re
import pandas as pd

########################
###  Logging Functions
########################

# DATA CLEANUP

def clean_window_title(window_title):
    """Clean up the window title."""
    if window_title and window_title.startswith("\u25CF "):
        window_title = window_title[2:].strip()
    return window_title

def determine_application(window_title):
    if window_title == "Figure 1":
        return "Visual Studio Code"
    if window_title.endswith(" - Google Chrome"):
        # print("Window Title Ends with Google Chrome, ", window_title)
        return "Google Chrome"
    elif window_title.endswith("- Visual Studio Code"):
        return "Visual Studio Code"
    elif window_title in ["Portal - Direct3D 9", "Windows PowerShell"]:
        return window_title
    elif "-" in window_title:
        parts = [part.strip() for part in window_title.split("-")]
        return parts[-1]
    else:
        return window_title
    
def vs_code_breakdown(window_title):
    if window_title == "Figure 1":
        return "prod", "Figure 1"
    abbreviated = window_title.split(" - Visual Studio Code")[0].strip()
    folder = abbreviated.split("-")[1].strip()
    file = abbreviated.split("-")[0].strip()
    return folder, file


chat_gpt_conversations = {
    "Session Tracking Logic":"prod",
    "Rename Columns in DB":"prod",
                          }

enders = [" - Google Chrome",
          "- Visual Studio Code",
          "| LinkedIn",
          "- Slack",
          "- Search",
          "- Wikipedia",
          "- Google Sheets",
          "- Google Docs",
          "| ESPN",
          "- Watch ESPN",
          "- YouTube"
          "NCAA.com"]            
beginners = ["Amazon.com",
             "Meet - ",
             "Google Calendar - ",
             "TherapyAI - Calendar - ",
             "- YouTube",
             "Messenger",
             "Slack", "Search", "Wikipedia", "Google Sheets", "ESPN", "Your Orders"]

def chrome_breakdown(window_title):
    abbreviated = window_title.split(" - Google Chrome")[0].strip()
    domain = abbreviated
    detail = None
    # try:
    #     # This is the list of ChatGPT conversations
        
    if abbreviated in chat_gpt_conversations:
        domain = "ChatGPT"
        detail = abbreviated
        return domain, detail
    elif abbreviated.endswith("Messenger"):
        domain = "FacebookMessenger"
        detail = abbreviated.split("| Messenger")[0].strip()
        return domain, detail
    for beginner in beginners:
        if abbreviated.startswith(beginner):
            # domain = beginner
            domain = re.sub(r'[ \|\:\;\-]', '', beginner)
            detail = abbreviated.split(beginner)[1].strip()
            return domain, detail
    for end in enders:
        if abbreviated.endswith(end):
            # domain = abbreviated.split(end)[0].strip()
            domain = re.sub(r'[ \|\:\;\-]', '', end)
            detail = abbreviated.split(end)[0].strip()
            return domain, detail
    return domain, detail

def assign_container_detail(window_title, application):
    # try:
    if application == "Visual Studio Code":
        return vs_code_breakdown(window_title)
    elif application == "Google Chrome":
        return chrome_breakdown(window_title)
    else:
        return None, None
    # except:
    #     return None, None


def determine_project(application, container, detail, previous_project):
    if application == "Visual Studio Code":
        return container
    
    if application == "WhatsApp":
        return "Communication"
    
    # if application in ["pgAdmin 4", "Calculator", "Task Switching"]:
    #     return previous_project
    
    if detail in ["Matt/Thomas 1:1 (recurring)", "Notes - Matt/Thomas 1:1 (recurring)"]:
        return "Matt/Thomas 1:1"
    
    elif application == "Google Chrome":
        if container == "ChatGPT":
            if detail in chat_gpt_conversations:
                return chat_gpt_conversations[detail]
            else:
                return previous_project
        else:
            return container
    else:
        return application

def update_focus_flow(old_flow_score, old_focus_score, 
                      project, previous_project, 
                      window_title, previous_window_title,
                      keyboard_events, mouse_events,
                      alpha = 0.15,
                      max_events = 20
                      ):
    """Update the focus and flow scores.
    These increment when there is activity and the thing remains the same. They reset when there is a switch. They do not change when the the thing remains the same but there is no activity. We don't penalize inactivity here bc there could be valuable things going on, but we don't want to automatically count it as a flow/focus.    
    """
    events = keyboard_events + mouse_events
    # Update focus_score
    if project == previous_project:
        row_focus_score = min(events/max_events, 1)
    else:
        row_focus_score = 0
        
    if window_title == previous_window_title:
        row_flow_score = min(events/max_events, 1)
    else:
        row_flow_score = 0
        
    flow_score = alpha * row_flow_score + (1 - alpha) * old_flow_score
    focus_score = alpha * row_focus_score + (1 - alpha) * old_focus_score

    return round(focus_score, 3), round(flow_score, 3)


def process_row(window_title, previous_project, previous_window_title, keyboard_events, mouse_events, focus_score, flow_score):
    window_title = clean_window_title(window_title)
    application = determine_application(window_title)
    domain, detail = assign_container_detail(window_title, application)
    project = determine_project(application, domain, detail, previous_project)
    focus_score, flow_score = update_focus_flow(flow_score, focus_score, 
                      project, previous_project, 
                      window_title, previous_window_title,
                      keyboard_events, mouse_events
                      )
    return window_title, application, domain, detail, project, focus_score, flow_score