import os
import json
from datetime import datetime
from app.database import get_all_events, get_connection
from app.blob_service import upload_log_to_blob
from dotenv import load_dotenv

load_dotenv()

def archive_logs_to_blob():
    try:
        # Get all events from database
        events = get_all_events(limit=1000)

        if not events:
            print("No events to archive.")
            return

        # Create a log file locally
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"security_log_{timestamp}.json"
        file_path = f"logs/{file_name}"

        os.makedirs("logs", exist_ok=True)

        # Write events to JSON file
        with open(file_path, "w") as f:
            json.dump([dict(e) for e in events], f, indent=2, default=str)

        print(f"Created log file: {file_path}")

        # Upload to Azure Blob Storage
        success = upload_log_to_blob(file_path, file_name)

        if success:
            # Record in database
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO archived_logs (file_name, blob_url)
                VALUES (%s, %s)
            """, (file_name, f"azure-blob://{file_name}"))
            conn.commit()
            cur.close()
            conn.close()
            print(f"✅ Successfully archived {len(events)} events to Azure Blob!")
        else:
            print("❌ Blob upload failed.")

    except Exception as e:
        print(f"Archive error: {e}")

if __name__ == "__main__":
    archive_logs_to_blob()
