"""
scheduler.py — runs the full content agent pipeline on a daily schedule.

Schedule:
  08:00 — fetch fresh Instagram data from Apify
  08:05 — send daily Telegram report

Run once to start: python scripts/scheduler.py
Keep it running in the background (or use a launchd/cron job).
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime

import scripts.fetch_data as fetcher
import scripts.telegram_bot as bot_reporter


def job_fetch():
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⏰ Running: fetch Instagram data")
    try:
        fetcher.main()
        print("✅ Data fetch complete")
    except Exception as e:
        print(f"❌ Data fetch failed: {e}")


def job_report():
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⏰ Running: send Telegram report")
    try:
        bot_reporter.main()
        print("✅ Telegram report sent")
    except Exception as e:
        print(f"❌ Telegram report failed: {e}")


def main():
    scheduler = BlockingScheduler(timezone="Asia/Kolkata")

    # Fetch data at 08:00 IST daily
    scheduler.add_job(job_fetch, CronTrigger(hour=8, minute=0), id="fetch_data")

    # Send report at 08:05 IST daily (after fetch completes)
    scheduler.add_job(job_report, CronTrigger(hour=8, minute=5), id="send_report")

    print("=" * 50)
    print("  ContentAgent OS — Scheduler Running")
    print("=" * 50)
    print("  📥 Data fetch  : daily at 08:00 IST")
    print("  📨 Telegram    : daily at 08:05 IST")
    print("  Press Ctrl+C to stop")
    print("=" * 50)

    scheduler.start()


if __name__ == "__main__":
    main()
