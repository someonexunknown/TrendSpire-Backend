# app.py

from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime

from config import KEYWORDS
from cache import cache_manager
from services import trends_service, marketplace_service, pinterest_service, scoring_engine

app = Flask(__name__)
CORS(app)  # Allow requests from Flutter app on any origin


def get_full_analysis(keyword: str) -> dict:
    """
    Core pipeline for one keyword:
    1. Check cache
    2. Fetch all three signals
    3. Compute score, classify, recommend
    4. Cache and return result
    """
    cache_key = f"analysis:{keyword}"
    cached = cache_manager.get(cache_key)
    if cached:
        cached["cached"] = True
        return cached

    # Fetch all three signals
    google     = trends_service.fetch_google_trends(keyword)
    marketplace = marketplace_service.get_marketplace_signal(keyword)
    pinterest  = pinterest_service.get_pinterest_signal(keyword)

    # Compute score and derive outputs
    trend_score    = scoring_engine.compute_trend_score(google, marketplace, pinterest)
    classification = scoring_engine.classify(trend_score, google["growth_pct"])
    rec            = scoring_engine.recommend(classification, trend_score)
    explanation    = scoring_engine.build_explanation(classification, google, marketplace, pinterest)

    result = {
        "keyword": keyword,
        "trend_score": trend_score,
        "classification": classification,
        "recommendation": rec["action"],
        "adjustment_pct": rec["adjustment_pct"],
        "explanation": explanation,
        "signals": {
            "google_trends": google,
            "marketplace": marketplace,
            "pinterest": pinterest
        },
        "generated_at": datetime.utcnow().isoformat(),
        "cached": False
    }

    cache_manager.set(cache_key, result)
    return result


# ─────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────

@app.route("/api/health", methods=["GET"])
def health():
    """Simple health check. Hit this first during demo to confirm server is up."""
    return jsonify({
        "status": "ok",
        "cache_size": cache_manager.size(),
        "timestamp": datetime.utcnow().isoformat()
    })


@app.route("/api/trends/summary", methods=["GET"])
def summary():
    """
<<<<<<< HEAD
    Returns a lightweight score summary for all active keywords.
=======
    Returns a lightweight score summary for all 15 keywords.
>>>>>>> d538cb6fd1283cbf5e3fc2816a648f147fb397f2
    This powers the main dashboard list in the Flutter app.
    """
    results = []
    for keyword in KEYWORDS:
        analysis = get_full_analysis(keyword)
        results.append({
            "keyword": analysis["keyword"],
            "trend_score": analysis["trend_score"],
            "classification": analysis["classification"],
            "recommendation": analysis["recommendation"],
            "adjustment_pct": analysis["adjustment_pct"],
            "signals": {
                "google_trends_score": analysis["signals"]["google_trends"]["normalized_score"],
                "marketplace_score": analysis["signals"]["marketplace"]["normalized_score"],
                "pinterest_score": analysis["signals"]["pinterest"]["normalized_score"]
            }
        })

    return jsonify({
        "status": "ok",
        "generated_at": datetime.utcnow().isoformat(),
        "count": len(results),
        "data": results
    })


@app.route("/api/trends/detail", methods=["GET"])
def detail():
    """
    Returns the full breakdown for a single keyword.
    Use: GET /api/trends/detail?keyword=oversized+linen+shirt
    This powers the detail screen in the Flutter app.
    """
    keyword = request.args.get("keyword", "").strip()

    if not keyword:
        return jsonify({"error": "Missing 'keyword' query parameter."}), 400

    if keyword not in KEYWORDS:
        return jsonify({
            "error": f"Keyword '{keyword}' is not in the supported list.",
            "supported_keywords": KEYWORDS
        }), 404

    result = get_full_analysis(keyword)
    return jsonify(result)


# ─────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
