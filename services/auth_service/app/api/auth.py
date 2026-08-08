from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from services.auth_service.app.database import get_db
from services.auth_service.app.models import User
from services.auth_service.app.schemas import (
    UserRegisterRequest,
    UserLoginRequest,
    UserResponse,
    TokenResponse
)
from shared.auth import hash_password, verify_password, create_access_token, get_current_user_id
from shared.logging import get_logger

logger = get_logger("auth-service")
router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(payload: UserRegisterRequest, db: Session = Depends(get_db)):
    """
    Register a new user account.
    """
    # Check existing username
    stmt_username = select(User).where(User.username == payload.username)
    if db.scalar(stmt_username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username is already registered"
        )

    # Check existing email
    stmt_email = select(User).where(User.email == payload.email)
    if db.scalar(stmt_email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered"
        )

    # Hash password securely
    hashed_pwd = hash_password(payload.password)
    user = User(
        username=payload.username,
        email=payload.email,
        hashed_password=hashed_pwd
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    logger.info(f"Registered user: {user.username} (id: {user.id})")
    return user


@router.post("/login", response_model=TokenResponse)
def login_user(payload: UserLoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate user and return JWT access token.
    """
    stmt = select(User).where(User.username == payload.username)
    user = db.scalar(stmt)

    if not user or not verify_password(payload.password, user.hashed_password):
        logger.warning(f"Failed login attempt for username: {payload.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Generate JWT
    token_payload = {
        "sub": user.id,
        "username": user.username
    }
    access_token = create_access_token(data=token_payload)

    logger.info(f"User logged in successfully: {user.username}")
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=user.id,
        username=user.username
    )


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Fetch profile of currently authenticated user.
    """
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
