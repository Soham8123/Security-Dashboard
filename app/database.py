import psycopg2
import psycopg2.extras
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT"),
        sslmode="require"
    )

def insert_event(event):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO security_events 
        (event_type, severity, source_ip, description, raw_log)
        VALUES (%s, %s, %s, %s, %s)
    """, (
        event["event_type"],
        event["severity"],
        event.get("source_ip"),
        event["description"],
        event.get("raw_log")
    ))
    conn.commit()
    cur.close()
    conn.close()

def get_all_events(limit=100):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""
        SELECT * FROM security_events 
        ORDER BY created_at DESC LIMIT %s
    """, (limit,))
    events = cur.fetchall()
    cur.close()
    conn.close()
    return events

def get_event_counts():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""
        SELECT severity, COUNT(*) as count 
        FROM security_events 
        GROUP BY severity
    """)
    counts = cur.fetchall()
    cur.close()
    conn.close()
    return counts

def get_alert_rules():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM alert_rules WHERE is_active = TRUE")
    rules = cur.fetchall()
    cur.close()
    conn.close()
    return rules
