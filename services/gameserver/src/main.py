#!/usr/bin/env python3
from fastapi import FastAPI, Depends, Request
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
from src.auth.admin import create_default_admin, create_default_player, create_default_factions
from src.api.middleware.security import setup_security_middleware

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
            create_default_factions(db)
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
    if settings.GITHUB_CLIENT_ID:
        logger.info("✅ GitHub OAuth credentials configured")
    else:
        logger.info("⚠️ WARNING: No GitHub OAuth credentials configured")
        logger.info("To enable GitHub OAuth, set CLIENT_ID_GITHUB and CLIENT_SECRET_GITHUB environment variables")

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

# Setup comprehensive security middleware first
setup_security_middleware(app)

# Configure CORS for GitHub Codespaces environment AFTER security middleware
# Detect current environment and set appropriate origins
import re

def get_allowed_origins():
    origins = [
        "http://localhost:3000",
        "http://localhost:8080", 
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080"
    ]
    
    # For GitHub Codespaces, detect the dynamic URL
    api_base_url = settings.get_api_base_url()
    frontend_url = settings.FRONTEND_URL
    
    if api_base_url and "app.github.dev" in api_base_url:
        origins.append(api_base_url)
        # Extract the codespace URL pattern and add port 3000 variant
        if match := re.search(r'(https://[^-]+-[^-]+-[^-]+-[^-]+)', api_base_url):
            base_url = match.group(1)
            origins.extend([
                f"{base_url}-3000.app.github.dev",
                f"{base_url}-8080.app.github.dev"
            ])
    
    if frontend_url and frontend_url not in origins:
        origins.append(frontend_url)
    
    return list(set(origins))  # Remove duplicates

codespace_urls = get_allowed_origins()

# For development, use a permissive CORS policy
# In production, this should be more restrictive
# Need to allow specific origins for credentials to work
app.add_middleware(
    CORSMiddleware,
    allow_origins=codespace_urls + [
        "http://localhost:3000",
        "http://localhost:8080", 
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
        "https://super-duper-carnival-qppjvq94q9vcxwqp-3000.app.github.dev",
        "https://super-duper-carnival-qppjvq94q9vcxwqp-8080.app.github.dev"
    ],
    allow_credentials=True,  # Required for Authorization headers
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=86400,  # 24 hours
)

# Log CORS configuration for debugging
logger.info(f"CORS configured with origins: {codespace_urls}")
logger.info("CORS allow_credentials: True")
logger.info("Security middleware initialized with OWASP compliance")

# Root endpoint for discoverability - kept at app level for easy access
@app.get("/")
async def hello_world(request: Request):
    environment = os.environ.get("ENVIRONMENT", "development")
    
    # Debugging log of request info for Codespaces issues
    logger.info(f"Root endpoint called from {request.client.host}:{request.client.port}")
    logger.info(f"Request headers: {dict(request.headers)}")
    
    return {
        "message": "Hello from Sector Wars 2102 Game API!",
        "environment": environment,
        "status": "operational",
        "api_version": "v1",
        "docs_url": "/api/v1/docs"
    }

# Add direct API status endpoints for backward compatibility with frontends
# These are outside the versioned API path for legacy support
@app.get("/api/status")
@app.get("/api/status/")  # Add with trailing slash too
async def api_status_direct(request: Request):
    """Direct endpoint for status that frontend expects."""
    # Log for debugging
    logger.info(f"Direct status endpoint called: {request.url}")
    # Standard response
    environment = os.environ.get("ENVIRONMENT", "development")
    return {
        "message": "Game API Server is operational",
        "environment": environment,
        "status": "healthy",
        "api_version": "v1"
    }

@app.get("/api/version")
@app.get("/api/version/")  # Add with trailing slash too
async def api_version_direct():
    """Direct endpoint for version that frontend expects."""
    return {"version": "0.1.0"}

# Add a middleware to handle CORS issues and URL normalization
@app.middleware("http")
async def add_cors_headers_and_fix_urls(request, call_next):
    # Special handling for GitHub Codespaces port forwarding
    host = request.headers.get("host", "")
    if host and ":8080" in host and "-8080.app.github.dev" in host:
        # This is a doubled port situation - log it for debugging
        logger.warning(f"Detected doubled port in host header: {host}")
        # Try to fix it by removing the explicit port
        fixed_host = host.replace(":8080", "")
        logger.info(f"Fixed host header: {fixed_host}")
        # Update the host header
        request.headers["host"] = fixed_host

    # Continue with normal request processing
    response = await call_next(request)

    # Add CORS headers to all responses (let the middleware handle origins properly)
    origin = request.headers.get("origin", "")
    allowed_origins = codespace_urls + [
        "http://localhost:3000",
        "http://localhost:8080", 
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
        "https://super-duper-carnival-qppjvq94q9vcxwqp-3000.app.github.dev",
        "https://super-duper-carnival-qppjvq94q9vcxwqp-8080.app.github.dev"
    ]
    
    if origin in allowed_origins:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
    else:
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Credentials"] = "false"
    
    response.headers["Access-Control-Allow-Methods"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Expose-Headers"] = "*"

    # Handle preflight OPTIONS requests specially
    if request.method == "OPTIONS":
        # Return 200 for preflight requests
        return response

    # Check if this is a redirect response (3xx) that might need port fixing
    if 300 <= response.status_code < 400:
        location = response.headers.get("location", "")
        if location and ":8080" in location and "-8080.app.github.dev" in location:
            # This is a doubled port in the location header - fix it
            logger.warning(f"Detected doubled port in Location header: {location}")
            fixed_location = location.replace(":8080", "")
            logger.info(f"Fixed Location header: {fixed_location}")
            response.headers["location"] = fixed_location

    return response

# Include API router with all routes
# This includes the status router that doesn't require authentication
app.include_router(api_router, prefix=settings.API_V1_STR)

# Start the application
if __name__ == "__main__":
    import uvicorn
    import os

    # Get port from environment or use 8080 as default for Replit
    port = int(os.environ.get("PORT", 8080))
    print(f"Starting server on port {port}")
    uvicorn.run("src.main:app", host="0.0.0.0", port=port, reload=True)