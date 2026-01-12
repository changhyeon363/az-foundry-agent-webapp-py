"""Agent metadata routes."""

import logging

from fastapi import APIRouter, Depends, HTTPException

from app.config import get_settings
from app.core.errors import ErrorResponseFactory
from app.dependencies import get_current_user
from app.models.agent import AgentMetadataResponse
from app.services.azure_ai_agent import AzureAIAgentService, get_agent_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("", response_model=AgentMetadataResponse)
async def get_agent_metadata(
    current_user: str = Depends(get_current_user),
    agent_service: AzureAIAgentService = Depends(get_agent_service),
) -> AgentMetadataResponse:
    """
    Get agent metadata.

    Returns agent information for display in the UI.
    """
    settings = get_settings()

    try:
        return await agent_service.get_agent_metadata()
    except Exception as e:
        logger.exception("Failed to get agent metadata: %s", e)
        error_response = ErrorResponseFactory.from_exception(
            e,
            status_code=500,
            is_development=settings.is_development,
        )
        raise HTTPException(
            status_code=error_response.status,
            detail=error_response.detail or error_response.title,
        )


@router.get("/info")
async def get_agent_info(
    current_user: str = Depends(get_current_user),
    agent_service: AzureAIAgentService = Depends(get_agent_service),
) -> dict:
    """
    Get agent info for debugging.

    Returns detailed agent information.
    """
    settings = get_settings()

    try:
        agent_info = await agent_service.get_agent_info()
        return {
            "info": agent_info,
            "status": "ready",
        }
    except Exception as e:
        logger.exception("Failed to get agent info: %s", e)
        error_response = ErrorResponseFactory.from_exception(
            e,
            status_code=500,
            is_development=settings.is_development,
        )
        raise HTTPException(
            status_code=error_response.status,
            detail=error_response.detail or error_response.title,
        )
