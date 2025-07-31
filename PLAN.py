from ics import Calendar, Event
from datetime import datetime, timedelta

# Define the project plan (Phase Name, Start Date, End Date, Description)
tasks = [
    ("Foundation & Scoping", "2024-06-18", "2024-06-22", "Literature review, problem definition, and use case finalization"),
    ("Stimuli & Baselines", "2024-06-23", "2024-06-25", "Select video stimuli and define baseline models"),
    ("Web Platform Finalization", "2024-06-26", "2024-06-28", "Build and test data collection web interface"),
    ("Pilot Data Collection & Preprocessing", "2024-06-29", "2024-07-05", "Pilot data collection and preprocessing pipeline"),
    ("Multi-user (3–4) Data Collection", "2024-07-06", "2024-07-10", "Small group data collection and variability analysis"),
    ("Baseline Model Training & Evaluation", "2024-07-11", "2024-07-18", "Train and evaluate baseline models"),
    ("Scaled Data Collection (20 Users)", "2024-07-19", "2024-08-10", "Full-scale data collection and aggregation"),
    ("Novel Model Development & Evaluation", "2024-08-11", "2024-09-05", "Develop and evaluate novel model"),
    ("Deployment & Final User Study", "2024-09-06", "2024-09-25", "Deploy model and run final user study"),
]

# Create a calendar
calendar = Calendar()

for title, start_str, end_str, description in tasks:
    start = datetime.strptime(start_str, "%Y-%m-%d")
    end = datetime.strptime(end_str, "%Y-%m-%d") + timedelta(days=1)  # ICS end date is exclusive
    event = Event()
    event.name = f"Phase: {title}"
    event.begin = start
    event.end = end
    event.description = description
    calendar.events.add(event)

# Save the calendar to a .ics file
with open("project_timeline.ics", "w") as f:
    f.writelines(calendar)

print("ICS file 'project_timeline.ics' created successfully.")
