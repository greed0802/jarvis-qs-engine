import re

def normalize_text(text):
    text = str(text).lower()

    # remove punctuation
    text = re.sub(r'[^a-z0-9 ]', '', text)

    # collapse spaces
    text = re.sub(r'\s+', ' ', text).strip()

    return text