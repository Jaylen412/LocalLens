# app.py
from fastapi import FastAPI, HTTPException, Query
import os, requests
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()
app = FastAPI(title="Reviews API")

SERP_API_KEY = os.getenv("SERP_API_KEY")
BASE_URL = "https://serpapi.com/search.json"

def http_get(params: Dict[str, Any]) -> Dict[str, Any]:
    r = requests.get(BASE_URL, params=params, timeout=30)
    if r.status_code != 200:
        raise HTTPException(r.status_code, f"SerpAPI error: {r.text[:500]}")
    return r.json()

def to_int(x: Any) -> Optional[int]:
    if isinstance(x, int):
        return x
    if isinstance(x, str) and x.isdigit():
        return int(x)
    return None

def normalize_reviews(raw: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Normalize to exactly: username, rating, contributor_id, description
    """
    out = []
    for r in raw or []:
        out.append({
            "username": r.get("username") or r.get("user") or r.get("author") or r.get("name"),
            "rating": r.get("rating"),
            "contributor_id": r.get("contributor_id") or r.get("user_id") or r.get("author_id"),
            "description": r.get("description") or r.get("snippet") or r.get("text"),
        })
    return out

@app.get("/reviews")
def reviews(
    q: str = Query("Fixins Soul Kitchen Detroit", description="Business name or query"),
    limit: int = Query(10, ge=1, le=100, description="Max number of reviews to return"),
    sort_by: str = Query("most_relevant", pattern="^(most_relevant|newest)$", description="Sort reviews")
):
    """
    Returns:
      - rating_summary: rating, reviews_total, type[], address
      - most_relevant: list[{username, rating, contributor_id, description}]
    """
    if not SERP_API_KEY:
        raise HTTPException(500, "SERP_API_KEY not found in .env or environment")

    # 1) Look up the place
    data = http_get({
        "engine": "google_maps",
        "q": q,
        "api_key": SERP_API_KEY,
        "hl": "en",
    })

    place = data.get("place_results") or {}
    rating_summary = {
        "rating": place.get("rating"),
        "reviews_total": to_int(place.get("reviews")),
        "type": place.get("type"),
        "address": place.get("address"),
    }

    # Try embedded reviews first (some places include a small sample)
    embedded = place.get("reviews")
    embedded_list = embedded if isinstance(embedded, list) else []
    collected = normalize_reviews(embedded_list)

    # 2) If we still need more, use google_maps_reviews with data_id / place_id
    if len(collected) < limit:
        data_id = place.get("data_id")
        place_id = place.get("place_id")  # sometimes present

        if not data_id and not place_id:
            # As a fallback, try the first local result’s IDs if present
            local_results = data.get("local_results") or []
            if local_results:
                data_id = local_results[0].get("data_id") or data_id
                place_id = local_results[0].get("place_id") or place_id

        if data_id or place_id:
            params = {
                "engine": "google_maps_reviews",
                "api_key": SERP_API_KEY,
                "hl": "en",
                "sort_by": sort_by,  # "most_relevant" or "newest"
            }
            if data_id:
                params["data_id"] = data_id
            if place_id and "data_id" not in params:
                params["place_id"] = place_id

            rev_payload = http_get(params)
            more_reviews = normalize_reviews(rev_payload.get("reviews") or [])
            collected = (collected + more_reviews)[:limit]

    return {
        "query": q,
        "rating_summary": rating_summary,
        "most_relevant": collected,
    }
