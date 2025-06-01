from typing import Dict, Optional, Any, Tuple
import uuid
import httpx
from fastapi import HTTPException, status, Request
from sqlalchemy.orm import Session
from urllib.parse import urlencode

from src.core.config import settings
from src.models.user import User
from src.models.oauth_account import OAuthAccount
from src.models.player import Player
from src.models.ship import Ship, ShipType


async def get_oauth_user(
    db: Session, 
    provider: str, 
    provider_user_id: str
) -> Optional[User]:
    """
    Get a user by OAuth provider and provider user ID.
    Check for both active and soft-deleted accounts.
    """
    oauth_account = db.query(OAuthAccount).filter(
        OAuthAccount.provider == provider,
        OAuthAccount.provider_user_id == provider_user_id
    ).first()
    
    if oauth_account:
        # If OAuth account is soft-deleted, reactivate it
        if oauth_account.deleted:
            oauth_account.deleted = False
            db.commit()
        
        # Get the associated user (only return if user is active)
        return db.query(User).filter(
            User.id == oauth_account.user_id,
            User.deleted == False
        ).first()
    
    return None


async def create_oauth_user(
    db: Session,
    provider: str,
    provider_user_id: str,
    user_data: Dict[str, Any]
) -> User:
    """
    Create a new user from OAuth data.
    Check if OAuth account already exists and handle appropriately.
    """
    # First check if OAuth account already exists (might be orphaned)
    existing_oauth = db.query(OAuthAccount).filter(
        OAuthAccount.provider == provider,
        OAuthAccount.provider_user_id == provider_user_id
    ).first()
    
    if existing_oauth:
        # OAuth account exists - check if user exists
        if existing_oauth.deleted:
            # Reactivate deleted OAuth account
            existing_oauth.deleted = False
            db.commit()
        
        # Get the associated user
        user = db.query(User).filter(
            User.id == existing_oauth.user_id,
            User.deleted == False
        ).first()
        
        if user:
            return user
        else:
            # OAuth account exists but user is deleted - clean up and recreate
            db.delete(existing_oauth)
            db.commit()
    
    username = user_data.get("username", f"{provider}_{provider_user_id}")
    email = user_data.get("email")
    
    # Create user
    user = User(
        username=username,
        email=email,
        is_active=True,
    )
    db.add(user)
    db.flush()
    
    # Create OAuth account
    oauth_account = OAuthAccount(
        user_id=user.id,
        provider=provider,
        provider_user_id=provider_user_id,
        provider_account_email=user_data.get("email"),
        provider_account_username=user_data.get("username"),
        deleted=False
    )
    db.add(oauth_account)
    
    # Create Player record for OAuth user
    player = await create_player_for_user(db, user)
    
    db.commit()
    
    return user


async def create_player_for_user(db: Session, user: User) -> Player:
    """
    Create a Player record for a User (OAuth or otherwise).
    Also creates a starter ship for the player.
    """
    # Create player
    player = Player(
        user_id=user.id,
        nickname=None,  # Can be set later by user
        credits=1000,   # Starting credits (as per FIRST_LOGIN.md)
        turns=1000,     # Starting turns
        reputation={},  # Empty reputation
        home_sector_id=1,     # Start in sector 1
        current_sector_id=1,  # Start in sector 1
        is_ported=False,
        is_landed=False,
        team_id=None,
        attack_drones=0,
        defense_drones=0,
        mines=0,
        insurance=None,
        settings={},
        first_login={"completed": False}
    )
    db.add(player)
    db.flush()  # Get the player ID
    
    # Create starter escape pod (as per FIRST_LOGIN.md)
    starter_ship = Ship(
        name="Escape Pod",
        type=ShipType.ESCAPE_POD,  # Start with escape pod
        owner_id=player.id,
        sector_id=1,  # Start in sector 1
        cargo={},
        current_speed=1.0,
        base_speed=1.0,
        turn_cost=1,  # Standard turn cost for escape pod
        combat={},
        maintenance={},
        is_flagship=True,
        purchase_value=1000,  # Escape pod value
        current_value=1000
    )
    db.add(starter_ship)
    db.flush()  # Get the ship ID
    
    # Set the starter ship as current ship
    player.current_ship_id = starter_ship.id
    
    return player


