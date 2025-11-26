import requests
from typing import Any, Dict
from fastapi import HTTPException
from app.core.config import BASE_URL

def http_get(params: Dict[str, Any]) -> Dict[str, Any]:
    r = requests.get(BASE_URL, params=params, timeout=30)
    if r.status_code != 200:
        raise HTTPException(r.status_code, f"SerpAPI error: {r.text[:500]}")
    try:
        return r.json()
    except Exception as e:
        raise HTTPException(500, f"JSON parse error: {e}")
