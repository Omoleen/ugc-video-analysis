"""Comment generation service using Gemini AI."""

import asyncio
import logging

from google import genai

from app.config import settings
from app.prompts.comment_generation import get_comment_generation_prompt

logger = logging.getLogger(__name__)

# Initialize Gemini client
client = genai.Client(api_key=settings.gemini_api_key)


async def generate_engagement_comments(
    platform: str,
    post_url: str,
    video_summary: str | None = None,
    caption: str | None = None,
) -> str:
    """
    Generate engagement comments for approved content using text context.

    Args:
        platform: Target platform (instagram or tiktok)
        post_url: URL to the post
        video_summary: Summary of the video review
        caption: Optional caption from the post

    Returns:
        Generated engagement comments
    """
    prompt = get_comment_generation_prompt(
        video_summary=video_summary or "",
        platform=platform,
        post_url=post_url,
        caption=caption,
    )

    logger.info("Generating comments from summary")
    response = await asyncio.to_thread(
        client.models.generate_content,
        model=settings.gemini_model,
        contents=prompt,
    )

    return response.text
