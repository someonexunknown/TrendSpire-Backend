# services/marketplace_service.py

import pandas as pd
import os

# Load the CSV once at startup — not on every request
_CSV_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'marketplace_data.csv')

try:
    _df = pd.read_csv(_CSV_PATH)
    print(f"[MARKETPLACE] Loaded {len(_df)} rows from CSV.")
except Exception as e:
    print(f"[MARKETPLACE] ERROR loading CSV: {e}")
    _df = pd.DataFrame()


def get_marketplace_signal(keyword: str) -> dict:
    """
    Computes rank velocity and sales growth from the pre-seeded CSV.
    Returns a normalized 0-100 score.
    """
    if _df.empty:
        return _neutral_fallback()

    row = _df[_df['keyword'] == keyword]
    if row.empty:
        print(f"[MARKETPLACE] Keyword not found: '{keyword}'")
        return _neutral_fallback()

    row = row.iloc[0]

    # Rank velocity: how many positions improved in 7 days
    # Positive = rising (e.g., was rank 30, now rank 12 = +18 improvement)
    rank_velocity = float(row['rank_7d_ago']) - float(row['rank_today'])

    # Sales growth vs 4-week average
    sales_growth_pct = (
        (float(row['weekly_sales_units']) - float(row['sales_4w_avg']))
        / (float(row['sales_4w_avg']) + 0.001)
    ) * 100

    # Normalize rank velocity: max meaningful improvement = 50 positions
    velocity_norm = min(max((rank_velocity / 50.0) * 100, 0), 100)

    # Normalize sales growth: cap at 100% growth
    sales_norm = min(max(sales_growth_pct, 0), 100)

    # Combined marketplace score (velocity weighted more than sales)
    normalized_score = (velocity_norm * 0.6) + (sales_norm * 0.4)

    return {
        "current_rank": int(row['rank_today']),
        "rank_7d_ago": int(row['rank_7d_ago']),
        "rank_velocity": round(rank_velocity, 1),
        "sales_growth_pct": round(sales_growth_pct, 1),
        "normalized_score": round(normalized_score, 1)
    }


def _neutral_fallback() -> dict:
    return {
        "current_rank": 50,
        "rank_7d_ago": 50,
        "rank_velocity": 0.0,
        "sales_growth_pct": 0.0,
        "normalized_score": 50.0
    }
