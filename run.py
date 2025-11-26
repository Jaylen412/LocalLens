import uvicorn
import os
from app.core.config import logger

if __name__ == "__main__":
    # Configuration for running the server
    host = os.getenv("HOST", "0.0.0.0")  # Use 127.0.0.1 for Cloudflare Tunnel
    port = int(os.getenv("PORT", "8000"))

    logger.info(f"Starting FastAPI server on {host}:{port}")
    logger.info("To expose via Cloudflare Tunnel, run: cloudflared tunnel --url http://127.0.0.1:8000")

    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )
