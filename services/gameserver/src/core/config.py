import os
from typing import Optional
from pydantic import PostgresDsn, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Base
    API_BASE_URL: str = os.environ.get("API_BASE_URL", "")  # Empty string to auto-detect
    API_V1_STR: str = "/api"
    ENVIRONMENT: str = os.environ.get("ENVIRONMENT", "development")
    DEBUG: bool = os.environ.get("DEBUG", "True").lower() == "true"

    # Development Environment Type
    DEV_ENVIRONMENT: str = os.environ.get("DEV_ENVIRONMENT", "")  # local, replit, codespaces

    # Database
    DATABASE_URL: PostgresDsn
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
            return os.environ.get("FRONTEND_URL")

        # Auto-detect based on environment
        env_type = self.detect_environment()

        if env_type == "codespaces":
            # For Codespaces, construct URL from environment variables
            # Make sure we handle any path proxying that might be happening in GitHub Codespaces
            codespace_name = os.environ.get("CODESPACE_NAME")
            github_codespaces_port_forwarding_domain = os.environ.get("GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN")

            if codespace_name and github_codespaces_port_forwarding_domain:
                # Full domain format with official GitHub Codespaces domain
                # Include port in the hostname for Codespaces URLs
                return f"https://{codespace_name}-3000.{github_codespaces_port_forwarding_domain}"
            elif codespace_name:
                # Legacy/default format with port in the hostname
                return f"https://{codespace_name}-3000.app.github.dev"

        elif env_type == "replit":
            # For Replit, derive from the API URL but on port 3000
            # This assumes player-client is on port 3000
            repl_slug = os.environ.get("REPL_SLUG")
            repl_owner = os.environ.get("REPL_OWNER")
            if repl_slug and repl_owner:
                return f"https://{repl_slug}.{repl_owner}.repl.co:3000"

        # Default for local development
        return "http://localhost:3000"

    def get_db_url(self) -> str:
        """Get the appropriate database URL based on environment."""
        if self.ENVIRONMENT == "production" and self.DATABASE_URL_PROD:
            return str(self.DATABASE_URL_PROD)
        return str(self.DATABASE_URL)

    # Security
    JWT_SECRET: str = os.environ.get("JWT_SECRET", "dev-secret-key")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60  # 1 hour
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7     # 7 days
    SECURE_COOKIES: bool = os.environ.get("SECURE_COOKIES", "False").lower() == "true"

    # OAuth
    # For development purposes only - replace with real credentials in production
    # Check both old and new environment variable names for backward compatibility
    GITHUB_CLIENT_ID: str = os.environ.get("CLIENT_ID_GITHUB",
                        os.environ.get("GITHUB_CLIENT_ID", "mock_github_client_id"))
    GITHUB_CLIENT_SECRET: str = os.environ.get("CLIENT_SECRET_GITHUB",
                             os.environ.get("GITHUB_CLIENT_SECRET", "mock_github_client_secret"))

    GOOGLE_CLIENT_ID: str = os.environ.get("GOOGLE_CLIENT_ID", "mock_google_client_id")
    GOOGLE_CLIENT_SECRET: str = os.environ.get("GOOGLE_CLIENT_SECRET", "mock_google_client_secret")

    STEAM_API_KEY: str = os.environ.get("STEAM_API_KEY", "mock_steam_api_key")

    # Frontend URLs (with auto-detection)
    @property
    def FRONTEND_URL(self) -> str:
        return self.get_frontend_url()

    ADMIN_FRONTEND_URL: str = os.environ.get("ADMIN_FRONTEND_URL", "http://localhost:3001")

    # Admin User
    DEFAULT_ADMIN_USERNAME: str = os.environ.get("DEFAULT_ADMIN_USERNAME", "admin")
    DEFAULT_ADMIN_PASSWORD: str = os.environ.get("DEFAULT_ADMIN_PASSWORD", "admin")

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 100

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()