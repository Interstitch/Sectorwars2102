import os
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request, Body
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session
from jose import JWTError

from src.auth.jwt import create_tokens, decode_token
from src.auth.dependencies import get_current_user
from src.models.user import User
from src.models.admin_credentials import AdminCredentials
from src.auth.oauth import GitHubOAuth, GoogleOAuth, SteamAuth, get_oauth_user, create_oauth_user
from src.core.database import get_db
from src.core.config import settings
from src.models.refresh_token import RefreshToken
from src.schemas.auth import Token, RefreshToken as RefreshTokenSchema, AuthResponse, LoginForm
from src.services.user_service import authenticate_admin, authenticate_player, update_user_last_login

router = APIRouter()


@router.post("/login", response_model=AuthResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Authenticate admin user with username and password using form data.
    Returns JWT tokens for API access.
    """
    # Get credentials from form data
    username = form_data.username
    password = form_data.password

    # Authenticate user
    user = authenticate_admin(db, username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create new tokens
    access_token, refresh_token = create_tokens(user.id, db)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user_id": str(user.id)
    }


@router.post("/login/json", response_model=AuthResponse)
async def login_json(
    json_data: LoginForm,
    db: Session = Depends(get_db)
):
    """
    Authenticate admin user with username and password using JSON.
    Returns JWT tokens for API access.
    """
    # Get credentials from JSON data
    username = json_data.username
    password = json_data.password
    
    # Optional debug logging - only for development/testing
    if settings.DEBUG:
        import logging
        logging.debug(f"Login attempt for username: {username}")
        
        # Check if the admin credentials exist in the database for debugging
        admin_user = db.query(User).filter(User.username == username, User.is_admin == True).first()
        if admin_user and settings.DEBUG:
            logging.debug(f"Admin user found in database with ID: {admin_user.id}")
            admin_creds = db.query(AdminCredentials).filter(AdminCredentials.user_id == admin_user.id).first()
            if admin_creds:
                logging.debug("Admin credentials found in database")
            else:
                logging.debug("Admin user exists but no credentials record found")
        elif settings.DEBUG:
            logging.debug(f"Admin user '{username}' not found in database")
    
    # Authenticate user
    user = authenticate_admin(db, username, password)
    if not user:
        logging.error("Authentication failed for admin user")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create new tokens
    access_token, refresh_token = create_tokens(user.id, db)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user_id": str(user.id)
    }

@router.options("/login/json")
async def options_login_json():
    """
    Handle preflight CORS requests for login/json endpoint.
    This is especially important for GitHub Codespaces.
    """
    return {
        "status": "ok"
    }

@router.options("/login")
async def options_login():
    """
    Handle preflight CORS requests for login endpoint.
    This is especially important for GitHub Codespaces.
    """
    return {
        "status": "ok"
    }

@router.post("/login/direct", response_model=AuthResponse)
async def login_direct(
    username: str = Body(...),
    password: str = Body(...),
    db: Session = Depends(get_db)
):
    """
    Direct authentication endpoint that doesn't require preflight CORS.
    This is a simplified endpoint for environments with CORS issues.
    """
    # Authenticate user
    user = authenticate_admin(db, username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    # Create new tokens
    access_token, refresh_token = create_tokens(user.id, db)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user_id": str(user.id)
    }


@router.post("/player/login", response_model=AuthResponse)
async def player_login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Authenticate player user with username and password using form data.
    Returns JWT tokens for API access.
    """
    # Get credentials from form data
    username = form_data.username
    password = form_data.password

    # Authenticate user
    user = authenticate_player(db, username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create new tokens
    access_token, refresh_token = create_tokens(user.id, db)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user_id": str(user.id)
    }


@router.post("/player/login/json", response_model=AuthResponse)
async def player_login_json(
    json_data: LoginForm,
    db: Session = Depends(get_db)
):
    """
    Authenticate player user with username and password using JSON.
    Returns JWT tokens for API access.
    """
    # Get credentials from JSON data
    username = json_data.username
    password = json_data.password

    # Authenticate user
    user = authenticate_player(db, username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create new tokens
    access_token, refresh_token = create_tokens(user.id, db)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user_id": str(user.id)
    }

@router.options("/player/login/json")
async def options_player_login_json():
    """
    Handle preflight CORS requests for player login/json endpoint.
    This is especially important for GitHub Codespaces.
    """
    return {
        "status": "ok"
    }

@router.options("/player/login")
async def options_player_login():
    """
    Handle preflight CORS requests for player login endpoint.
    This is especially important for GitHub Codespaces.
    """
    return {
        "status": "ok"
    }

@router.post("/register", response_model=dict)
async def register_user(
    username: str = Body(...),
    email: str = Body(...),
    password: str = Body(...),
    db: Session = Depends(get_db)
):
    """
    Register a new user with username, email, and password.
    """
    # Check if username or email already exists
    existing_user = db.query(User).filter(
        (User.username == username) | (User.email == email),
        User.deleted == False
    ).first()

    if existing_user:
        if existing_user.username == username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )

    # Create new user
    from src.core.security import get_password_hash

    new_user = User(
        username=username,
        email=email,
        hashed_password=get_password_hash(password),
        is_active=True,
        is_admin=False
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "id": str(new_user.id),
        "username": new_user.username,
        "email": new_user.email,
        "is_active": new_user.is_active,
        "is_admin": new_user.is_admin
    }


