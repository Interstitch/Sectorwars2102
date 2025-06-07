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
from src.api.routes.player_combat import router as player_combat_router
from src.api.routes.events import router as events_router
from src.api.routes.economy import router as economy_router
from src.api.routes.websocket import router as websocket_router
from src.api.routes.trading import router as trading_router
from src.api.routes.player import router as player_router
from src.api.routes.sectors import router as sectors_router
from src.api.routes.ai import router as ai_router
# from src.api.routes.enhanced_ai import router as enhanced_ai_router  # Temporarily disabled due to model issues
from src.api.routes.audit import router as audit_router
from src.api.routes.messages import router as messages_router
from src.api.routes.admin_messages import router as admin_messages_router
from src.api.routes.factions import router as factions_router
from src.api.routes.admin_factions import router as admin_factions_router
from src.api.routes.drones import router as drones_router
from src.api.routes.admin_drones import router as admin_drones_router
from src.api.routes.fleets import router as fleets_router
from src.api.routes.admin_fleets import router as admin_fleets_router
from src.api.routes.planets import router as planets_router
from src.api.routes.teams import router as teams_router
from src.api.routes.admin_economy import router as admin_economy_router
from src.api.routes.admin_combat import router as admin_combat_router
from src.api.routes.admin_ships import router as admin_ships_router
from src.api.routes.admin_colonization import router as admin_colonization_router
from src.api.routes.mfa import router as mfa_router
from src.api.routes.paypal import router as paypal_router
from src.api.routes.nexus import router as nexus_router
from src.api.routes.regional_governance import router as regional_governance_router
from src.api.routes.translation import router as translation_router
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
api_router.include_router(player_combat_router, tags=["player-combat"])
api_router.include_router(events_router, tags=["events"])
api_router.include_router(economy_router, tags=["economy"])
api_router.include_router(websocket_router, tags=["websocket"])
api_router.include_router(trading_router, tags=["trading"])
api_router.include_router(player_router, tags=["player"])
api_router.include_router(sectors_router, tags=["sectors"])
api_router.include_router(ai_router, tags=["ai-trading"])
# api_router.include_router(enhanced_ai_router, tags=["enhanced-ai"])  # Temporarily disabled
api_router.include_router(audit_router, tags=["audit"])
api_router.include_router(messages_router, tags=["messages"])
api_router.include_router(admin_messages_router, tags=["admin-messages"])
api_router.include_router(factions_router, tags=["factions"])
api_router.include_router(admin_factions_router, tags=["admin-factions"])
api_router.include_router(drones_router, tags=["drones"])
api_router.include_router(admin_drones_router, tags=["admin-drones"])
api_router.include_router(fleets_router, tags=["fleets"])
api_router.include_router(admin_fleets_router, tags=["admin-fleets"])
api_router.include_router(planets_router, tags=["planets"])
api_router.include_router(teams_router, tags=["teams"])
api_router.include_router(admin_economy_router, tags=["admin-economy"])
api_router.include_router(admin_combat_router, tags=["admin-combat"])
api_router.include_router(admin_ships_router, tags=["admin-ships"])
api_router.include_router(admin_colonization_router, prefix="/admin", tags=["admin-colonization"])
api_router.include_router(mfa_router, tags=["mfa"])
api_router.include_router(paypal_router, tags=["paypal"])
api_router.include_router(nexus_router, tags=["nexus"])
api_router.include_router(regional_governance_router, tags=["regional-governance"])
api_router.include_router(translation_router, tags=["translation"])

# Only include test routes in development/test environments
if settings.TESTING or settings.DEVELOPMENT_MODE:
    api_router.include_router(test_router, prefix="/test", tags=["test"])

# Add additional routers here as they are created
# Example:
# api_router.include_router(game_router, prefix="/game", tags=["game"])