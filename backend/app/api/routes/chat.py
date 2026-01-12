"""Chat streaming routes."""

import json
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse

from app.config import get_settings
from app.core.errors import ErrorResponseFactory
from app.dependencies import get_current_user
from app.models.chat import ChatRequest
from app.services.azure_ai_agent import AzureAIAgentService, get_agent_service

logger = logging.getLogger(__name__)

router = APIRouter()


def format_sse_event(event_type: str, data: dict | None = None) -> str:
    """Format data as SSE event."""
    payload = {"type": event_type}
    if data:
        payload.update(data)
    return f"data: {json.dumps(payload)}\n\n"


async def chat_event_generator(
    request: ChatRequest,
    agent_service: AzureAIAgentService,
    current_user: str,
):
    """Generate SSE events for chat streaming."""
    settings = get_settings()

    try:
        # Create or use existing conversation
        conversation_id = request.conversationId
        if not conversation_id:
            conversation_id = await agent_service.create_conversation(request.message)

        # Send conversation ID event
        yield format_sse_event("conversationId", {"conversationId": conversation_id})

        start_time = datetime.now(timezone.utc)

        # Stream message response
        async for chunk in agent_service.stream_message(
            conversation_id=conversation_id,
            message=request.message,
            image_data_uris=request.imageDataUris,
        ):
            yield format_sse_event("chunk", {"content": chunk})

        # Calculate duration
        duration_ms = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000

        # Get usage info
        usage = agent_service.get_last_usage()
        if usage:
            yield format_sse_event("usage", {
                "duration": duration_ms,
                "promptTokens": usage.prompt_tokens,
                "completionTokens": usage.completion_tokens,
                "totalTokens": usage.total_tokens,
            })

        # Send done event
        yield format_sse_event("done")

    except ValueError as e:
        # Validation errors (image validation, empty message)
        error_msg = str(e)
        if "Invalid image attachments" in error_msg:
            logger.warning("Image validation error: %s", error_msg)
        yield format_sse_event("error", {"message": error_msg})

    except Exception as e:
        logger.exception("Error in chat stream: %s", e)
        error_response = ErrorResponseFactory.from_exception(
            e,
            status_code=500,
            is_development=settings.is_development,
        )
        yield format_sse_event("error", {
            "message": error_response.detail or error_response.title
        })


@router.post("/stream")
async def stream_chat(
    request: ChatRequest,
    current_user: str = Depends(get_current_user),
    agent_service: AzureAIAgentService = Depends(get_agent_service),
) -> StreamingResponse:
    """
    Stream chat response via Server-Sent Events.

    SSE Event Sequence:
    1. conversationId - New or existing conversation ID
    2. chunk (multiple) - Text content chunks
    3. usage - Token usage statistics
    4. done - Stream completion marker

    Or on error:
    - error - Error message
    """
    return StreamingResponse(
        chat_event_generator(request, agent_service, current_user),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        },
    )
