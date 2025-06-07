#!/usr/bin/env python3
"""
Main FastAPI application for Sectorwars2102 Game Server
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging
import sys
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Import core components
from src.core.config import settings
from src.core.database import engine, Base
from src.api.api import api_router
from src.api.middleware.security import setup_security_middleware

# Import models to ensure they're registered with SQLAlchemy
from src.models import *  # This ensures all models are imported

# Create FastAPI application
app = FastAPI(
    title="Sectorwars 2102 Game Server",
    description="Web-based space trading simulation game backend API",
    version="2.1.0",
    docs_url="/docs" if settings.DEVELOPMENT_MODE else None,
    redoc_url="/redoc" if settings.DEVELOPMENT_MODE else None,
    openapi_url="/openapi.json" if settings.DEVELOPMENT_MODE else None,
)

# Exception handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions with proper JSON responses"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "path": str(request.url.path)}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors"""
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation error",
            "details": exc.errors(),
            "path": str(request.url.path)
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "path": str(request.url.path)
        }
    )

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Player client
        "http://localhost:3001",  # Admin UI
        settings.get_frontend_url(),  # Dynamic frontend URL
        settings.get_api_base_url(),  # API base URL
        "https://*.app.github.dev",  # GitHub Codespaces
        "https://*.repl.co",  # Replit
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)

# Add trusted host middleware for security
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=[
        "localhost",
        "127.0.0.1",
        "*.app.github.dev",  # GitHub Codespaces
        "*.repl.co",  # Replit
        "*",  # Allow all hosts in development
    ]
)

# Setup security middleware
setup_security_middleware(app)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint providing basic API information"""
    return {
        "message": "Welcome to Sectorwars 2102 Game Server",
        "version": "2.1.0",
        "status": "operational",
        "environment": settings.ENVIRONMENT,
        "api_docs": "/docs" if settings.DEVELOPMENT_MODE else "disabled",
        "api_prefix": settings.API_V1_STR
    }

# Health check endpoint (outside API prefix for monitoring)
@app.get("/health")
async def health_check():
    """Health check endpoint for container orchestration"""
    try:
        # Test database connection
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": "2025-06-07T00:00:00Z",
            "environment": settings.ENVIRONMENT
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(e),
                "timestamp": "2025-06-07T00:00:00Z"
            }
        )

# Include API routes with version prefix
app.include_router(api_router, prefix=settings.API_V1_STR)

# Startup event
@app.on_event("startup")
async def startup_event():
    """Application startup tasks"""
    logger.info("Starting Sectorwars 2102 Game Server...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"API Base URL: {settings.get_api_base_url()}")
    logger.info(f"Frontend URL: {settings.get_frontend_url()}")
    logger.info(f"Database URL: {settings.get_db_url()[:50]}...")
    
    # Ensure logs directory exists
    log_dir = "/app/logs" if os.path.exists("/app") else "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    # Add file handler for logs
    file_handler = logging.FileHandler(f"{log_dir}/gameserver.log", mode="a")
    file_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    logging.getLogger().addHandler(file_handler)
    
    # Create database tables if they don't exist
    try:
        Base.metadata.create_all(bind=engine, checkfirst=True)
        logger.info("Database tables verified/created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
    
    logger.info("Game server startup completed")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown tasks"""
    logger.info("Shutting down Sectorwars 2102 Game Server...")
    
    # Close database connections
    try:
        engine.dispose()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error closing database connections: {e}")
    
    logger.info("Game server shutdown completed")

# Make app available for imports (required for uvicorn)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8080,
        reload=settings.DEVELOPMENT_MODE,
        log_level="info"
    )