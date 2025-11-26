from fastapi import APIRouter
from app.api.endpoints import health, reviews

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(reviews.router, tags=["reviews"])
