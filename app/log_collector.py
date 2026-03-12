import re
import random
from datetime import datetime
from app.database import insert_event, get_alert_rules

# Simulated log messages (since WSL has limited system logs)
SAMPLE_LOGS = [
    "Failed password for root from 192.168.1.105 port 22 ssh2",
    "Failed password for invalid user admin from 10.0.0.22 port 22",
    "Invalid user test from 203.0.113.42 port 52614",
    "Accepted password for walunj08 from 127.0.0.1 port 22",
    "Connection refused from 192.168.1.200 port 8080",
    "root login attempt from 45.33.32.156",
    "port scan detected from 198.51.100.0",
    "sudo: walunj08 : TTY=pts/0 ; USER=root ; COMMAND=/bin/bash",
    "New session opened for user walunj08",
    "System startup completed successfully",
]

def get_severity(log_line, rules):
    for rule in rules:
        if rule["pattern"].lower() in log_line.lower():
            return rule["severity"], rule["rule_name"]
    return "LOW", "General Log"

def extract_ip(log_line):
    ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
    match = re.search(ip_pattern, log_line)
    return match.group() if match else None

def collect_and_process_logs():
    try:
        rules = get_alert_rules()

        # Pick a random sample log to simulate real-time collection
        log_line = random.choice(SAMPLE_LOGS)
        severity, event_type = get_severity(log_line, rules)
        source_ip = extract_ip(log_line)

        event = {
            "event_type": event_type,
            "severity": severity,
            "source_ip": source_ip,
            "description": log_line[:200],
            "raw_log": log_line
        }

        insert_event(event)
        print(f"[{datetime.now()}] Event logged: {severity} - {event_type}")
        return event

    except Exception as e:
        print(f"Log collection error: {e}")
        return None