@router.post("/refresh", response_model=AuthResponse)
async def refresh_token(
    token_data: RefreshTokenSchema,
    db: Session = Depends(get_db)
):
    """
    Get a new access token using a refresh token.
    Implements refresh token rotation for security.
    """
    refresh = db.query(RefreshToken).filter(
        RefreshToken.token == token_data.refresh_token, 
        RefreshToken.revoked == False
    ).first()
    
    if not refresh:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
    
    # Revoke the current refresh token (token rotation)
    refresh.revoked = True
    db.commit()
    
    # Create new tokens
    access_token, new_refresh_token = create_tokens(str(refresh.user_id), db)
    update_user_last_login(db, str(refresh.user_id))
    
    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
        "user_id": str(refresh.user_id)
    }


@router.post("/logout")
async def logout(
    token_data: RefreshTokenSchema,
    db: Session = Depends(get_db)
):
    """
    Revoke a refresh token, effectively logging the user out.
    """
    refresh = db.query(RefreshToken).filter(
        RefreshToken.token == token_data.refresh_token,
        RefreshToken.revoked == False
    ).first()

    if refresh:
        refresh.revoked = True
        db.commit()

    return {"detail": "Successfully logged out"}


@router.get("/me")
async def get_current_user_info(current_user = Depends(get_current_user)):
    """
    Get information about the currently authenticated user.
    """
    return {
        "id": str(current_user.id),
        "username": current_user.username,
        "email": current_user.email,
        "is_admin": current_user.is_admin,
        "is_active": current_user.is_active,
        "last_login": current_user.last_login
    }

@router.options("/me")
async def options_me():
    """
    Handle preflight CORS requests for the /me endpoint.
    This is especially important for GitHub Codespaces.
    """
    return {
        "status": "ok"
    }

@router.post("/me/token", response_model=dict)
async def get_user_by_token(
    token: str = Body(...),
    db: Session = Depends(get_db)
):
    """
    Alternative endpoint to get user info by providing the token directly in the request body.
    This avoids CORS preflight issues with the Authorization header.
    """
    try:
        # Decode token
        payload = decode_token(token)
        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )

        # Get user from database
        user = db.query(User).filter(User.id == user_id, User.deleted == False).first()

        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
            )

        # Return user info
        return {
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
            "is_admin": user.is_admin,
            "is_active": user.is_active,
            "last_login": user.last_login
        }
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate token",
        )


