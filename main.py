"""
main.py — production entry point for Render.
Starts the APScheduler in a background thread, then serves Flask via gunicorn.
"""

import threading
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime

import scripts.fetch_data as fetcher
import scripts.telegram_bot as bot_reporter
from dashboard.app import app


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


def start_scheduler():
    scheduler = BackgroundScheduler(timezone="Asia/Kolkata")
    scheduler.add_job(job_fetch, CronTrigger(hour=8, minute=0), id="fetch_data")
    scheduler.add_job(job_report, CronTrigger(hour=8, minute=5), id="send_report")
    scheduler.start()
    print("✅ Scheduler started (08:00 + 08:05 IST daily)")


# Start scheduler in background thread before gunicorn forks
start_scheduler()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5050)))
