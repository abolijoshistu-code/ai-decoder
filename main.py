import logging
import os
import sys
import json
from pathlib import Path

# --- 1. SETUP PATHING & IMPORTS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from ingest.fetcher import DataFetcher
from extract.concept_extractor import ConceptExtractor
from process.llm_client import LLMEngine
from storage.manager import StorageManager
from email_service.sender import EmailService
from dotenv import load_dotenv

load_dotenv()

# --- 2. CONFIGURATION ---
DATA_PATH = os.path.join(BASE_DIR, "data")
CONFIG_PATH = os.path.join(BASE_DIR, "config", "sources.json")
PROCESSED_ARTICLES_FILE = os.path.join(DATA_PATH, "processed_articles.json")

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(BASE_DIR, "pipeline.log"), encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

def run_daily_pipeline():
    # Initialize components
    fetcher = DataFetcher(CONFIG_PATH)
    extractor = ConceptExtractor()
    llm = LLMEngine()
    storage = StorageManager(DATA_PATH)
    mailer = EmailService()

    # Load previously processed articles
    processed_titles = []
    if os.path.exists(PROCESSED_ARTICLES_FILE):
        try:
            with open(PROCESSED_ARTICLES_FILE, 'r', encoding='utf-8') as f:
                processed_titles = json.load(f)
        except:
            processed_titles = []

    # STEP 1: FETCH ALL (This now gets everything from ALL feeds in sources.json)
    all_articles = fetcher.fetch_all()
    logging.info(f"Total articles gathered from all feeds: {len(all_articles)}")
    
    new_term_decoded_today = False

    # STEP 2: ITERATE THROUGH EVERY ARTICLE ACROSS ALL BLOGS
    for art in all_articles:
        # If we already found our 1 term for the day, stop everything
        if new_term_decoded_today:
            break

        # Skip if we've already analyzed this article in a previous run
        if art['title'] in processed_titles:
            continue
        
        logging.info(f"Scanning Article: '{art['title']}' from source: {art.get('source', 'Unknown')}")
        
        # STEP 3: EXTRACT TERMS
        potential_terms = extractor.extract_terms(art)
        
        if not potential_terms:
            # If Gemini finds no technical terms, mark article as seen and move on
            processed_titles.append(art['title'])
            continue

        for item in potential_terms:
            term_name = item.get('term', '').strip()
            
            # STEP 4: DEDUPLICATE (Is this term new to our dictionary?)
            if not term_name or storage.is_duplicate(term_name):
                continue

            # STEP 5: DECODE (We found a winner!)
            logging.info(f"✨ FOUND NEW JARGON: '{term_name}'. Decoding now...")
            simplified_data = llm.get_structured_concept(term_name, item.get('context', ''))
            
            if simplified_data:
                # Save to Data Storage
                storage.save_concept(simplified_data)
                
                # Send Email to Subscribers
                subscribers = storage.get_subscribers()
                if subscribers:
                    mailer.send_daily_term(simplified_data, subscribers)
                
                new_term_decoded_today = True
                # Mark article as processed since we used it
                processed_titles.append(art['title'])
                break # Exit the terms loop

        # Even if we didn't find a term, mark article as processed to avoid re-scanning
        if art['title'] not in processed_titles:
            processed_titles.append(art['title'])

    # Save progress
    with open(PROCESSED_ARTICLES_FILE, 'w', encoding='utf-8') as f:
        json.dump(processed_titles[-200:], f, indent=2) # Keep history of last 200 articles

    if new_term_decoded_today:
        logging.info("✅ Daily Pipeline Success: One new term decoded and emailed.")
    else:
        logging.info("Ø Daily Pipeline Finished: No new jargon found in any available feeds.")

if __name__ == "__main__":
    run_daily_pipeline()