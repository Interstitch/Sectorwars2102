from fastapi import APIRouter

from src.api.routes.auth import router as auth_router
from src.api.routes.users import router as users_router
from src.api.routes.test import router as test_router
from src.api.routes.status import router as status_router
from src.api.routes.first_login import router as first_login_router
from src.api.routes.admin import router as admin_router
from src.api.routes.admin_enhanced import router as admin_enhanced_router
from src.api.routes.admin_comprehensive import router as admin_comprehensive_router
from src.api.routes.combat import router as combat_router
from src.api.routes.events import router as events_router
from src.api.routes.economy import router as economy_router
from src.api.routes.websocket import router as websocket_router
from src.api.routes.trading import router as trading_router
from src.api.routes.player import router as player_router
from src.api.routes.sectors import router as sectors_router
from src.api.routes.ai import router as ai_router
from src.core.config import settings

# Main API router - note that the version is now in the main API_V1_STR prefix
# so we don't need to add 'v1' in the router prefixes here
api_router = APIRouter()

# Include status router first - these endpoints don't require authentication
api_router.include_router(status_router, prefix="/status", tags=["status"])

# Include all authenticated route modules here
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(first_login_router, prefix="/first-login", tags=["first-login"])
api_router.include_router(admin_router, prefix="/admin", tags=["admin"])
api_router.include_router(admin_enhanced_router, prefix="/admin", tags=["admin-enhanced"])
api_router.include_router(admin_comprehensive_router, prefix="/admin", tags=["admin-comprehensive"])
api_router.include_router(combat_router, tags=["combat"])
api_router.include_router(events_router, tags=["events"])
api_router.include_router(economy_router, tags=["economy"])
api_router.include_router(websocket_router, tags=["websocket"])
api_router.include_router(trading_router, tags=["trading"])
api_router.include_router(player_router, tags=["player"])
api_router.include_router(sectors_router, tags=["sectors"])
api_router.include_router(ai_router, tags=["ai-trading"])

# Only include test routes in development/test environments
if settings.TESTING or settings.DEVELOPMENT_MODE:
    api_router.include_router(test_router, prefix="/test", tags=["test"])

# Add additional routers here as they are created
# Example:
# api_router.include_router(game_router, prefix="/game", tags=["game"])