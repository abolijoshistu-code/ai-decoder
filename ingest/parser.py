from bs4 import BeautifulSoup
import re

class ContentParser:
    @staticmethod
    def clean_html(raw_html):
        if not raw_html: return ""
        soup = BeautifulSoup(raw_html, "html.parser")
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        text = soup.get_text(separator=' ')
        # Clean whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text