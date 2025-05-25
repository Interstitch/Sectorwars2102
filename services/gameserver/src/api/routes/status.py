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

# AI Provider Health Check Endpoints
@router.get("/ai/providers")
@router.get("/ai/providers/")
async def ai_providers_health():
    """
    Check health status of all AI providers.
    This endpoint does not require authentication.
    """
    import time
    from src.services.ai_provider_service import get_ai_provider_service, ProviderType
    
    start_time = time.time()
    service = get_ai_provider_service()
    
    # Check each provider
    providers_status = {}
    
    # OpenAI Health Check
    try:
        openai_start = time.time()
        openai_configured = bool(os.environ.get("OPENAI_API_KEY"))
        openai_available = service.is_ai_available() and ProviderType.OPENAI in service.get_available_providers()
        
        # Test actual connectivity if configured
        openai_reachable = False
        openai_error = None
        if openai_configured and openai_available:
            try:
                # Quick test with OpenAI API
                import openai
                client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
                # Use a minimal request to test connectivity
                response = client.models.list()
                openai_reachable = True
            except Exception as e:
                openai_error = str(e)
        
        openai_response_time = (time.time() - openai_start) * 1000
        
        providers_status["openai"] = {
            "provider": "openai",
            "status": "healthy" if (openai_configured and openai_reachable) else "degraded" if openai_configured else "unavailable",
            "configured": openai_configured,
            "reachable": openai_reachable,
            "response_time": round(openai_response_time, 2),
            "last_check": datetime.datetime.now().isoformat(),
            "error": openai_error
        }
    except Exception as e:
        providers_status["openai"] = {
            "provider": "openai",
            "status": "unavailable",
            "configured": bool(os.environ.get("OPENAI_API_KEY")),
            "reachable": False,
            "response_time": 0,
            "last_check": datetime.datetime.now().isoformat(),
            "error": str(e)
        }
    
    # Anthropic Health Check
    try:
        anthropic_start = time.time()
        anthropic_configured = bool(os.environ.get("ANTHROPIC_API_KEY"))
        anthropic_available = service.is_ai_available() and ProviderType.ANTHROPIC in service.get_available_providers()
        
        # Test actual connectivity if configured
        anthropic_reachable = False
        anthropic_error = None
        if anthropic_configured and anthropic_available:
            try:
                # Quick test with Anthropic API
                import anthropic
                client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
                # Use a minimal request to test connectivity
                response = client.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=10,
                    messages=[{"role": "user", "content": "test"}]
                )
                anthropic_reachable = True
            except Exception as e:
                anthropic_error = str(e)
        
        anthropic_response_time = (time.time() - anthropic_start) * 1000
        
        providers_status["anthropic"] = {
            "provider": "anthropic",
            "status": "healthy" if (anthropic_configured and anthropic_reachable) else "degraded" if anthropic_configured else "unavailable",
            "configured": anthropic_configured,
            "reachable": anthropic_reachable,
            "response_time": round(anthropic_response_time, 2),
            "last_check": datetime.datetime.now().isoformat(),
            "error": anthropic_error
        }
    except Exception as e:
        providers_status["anthropic"] = {
            "provider": "anthropic",
            "status": "unavailable",
            "configured": bool(os.environ.get("ANTHROPIC_API_KEY")),
            "reachable": False,
            "response_time": 0,
            "last_check": datetime.datetime.now().isoformat(),
            "error": str(e)
        }
    
    # Overall status
    total_response_time = (time.time() - start_time) * 1000
    
    # Determine overall status
    healthy_count = sum(1 for p in providers_status.values() if p["status"] == "healthy")
    configured_count = sum(1 for p in providers_status.values() if p["configured"])
    
    overall_status = "healthy" if healthy_count > 0 else "degraded" if configured_count > 0 else "unavailable"
    
    return {
        "provider": "all",
        "status": overall_status,
        "providers": providers_status,
        "summary": {
            "healthy": healthy_count,
            "configured": configured_count,
            "total": len(providers_status)
        },
        "response_time": round(total_response_time, 2),
        "last_check": datetime.datetime.now().isoformat()
    }

@router.get("/ai/openai")
@router.get("/ai/openai/")
async def openai_health():
    """
    Check OpenAI API health status.
    This endpoint does not require authentication.
    """
    import time
    start_time = time.time()
    
    configured = bool(os.environ.get("OPENAI_API_KEY"))
    reachable = False
    error = None
    
    if configured:
        try:
            import openai
            client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
            # Quick test with OpenAI API
            response = client.models.list()
            reachable = True
        except Exception as e:
            error = str(e)
    
    response_time = (time.time() - start_time) * 1000
    status = "healthy" if (configured and reachable) else "degraded" if configured else "unavailable"
    
    result = {
        "provider": "openai",
        "status": status,
        "configured": configured,
        "reachable": reachable,
        "response_time": round(response_time, 2),
        "last_check": datetime.datetime.now().isoformat()
    }
    
    if error:
        result["error"] = error
    
    return result

@router.get("/ai/anthropic")
@router.get("/ai/anthropic/")
async def anthropic_health():
    """
    Check Anthropic API health status.
    This endpoint does not require authentication.
    """
    import time
    start_time = time.time()
    
    configured = bool(os.environ.get("ANTHROPIC_API_KEY"))
    reachable = False
    error = None
    
    if configured:
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
            # Quick test with Anthropic API
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=10,
                messages=[{"role": "user", "content": "test"}]
            )
            reachable = True
        except Exception as e:
            error = str(e)
    
    response_time = (time.time() - start_time) * 1000
    status = "healthy" if (configured and reachable) else "degraded" if configured else "unavailable"
    
    result = {
        "provider": "anthropic",
        "status": status,
        "configured": configured,
        "reachable": reachable,
        "response_time": round(response_time, 2),
        "last_check": datetime.datetime.now().isoformat()
    }
    
    if error:
        result["error"] = error
    
    return result