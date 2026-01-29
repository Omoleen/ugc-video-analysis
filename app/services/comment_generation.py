"""Comment generation service using Gemini AI."""

import asyncio
import logging
from pathlib import Path

from google import genai
from google.genai import types

from app.config import settings
from app.prompts.comment_generation import get_comment_generation_prompt

logger = logging.getLogger(__name__)

# Initialize Gemini client
client = genai.Client(api_key=settings.gemini_api_key)


async def generate_engagement_comments(
    platform: str,
    post_url: str,
    video_path: str | None = None,
    video_summary: str | None = None,
    caption: str | None = None,
) -> str:
    """
    Generate engagement comments for approved content.

    If video_path is provided, the video will be uploaded to Gemini for
    context-aware comment generation. Otherwise falls back to video_summary.

    Args:
        platform: Target platform (instagram or tiktok)
        post_url: URL to the post
        video_path: Path to the video file (preferred)
        video_summary: Fallback summary if video not available
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

    # If we have the video, upload it to Gemini for better context
    if video_path and Path(video_path).exists():
        logger.info(f"Uploading video for comment generation: {video_path}")

        # Upload video to Gemini File API
        video_file = await asyncio.to_thread(
            client.files.upload,
            file=Path(video_path),
        )

        try:
            # Wait for video processing
            while video_file.state.name == "PROCESSING":
                await asyncio.sleep(1)
                video_file = await asyncio.to_thread(
                    client.files.get,
                    name=video_file.name,
                )

            if video_file.state.name == "FAILED":
                logger.error("Video processing failed, falling back to summary")
                response = await asyncio.to_thread(
                    client.models.generate_content,
                    model=settings.gemini_model,
                    contents=prompt,
                )
            else:
                # Generate with video context
                response = await asyncio.to_thread(
                    client.models.generate_content,
                    model=settings.gemini_model,
                    contents=[
                        types.Content(
                            role="user",
                            parts=[
                                types.Part.from_uri(
                                    file_uri=video_file.uri,
                                    mime_type=video_file.mime_type,
                                ),
                                types.Part.from_text(text=prompt),
                            ],
                        ),
                    ],
                )
                logger.info("Generated comments with video context")

        finally:
            # Clean up the uploaded file from Gemini
            try:
                await asyncio.to_thread(client.files.delete, name=video_file.name)
            except Exception as e:
                logger.warning(f"Failed to delete Gemini file: {e}")
    else:
        # Fallback to text-only generation
        logger.info("Generating comments from summary (no video)")
        response = await asyncio.to_thread(
            client.models.generate_content,
            model=settings.gemini_model,
            contents=prompt,
        )

    return response.text
