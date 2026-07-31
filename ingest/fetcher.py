import feedparser
import requests
import json
import logging
import os
from .parser import ContentParser

class DataFetcher:
    def __init__(self, config_path):
        """
        Initializes the fetcher with a path to sources.json.
        """
        if not os.path.exists(config_path):
            logging.error(f"Config file not found at: {config_path}")
            self.config = {"rss_feeds": [], "blogs": []}
        else:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        
        self.parser = ContentParser()
        
        # Professional Headers to avoid being blocked by blogs
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        }

    def fetch_rss(self, url):
        """
        Parses an RSS feed and returns a list of cleaned articles.
        """
        articles = []
        try:
            logging.info(f"Connecting to RSS: {url}")
            # We use a timeout via the underlying socket if possible
            feed = feedparser.parse(url)
            
            if not feed.entries:
                logging.warning(f"No entries found in RSS feed: {url}")
                return []

            for entry in feed.entries:
                # Extract the most complete content available in the RSS entry
                raw_content = entry.get('content', [{}])[0].get('value', '') or \
                              entry.get('summary', '') or \
                              entry.get('description', '')
                
                articles.append({
                    "title": entry.title,
                    "content": self.parser.clean_html(raw_content),
                    "source": url,       # The parent feed URL
                    "url": entry.link    # The direct link to the article
                })
        except Exception as e:
            logging.error(f"Failed to fetch RSS {url}: {str(e)}")
            
        return articles

    def fetch_static_blog(self, url):
        """
        Fetches a non-RSS blog page using raw HTML scraping.
        """
        articles = []
        try:
            logging.info(f"Scraping Static Blog: {url}")
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            
            # For static blogs, we treat the whole page as one entry for the LLM to scan
            # In a more advanced version, you'd split this by <h2> or 🚢 tags
            articles.append({
                "title": f"Update from {url}",
                "content": self.parser.clean_html(response.text),
                "source": url,
                "url": url
            })
        except Exception as e:
            logging.error(f"Failed to scrape blog {url}: {str(e)}")
            
        return articles

    def fetch_all(self):
        """
        The main orchestrator: Gathers content from all sources in config.
        """
        all_results = []
        
        # 1. Process all RSS feeds (OpenAI, DeepMind, etc.)
        rss_sources = self.config.get('rss_feeds', [])
        for source_url in rss_sources:
            feed_articles = self.fetch_rss(source_url)
            all_results.extend(feed_articles)
            
        # 2. Process all static blog URLs
        blog_sources = self.config.get('blogs', [])
        for source_url in blog_sources:
            blog_articles = self.fetch_static_blog(source_url)
            all_results.extend(blog_articles)
            
        logging.info(f"Ingest complete. Total raw articles to analyze: {len(all_results)}")
        return all_results