class GitHubOAuth:
    """GitHub OAuth implementation."""

    @staticmethod
    def get_authorization_url(redirect_uri: str) -> str:
        """Get the GitHub authorization URL."""
        params = {
            "client_id": settings.GITHUB_CLIENT_ID,
            "redirect_uri": redirect_uri,
            "scope": "read:user user:email",
            "state": str(uuid.uuid4()),
        }
        return f"https://github.com/login/oauth/authorize?{urlencode(params)}"

    @staticmethod
    async def exchange_code_for_token(code: str, redirect_uri: str) -> str:
        """Exchange authorization code for access token."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://github.com/login/oauth/access_token",
                data={
                    "client_id": settings.GITHUB_CLIENT_ID,
                    "client_secret": settings.GITHUB_CLIENT_SECRET,
                    "code": code,
                    "redirect_uri": redirect_uri,
                },
                headers={"Accept": "application/json"}
            )

            data = response.json()
            if "error" in data:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"GitHub auth error: {data.get('error_description', data['error'])}"
                )

            return data.get("access_token")

    @staticmethod
    async def get_user_info(token: str) -> Tuple[str, Dict[str, Any]]:
        """Get user info from GitHub using the access token."""
        async with httpx.AsyncClient() as client:
            # Get user profile
            user_response = await client.get(
                "https://api.github.com/user",
                headers={
                    "Authorization": f"token {token}",
                    "Accept": "application/json"
                }
            )
            user_data = user_response.json()

            # Get user emails
            email_response = await client.get(
                "https://api.github.com/user/emails",
                headers={
                    "Authorization": f"token {token}",
                    "Accept": "application/json"
                }
            )
            email_data = email_response.json()

            # Find primary email
            primary_email = next(
                (email["email"] for email in email_data if email["primary"]),
                None
            )

            # Extract needed user data
            provider_user_id = str(user_data["id"])
            profile_data = {
                "username": user_data.get("login"),
                "email": primary_email,
                "name": user_data.get("name"),
                "avatar_url": user_data.get("avatar_url"),
                "github_url": user_data.get("html_url"),
                "raw_github_data": user_data
            }

            return provider_user_id, profile_data


class GoogleOAuth:
    """Google OAuth implementation."""

    @staticmethod
    def get_authorization_url(redirect_uri: str) -> str:
        """Get the Google authorization URL."""
        params = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "state": str(uuid.uuid4()),
            "access_type": "offline",
            "prompt": "consent",
        }
        return f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"

    @staticmethod
    async def exchange_code_for_token(code: str, redirect_uri: str) -> Dict[str, Any]:
        """Exchange authorization code for tokens."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "code": code,
                    "redirect_uri": redirect_uri,
                    "grant_type": "authorization_code",
                },
                headers={"Accept": "application/json"}
            )

            data = response.json()
            if "error" in data:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Google auth error: {data.get('error_description', data['error'])}"
                )

            return data

    @staticmethod
    async def get_user_info(token_data: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """Get user info from Google using the ID token."""
        access_token = token_data.get("access_token")

        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/json"
                }
            )
            user_data = response.json()

            # Extract needed user data
            provider_user_id = user_data.get("id")
            profile_data = {
                "username": user_data.get("email").split("@")[0],  # Use email prefix as username
                "email": user_data.get("email"),
                "name": user_data.get("name"),
                "avatar_url": user_data.get("picture"),
                "raw_google_data": user_data
            }

            return provider_user_id, profile_data


class SteamAuth:
    """Steam authentication implementation."""

    @staticmethod
    def get_authorization_url(redirect_uri: str) -> str:
        """Get the Steam authentication URL."""
        # Steam uses OpenID 2.0
        params = {
            "openid.ns": "http://specs.openid.net/auth/2.0",
            "openid.mode": "checkid_setup",
            "openid.return_to": redirect_uri,
            "openid.realm": redirect_uri.rsplit("/", 1)[0],  # Base URL without path
            "openid.identity": "http://specs.openid.net/auth/2.0/identifier_select",
            "openid.claimed_id": "http://specs.openid.net/auth/2.0/identifier_select",
        }
        return f"https://steamcommunity.com/openid/login?{urlencode(params)}"

    @staticmethod
    async def verify_response(request: Request) -> str:
        """Verify the Steam OpenID response and extract Steam ID."""
        # Get parameters from the request
        params = dict(request.query_params)

        # Construct verification params
        params["openid.mode"] = "check_authentication"

        async with httpx.AsyncClient() as client:
            # Verify with Steam
            response = await client.post(
                "https://steamcommunity.com/openid/login",
                data=params
            )

            # Check if verification succeeded
            if "is_valid:true" not in response.text:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Steam authentication failed"
                )

            # Extract Steam ID from claimed_id
            claimed_id = params.get("openid.claimed_id", "")
            if not claimed_id or "steamcommunity.com/openid/id/" not in claimed_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid Steam ID format"
                )

            steam_id = claimed_id.split("/")[-1]
            return steam_id

    @staticmethod
    async def get_user_info(steam_id: str) -> Dict[str, Any]:
        """Get user info from Steam API using Steam ID."""
        async with httpx.AsyncClient() as client:
            url = (
                f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/"
                f"?key={settings.STEAM_API_KEY}&steamids={steam_id}"
            )
            response = await client.get(url)
            data = response.json()

            try:
                player = data["response"]["players"][0]
            except (KeyError, IndexError):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Steam user not found"
                )

            profile_data = {
                "username": player.get("personaname"),
                "avatar_url": player.get("avatarfull"),
                "steam_url": player.get("profileurl"),
                "raw_steam_data": player
            }

            return profile_data