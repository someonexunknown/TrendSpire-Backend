# services/pinterest_service.py

import pandas as pd
import os

_CSV_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'pinterest_data.csv')

try:
    _df = pd.read_csv(_CSV_PATH)
    print(f"[PINTEREST] Loaded {len(_df)} rows from CSV.")
except Exception as e:
    print(f"[PINTEREST] ERROR loading CSV: {e}")
    _df = pd.DataFrame()


def get_pinterest_signal(keyword: str) -> dict:
    """
    Computes save growth and board growth from the pre-seeded Pinterest CSV.
    Returns a normalized 0-100 score.
    """
    if _df.empty:
        return _neutral_fallback()

    row = _df[_df['keyword'] == keyword]
    if row.empty:
        print(f"[PINTEREST] Keyword not found: '{keyword}'")
        return _neutral_fallback()

    row = row.iloc[0]

    save_growth = (
        (float(row['weekly_saves']) - float(row['saves_4w_avg']))
        / (float(row['saves_4w_avg']) + 0.001)
    ) * 100

    board_growth = (
        (float(row['board_count']) - float(row['boards_4w_avg']))
        / (float(row['boards_4w_avg']) + 0.001)
    ) * 100

    # Normalize: cap at 100% growth
    save_norm = min(max(save_growth, 0), 100)
    board_norm = min(max(board_growth, 0), 100)

    # Saves are a stronger signal than boards
    normalized_score = (save_norm * 0.7) + (board_norm * 0.3)

    return {
        "weekly_saves": int(row['weekly_saves']),
        "save_growth_pct": round(save_growth, 1),
        "board_count": int(row['board_count']),
        "board_growth_pct": round(board_growth, 1),
        "normalized_score": round(normalized_score, 1)
    }


def _neutral_fallback() -> dict:
    return {
        "weekly_saves": 0,
        "save_growth_pct": 0.0,
        "board_count": 0,
        "board_growth_pct": 0.0,
        "normalized_score": 40.0
    }
