from fastapi import APIRouter

from src.api.routes.auth import router as auth_router
from src.api.routes.users import router as users_router
from src.api.routes.test import router as test_router
from src.core.config import settings

# Main API router - note that the version is now in the main API_V1_STR prefix
# so we don't need to add 'v1' in the router prefixes here
api_router = APIRouter()

# Include all route modules here
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(users_router, prefix="/users", tags=["users"])

# Only include test routes in development/test environments
if settings.TESTING or settings.DEVELOPMENT_MODE:
    api_router.include_router(test_router, prefix="/test", tags=["test"])

# Add additional routers here as they are created
# Example:
# api_router.include_router(game_router, prefix="/game", tags=["game"])