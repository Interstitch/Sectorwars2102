"""
Test routes for use in e2e testing.
These endpoints should only be accessible in test/dev environments.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from uuid import uuid4

from src.core.database import get_db
from src.core.config import settings
from src.models.user import User
from src.models.admin_credentials import AdminCredentials
from src.core.security import get_password_hash

router = APIRouter()


class CreateAdminRequest(BaseModel):
    username: str
    password: str
    email: str


@router.get("/check-admin-exists")
async def check_admin_exists(
    username: str = Query(..., description="Username to check"),
    db: Session = Depends(get_db)
):
    """
    Check if an admin user with the given username exists.
    This endpoint is for testing purposes only.
    """
    if not settings.TESTING and not settings.DEVELOPMENT_MODE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint is only available in test environments"
        )
    
    user = db.query(User).filter(User.username == username, User.is_admin == True).first()
    return {"exists": user is not None}


@router.post("/create-admin", status_code=status.HTTP_201_CREATED)
async def create_admin(
    request: CreateAdminRequest,
    db: Session = Depends(get_db)
):
    """
    Create an admin user for testing purposes.
    This endpoint is for testing purposes only.
    """
    if not settings.TESTING and not settings.DEVELOPMENT_MODE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint is only available in test environments"
        )
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.username == request.username).first()
    if existing_user:
        return {"message": "User already exists", "user_id": str(existing_user.id)}
    
    # Create the user
    user = User(
        id=uuid4(),
        username=request.username,
        email=request.email,
        is_admin=True,
        is_active=True
    )
    db.add(user)
    db.flush()  # Flush to get the ID
    
    # Create admin credentials
    admin_creds = AdminCredentials(
        id=uuid4(),
        user_id=user.id,
        password_hash=get_password_hash(request.password)
    )
    db.add(admin_creds)
    
    # Commit the transaction
    db.commit()
    
    return {"message": "Admin user created successfully", "user_id": str(user.id)}
