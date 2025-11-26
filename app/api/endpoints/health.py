import os
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Reviews API is running",
        "status": "healthy",
        "docs": "/docs"
    }

@router.get("/health")
async def health_check():
    """Detailed health check for monitoring"""
    serp_configured = bool(os.getenv("SERP_API_KEY"))
    return {
        "status": "healthy",
        "serp_api_configured": serp_configured,
        "version": "1.1.0"
    }
