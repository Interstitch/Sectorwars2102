"""
Mock FastAPI application for testing.
This file provides a minimal FastAPI app that can be used for testing without
importing the real app which would trigger validation errors.
"""
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
from tests.mock_config import mock_settings

# Create a minimal FastAPI app for testing
mock_app = FastAPI(
    title="Sector Wars API Test Mock",
    description="Test mock for the Sector Wars 2102 game API",
    version="0.1.0",
)

# Root route for basic testing
@mock_app.get("/")
async def root():
    return {"message": "Welcome to the Sector Wars 2102 API (Test Mock)"}

# Health check route
@mock_app.get("/health")
async def health_check():
    return {"status": "ok", "environment": "test"}

# Authentication routes for testing
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class UserCredentials(BaseModel):
    username: str
    password: str

@mock_app.post("/api/auth/login/json", response_model=TokenResponse)
async def login(credentials: UserCredentials):
    if credentials.username == "testuser" and credentials.password == "password123":
        return {
            "access_token": "mock_access_token",
            "refresh_token": "mock_refresh_token",
            "token_type": "bearer"
        }
    raise HTTPException(status_code=401, detail="Incorrect username or password")
