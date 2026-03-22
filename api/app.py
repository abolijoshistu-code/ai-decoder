import os
import sys
import json
from flask import Flask, render_template, request, redirect, url_for, jsonify

# Path Fixing
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path: sys.path.insert(0, BASE_DIR)

from storage.manager import StorageManager
from process.llm_client import LLMEngine

app = Flask(__name__)
DATA_PATH = os.path.join(BASE_DIR, "data")
storage = StorageManager(base_path=DATA_PATH)
llm = LLMEngine()

# Global Cache
_CACHE = {"data": [], "last_updated": None}

def get_concepts(force_refresh=False):
    """Fetches all concepts and updates the cache."""
    if _CACHE["data"] and not force_refresh:
        return _CACHE["data"]
    
    all_c = []
    if not os.path.exists(DATA_PATH): return []
    
    # Sort date folders newest to oldest
    folders = sorted([d for d in os.listdir(DATA_PATH) if os.path.isdir(os.path.join(DATA_PATH, d))], reverse=True)
    
    for d in folders:
        p = os.path.join(DATA_PATH, d, "concepts.json")
        if os.path.exists(p):
            with open(p, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    all_c.extend(data)
                except: continue
    
    _CACHE["data"] = all_c
    return all_c

@app.route('/')
def index():
    # Fresh load for the homepage
    items = get_concepts(force_refresh=True)
    tod = items[0] if items else None
    archive = items[1:] if len(items) > 1 else []
    return render_template('index.html', tod=tod, concepts=archive, is_search=False)

@app.route('/search')
def search():
    query = request.args.get('q', '').strip()
    if not query: return redirect(url_for('index'))

    # 1. Find local or decode new
    res = storage.search_local(query)
    if not res:
        res = llm.get_structured_concept(query)
        if res:
            storage.save_concept(res)
    else:
        # Move existing term to the top (Index 0) for the current view
        storage.save_concept(res)

    # 2. CRITICAL: Refresh the cache so the search result is at Index 0
    all_items = get_concepts(force_refresh=True)
    
    # 3. Separate the 'Search Result' from the 'Archive'
    tod = all_items[0] if all_items else None
    archive = all_items[1:] if len(all_items) > 1 else []

    return render_template('index.html', 
                           tod=tod, 
                           concepts=archive, 
                           search_query=query, 
                           is_search=True)
@app.route('/concept/<slug>')
def concept_detail(slug):
    item = storage.get_by_slug(slug)
    if not item: return "Not Found", 404
    
    # Use .get() to safely check for slugs, or fallback to an empty string
    all_items = get_concepts()
    archive = [i for i in all_items if i.get('slug') != slug] 
    
    # We pass 'is_detail=True' to tell index.html to show back buttons
    return render_template('index.html', tod=item, concepts=archive, is_search=True)

@app.route('/subscribe', methods=['POST'])
def subscribe():
    email = request.form.get('email')
    if email: storage.add_subscriber(email)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)