"""
FastAPI application for the Learner Engagement Platform.
Provides REST API endpoints for learner management and AI-powered interventions.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import Dict, Any
import logging

# Import database utilities
from .lib_db import create_tables

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI application instance
app = FastAPI(
    title="Learner Engagement Platform API",
    description="AI-powered platform for identifying at-risk learners and generating personalized interventions",
    version="1.0.0"
)

# Configure CORS middleware for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8501", "http://127.0.0.1:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event() -> None:
    """
    Application startup event handler.
    Creates database tables if they don't exist.
    """
    logger.info("Starting Learner Engagement Platform API...")
    try:
        await create_tables()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        # Don't raise to allow server to start even if DB fails
        pass

@app.get("/api/health")
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint for monitoring and load balancer probes.
    
    Returns:
        Dict containing status and current timestamp
    """
    return {
        "status": "ok",
        "time": datetime.utcnow().isoformat(),
        "service": "learner-engagement-platform"
    }

# Import and register routers
from .routers.learners import router as learners_router
app.include_router(learners_router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )