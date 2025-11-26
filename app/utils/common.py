from typing import Any, Dict, List, Optional

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
