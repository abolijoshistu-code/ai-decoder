import re

def slugify(text):
    text = text.lower()
    # Remove non-alphanumeric characters
    text = re.sub(r'[^\w\s-]', '', text)
    # Replace whitespace with hyphens
    return re.sub(r'[-\s]+', '-', text).strip('-')