import os
import json
import re
from pathlib import Path

# Helper to create slug
def slugify(text):
    text = text.lower().strip()
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    return re.sub(r'[\s-]+', '-', text)

def migrate():
    base_path = Path("data").resolve()
    print(f"Checking for data in: {base_path}")
    
    if not base_path.exists():
        print("No data folder found.")
        return

    for folder in base_path.iterdir():
        if folder.is_dir():
            file_path = folder / "concepts.json"
            if file_path.exists():
                print(f"Migrating: {file_path}")
                with open(file_path, 'r', encoding='utf-8') as f:
                    concepts = json.load(f)
                
                updated = False
                for c in concepts:
                    if 'slug' not in c:
                        c['slug'] = slugify(c['title'])
                        updated = True
                        print(f"  -> Added slug to: {c['title']}")
                
                if updated:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(concepts, f, indent=2)
                    print(f"  ✅ Saved {file_path}")

if __name__ == "__main__":
    migrate()
    print("\nMigration Complete! Restart your Flask app.")