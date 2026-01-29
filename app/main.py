"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request

from app.core import slack_handler, init_db

# Import handler to register event listener
from app.handlers import message_handler  # noqa: F401

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events."""
    # Startup
    await init_db()
    logger.info("Database initialized")
    yield
    # Shutdown
    logger.info("Shutting down")


api = FastAPI(
    title="UGC Video Analysis",
    description="Slack-integrated UGC video review system using Gemini AI",
    version="0.1.0",
    lifespan=lifespan,
)


@api.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@api.post("/slack/events")
async def slack_events(request: Request):
    """Handle Slack events."""
    logger.info(f"Received Slack request from {request.client}")
    return await slack_handler.handle(request)
