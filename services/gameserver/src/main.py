#!/usr/bin/env python3
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import os
import sys
import datetime
from sqlalchemy.orm import Session

# Import project modules
from src.api.api import api_router
from src.core.config import settings
from src.core.database import get_db
from src.auth.admin import create_default_admin, create_default_player

# Print environment information to help debugging
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")
print(f"sys.path: {sys.path}")
print(f"PYTHONPATH: {os.environ.get('PYTHONPATH', 'Not set')}")
print(f"CLIENT_ID_GITHUB: {os.environ.get('CLIENT_ID_GITHUB', 'Not set')}")
print(f"Is using mock GitHub: {settings.CLIENT_ID_GITHUB.startswith('mock_') if settings.CLIENT_ID_GITHUB else False}")

# Create FastAPI app
app = FastAPI(
    title="Sector Wars 2102 Game API",
    description="API for the Sector Wars 2102 space trading game",
    version="0.1.0",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    openapi_url="/api/v1/openapi.json"
)

# Configure CORS to work across all environments (Replit, Codespaces, Docker)
app.add_middleware(
    CORSMiddleware,
    # Must use wildcard for Replit, Codespaces, and local development
    allow_origins=["*"],
    # Must be False when using "*" as origin
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=86400,  # 24 hours
)

# Create a status router for utility endpoints
from fastapi import APIRouter
status_router = APIRouter(prefix="/status", tags=["status"])

# Health check endpoint - moved to versioned API
@status_router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "gameserver"}

# Hello World endpoint - root endpoint remains for discoverability
@app.get("/")
async def hello_world():
    environment = os.environ.get("ENVIRONMENT", "development")
    return {
        "message": "Hello from Sector Wars 2102 Game API!",
        "environment": environment,
        "status": "operational",
        "api_version": "v1",
        "docs_url": "/api/v1/docs"
    }

# Hello World endpoint - also available in versioned API
@status_router.get("/")
async def status_root():
    environment = os.environ.get("ENVIRONMENT", "development")
    return {
        "message": "Game API Server is operational",
        "environment": environment,
        "status": "healthy",
        "api_version": "v1"
    }

# API version endpoint - moved to versioned status router
@status_router.get("/version")
async def api_version():
    return {"version": "0.1.0"}

# API ping endpoint for simple connectivity testing - moved to versioned status router
@status_router.get("/ping")
async def api_ping():
    environment = os.environ.get("ENVIRONMENT", "development")
    return {
        "message": "pong",
        "environment": environment,
        "timestamp": datetime.datetime.now().isoformat()
    }

# Add a middleware to handle CORS issues
@app.middleware("http")
async def add_cors_headers(request, call_next):
    response = await call_next(request)

    # Add CORS headers to all responses
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Credentials"] = "false"
    response.headers["Access-Control-Allow-Methods"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Expose-Headers"] = "*"

    # Handle preflight OPTIONS requests specially
    if request.method == "OPTIONS":
        # Return 200 for preflight requests
        return response

    return response

# Include status router with all utility endpoints
app.include_router(status_router, prefix=settings.API_V1_STR)

# Include API router with all routes
app.include_router(api_router, prefix=settings.API_V1_STR)


# Startup event
@app.on_event("startup")
async def startup_event():
    # Initialize the database with default admin user
    db = next(get_db())
    try:
        create_default_admin(db)
        create_default_player(db)
    finally:
        db.close()

    # Print database environment info
    # Hide password from the logged URL by splitting at @ and only showing host
    def hide_password(url_str):
        if '@' in url_str:
            # Take only the part after @ (host:port/database)
            return url_str.split('@')[1]
        return url_str

    if settings.ENVIRONMENT == "production":
        print(f"Server started in {settings.ENVIRONMENT.upper()} mode")
        print("🚨 IMPORTANT: Running with PRODUCTION database 🚨")
        print(f"Database URL: ...@{hide_password(settings.get_db_url())}")
    else:
        print(f"Server started in {settings.ENVIRONMENT.upper()} mode")
        print("Using DEVELOPMENT database")
        print(f"Database URL: ...@{hide_password(settings.get_db_url())}")

    # Print OAuth configuration
    using_mock_github = settings.GITHUB_CLIENT_ID.startswith("mock_")
    if using_mock_github:
        print("⚠️ WARNING: Using mock GitHub OAuth - simulating OAuth flow")
        print("To use real GitHub OAuth, set CLIENT_ID_GITHUB and CLIENT_SECRET_GITHUB environment variables")
    else:
        print("✅ Using real GitHub OAuth credentials")

    # Print detected environment
    print(f"Detected environment: {settings.detect_environment()}")
    print(f"API Base URL: {settings.get_api_base_url()}")
    print(f"Frontend URL: {settings.FRONTEND_URL}")


# Start the application
if __name__ == "__main__":
    import uvicorn
    import os

    # Get port from environment or use 8080 as default for Replit
    port = int(os.environ.get("PORT", 8080))
    print(f"Starting server on port {port}")
    uvicorn.run("src.main:app", host="0.0.0.0", port=port, reload=True)