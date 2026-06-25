"""
main.py — production entry point for Render.
Starts the APScheduler in a background thread, then serves Flask via gunicorn.
Auto-fetches data on boot if data.json is empty.
"""

import threading
import json
import sys
import os
from pathlib import Path
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

import scripts.fetch_data as fetcher
import scripts.telegram_bot as bot_reporter
from dashboard.app import app

DATA_PATH = Path(__file__).parent / "dashboard" / "data" / "data.json"


def job_fetch():
    print(f"[{datetime.now()}] ⏰ Fetching Instagram data...")
    try:
        fetcher.main()
        print(f"[{datetime.now()}] ✅ Fetch complete")
    except Exception as e:
        print(f"[{datetime.now()}] ❌ Fetch failed: {e}")


def job_report():
    print(f"[{datetime.now()}] ⏰ Sending Telegram report...")
    try:
        bot_reporter.main()
        print(f"[{datetime.now()}] ✅ Report sent")
    except Exception as e:
        print(f"[{datetime.now()}] ❌ Report failed: {e}")


def boot_fetch():
    """Fetch data on startup if data.json is empty or has no profile."""
    try:
        data = json.loads(DATA_PATH.read_text()) if DATA_PATH.exists() else {}
    except Exception:
        data = {}

    if not data.get("my_profile", {}).get("username"):
        print("🚀 No data found — running initial fetch on boot...")
        threading.Thread(target=job_fetch, daemon=True).start()
    else:
        print(f"✅ Data already present for @{data['my_profile']['username']} — skipping boot fetch")


def start_scheduler():
    scheduler = BackgroundScheduler(timezone="Asia/Kolkata")
    scheduler.add_job(job_fetch, CronTrigger(hour=8, minute=0), id="fetch_data")
    scheduler.add_job(job_report, CronTrigger(hour=8, minute=5), id="send_report")
    scheduler.start()
    print("✅ Scheduler started (08:00 + 08:05 IST daily)")


start_scheduler()
boot_fetch()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5050)))
