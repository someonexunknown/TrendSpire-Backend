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
