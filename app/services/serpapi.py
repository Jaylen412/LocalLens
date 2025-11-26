from typing import Any, Dict, List
from fastapi import HTTPException
import logging
from app.core.config import get_serp_api_key
from app.utils.http import http_get
from app.utils.common import (
    extract_place_core,
    normalize_reviews,
    first,
    extract_competitors,
    extract_popular_times
)

logger = logging.getLogger(__name__)

def fetch_reviews_data(
    q: str,
    limit: int,
    sort_by: str,
    include_competitors: bool,
    include_popular_times: bool
) -> Dict[str, Any]:
    SERP_API_KEY = get_serp_api_key()

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
