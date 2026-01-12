"""Agent models."""

from pydantic import BaseModel, Field


class AgentMetadataResponse(BaseModel):
    """Agent metadata response model."""

    id: str = Field(..., description="Agent ID")
    object: str = Field(default="agent", description="Object type")
    createdAt: int = Field(..., description="Creation timestamp (Unix)")
    name: str = Field(..., description="Agent name")
    description: str | None = Field(default=None, description="Agent description")
    model: str = Field(..., description="Model name")
    instructions: str | None = Field(default=None, description="System instructions")
    metadata: dict[str, str] | None = Field(default=None, description="Additional metadata")
