from bs4 import BeautifulSoup
import re

class ContentParser:
    @staticmethod
    def clean_html(raw_html):
        if not raw_html:
            return ""
        
        soup = BeautifulSoup(raw_html, "html.parser")
        
        # Remove non-text elements
        for script_or_style in soup(["script", "style", "nav", "footer", "header"]):
            script_or_style.decompose()
            
        # Get text
        text = soup.get_text(separator=' ')
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Return only the first 10,000 chars to avoid LLM context overflow
        return text[:10000]