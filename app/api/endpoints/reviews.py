from fastapi import APIRouter, Query
from app.services.serpapi import fetch_reviews_data

router = APIRouter()

@router.get("/reviews")
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
    return fetch_reviews_data(q, limit, sort_by, include_competitors, include_popular_times)
