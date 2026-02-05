"""
Authentication routes
User registration, login, logout
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import get_db
from database.models import User
from security import AuthService, create_user_tokens, get_current_user
from security.audit_logger import AuditLogger

router = APIRouter(prefix="/auth")


# Pydantic models for request/response
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    phone: str = None
    language_preference: str = "en"


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    phone: str = None
    is_active: bool
    language_preference: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    user: UserResponse


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    Register a new user
    
    Creates a new user account and returns authentication tokens
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    new_user = User(
        email=user_data.email,
        hashed_password=AuthService.get_password_hash(user_data.password),
        full_name=user_data.full_name,
        phone=user_data.phone,
        language_preference=user_data.language_preference,
        is_active=True,
        is_verified=False  # Email verification can be added
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create tokens
    tokens = create_user_tokens(new_user)
    
    # Log registration
    AuditLogger.log_event(
        db=db,
        user_id=new_user.id,
        event_type="user_registration",
        action="create"
    )
    
    return {
        **tokens,
        "user": UserResponse.from_orm(new_user)
    }


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Login with email and password
    
    Returns access and refresh tokens
    """
    # Authenticate user
    user = AuthService.authenticate_user(db, form_data.username, form_data.password)
    
    if not user:
        # Log failed login attempt
        AuditLogger.log_login(
            db=db,
            user_id=None,
            ip_address="",
            user_agent="",
            success=False
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account"
        )
    
    # Create tokens
    tokens = create_user_tokens(user)
    
    # Log successful login
    AuditLogger.log_login(
        db=db,
        user_id=user.id,
        ip_address="",
        user_agent="",
        success=True
    )
    
    return {
        **tokens,
        "user": UserResponse.from_orm(user)
    }


@router.post("/refresh")
async def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token
    """
    try:
        payload = AuthService.decode_token(refresh_token)
        
        # Verify it's a refresh token
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        user_id = int(payload.get("sub"))
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Create new tokens
        tokens = create_user_tokens(user)
        
        return tokens
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current user information
    
    Requires authentication
    """
    return UserResponse.from_orm(current_user)


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Logout current user
    
    Note: In a stateless JWT system, actual token invalidation
    would require a token blacklist or short expiry times
    """
    # Log logout
    AuditLogger.log_logout(
        db=db,
        user_id=current_user.id,
        ip_address="",
        user_agent=""
    )
    
    return {"message": "Successfully logged out"}
