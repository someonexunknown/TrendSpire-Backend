# services/scoring_engine.py

from config import SCORING_WEIGHTS


def compute_trend_score(google: dict, marketplace: dict, pinterest: dict) -> float:
    """
    Weighted composite of the three normalized signal scores.
    Formula: TMS = (Google x 0.45) + (Marketplace x 0.35) + (Pinterest x 0.20)
    """
    score = (
        google["normalized_score"] * SCORING_WEIGHTS["google"] +
        marketplace["normalized_score"] * SCORING_WEIGHTS["marketplace"] +
        pinterest["normalized_score"] * SCORING_WEIGHTS["pinterest"]
    )
    return round(score, 1)


def classify(trend_score: float, google_growth_pct: float) -> str:
    """
    Classifies a keyword based on its overall TMS and Google search growth rate.
    Using both prevents a keyword with a high static score but flat growth
    from being falsely classified as Accelerating.
    """
    if trend_score >= 70 and google_growth_pct >= 15:
        return "Accelerating"
    elif trend_score >= 55 and google_growth_pct >= 5:
        return "Emerging"
    elif trend_score >= 35:
        return "Stable"
    else:
        return "Declining"


def recommend(classification: str, trend_score: float) -> dict:
    """
    Rule-based stock recommendation. Transparent and explainable — no black box.
    Returns the action (Increase/Maintain/Reduce) and suggested % adjustment.
    """
    if classification == "Accelerating":
        adjustment = 30 if trend_score >= 80 else 20
        return {"action": "Increase", "adjustment_pct": adjustment}

    elif classification == "Emerging":
        return {"action": "Increase", "adjustment_pct": 10}

    elif classification == "Stable":
        return {"action": "Maintain", "adjustment_pct": 0}

    else:  # Declining
        adjustment = -20 if trend_score < 25 else -10
        return {"action": "Reduce", "adjustment_pct": adjustment}


def build_explanation(classification: str, google: dict, marketplace: dict, pinterest: dict) -> str:
    """Generates a human-readable explanation for the recommendation."""
    parts = []

    g_growth = google["growth_pct"]
    if g_growth >= 15:
        parts.append(f"Strong Google search surge (+{g_growth:.0f}% vs 4-week avg)")
    elif g_growth >= 5:
        parts.append(f"Moderate Google search growth (+{g_growth:.0f}%)")
    elif g_growth < 0:
        parts.append(f"Declining Google search interest ({g_growth:.0f}%)")
    else:
        parts.append("Flat Google search interest")

    rv = marketplace["rank_velocity"]
    if rv >= 10:
        parts.append(f"rising marketplace rank (+{rv:.0f} positions in 7 days)")
    elif rv < 0:
        parts.append(f"falling marketplace rank ({rv:.0f} positions in 7 days)")

    sg = pinterest["save_growth_pct"]
    if sg >= 15:
        parts.append(f"high Pinterest save rate (+{sg:.0f}%)")
    elif sg < 0:
        parts.append(f"declining Pinterest engagement ({sg:.0f}%)")

    if not parts:
        return "Mixed signals across all channels."

    return ". ".join(parts).capitalize() + "."
