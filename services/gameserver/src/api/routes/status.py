"""
Status routes for checking API health without authentication.
These endpoints are available without authentication and are used
by frontends to check if the API is up and running.
"""
import os
import datetime
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import settings

# Create a dedicated status router without authentication
router = APIRouter()

# Standard status response with environment info
def get_status_response():
    environment = os.environ.get("ENVIRONMENT", "development")
    return {
        "message": "Game API Server is operational",
        "environment": environment,
        "status": "healthy",
        "api_version": "v1"
    }

# Status endpoint for health checks
@router.get("/")
@router.get("")  # Handle both with and without trailing slash
async def status_root(request: Request):
    """
    Get the status of the API.
    This endpoint does not require authentication.
    """
    host = request.headers.get("host", "")
    origin = request.headers.get("origin", "")
    forwarded_host = request.headers.get("x-forwarded-host", "")
    forwarded_proto = request.headers.get("x-forwarded-proto", "")
    
    # Include request debugging information in development
    if settings.DEBUG:
        response = get_status_response()
        response["debug"] = {
            "host": host,
            "origin": origin,
            "x-forwarded-host": forwarded_host,
            "x-forwarded-proto": forwarded_proto,
            "headers": dict(request.headers),
            "url": str(request.url),
            "base_url": str(request.base_url),
            "method": request.method,
            "client": request.client.host if request.client else None,
            "timestamp": datetime.datetime.now().isoformat()
        }
        return response
    
    return get_status_response()

# Add a simple ping endpoint that's easy to access
@router.get("/ping")
async def ping():
    """
    Simple ping endpoint for testing connectivity.
    Returns a simple response with no additional processing.
    """
    return {"ping": "pong", "timestamp": datetime.datetime.now().isoformat()}

# Version endpoint
@router.get("/version")
@router.get("/version/")  # Add version with trailing slash
async def api_version():
    """
    Get the version of the API.
    This endpoint does not require authentication.
    """
    return {"version": "0.1.0"}

# Ping endpoint for simple connectivity testing
@router.get("/ping")
@router.get("/ping/")  # Add with trailing slash too
async def api_ping():
    """
    Simple ping endpoint for connectivity testing.
    This endpoint does not require authentication.
    """
    environment = os.environ.get("ENVIRONMENT", "development")
    return {
        "message": "pong",
        "environment": environment,
        "timestamp": datetime.datetime.now().isoformat()
    }

# Health check endpoint
@router.get("/health")
@router.get("/health/")
async def health_check():
    """
    Health check endpoint for monitoring.
    This endpoint does not require authentication.
    """
    return {"status": "healthy", "service": "gameserver"}