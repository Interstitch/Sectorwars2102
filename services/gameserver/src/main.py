#!/usr/bin/env python3
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import os
import sys
import datetime
import logging
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, OperationalError

# Import project modules
from src.api.api import api_router
from src.core.config import settings
from src.core.database import get_db
from src.auth.admin import create_default_admin, create_default_player

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

# Print environment information to help debugging
logger.info(f"Python version: {sys.version}")
logger.info(f"Current directory: {os.getcwd()}")
logger.info(f"sys.path: {sys.path}")
logger.info(f"PYTHONPATH: {os.environ.get('PYTHONPATH', 'Not set')}")
logger.info(f"CLIENT_ID_GITHUB: {os.environ.get('CLIENT_ID_GITHUB', 'Not set')}")
logger.info(f"Is using mock GitHub: {settings.CLIENT_ID_GITHUB.startswith('mock_') if settings.CLIENT_ID_GITHUB else False}")

# Define lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database schema if needed
    from src.core.db_init import initialize_database
    
    try:
        # Run migrations if database tables don't exist
        if initialize_database():
            logger.info("Database schema is ready")
        else:
            logger.error("Failed to initialize database schema - the app may not work correctly")
    except Exception as e:
        logger.error(f"Error initializing database schema: {str(e)}")
    
    # Initialize database and ensure default admin exists
    try:
        db = next(get_db())
        try:
            logger.info("Checking for default admin user...")
            create_default_admin(db)
            create_default_player(db)
            logger.info("Database initialization complete")
        except OperationalError as e:
            logger.error(f"Failed to connect to database during startup: {str(e)}")
            logger.error(f"Check that the database connection is properly configured: {settings.get_db_url()}")
        except SQLAlchemyError as e:
            logger.error(f"Database error during startup: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during database initialization: {str(e)}")
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Failed to initialize database session: {str(e)}")

    # Print database environment info
    # Hide password from the logged URL by splitting at @ and only showing host
    def hide_password(url_str):
        if '@' in url_str:
            # Take only the part after @ (host:port/database)
            return url_str.split('@')[1]
        return url_str

    if settings.ENVIRONMENT == "production":
        logger.info(f"Server started in {settings.ENVIRONMENT.upper()} mode")
        logger.info("🚨 IMPORTANT: Running with PRODUCTION database 🚨")
        logger.info(f"Database URL: ...@{hide_password(settings.get_db_url())}")
    else:
        logger.info(f"Server started in {settings.ENVIRONMENT.upper()} mode")
        logger.info("Using DEVELOPMENT database")
        logger.info(f"Database URL: ...@{hide_password(settings.get_db_url())}")

    # Print OAuth configuration
    using_mock_github = settings.GITHUB_CLIENT_ID.startswith("mock_")
    if using_mock_github:
        logger.info("⚠️ WARNING: Using mock GitHub OAuth - simulating OAuth flow")
        logger.info("To use real GitHub OAuth, set CLIENT_ID_GITHUB and CLIENT_SECRET_GITHUB environment variables")
    else:
        logger.info("✅ Using real GitHub OAuth credentials")

    # Print detected environment
    logger.info(f"Detected environment: {settings.detect_environment()}")
    logger.info(f"API Base URL: {settings.get_api_base_url()}")
    logger.info(f"Frontend URL: {settings.FRONTEND_URL}")
    
    yield  # This is where FastAPI runs
    
    # Cleanup tasks can go here (on shutdown)
    logger.info("Shutting down application...")

# Create FastAPI app with lifespan
app = FastAPI(
    title="Sector Wars 2102 Game API",
    description="API for the Sector Wars 2102 space trading game",
    version="0.1.0",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    openapi_url="/api/v1/openapi.json",
    lifespan=lifespan
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

# Add direct endpoints for backward compatibility with frontend
# These match the paths the frontend expects
@app.get("/api/status")
async def api_status_direct():
    """Direct endpoint for status that frontend expects."""
    environment = os.environ.get("ENVIRONMENT", "development")
    return {
        "message": "Game API Server is operational",
        "environment": environment,
        "status": "healthy",
        "api_version": "v1"
    }

@app.get("/api/version")
async def api_version_direct():
    """Direct endpoint for version that frontend expects."""
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

# Start the application
if __name__ == "__main__":
    import uvicorn
    import os

    # Get port from environment or use 8080 as default for Replit
    port = int(os.environ.get("PORT", 8080))
    print(f"Starting server on port {port}")
    uvicorn.run("src.main:app", host="0.0.0.0", port=port, reload=True)