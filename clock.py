import os
import sys
import logging
from apscheduler.schedulers.background import BlockingScheduler
from datetime import datetime

# Fix pathing to find main.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from main import run_daily_pipeline

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [CLOCK] %(message)s',
    handlers=[logging.FileHandler("scheduler.log"), logging.StreamHandler()]
)

def scheduled_job():
    logging.info("--- ⏰ CRON TRIGGERED: Starting Daily Pipeline ---")
    try:
        run_daily_pipeline()
        logging.info("--- ✅ CRON FINISHED: Daily Pipeline Success ---")
    except Exception as e:
        logging.error(f"--- ❌ CRON FAILED: {str(e)} ---")

if __name__ == "__main__":
    scheduler = BlockingScheduler()

    # SCHEDULE: Every day at 09:00 AM
    # You can change this to hours=24 or a specific time
    scheduler.add_job(scheduled_job, 'cron', hour=9, minute=0)
    
    # FOR TESTING: Uncomment the line below to run every 5 minutes
    # scheduler.add_job(scheduled_job, 'interval', minutes=5)

    logging.info("Scheduler started. Waiting for next trigger at 09:00 AM daily...")
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logging.info("Scheduler stopped.")
        
        
        
        