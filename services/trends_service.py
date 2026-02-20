# services/trends_service.py

import requests
import json
import time
import random

# ─────────────────────────────────────────────
# Google Trends – Direct HTTP Fetcher
# ─────────────────────────────────────────────
# Instead of using the archived `pytrends` library, we directly hit
# Google Trends' internal API endpoints with a browser-like session.
#
# Flow:
#   1. GET /trends/api/explore  → returns widget tokens
#   2. GET /trends/api/widgetdata/multiline → returns interest-over-time JSON
#
# This is the same approach pytrends used internally, but we control the
# headers, cookies, and retry logic ourselves.
# ─────────────────────────────────────────────

_BASE_URL = "https://trends.google.com/trends"
_EXPLORE_URL = f"{_BASE_URL}/api/explore"
_MULTILINE_URL = f"{_BASE_URL}/api/widgetdata/multiline"

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://trends.google.com/trends/explore",
}

MAX_RETRIES = 2
RETRY_DELAY = 3  # seconds between retries


def fetch_google_trends(keyword: str) -> dict:
    """
    Fetches 4 weeks of Google Trends data for a keyword in India.
    Uses direct HTTP requests to Google Trends' internal API.

    Returns a dict with current interest, average, growth %, and normalized score.
    Falls back to neutral values (score=50) if the API fails or returns empty data.
    """
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return _fetch_live(keyword)
        except Exception as e:
            print(f"[TRENDS] Attempt {attempt}/{MAX_RETRIES} failed for '{keyword}': {e}")
            if attempt < MAX_RETRIES:
                delay = RETRY_DELAY * attempt + random.uniform(0, 1)
                print(f"[TRENDS] Retrying in {delay:.1f}s...")
                time.sleep(delay)

    return _neutral_fallback(keyword, reason="all_retries_exhausted")


def _fetch_live(keyword: str) -> dict:
    """
    Core fetcher: creates a session, gets a token from /explore,
    then fetches interest-over-time data from /widgetdata/multiline.
    """
    session = requests.Session()
    session.headers.update(_HEADERS)

    # Step 0: Visit the trends page to pick up initial cookies (NID, etc.)
    session.get(f"{_BASE_URL}/explore", timeout=15)
    time.sleep(random.uniform(0.5, 1.5))

    # Step 1: Call /explore to get the TIMESERIES widget token
    explore_payload = {
        "comparisonItem": [
            {
                "keyword": keyword,
                "geo": "IN",
                "time": "today 1-m",  # last ~4 weeks
            }
        ],
        "category": 0,
        "property": "",
    }

    params = {
        "hl": "en-IN",
        "tz": "-330",
        "req": json.dumps(explore_payload),
    }

    resp = session.get(_EXPLORE_URL, params=params, timeout=15)
    resp.raise_for_status()

    # Google prefixes response with ")]}',\n" to prevent JSON hijacking
    raw_text = resp.text
    if raw_text.startswith(")]}'"):
        raw_text = raw_text[5:]

    explore_data = json.loads(raw_text)

    # Find the TIMESERIES widget
    token = None
    req_payload = None
    for widget in explore_data.get("widgets", []):
        if widget.get("id") == "TIMESERIES":
            token = widget.get("token")
            req_payload = widget.get("request")
            break

    if not token or not req_payload:
        raise ValueError("Could not find TIMESERIES widget token in explore response")

    time.sleep(random.uniform(1.0, 2.0))

    # Step 2: Fetch the actual interest-over-time data
    multiline_params = {
        "hl": "en-IN",
        "tz": "-330",
        "req": json.dumps(req_payload),
        "token": token,
    }

    resp2 = session.get(_MULTILINE_URL, params=multiline_params, timeout=15)
    resp2.raise_for_status()

    raw_text2 = resp2.text
    if raw_text2.startswith(")]}'"):
        raw_text2 = raw_text2[5:]

    multiline_data = json.loads(raw_text2)

    # Parse the timeline data points
    timeline = multiline_data.get("default", {}).get("timelineData", [])

    if not timeline:
        raise ValueError("Empty timeline data returned from Google")

    values = [point["value"][0] for point in timeline if point.get("value")]

    if len(values) == 0:
        raise ValueError("No values in timeline data")

    current = float(values[-1])             # Most recent data point
    four_week_avg = sum(values) / len(values)

    # Growth % = how much the current value exceeds the average
    # +0.001 avoids division by zero if avg is 0
    growth_pct = ((current - four_week_avg) / (four_week_avg + 0.001)) * 100

    print(f"[TRENDS] ✓ Live data for '{keyword}': current={current}, avg={four_week_avg:.1f}, growth={growth_pct:.1f}%")

    return {
        "current_interest": round(current, 1),
        "four_week_avg": round(four_week_avg, 1),
        "growth_pct": round(growth_pct, 1),
        "normalized_score": round(current, 1),  # Google Trends is already 0–100
        "source": "live",
    }


def _neutral_fallback(keyword: str, reason: str = "unknown") -> dict:
    """
    Returns a neutral 50-point score when the API fails.
    This keeps the scoring pipeline alive — a fallback Google score
    of 50 means the keyword is treated as 'average interest'.
    The 'source' field tells you in the API response whether this was live or fallback.
    """
    print(f"[TRENDS] Using fallback for '{keyword}'. Reason: {reason}")
    return {
        "current_interest": 50.0,
        "four_week_avg": 50.0,
        "growth_pct": 0.0,
        "normalized_score": 50.0,
        "source": "fallback",
    }
