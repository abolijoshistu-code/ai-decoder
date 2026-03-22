import os
import sys
import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime

# 1. FIX PATHING
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# 2. IMPORT YOUR PIPELINE
from main import run_daily_pipeline

# 3. SETUP LOGGING
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [CLOCK] %(message)s',
    handlers=[
        logging.FileHandler("scheduler.log", encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

def scheduled_job():
    """Triggered every 2 minutes for testing."""
    logging.info("--- ⏰ TEST TRIGGER: Starting Pipeline ---")
    try:
        run_daily_pipeline()
        logging.info("--- ✅ SUCCESS: Pipeline finished. Waiting 2 minutes... ---")
    except Exception as e:
        logging.error(f"--- ❌ ERROR: {str(e)} ---")

if __name__ == "__main__":
    scheduler = BlockingScheduler()

    # TEST SCHEDULE: Run immediately, then every 2 minutes
    scheduler.add_job(
        scheduled_job, 
        'interval', 
        minutes=2, 
        next_run_time=datetime.now() # Runs immediately on start
    )

    logging.info("TEST MODE: Scheduler started. Running every 2 minutes.")
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logging.info("Test stopped.")