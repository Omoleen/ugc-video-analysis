"""Slack Bolt application setup."""

from slack_bolt.adapter.fastapi.async_handler import AsyncSlackRequestHandler
from slack_bolt.async_app import AsyncApp

from app.config import settings

# Initialize the Slack Bolt app
slack_app = AsyncApp(
    token=settings.slack_bot_token,
    signing_secret=settings.slack_signing_secret,
)

# Create the handler for FastAPI integration
slack_handler = AsyncSlackRequestHandler(slack_app)
