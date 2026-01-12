"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import agent, auth, chat, health
from app.config import get_settings
from app.core.errors import ErrorResponseFactory
from app.services.azure_ai_agent import get_agent_service

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if get_settings().is_development else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting up Azure AI Agent Web App...")

    # Pre-load agent at startup
    try:
        agent_service = get_agent_service()
        await agent_service.preload_agent()
    except Exception as e:
        logger.error("Failed to preload agent: %s", e)

    yield

    # Shutdown
    logger.info("Shutting down Azure AI Agent Web App...")


# Create FastAPI application
app = FastAPI(
    title="Azure AI Agent Web App",
    description="Python FastAPI backend for Azure AI Foundry Agent",
    version="1.0.0",
    lifespan=lifespan,
)

# Get settings
settings = get_settings()

# Configure CORS
if settings.is_development:
    # Development: Allow any localhost origin
    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    logger.info("CORS configured for development (localhost)")
else:
    # Production: Only configured origins
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    logger.info("CORS configured for production: %s", settings.cors_origins)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle uncaught exceptions."""
    logger.exception("Unhandled exception: %s", exc)

    error_response = ErrorResponseFactory.from_exception(
        exc,
        status_code=500,
        is_development=settings.is_development,
    )

    return JSONResponse(
        status_code=error_response.status,
        content={
            "type": error_response.type,
            "title": error_response.title,
            "detail": error_response.detail,
            "status": error_response.status,
        },
    )


# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(agent.router, prefix="/api/agent", tags=["agent"])


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Azure AI Agent Web App API", "status": "running"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.is_development,
    )
