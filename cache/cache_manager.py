# cache/cache_manager.py

import time

_store = {}

def get(key: str):
    """Return cached value if it exists and hasn't expired. Otherwise return None."""
    from config import CACHE_TTL_SECONDS
    if key in _store:
        value, timestamp = _store[key]
        if time.time() - timestamp < CACHE_TTL_SECONDS:
            return value
        else:
            del _store[key]
    return None

def set(key: str, value):
    """Store a value with the current timestamp."""
    _store[key] = (value, time.time())

def size() -> int:
    """Return how many items are currently cached."""
    return len(_store)