# OAuth endpoints
@router.get("/github")
async def login_github(request: Request, register: bool = False):
    """
    Redirect to GitHub OAuth login/registration page.
    """
    # Use the auto-detected API base URL
    api_base_url = settings.get_api_base_url()

    # For GitHub Codespaces, ALWAYS use the API_BASE_URL from settings
    # This ensures we use the proper public URL without any port numbers
    if settings.detect_environment() == "codespaces":
        # In Codespaces, we shouldn't rely on host headers - instead use the
        # configured API_BASE_URL that includes the Codespace name
        if api_base_url.endswith(settings.API_V1_STR):
            base = api_base_url
        else:
            base = f"{api_base_url}{settings.API_V1_STR}"

        # Debug information about what we're using
        host = request.headers.get("host", "")
        scheme = request.headers.get("x-forwarded-proto", "https")
        print(f"Codespaces detected. Original request host: {host}, scheme: {scheme}")
        print(f"Using configured API_BASE_URL instead: {api_base_url}")
        
        # Debug all request headers to help understand the tunneling mechanism
        print("All request headers:")
        for header_name, header_value in request.headers.items():
            print(f"  {header_name}: {header_value}")

        # Always use the API_BASE_URL setting for Codespaces
        redirect_uri = f"{base}/auth/github/callback?register={register}"
    else:
        # Standard environment handling
        if api_base_url.endswith(settings.API_V1_STR):
            base = api_base_url
        else:
            base = f"{api_base_url}{settings.API_V1_STR}"

        redirect_uri = f"{base}/auth/github/callback?register={register}"

    # Debug information
    print(f"GitHub OAuth redirect URI: {redirect_uri}")
    print(f"Environment detected: {settings.detect_environment()}")
    print(f"GitHub Client ID: {settings.GITHUB_CLIENT_ID}")
    print(f"Request host: {request.headers.get('host', '')}")
    print(f"X-Forwarded-Host: {request.headers.get('x-forwarded-host', 'Not set')}")
    print(f"X-Forwarded-Proto: {request.headers.get('x-forwarded-proto', 'Not set')}")
    print(f"Request method: {request.method}")
    print(f"Request URL: {request.url}")
    print(f"API Base URL: {settings.get_api_base_url()}")
    print(f"CODESPACE_NAME env: {os.environ.get('CODESPACE_NAME', 'Not set')}")

    authorization_url = GitHubOAuth.get_authorization_url(redirect_uri)
    return RedirectResponse(authorization_url)


