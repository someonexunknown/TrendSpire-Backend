<<<<<<< HEAD
import os
import csv

def load_keywords_from_csv():
    """
    Loads active keywords from data/keywords.csv.
    Expected CSV columns: keyword, category, active
    """
    keywords = []
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, "data", "keywords.csv")
    
    if not os.path.exists(csv_path):
        print(f"Warning: {csv_path} not found. Using empty keyword list.")
        return []

    try:
        with open(csv_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('active', '').lower() == 'true':
                    keywords.append(row['keyword'])
    except Exception as e:
        print(f"Error reading keywords from {csv_path}: {e}")
        return []

    return keywords

# Dynamically load keywords from CSV
KEYWORDS = load_keywords_from_csv()
=======
# config.py

KEYWORDS = [
    "oversized linen shirt",
    "cargo pants men",
    "relaxed fit jeans men",
    "chino trousers men",
    "men polo shirt",
    "printed resort shirt",
    "neon graphic tee",
    "men jogger pants",
    "men bomber jacket",
    "men terry shorts",
    "men kurta casual",
    "men denim jacket",
    "men track pants",
    "men waffle tee",
    "men co-ord set",
]
>>>>>>> d538cb6fd1283cbf5e3fc2816a648f147fb397f2

# How long to keep cached results (in seconds). 12 hours.
CACHE_TTL_SECONDS = 43200

# Weight of each signal in the final Trend Momentum Score
SCORING_WEIGHTS = {
    "google": 0.45,
    "marketplace": 0.35,
    "pinterest": 0.20
}

# Classification thresholds
THRESHOLDS = {
    "accelerating": {"min_score": 70, "min_growth": 15},
    "emerging":     {"min_score": 55, "min_growth": 5},
    "stable":       {"min_score": 35},
}
