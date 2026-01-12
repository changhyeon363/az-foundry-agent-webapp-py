"""Authentication routes."""

from datetime import timedelta

from fastapi import APIRouter, HTTPException, status

from app.config import get_settings
from app.core.security import authenticate_user, create_access_token
from app.models.auth import LoginRequest, LoginResponse

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest) -> LoginResponse:
    """
    Authenticate user and return JWT token.

    Credentials are validated against environment variables:
    - AUTH_USERNAME
    - AUTH_PASSWORD_HASH (bcrypt hashed)
    """
    if not authenticate_user(request.username, request.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    settings = get_settings()
    expires_delta = timedelta(minutes=settings.JWT_EXPIRATION_MINUTES)

    access_token = create_access_token(
        data={"sub": request.username},
        expires_delta=expires_delta,
    )

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.JWT_EXPIRATION_MINUTES * 60,  # Convert to seconds
    )
