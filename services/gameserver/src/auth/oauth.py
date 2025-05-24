from typing import Dict, Optional, Any, Tuple
import uuid
import httpx
import random
import datetime
from fastapi import HTTPException, status, Request
from sqlalchemy.orm import Session
import xml.etree.ElementTree as ET
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
    """
    oauth_account = db.query(OAuthAccount).filter(
        OAuthAccount.provider == provider,
        OAuthAccount.provider_user_id == provider_user_id,
        OAuthAccount.deleted == False
    ).first()
    
    if oauth_account:
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
    """
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
        credits=10000,  # Starting credits
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
    
    # Create starter ship
    starter_ship = Ship(
        name="Starter Ship",
        type=ShipType.LIGHT_FREIGHTER,
        owner_id=player.id,
        sector_id=1,  # Start in sector 1
        cargo={},
        current_speed=1.0,
        base_speed=1.0,
        combat={},
        maintenance={},
        is_flagship=True,
        purchase_value=10000,
        current_value=10000
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
        # For development with mock credentials, simulate direct callback
        if settings.GITHUB_CLIENT_ID.startswith("mock_"):
            # Create a simulated callback URL with code parameter
            simulated_code = f"mock_code_{uuid.uuid4()}"

            # Check if redirect_uri already has query parameters
            if "?" in redirect_uri:
                return f"{redirect_uri}&code={simulated_code}"
            else:
                return f"{redirect_uri}?code={simulated_code}"

        # Real implementation for production
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
        # For development with mock credentials, generate a fake token
        if settings.GITHUB_CLIENT_ID.startswith("mock_") and code.startswith("mock_code_"):
            return f"mock_github_token_{uuid.uuid4()}"

        # Real implementation for production
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
        # For development with mock credentials, generate fake user data
        if token.startswith("mock_github_token_"):
            # Generate a random user ID
            provider_user_id = str(uuid.uuid4())
            profile_data = {
                "username": f"github_user_{provider_user_id[:8]}",
                "email": f"github_{provider_user_id[:8]}@example.com",
                "name": f"GitHub User {provider_user_id[:8]}",
                "avatar_url": "https://avatars.githubusercontent.com/u/583231?v=4",
                "github_url": f"https://github.com/user_{provider_user_id[:8]}",
                "raw_github_data": {"id": provider_user_id}
            }
            return provider_user_id, profile_data

        # Real implementation for production
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
        # For development with mock credentials, simulate direct callback
        if settings.GOOGLE_CLIENT_ID.startswith("mock_"):
            # Create a simulated callback URL with code parameter
            simulated_code = f"mock_code_{uuid.uuid4()}"

            # Check if redirect_uri already has query parameters
            if "?" in redirect_uri:
                return f"{redirect_uri}&code={simulated_code}"
            else:
                return f"{redirect_uri}?code={simulated_code}"

        # Real implementation for production
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
        # For development with mock credentials, generate fake token data
        if settings.GOOGLE_CLIENT_ID.startswith("mock_") and code.startswith("mock_code_"):
            return {
                "access_token": f"mock_google_token_{uuid.uuid4()}",
                "id_token": f"mock_google_id_token_{uuid.uuid4()}",
                "token_type": "Bearer",
                "expires_in": 3600
            }

        # Real implementation for production
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

        # For development with mock credentials, generate fake user data
        if access_token and access_token.startswith("mock_google_token_"):
            # Generate a random user ID
            provider_user_id = str(uuid.uuid4())
            profile_data = {
                "username": f"google_user_{provider_user_id[:8]}",
                "email": f"google_{provider_user_id[:8]}@example.com",
                "name": f"Google User {provider_user_id[:8]}",
                "avatar_url": "https://lh3.googleusercontent.com/a/default-user",
                "raw_google_data": {"id": provider_user_id}
            }
            return provider_user_id, profile_data

        # Real implementation for production
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
        # For development with mock credentials, simulate direct callback
        if settings.STEAM_API_KEY.startswith("mock_"):
            # For Steam, we need to include OpenID parameters for compatibility
            # Simulate a valid OpenID response
            params = {
                "openid.ns": "http://specs.openid.net/auth/2.0",
                "openid.mode": "id_res",
                "openid.op_endpoint": "https://steamcommunity.com/openid/login",
                "openid.claimed_id": f"https://steamcommunity.com/openid/id/mock_steam_{uuid.uuid4()}",
                "openid.identity": f"https://steamcommunity.com/openid/id/mock_steam_{uuid.uuid4()}",
                "openid.return_to": redirect_uri,
                "openid.response_nonce": f"{datetime.datetime.now().isoformat()}mock{uuid.uuid4()}",
                "openid.assoc_handle": f"mock_assoc_{uuid.uuid4()}",
                "openid.signed": "signed,op_endpoint,claimed_id,identity,return_to,response_nonce,assoc_handle",
                "openid.sig": f"mock_sig_{uuid.uuid4()}"
            }

            # Check if redirect_uri already has query parameters
            if "?" in redirect_uri:
                return f"{redirect_uri}&{urlencode(params)}"
            else:
                return f"{redirect_uri}?{urlencode(params)}"

        # Real implementation for production
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

        # For development with mock credentials
        claimed_id = params.get("openid.claimed_id", "")
        if claimed_id and "mock_steam_" in claimed_id:
            # Extract the mock Steam ID from the claim
            steam_id = claimed_id.split("mock_steam_")[-1]
            return f"mock_steam_{steam_id}"

        # Real implementation for production
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
        # For development with mock credentials
        if steam_id.startswith("mock_steam_"):
            # Generate mock player data
            random_id = steam_id.split("mock_steam_")[-1]
            profile_data = {
                "username": f"SteamUser_{random_id[:8]}",
                "avatar_url": "https://avatars.akamai.steamstatic.com/fef49e7fa7e1997310d705b2a6158ff8dc1cdfeb_full.jpg",
                "steam_url": f"https://steamcommunity.com/profiles/mock_{random_id}",
                "raw_steam_data": {
                    "steamid": f"7656119{random.randint(10000000, 99999999)}",
                    "personaname": f"SteamUser_{random_id[:8]}",
                    "profileurl": f"https://steamcommunity.com/profiles/mock_{random_id}",
                    "avatar": "fef49e7fa7e1997310d705b2a6158ff8dc1cdfeb_full.jpg"
                }
            }
            return profile_data

        # Real implementation for production
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