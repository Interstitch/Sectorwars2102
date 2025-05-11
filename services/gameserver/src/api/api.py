from fastapi import APIRouter

from src.api.routes.auth import router as auth_router
from src.api.routes.users import router as users_router

# Main API router
api_router = APIRouter()

# Include all route modules here
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(users_router, prefix="/users", tags=["users"])

# Add additional routers here as they are created
# Example:
# api_router.include_router(game_router, prefix="/game", tags=["game"])