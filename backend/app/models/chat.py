"""Chat models."""

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Chat request model."""

    message: str = Field(..., min_length=1, description="User message")
    conversationId: str | None = Field(
        default=None,
        description="Existing conversation ID (optional)",
    )
    imageDataUris: list[str] | None = Field(
        default=None,
        description="List of base64 encoded image data URIs (optional, max 5)",
    )
