import logging
import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Guard: Check environment variables before execution
def check_env():
    # Update required keys for SMTP
    required = ["SMTP_SERVER", "SMTP_PORT", "EMAIL_USER", "EMAIL_PASS", "GEMINI_API_KEY"]
    missing = [k for k in required if not os.getenv(k)]
    if missing:
        logging.error(f"CRITICAL ERROR: Missing environment variables: {missing}")
        sys.exit(1)

from ingest.fetcher import DataFetcher
from extract.concept_extractor import ConceptExtractor
from process.llm_client import LLMEngine
from storage.manager import StorageManager
from email_service.sender import EmailService

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data")
CONFIG_PATH = os.path.join(BASE_DIR, "config", "sources.json")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_daily_pipeline():
    check_env()
    logging.info("Pipeline started.")
    
    fetcher = DataFetcher(CONFIG_PATH)
    extractor = ConceptExtractor()
    llm = LLMEngine()
    storage = StorageManager(DATA_PATH)
    mailer = EmailService()

    articles = fetcher.fetch_all()
    found = 0
    for art in articles:
        if found >= 1: break 
        
        terms = extractor.extract_terms(art)
        for t in terms:
            if not storage.is_duplicate(t['term']):
                data = llm.get_structured_concept(t['term'], t['context'])
                if data:
                    storage.save_concept(data)
                    subs = storage.get_subscribers()
                    if subs:
                        mailer.send_daily_term(data, subs)
                    found += 1
                    break
    logging.info("Pipeline execution finished.")

if __name__ == "__main__":
    run_daily_pipeline()