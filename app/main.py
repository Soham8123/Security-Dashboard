from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
import threading, time
from app.database import (get_all_events, get_event_counts, 
                          insert_event, delete_event, 
                          update_event, get_event_by_id)
from app.log_collector import collect_and_process_logs

app = FastAPI(title="Security Dashboard")
templates = Jinja2Templates(directory="app/templates")

app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_methods=["*"], allow_headers=["*"])

def background_collector():
    while True:
        collect_and_process_logs()
        time.sleep(30)

threading.Thread(target=background_collector, daemon=True).start()

# ── Page Routes ──────────────────────────
@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    events = get_all_events(50)
    counts = get_event_counts()
    stats = {"CRITICAL":0,"HIGH":0,"MEDIUM":0,"LOW":0}
    for c in counts:
        stats[c["severity"]] = c["count"]
    return templates.TemplateResponse("dashboard.html", {
        "request": request, "events": events, "stats": stats
    })

@app.get("/events", response_class=HTMLResponse)
def events_page(request: Request):
    events = get_all_events(100)
    return templates.TemplateResponse("events.html", {
        "request": request, "events": events
    })

# ── CRUD API Routes ───────────────────────
@app.get("/api/events")
def api_events():
    return {"events": [dict(e) for e in get_all_events(50)]}

@app.get("/api/stats")
def api_stats():
    counts = get_event_counts()
    return {"stats": [dict(c) for c in counts]}

@app.get("/api/collect")
def trigger_collect():
    event = collect_and_process_logs()
    return {"message": "Collected", "event": event}

@app.post("/events/add")
def add_event(
    event_type: str = Form(...),
    severity: str = Form(...),
    source_ip: str = Form(...),
    description: str = Form(...)
):
    insert_event({
        "event_type": event_type,
        "severity": severity,
        "source_ip": source_ip,
        "description": description,
        "raw_log": description
    })
    return RedirectResponse(url="/events", status_code=303)

@app.post("/events/delete/{event_id}")
def remove_event(event_id: int):
    delete_event(event_id)
    return RedirectResponse(url="/events", status_code=303)

@app.post("/events/update/{event_id}")
def edit_event(
    event_id: int,
    event_type: str = Form(...),
    severity: str = Form(...),
    source_ip: str = Form(...),
    description: str = Form(...)
):
    update_event(event_id, {
        "event_type": event_type,
        "severity": severity,
        "source_ip": source_ip,
        "description": description
    })
    return RedirectResponse(url="/events", status_code=303)