@router.get("/github/callback")
async def github_callback(request: Request, code: str, register: bool = False, db: Session = Depends(get_db)):
    """
    Process GitHub OAuth callback.
    """
    # Use the auto-detected API base URL
    api_base_url = settings.get_api_base_url()

    # Get the actual request URL used to access this endpoint
    callback_url = str(request.url)

    # Detailed debug for the callback
    print(f"Raw callback URL received: {callback_url}")
    print(f"GitHub Codespaces detected: {settings.detect_environment() == 'codespaces'}")
    print(f"GitHub OAuth code received: {code}")

    # For Codespaces, use the same URL that was used in the initial request
    if settings.detect_environment() == "codespaces":
        # In Codespaces, we shouldn't rely on host headers - instead use the
        # configured API_BASE_URL that includes the Codespace name
        if api_base_url.endswith(settings.API_V1_STR):
            base = api_base_url
        else:
            base = f"{api_base_url}{settings.API_V1_STR}"

        # Debug information about what we're using
        host = request.headers.get("host", "")
        scheme = request.headers.get("x-forwarded-proto", "https")
        print(f"Codespaces callback. Original host header: {host}, scheme: {scheme}")
        print(f"Using configured API_BASE_URL instead: {api_base_url}")

        # Always use the API_BASE_URL setting for Codespaces
        redirect_uri = f"{base}/auth/github/callback?register={register}"
        print(f"Codespaces redirect_uri: {redirect_uri}")
    else:
        # Include the registration flag in the redirect URI
        # Remove any duplicate api prefix if present in the base_url
        if api_base_url.endswith(settings.API_V1_STR):
            base = api_base_url
        else:
            base = f"{api_base_url}{settings.API_V1_STR}"

        redirect_uri = f"{base}/auth/github/callback?register={register}"

    # Debug information
    print(f"GitHub OAuth callback URI: {redirect_uri}")

    try:
        # Exchange code for token and get user info
        token = await GitHubOAuth.exchange_code_for_token(code, redirect_uri)
        provider_user_id, user_data = await GitHubOAuth.get_user_info(token)

        # Get or create user
        user = await get_oauth_user(db, "github", provider_user_id)
        is_new_user = False

        if not user:
            user = await create_oauth_user(db, "github", provider_user_id, user_data)
            is_new_user = True

        # Create tokens and update last login
        access_token, refresh_token = create_tokens(str(user.id), db)
        update_user_last_login(db, str(user.id))

        # Get the frontend URL for the OAuth callback page
        frontend_url = f"{settings.FRONTEND_URL}/oauth-callback?access_token={access_token}&refresh_token={refresh_token}&user_id={user.id}&is_new_user={is_new_user}"

        # Debug information - more verbose
        print(f"==== OAuth Callback Debug ====")
        print(f"Redirecting to frontend URL: {frontend_url}")
        print(f"Is new user: {is_new_user}")
        print(f"Access token provided: {bool(access_token)}")
        print(f"Refresh token provided: {bool(refresh_token)}")
        print(f"User ID provided: {bool(user.id)}")
        print(f"Frontend URL from settings: {settings.FRONTEND_URL}")
        print(f"Codespace environment: {settings.detect_environment() == 'codespaces'}")
        print(f"============================")

        # Ensure our redirect is absolute
        if not frontend_url.startswith(('http://', 'https://')):
            print(f"WARNING: Frontend URL is not absolute: {frontend_url}")
            # Try to fix it
            if settings.detect_environment() == 'codespaces':
                # Extract codespace name
                import os
                codespace_name = os.environ.get('CODESPACE_NAME', '')
                if codespace_name:
                    frontend_url = f"https://{codespace_name}-3000.app.github.dev/oauth-callback?access_token={access_token}&refresh_token={refresh_token}&user_id={user.id}&is_new_user={is_new_user}"
                    print(f"Fixed frontend URL to: {frontend_url}")

        # Redirect to the frontend with the tokens
        print(f"Final redirect URL: {frontend_url}")
        return RedirectResponse(frontend_url)

    except Exception as e:
        # Log the full error for debugging
        import traceback
        error_details = traceback.format_exc()
        print(f"GitHub OAuth error: {str(e)}")
        print(f"Error details: {error_details}")

        # Return a user-friendly error page with debugging information
        error_html = f"""
<html>
    <head>
        <title>OAuth Error</title>
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
            .error {{ background: #ffeeee; border: 1px solid #ffaaaa; padding: 15px; border-radius: 5px; }}
            .debug {{ background: #eeeeff; border: 1px solid #aaaaff; padding: 15px; border-radius: 5px; margin-top: 20px; }}
            code {{ background: #f0f0f0; padding: 2px 5px; border-radius: 3px; }}
        </style>
    </head>
    <body>
        <h1>OAuth Authentication Error</h1>
        <div class="error">
            <h3>Error: {str(e)}</h3>
            <p>There was a problem authenticating with GitHub. Please try again or contact support.</p>
        </div>
        <div class="debug">
            <h3>Debug Information</h3>
            <ul>
                <li>Environment: {settings.detect_environment()}</li>
                <li>Callback URL: <code>{callback_url}</code></li>
                <li>Redirect URI: <code>{redirect_uri}</code></li>
                <li>Frontend URL: <code>{settings.FRONTEND_URL}</code></li>
                <li>Mock GitHub: <code>{"Yes" if settings.GITHUB_CLIENT_ID.startswith("mock_") else "No"}</code></li>
            </ul>
            <p>Try going back to the <a href="{settings.FRONTEND_URL}">login page</a> and trying again.</p>
        </div>
    </body>
</html>
"""
        return HTMLResponse(content=error_html, status_code=500)


