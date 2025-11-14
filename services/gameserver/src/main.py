"""
Sectorwars 2102 Game Server - Main FastAPI Application
"""

import logging
import os
from datetime import datetime
from typing import Any, Dict

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

from src.core.config import settings
from src.core.database import Base, async_engine, get_async_session
from src.api.api import api_router
from src.utils.error_handling import setup_error_handling

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Sectorwars 2102 Game Server",
    description="Advanced space trading simulation game server with AI intelligence",
    version="2.1.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None
)

# Security middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"] if settings.DEVELOPMENT_MODE else ["localhost", "*.app.github.dev", "*.repl.co"]
)

# CORS middleware
allowed_origins = ["*"] if settings.DEVELOPMENT_MODE else [
    settings.get_frontend_url(),
    "https://*.app.github.dev",
    "https://*.repl.co"
]

# Always allow localhost origins for development
if settings.DEVELOPMENT_MODE:
    allowed_origins = ["*"]
else:
    allowed_origins.extend([
        "http://localhost:3000",
        "http://localhost:3001", 
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001"
    ])

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "status_code": exc.status_code}
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "body": exc.body}
    )


@app.exception_handler(SQLAlchemyError)
async def database_exception_handler(request: Request, exc: SQLAlchemyError):
    """Handle database errors"""
    logger.error(f"Database error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Database error occurred"}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all other exceptions"""
    logger.error(f"Unexpected error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )


@app.on_event("startup")
async def startup_event():
    """Initialize application"""
    logger.info("Starting Sectorwars 2102 Game Server...")

    try:
        # Create database tables
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables initialized")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")

    # Initialize default admin user if needed
    try:
        from src.auth.admin import create_default_admin
        from src.core.database import SessionLocal

        db = SessionLocal()
        try:
            create_default_admin(db)
            logger.info("Admin user initialization completed")
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Admin user initialization failed: {e}")
        # Don't crash the server if admin creation fails

    logger.info("Sectorwars 2102 Game Server started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Sectorwars 2102 Game Server...")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Sectorwars 2102 Game Server",
        "version": "2.1.0",
        "status": "online",
        "timestamp": datetime.utcnow().isoformat(),
        "api_docs": "/docs" if settings.DEBUG else "disabled",
        "environment": settings.detect_environment()
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        from src.core.database import AsyncSessionLocal
        async with AsyncSessionLocal() as session:
            from sqlalchemy import text
            await session.execute(text("SELECT 1"))
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "database": "connected",
            "environment": settings.detect_environment(),
            "api_version": settings.API_V1_STR
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "database": "disconnected",
                "error": str(e)
            }
        )


# Setup error handling
setup_error_handling(app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8080,
        reload=settings.DEBUG,
        log_level="info"
    )