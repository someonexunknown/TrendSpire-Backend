# utils/normalizer.py

def min_max_normalize(value: float, min_val: float, max_val: float) -> float:
    """
    Converts a value to a 0-100 scale given a known min and max.
    Clamps output so it never goes below 0 or above 100.
    """
    if max_val == min_val:
        return 50.0  # Avoid division by zero — return neutral score
    normalized = ((value - min_val) / (max_val - min_val)) * 100
    return round(max(0.0, min(100.0, normalized)), 1)

def clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    """Force a value to stay within a given range."""
    return round(max(low, min(high, value)), 1)
