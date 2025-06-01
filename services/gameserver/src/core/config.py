import os
from typing import Optional
from pydantic import PostgresDsn, Field
from pydantic_settings import BaseSettings

# Note: DATABASE_URL validation will happen in the Settings class below
# which properly loads from .env files using Pydantic


class Settings(BaseSettings):
    # Base
    API_BASE_URL: str = os.environ.get("API_BASE_URL", "")  # Empty string to auto-detect
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = os.environ.get("ENVIRONMENT", "development")
    DEBUG: bool = os.environ.get("DEBUG", "True").lower() == "true"
    
    # Test and development mode flags
    TESTING: bool = os.environ.get("TESTING", "False").lower() == "true"
    DEVELOPMENT_MODE: bool = os.environ.get("ENVIRONMENT", "development").lower() == "development"
    
    JWT_SECRET: str = os.environ.get("JWT_SECRET", "your-secret-key")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))  # 24 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.environ.get("REFRESH_TOKEN_EXPIRE_DAYS", "30"))  # 30 days

    # Admin credentials
    ADMIN_USERNAME: str = os.environ.get("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD: str = os.environ.get("ADMIN_PASSWORD", "admin")  # Changed from "adminpassword"
    
    # AI Provider Configuration
    OPENAI_API_KEY: Optional[str] = os.environ.get("OPENAI_API_KEY")
    ANTHROPIC_API_KEY: Optional[str] = os.environ.get("ANTHROPIC_API_KEY")
    AI_PROVIDER_PRIMARY: str = os.environ.get("AI_PROVIDER_PRIMARY", "openai")
    AI_PROVIDER_SECONDARY: str = os.environ.get("AI_PROVIDER_SECONDARY", "anthropic")
    AI_PROVIDER_FALLBACK: str = os.environ.get("AI_PROVIDER_FALLBACK", "manual")
    
    # AI Model Configuration
    OPENAI_MODEL: str = os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo")
    ANTHROPIC_MODEL: str = os.environ.get("ANTHROPIC_MODEL", "claude-3-sonnet-20240229")
    AI_DIALOGUE_ENABLED: bool = os.environ.get("AI_DIALOGUE_ENABLED", "true").lower() == "true"

    # Development Environment Type
    DEV_ENVIRONMENT: str = os.environ.get("DEV_ENVIRONMENT", "")  # local, replit, codespaces
    NODE_ENV: Optional[str] = os.environ.get("NODE_ENV")
    FRONTEND_URL: Optional[str] = os.environ.get("FRONTEND_URL")
    CODESPACE_NAME: Optional[str] = os.environ.get("CODESPACE_NAME")
    CLIENT_ID_GITHUB: Optional[str] = os.environ.get("CLIENT_ID_GITHUB")
    CLIENT_SECRET_GITHUB: Optional[str] = os.environ.get("CLIENT_SECRET_GITHUB")
    
    # Important: GitHub OAuth variables must not start with GITHUB_ as GitHub reserves this prefix
    # for their own environment variables in GitHub Actions and Codespaces
    @property
    def GITHUB_CLIENT_ID(self) -> Optional[str]:
        """For backward compatibility. Please use CLIENT_ID_GITHUB instead."""
        return self.CLIENT_ID_GITHUB
        
    @property
    def GITHUB_CLIENT_SECRET(self) -> Optional[str]:
        """For backward compatibility. Please use CLIENT_SECRET_GITHUB instead."""
        return self.CLIENT_SECRET_GITHUB


    # Database
    DATABASE_URL: PostgresDsn = Field(
        description="PostgreSQL database URL"
    )
    DATABASE_TEST_URL: Optional[PostgresDsn] = Field(
        default=None,
        description="PostgreSQL test database URL (optional)"
    )
    DATABASE_URL_PROD: Optional[PostgresDsn] = None
    SQLALCHEMY_POOL_SIZE: int = 10
    SQLALCHEMY_MAX_OVERFLOW: int = 20

    def detect_environment(self) -> str:
        """Detect the development environment type."""
        # If explicitly set, use that
        if self.DEV_ENVIRONMENT:
            return self.DEV_ENVIRONMENT

        # Check for Replit
        if os.environ.get("REPL_ID") or os.environ.get("REPL_SLUG"):
            return "replit"

        # Check for GitHub Codespaces
        if os.environ.get("CODESPACE_NAME") or os.environ.get("GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN"):
            return "codespaces"

        # Default to local
        return "local"

    def get_api_base_url(self) -> str:
        """Get the appropriate API base URL based on environment."""
        # If explicitly set through environment variable, use that
        if self.API_BASE_URL:
            return self.API_BASE_URL

        # Auto-detect based on environment
        env_type = self.detect_environment()

        if env_type == "codespaces":
            # For Codespaces, construct URL from environment variables
            codespace_name = os.environ.get("CODESPACE_NAME")
            if codespace_name:
                # Include port in Codespaces URL as the port is embedded in the hostname
                return f"https://{codespace_name}-8080.app.github.dev"

        elif env_type == "replit":
            # For Replit, use REPL_SLUG if available
            repl_slug = os.environ.get("REPL_SLUG")
            repl_owner = os.environ.get("REPL_OWNER")
            if repl_slug and repl_owner:
                return f"https://{repl_slug}.{repl_owner}.repl.co"

        # Default for local development
        return "http://localhost:8080"

    def get_frontend_url(self) -> str:
        """Get the appropriate frontend URL based on environment."""
        # If explicitly set through FRONTEND_URL environment variable, use that
        if os.environ.get("FRONTEND_URL"):
            frontend_url = os.environ.get("FRONTEND_URL")
            print(f"Using explicitly set FRONTEND_URL from environment: {frontend_url}")
            return frontend_url

        # Auto-detect based on environment
        env_type = self.detect_environment()
        print(f"Auto-detecting frontend URL for environment: {env_type}")

        if env_type == "codespaces":
            # For Codespaces, construct URL from environment variables
            # Make sure we handle any path proxying that might be happening in GitHub Codespaces
            codespace_name = os.environ.get("CODESPACE_NAME")
            github_codespaces_port_forwarding_domain = os.environ.get("GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN")

            if codespace_name and github_codespaces_port_forwarding_domain:
                # Full domain format with official GitHub Codespaces domain
                # Include port in the hostname for Codespaces URLs
                frontend_url = f"https://{codespace_name}-3000.{github_codespaces_port_forwarding_domain}"
                print(f"Using modern Codespaces URL format: {frontend_url}")
                return frontend_url
            elif codespace_name:
                # Legacy/default format with port in the hostname
                frontend_url = f"https://{codespace_name}-3000.app.github.dev"
                print(f"Using legacy Codespaces URL format: {frontend_url}")
                return frontend_url
            else:
                print("WARNING: In Codespaces environment but CODESPACE_NAME not set!")

        elif env_type == "replit":
            # For Replit, derive from the API URL but on port 3000
            # This assumes player-client is on port 3000
            repl_slug = os.environ.get("REPL_SLUG")
            repl_owner = os.environ.get("REPL_OWNER")
            if repl_slug and repl_owner:
                frontend_url = f"https://{repl_slug}.{repl_owner}.repl.co:3000"
                print(f"Using Replit URL format: {frontend_url}")
                return frontend_url

        # Default for local development
        frontend_url = "http://localhost:3000"
        print(f"Using default frontend URL: {frontend_url}")
        return frontend_url

    def get_db_url(self) -> str:
        """Get the appropriate database URL based on environment."""
        # Ensure correct type casting for Pydantic DSNs
        if self.ENVIRONMENT == "testing" and self.DATABASE_TEST_URL:
            db_url = str(self.DATABASE_TEST_URL)
        elif self.ENVIRONMENT == "production" and self.DATABASE_URL_PROD:
            db_url = str(self.DATABASE_URL_PROD)
        else:
            db_url = str(self.DATABASE_URL)
        
        # Add endpoint parameter for Neon databases if not already present
        if "neon.tech" in db_url and "options=endpoint" not in db_url:
            # Extract the endpoint ID from the host
            import re
            match = re.search(r'@(ep-[a-z0-9-]+)', db_url)
            if match:
                endpoint_id = match.group(1)
                # Add or append to existing parameters
                if "?" in db_url:
                    db_url += f"&options=endpoint%3D{endpoint_id}"
                else:
                    db_url += f"?options=endpoint%3D{endpoint_id}"
        
        return db_url

    # Using model_config for newer Pydantic versions
    model_config = {
        "env_file": ["../../.env", ".env"],  # Look in parent directory first, then current
        "env_file_encoding": "utf-8",
        "extra": "ignore",  # Ignore extra fields from .env
    }

# Load .env file if DATABASE_URL not in environment
if not os.environ.get("DATABASE_URL"):
    import pathlib
    from dotenv import load_dotenv
    
    # Try to load from parent directory .env file
    env_path = pathlib.Path(__file__).parent.parent.parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)

# Create settings instance
settings = Settings()