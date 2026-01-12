"""Azure AI Agent Service client."""

import asyncio
import base64
import logging
from collections.abc import AsyncGenerator
from dataclasses import dataclass
from typing import Any

from azure.ai.projects import AIProjectClient
from azure.identity import (
    AzureCliCredential,
    AzureDeveloperCliCredential,
    ChainedTokenCredential,
    ManagedIdentityCredential,
)

from app.config import get_settings
from app.models.agent import AgentMetadataResponse
from app.utils.image_validation import parse_data_uri, validate_image_data_uris

logger = logging.getLogger(__name__)


@dataclass
class UsageInfo:
    """Token usage information."""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class AzureAIAgentService:
    """Azure AI Foundry Agent Service client with streaming support."""

    def __init__(self) -> None:
        """Initialize the Azure AI Agent Service client."""
        settings = get_settings()

        self._agent_id = settings.AI_AGENT_ID
        self._endpoint = settings.AI_AGENT_ENDPOINT

        logger.info(
            "Initializing Azure AI Agent Service client for endpoint: %s, Agent ID: %s",
            self._endpoint,
            self._agent_id,
        )

        # Select credential based on environment
        if settings.is_development:
            logger.info(
                "Development environment: Using ChainedTokenCredential (AzureCli -> AzureDeveloperCli)"
            )
            credential = ChainedTokenCredential(
                AzureCliCredential(),
                AzureDeveloperCliCredential(),
            )
        else:
            logger.info(
                "Production environment: Using ManagedIdentityCredential (system-assigned)"
            )
            credential = ManagedIdentityCredential()

        # Create AI Project client
        self._client = AIProjectClient(
            endpoint=self._endpoint,
            credential=credential,
        )
        
        # Get OpenAI client for threads/messages/runs
        self._openai_client = self._client.get_openai_client()

        # Cached values
        self._agent: Any | None = None
        self._agent_metadata: AgentMetadataResponse | None = None
        self._last_usage: UsageInfo | None = None
        self._lock = asyncio.Lock()

        logger.info("Azure AI Agent Service client initialized successfully")

    async def preload_agent(self) -> None:
        """Pre-load the agent at startup for faster first request."""
        try:
            await self._get_agent()
            logger.info("Agent pre-loaded successfully at startup")
        except Exception as e:
            logger.error("Failed to pre-load agent at startup: %s", e)

    async def _get_agent(self) -> Any:
        """Get the agent, loading it if necessary."""
        if self._agent is not None:
            return self._agent

        async with self._lock:
            # Double-check after acquiring lock
            if self._agent is not None:
                return self._agent

            logger.info("Loading agent from Azure AI Agent Service: %s", self._agent_id)

            # Get the agent by name (sync call wrapped for async context)
            loop = asyncio.get_event_loop()
            agent_details = await loop.run_in_executor(
                None,
                lambda: self._client.agents.get(agent_name=self._agent_id),
            )
            
            # Extract the latest version agent from AgentDetails
            self._agent = agent_details.versions.latest
            
            logger.info("Successfully loaded agent: %s", self._agent_id)

            return self._agent

    async def get_agent_info(self) -> str:
        """Get agent info string for debugging."""
        agent = await self._get_agent()
        return str(agent) if agent else "AI Assistant"

    async def get_agent_metadata(self) -> AgentMetadataResponse:
        """
        Get agent metadata for display in UI.

        Cached after first call to avoid repeated API calls.
        """
        if self._agent_metadata is not None:
            logger.debug("Returning cached agent metadata")
            return self._agent_metadata

        agent = await self._get_agent()

        # Extract metadata from agent
        definition = getattr(agent, "definition", None)

        self._agent_metadata = AgentMetadataResponse(
            id=agent.id,
            object="agent",
            createdAt=int(agent.created_at.timestamp()),
            name=agent.name or "AI Assistant",
            description=agent.description,
            model=getattr(definition, "model", "") if definition else "",
            instructions=getattr(definition, "instructions", "") if definition else "",
            metadata=dict(agent.metadata) if agent.metadata else None,
        )

        logger.info("Cached agent metadata for future requests")
        return self._agent_metadata

    async def create_conversation(self, first_message: str | None = None) -> str:
        """
        Create a new conversation ID (Responses API doesn't use threads).

        Args:
            first_message: Optional first message to set as title

        Returns:
            Conversation ID (UUID)
        """
        import uuid
        
        conversation_id = str(uuid.uuid4())
        logger.info("Created conversation ID: %s", conversation_id)
        
        return conversation_id

    async def stream_message(
        self,
        conversation_id: str,
        message: str,
        image_data_uris: list[str] | None = None,
    ) -> AsyncGenerator[str, None]:
        """
        Stream agent response for a message using Responses API.

        Args:
            conversation_id: Conversation ID (not used in Responses API)
            message: User message
            image_data_uris: Optional list of base64 image data URIs

        Yields:
            Text chunks as they arrive
        """
        agent = await self._get_agent()

        logger.info(
            "Streaming response for conversation: %s, ImageCount: %d",
            conversation_id,
            len(image_data_uris) if image_data_uris else 0,
        )

        if not message or not message.strip():
            raise ValueError("Message cannot be null or whitespace")

        # Validate images
        validation_errors = validate_image_data_uris(image_data_uris)
        if validation_errors:
            logger.warning("Image validation failed: %s", "; ".join(validation_errors))
            raise ValueError(f"Invalid image attachments: {', '.join(validation_errors)}")

        # Build input message for Responses API
        if image_data_uris:
            # Multiple content parts (text + images) using Responses API format
            content_parts = [{"type": "input_text", "text": message}]
            
            for data_uri in image_data_uris:
                parsed = parse_data_uri(data_uri)
                if parsed:
                    media_type, image_bytes = parsed
                    # Responses API expects input_image with image_url as string (not object)
                    content_parts.append({
                        "type": "input_image",
                        "image_url": data_uri,  # Direct string, not {"url": ...}
                    })
            input_message = {"role": "user", "content": content_parts}
        else:
            # Simple text content
            input_message = {"role": "user", "content": message}

        loop = asyncio.get_event_loop()

        # Create streaming response using Responses API
        def create_stream():
            return self._openai_client.responses.create(
                input=[input_message],
                extra_body={
                    "agent": {
                        "name": agent.name,
                        "type": "agent_reference"
                    }
                },
                stream=True,
            )

        stream = await loop.run_in_executor(None, create_stream)

        try:
            # Process stream chunks
            for chunk in stream:
                # Check event type
                event_type = getattr(chunk, 'type', None)
                
                # Extract text from delta events
                if event_type == 'response.output_text.delta':
                    if hasattr(chunk, 'delta') and chunk.delta:
                        yield chunk.delta
                elif hasattr(chunk, 'delta') and chunk.delta:
                    # Fallback for other delta formats
                    yield chunk.delta
                    
                # Extract usage from completed event
                if event_type == 'response.completed':
                    if hasattr(chunk, 'response') and hasattr(chunk.response, 'usage'):
                        usage = chunk.response.usage
                        self._last_usage = UsageInfo(
                            prompt_tokens=getattr(usage, "input_tokens", 0),
                            completion_tokens=getattr(usage, "output_tokens", 0),
                            total_tokens=getattr(usage, "total_tokens", 0),
                        )
                        logger.info(
                            "Usage info - Input: %d, Output: %d, Total: %d",
                            self._last_usage.prompt_tokens,
                            self._last_usage.completion_tokens,
                            self._last_usage.total_tokens,
                        )
        finally:
            logger.info("Completed streaming response for conversation: %s", conversation_id)

    def get_last_usage(self) -> UsageInfo | None:
        """Get the usage info from the last streaming response."""
        return self._last_usage


# Singleton instance
_agent_service: AzureAIAgentService | None = None


def get_agent_service() -> AzureAIAgentService:
    """Get the singleton agent service instance."""
    global _agent_service
    if _agent_service is None:
        _agent_service = AzureAIAgentService()
    return _agent_service
