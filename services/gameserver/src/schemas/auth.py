from typing import Optional
from pydantic import BaseModel, Field


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: Optional[str] = None
    exp: Optional[int] = None
    type: Optional[str] = None


class LoginForm(BaseModel):
    username: str = Field(..., description="Admin username")
    password: str = Field(..., description="Admin password")
    mfa_code: Optional[str] = Field(None, description="MFA code (required if MFA is enabled)")


class RefreshToken(BaseModel):
    refresh_token: str = Field(..., description="Refresh token to get new access token")


class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user_id: str
    requires_mfa: Optional[bool] = False
    mfa_enabled: Optional[bool] = False