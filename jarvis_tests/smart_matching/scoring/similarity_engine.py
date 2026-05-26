from rapidfuzz import fuzz
from jarvis_tests.smart_matching.core.text_normalizer import normalize_text

def similarity_score(a, b):
    a = normalize_text(a)
    b = normalize_text(b)

    return fuzz.token_sort_ratio(a, b)