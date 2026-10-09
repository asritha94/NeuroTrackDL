import json
import time
import csv
import os
from smart_scheduler import smart_schedule

# ================== FILES ==================
STATUS_FILE = "current_status.json"
LOG_FILE = "fatigue_log.csv"

# ================== CSV SETUP ==================
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "time",
            "blink_count",
            "ear",
            "pitch",
            "yaw",
            "roll",
            "fatigue",
            "suggestion"
        ])

print("✅ NeuroTrackDL Logger Started")
print("📄 Waiting for live data from camera.py ...")

# ================== MAIN LOOP ==================
while True:
    if not os.path.exists(STATUS_FILE):
        time.sleep(1)
        continue

    try:
        with open(STATUS_FILE, "r") as f:
            status = json.load(f)

        # READ VALUES
        ear = status.get("ear", 0)
        blink_count = status.get("blink_count", 0)
        pitch = status.get("pitch", 0)
        yaw = status.get("yaw", 0)
        roll = status.get("roll", 0)

        # SMART SCHEDULING
        fatigue, suggestion = smart_schedule(blink_count, ear, pitch)

        # UPDATE STATUS (optional overwrite)
        status["fatigue"] = fatigue
        status["suggestion"] = suggestion

        with open(STATUS_FILE, "w") as f:
            json.dump(status, f)

        # CSV LOG
        with open(LOG_FILE, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                status.get("time"),
                blink_count,
                ear,
                pitch,
                yaw,
                roll,
                fatigue,
                suggestion
            ])

        print(
            f"[{status.get('time')}] "
            f"EAR={ear} | Blinks={blink_count} | "
            f"Pitch={pitch} | Fatigue={fatigue}"
        )

        time.sleep(1)

    except Exception as e:
        print("⚠️ Error:", e)
        time.sleep(1)
