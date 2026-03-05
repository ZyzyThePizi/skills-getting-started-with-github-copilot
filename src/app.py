"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path
from typing import Dict

# Default activity database
DEFAULT_ACTIVITIES = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Basketball Team": {
        "description": "Competitive basketball training and matches",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 15,
        "participants": ["alex@mergington.edu"]
    },
    "Tennis Club": {
        "description": "Tennis skills development and friendly competitions",
        "schedule": "Saturdays, 10:00 AM - 12:00 PM",
        "max_participants": 16,
        "participants": ["james@mergington.edu", "isabella@mergington.edu"]
    },
    "Drama Club": {
        "description": "Theater performance and script writing",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 25,
        "participants": ["grace@mergington.edu"]
    },
    "Art Studio": {
        "description": "Painting, drawing, and sculpture classes",
        "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
        "max_participants": 18,
        "participants": ["aria@mergington.edu", "maya@mergington.edu"]
    },
    "Debate Team": {
        "description": "Competitive debate and critical thinking skills",
        "schedule": "Wednesdays, 3:30 PM - 4:30 PM",
        "max_participants": 14,
        "participants": ["lucas@mergington.edu"]
    },
    "Science Club": {
        "description": "Explore STEM concepts through hands-on experiments",
        "schedule": "Fridays, 2:00 PM - 3:30 PM",
        "max_participants": 20,
        "participants": ["noah@mergington.edu", "ava@mergington.edu"]
    }
}

# In-memory activity database (mutable instance)
activities = DEFAULT_ACTIVITIES.copy()


def get_activities_db() -> Dict:
    """Dependency injection for activities database"""
    return activities


app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_all_activities(activities_db: Dict = Depends(get_activities_db)):
    return activities_db


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str, activities_db: Dict = Depends(get_activities_db)):
    """Sign up a student for an activity"""
    # Validate activity exists
    if activity_name not in activities_db:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities_db[activity_name]

    # Validate student is not already signed up
    if email in activity["participants"]:
        raise HTTPException(status_code=400, detail="Student already signed up")

    # Add student
    activity["participants"].append(email)
    return {"message": f"Signed up {email} for {activity_name}"}


@app.post("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str, activities_db: Dict = Depends(get_activities_db)):
    """Unregister a student from an activity"""
    # Validate activity exists
    if activity_name not in activities_db:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities_db[activity_name]

    # Remove student if they exist in the participants list
    if email in activity["participants"]:
        activity["participants"].remove(email)
        return {"message": f"Removed {email} from {activity_name}"}
    else:
        raise HTTPException(status_code=404, detail="Student not found in this activity")
