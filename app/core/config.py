import os
import logging
from dotenv import load_dotenv
from fastapi import HTTPException

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env in development
if os.path.exists('.env'):
    load_dotenv()
else:
    logger.info("Running in production, using environment variables")

BASE_URL = "https://serpapi.com/search.json"

def get_serp_api_key():
    """Get SERP API key from environment"""
    key = os.getenv("SERP_API_KEY")
    if not key:
        logger.error("SERP_API_KEY not found in environment variables")
        raise HTTPException(500, "SERP_API_KEY not configured")
    return key
