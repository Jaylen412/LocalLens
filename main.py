from fastapi import FastAPI, HTTPException, Query
import os, requests
from typing import Any, Dict, List, Optional, Tuple
from dotenv import load_dotenv
import uvicorn
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
app = FastAPI(
    title="Reviews API",
    description="FastAPI application for fetching business reviews via SerpAPI",
    version="1.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

SERP_API_KEY = os.getenv("SERP_API_KEY")
BASE_URL = "https://serpapi.com/search.json"

# -----------------------------
# Utilities
# -----------------------------
def http_get(params: Dict[str, Any]) -> Dict[str, Any]:
    r = requests.get(BASE_URL, params=params, timeout=30)
    if r.status_code != 200:
        raise HTTPException(r.status_code, f"SerpAPI error: {r.text[:500]}")
    try:
        return r.json()
    except Exception as e:
        raise HTTPException(500, f"JSON parse error: {e}")

def to_int(x: Any) -> Optional[int]:
    if isinstance(x, int):
        return x
    if isinstance(x, str):
        try:
            return int(x.replace(",", "").strip())
        except:
            return None
    return None

def first(items: Optional[List[Dict[str, Any]]]) -> Dict[str, Any]:
    if isinstance(items, list) and items:
        return items[0]
    return {}

def normalize_review_item(r: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize review fields we care about for consulting:
    rating, description, date
    """

    return {
        "rating": r.get("rating"),
        "description": r.get("description") or r.get("snippet") or r.get("text"),
        "date": r.get("date")
    }

def normalize_reviews(raw: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [normalize_review_item(r) for r in (raw or [])]

def compute_rating_kpis(rating_summary_blocks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    rating_summary from place_results looks like:
       [{"stars":1,"amount":87},...,{"stars":5,"amount":990}]
    Return mix and quick KPIs.
    """
    counts = {b.get("stars"): to_int(b.get("amount")) or 0 for b in (rating_summary_blocks or [])}
    total = sum(counts.values()) or 0
    def share(n: int) -> float:
        return round(100.0 * (n / total), 2) if total else 0.0

    high = (counts.get(4, 0) + counts.get(5, 0))
    low = (counts.get(1, 0) + counts.get(2, 0))
    return {
        "distribution_counts": counts,           # {1: n, 2: n, ...}
        "total_in_distribution": total,
        "high_star_share_pct": share(high),      # 4-5★ %
        "low_star_share_pct": share(low),        # 1-2★ %
        "five_star_share_pct": share(counts.get(5, 0)),
        "one_star_share_pct": share(counts.get(1, 0)),
    }

def extract_competitors(pasf: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    people_also_search_for schema → list of peers with rating/reviews
    """
    out: List[Dict[str, Any]] = []
    if not pasf:
        return out
    for block in pasf.get("local_results", []):
        out.append({
            "title": block.get("title"),
            "rating": block.get("rating"),
            "reviews": to_int(block.get("reviews")),
            "gps_coordinates": block.get("gps_coordinates"),
            "type": block.get("type"),
            "data_id": block.get("data_id"),
            "data_cid": block.get("data_cid")
        })
    return out

def extract_popular_times(pop: Dict[str, Any]) -> Dict[str, Any]:
    """
    Return the raw popular times (graph_results) + live_hash (dwell time / live busyness)
    """
    if not pop:
        return {}
    return {
        "graph_results": pop.get("graph_results"),
        "live": pop.get("live_hash")
    }

def extract_place_core(place: Dict[str, Any]) -> Dict[str, Any]:
    """
    Flatten the important consulting-grade fields from place_results
    """
    out: Dict[str, Any] = {
        # stable identifiers for joins
        "place_id": place.get("place_id"),
        "data_id": place.get("data_id"),
        "data_cid": place.get("data_cid"),
        "provider_id": place.get("provider_id"),

        # basic profile
        "title": place.get("title"),
        "type": place.get("type"),
        "type_ids": place.get("type_ids"),
        "website": place.get("website"),
        "phone": place.get("phone"),
        "address": place.get("address"),
        "gps_coordinates": place.get("gps_coordinates"),
        "open_state": place.get("open_state"),
        "hours": place.get("hours"),

        # conversion paths
        "reservation_link": place.get("reservation", {}).get("link") or place.get("booking_link"),
        "reserve_a_table": place.get("reserve_a_table"),
        "order_online_link": place.get("order_online_link"),

        # price & menu positioning
        "price": place.get("price"),
        "price_details": place.get("price_details"),

        # ops promises / marketing copy scaffolding
        "extensions": place.get("extensions"),
        "service_options": place.get("service_options"),

        # links for further pulls
        "reviews_link": place.get("reviews_link"),
        "photos_link": place.get("photos_link"),
        "place_id_search": place.get("place_id_search"),

        # handy media / gallery
        # "thumbnail": place.get("thumbnail"),
        # "images": place.get("images"),

        # Q&A for preemptive FAQ
        "questions_and_answers": place.get("questions_and_answers")
    }

    # rating basics
    out["rating"] = place.get("rating")
    out["reviews_total"] = to_int(place.get("reviews"))

    # star distribution (Google sometimes provides this block)
    out["rating_summary_blocks"] = place.get("rating_summary") or []

    # computed KPIs from the block
    out["rating_kpis"] = compute_rating_kpis(out["rating_summary_blocks"])

    return out


# -----------------------------
# Endpoints
# -----------------------------
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Reviews API is running",
        "status": "healthy",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Detailed health check for monitoring"""
    serp_configured = bool(SERP_API_KEY)
    return {
        "status": "healthy",
        "serp_api_configured": serp_configured,
        "version": "1.1.0"
    }

@app.get("/reviews")
def reviews(
    q: str = Query(..., description="Business name (e.g., 'Fixins Soul Kitchen Detroit')"),
    limit: int = Query(10, ge=1, le=100, description="Max number of reviews to return"),
    sort_by: str = Query("most_relevant", pattern="^(most_relevant|newest)$", description="Sort reviews"),
    include_competitors: bool = Query(True, description="Include local competitors"),
    include_popular_times: bool = Query(True, description="Include Google popular times + live/dwell info"),
):
    """
    Fetch business reviews + consulting-grade place details via SerpAPI

    Response includes:
      - place_details: IDs, contact, links, hours, price_details, extensions, service_options,
                       rating & distribution, computed rating KPIs, Q&A, images
      - reviews: list[{username, rating, contributor_id, description, date, link, images_count}]
      - competitors: simplified 'people also search for' set (optional)
      - popular_times: graph + live_hash (optional)
    """
    if not SERP_API_KEY:
        raise HTTPException(500, "SERP_API_KEY not found in .env or environment")

    logger.info(f"Fetching place & reviews for: {q}")

    # 1) Place lookup
    data = http_get({
        "engine": "google_maps",
        "q": q,
        "api_key": SERP_API_KEY,
        "hl": "en",
    })

    place = data.get("place_results") or {}
    if not place:
        # sometimes results are in local_results; try first result if present
        local_results = data.get("local_results") or []
        if local_results:
            # fetch place via data_id if we have it
            fallback_id = local_results[0].get("data_id")
            if fallback_id:
                data = http_get({
                    "engine": "google_maps",
                    "data_id": fallback_id,
                    "api_key": SERP_API_KEY,
                    "hl": "en",
                })
                place = data.get("place_results") or {}

    if not place:
        raise HTTPException(404, f"No place found for query: {q}")

    # Core consulting-grade snapshot
    place_details = extract_place_core(place)

    # 2) Embedded reviews (rare)
    embedded = place.get("reviews")
    embedded_list = embedded if isinstance(embedded, list) else []
    collected = normalize_reviews(embedded_list)

    # 3) Pull reviews via google_maps_reviews (data_id/place_id)
    if len(collected) < limit:
        data_id = place.get("data_id")
        place_id = place.get("place_id")

        if not data_id and not place_id:
            # As a fallback, try the first local result's IDs if present
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

    # 4) Competitors (people also search for)
    competitors: List[Dict[str, Any]] = []
    if include_competitors:
        # PASF can be nested; in your example it's under place_results.people_also_search_for[0].local_results
        pasf_blocks = place.get("people_also_search_for") or []
        pasf = first(pasf_blocks) if isinstance(pasf_blocks, list) else pasf_blocks
        competitors = extract_competitors(pasf)

    # 5) Popular times (graph + live/dwell)
    popular_times_payload: Dict[str, Any] = {}
    if include_popular_times:
        popular_times_payload = extract_popular_times(place.get("popular_times") or {})

    logger.info(f"Retrieved {len(collected)} reviews for: {q}")

    return {
        "query": q,
        "place_details": place_details,
        "reviews": collected,
        "competitors": competitors,
        "popular_times": popular_times_payload
    }


if __name__ == "__main__":
    # Configuration for running the server
    host = os.getenv("HOST", "127.0.0.1")  # Use 127.0.0.1 for Cloudflare Tunnel
    port = int(os.getenv("PORT", "8000"))

    logger.info(f"Starting FastAPI server on {host}:{port}")
    logger.info("To expose via Cloudflare Tunnel, run: cloudflared tunnel --url http://127.0.0.1:8000")

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )
