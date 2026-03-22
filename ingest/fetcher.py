import feedparser
import requests
import json
import logging
from .parser import ContentParser

class DataFetcher:
    def __init__(self, config_path):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        self.parser = ContentParser()

    def fetch_all(self):
        articles = []
        # Process RSS
        for url in self.config.get('rss_feeds', []):
            logging.info(f"Fetching RSS: {url}")
            feed = feedparser.parse(url)
            for entry in feed.entries[:5]: # Limit per source
                articles.append({
                    "title": entry.title,
                    "content": self.parser.clean_html(entry.get('summary', '') or entry.get('description', '')),
                    "source": url
                })
        
        # Process Blogs (Generic Request)
        for url in self.config.get('blogs', []):
            try:
                logging.info(f"Fetching Blog: {url}")
                res = requests.get(url, timeout=10)
                if res.status_code == 200:
                    articles.append({
                        "title": "Blog Update",
                        "content": self.parser.clean_html(res.text[:5000]), # Simple clip
                        "source": url
                    })
            except Exception as e:
                logging.error(f"Error fetching blog {url}: {e}")
                
        return articles