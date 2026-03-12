from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import threading
import time
import os

from app.database import get_all_events, get_event_counts, insert_event
from app.log_collector import collect_and_process_logs
from app.blob_service import upload_log_to_blob

app = FastAPI(title="Security Dashboard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Background log collector (runs every 30 seconds) ───
def background_collector():
    while True:
        collect_and_process_logs()
        time.sleep(30)

collector_thread = threading.Thread(
    target=background_collector, daemon=True
)
collector_thread.start()

# ─── API Routes ───
@app.get("/")
def home():
    return {"message": "Security Dashboard API is running!"}

@app.get("/api/events")
def get_events():
    events = get_all_events(limit=50)
    return {"events": [dict(e) for e in events]}

@app.get("/api/stats")
def get_stats():
    counts = get_event_counts()
    return {"stats": [dict(c) for c in counts]}

@app.post("/api/events")
def create_event(event: dict):
    insert_event(event)
    return {"message": "Event created successfully"}

@app.get("/api/collect")
def trigger_collection():
    event = collect_and_process_logs()
    return {"message": "Log collected", "event": event}

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    with open("app/templates/dashboard.html") as f:
        return f.read()