@router.get("/google")
async def login_google(request: Request, register: bool = False):
    """
    Redirect to Google OAuth login/registration page.
    """
    # Use the auto-detected API base URL
    api_base_url = settings.get_api_base_url()

    # Pass the registration flag in the callback URL
    # Remove any duplicate api prefix if present in the base_url
    if api_base_url.endswith(settings.API_V1_STR):
        base = api_base_url
    else:
        base = f"{api_base_url}{settings.API_V1_STR}"

    redirect_uri = f"{base}/auth/google/callback?register={register}"

    # Debug information
    print(f"Google OAuth redirect URI: {redirect_uri}")

    authorization_url = GoogleOAuth.get_authorization_url(redirect_uri)
    return RedirectResponse(authorization_url)


@router.get("/google/callback")
async def google_callback(request: Request, code: str, register: bool = False, db: Session = Depends(get_db)):
    """
    Process Google OAuth callback.
    """
    # Use the auto-detected API base URL
    api_base_url = settings.get_api_base_url()

    # Include the registration flag in the redirect URI
    # Remove any duplicate api prefix if present in the base_url
    if api_base_url.endswith(settings.API_V1_STR):
        base = api_base_url
    else:
        base = f"{api_base_url}{settings.API_V1_STR}"

    redirect_uri = f"{base}/auth/google/callback?register={register}"

    # Debug information
    print(f"Google OAuth callback URI: {redirect_uri}")

    # Exchange code for tokens and get user info
    token_data = await GoogleOAuth.exchange_code_for_token(code, redirect_uri)
    provider_user_id, user_data = await GoogleOAuth.get_user_info(token_data)

    # Get or create user
    user = await get_oauth_user(db, "google", provider_user_id)
    is_new_user = False

    if not user:
        user = await create_oauth_user(db, "google", provider_user_id, user_data)
        is_new_user = True

    # Create tokens and update last login
    access_token, refresh_token = create_tokens(str(user.id), db)
    update_user_last_login(db, str(user.id))

    # Use auto-detected frontend URL
    frontend_url = f"{settings.FRONTEND_URL}/oauth-callback?access_token={access_token}&refresh_token={refresh_token}&user_id={user.id}&is_new_user={is_new_user}"

    # Debug information
    print(f"Redirecting to frontend URL: {frontend_url}")

    return RedirectResponse(frontend_url)


@router.get("/steam")
async def login_steam(request: Request, register: bool = False):
    """
    Redirect to Steam authentication page.
    """
    # Use the auto-detected API base URL
    api_base_url = settings.get_api_base_url()

    # Pass the registration flag in the callback URL
    # Remove any duplicate api prefix if present in the base_url
    if api_base_url.endswith(settings.API_V1_STR):
        base = api_base_url
    else:
        base = f"{api_base_url}{settings.API_V1_STR}"

    redirect_uri = f"{base}/auth/steam/callback?register={register}"

    # Debug information
    print(f"Steam OAuth redirect URI: {redirect_uri}")

    authorization_url = SteamAuth.get_authorization_url(redirect_uri)
    return RedirectResponse(authorization_url)


@router.get("/steam/callback")
async def steam_callback(request: Request, register: bool = False, db: Session = Depends(get_db)):
    """
    Process Steam authentication callback.
    """
    # Verify response and get Steam ID
    steam_id = await SteamAuth.verify_response(request)

    # Debug information
    print(f"Steam ID received: {steam_id}")

    # Get Steam user info
    user_data = await SteamAuth.get_user_info(steam_id)

    # Get or create user
    user = await get_oauth_user(db, "steam", steam_id)
    is_new_user = False

    if not user:
        user = await create_oauth_user(db, "steam", steam_id, user_data)
        is_new_user = True

    # Create tokens and update last login
    access_token, refresh_token = create_tokens(str(user.id), db)
    update_user_last_login(db, str(user.id))

    # Use auto-detected frontend URL
    frontend_url = f"{settings.FRONTEND_URL}/oauth-callback?access_token={access_token}&refresh_token={refresh_token}&user_id={user.id}&is_new_user={is_new_user}"

    # Debug information
    print(f"Redirecting to frontend URL: {frontend_url}")

    return RedirectResponse(frontend_url)