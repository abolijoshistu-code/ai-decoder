import json
import os
import re
from datetime import datetime
from pathlib import Path

class StorageManager:
    def __init__(self, base_path):
        self.base_path = Path(base_path).resolve()
        self.history_file = self.base_path / "history.json"
        self.sub_file = self.base_path / "subscribers.json"
        self.base_path.mkdir(exist_ok=True, parents=True)

    def slugify(self, text):
        """Converts 'AI Search' to 'ai-search'"""
        text = text.lower().strip()
        text = re.sub(r'[^a-z0-9\s-]', '', text)
        return re.sub(r'[\s-]+', '-', text)

    def is_duplicate(self, term):
        if not self.history_file.exists(): return False
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
                return term.lower() in [t.lower() for t in history]
        except: return False

    def save_concept(self, data):
        """Saves data using Atomic Replacement (Safe on Windows & Linux)"""
        if not data or 'title' not in data: return
        
        data['slug'] = self.slugify(data['title'])
        date_str = datetime.now().strftime("%Y-%m-%d")
        day_folder = self.base_path / date_str
        day_folder.mkdir(exist_ok=True, parents=True)
        
        file_path = day_folder / "concepts.json"
        
        concepts = []
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    concepts = json.load(f)
            except: concepts = []
        
        # Prepend logic: Remove old version if exists, add new to top
        concepts = [c for c in concepts if c['title'].lower() != data['title'].lower()]
        concepts.insert(0, data)

        # ATOMIC WRITE: This prevents file corruption if the app crashes mid-write
        # 1. Write to a temporary file
        temp_file = file_path.with_suffix('.tmp')
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(concepts, f, indent=2)
        
        # 2. Rename temp file to real file (Atomic operation on Windows & Linux)
        try:
            os.replace(temp_file, file_path)
        except OSError:
            # Fallback if replace fails (rare)
            os.remove(file_path)
            os.rename(temp_file, file_path)

        # Update History
        self._update_history(data['title'])

    def _update_history(self, title):
        history = []
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            except: history = []
        
        if title not in history:
            history.append(title)
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2)

    def get_by_slug(self, slug):
        """Finds a concept by slug across all folders."""
        for folder in self.base_path.iterdir():
            if folder.is_dir():
                file_path = folder / "concepts.json"
                if file_path.exists():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        try:
                            concepts = json.load(f)
                            for c in concepts:
                                if c.get('slug') == slug: return c
                        except: continue
        return None

    def search_local(self, query):
        query = query.lower()
        for folder in sorted(self.base_path.iterdir(), reverse=True):
            if folder.is_dir():
                file_path = folder / "concepts.json"
                if file_path.exists():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        try:
                            concepts = json.load(f)
                            for c in concepts:
                                if query in c['title'].lower(): return c
                        except: continue
        return None

    def add_subscriber(self, email):
        subs = self.get_subscribers()
        email = email.strip().lower()
        if email not in subs:
            subs.append(email)
            with open(self.sub_file, 'w', encoding='utf-8') as f:
                json.dump(subs, f, indent=2)
            return True
        return False

    def get_subscribers(self):
        if self.sub_file.exists():
            with open(self.sub_file, 'r', encoding='utf-8') as f:
                try: return json.load(f)
                except: return []
        return []