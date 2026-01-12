"""Health check routes."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends

from app.dependencies import get_current_user

router = APIRouter()


@router.get("/health")
async def health_check(current_user: str = Depends(get_current_user)) -> dict:
    """
    Health check endpoint.

    Returns health status with authenticated user info.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "authenticated": True,
        "user": {"name": current_user},
    }
