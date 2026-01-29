"""Video analysis service using Gemini AI."""

import asyncio
from pathlib import Path

from google import genai
from google.genai import types

from app.config import settings
from app.models.video_review import VideoReview
from app.prompts.video_review import get_video_review_prompt

# Initialize Gemini client
client = genai.Client(api_key=settings.gemini_api_key)


async def analyze_video(video_path: Path, caption: str | None = None) -> VideoReview:
    """
    Analyze a video using Gemini's vision capabilities with structured output.

    Args:
        video_path: Path to the video file
        caption: Optional planned caption for the post

    Returns:
        VideoReview object with structured analysis results
    """
    # Upload the video file to Gemini
    video_file = await asyncio.to_thread(
        client.files.upload,
        file=video_path,
    )

    # Wait for video processing to complete
    while video_file.state == "PROCESSING":
        await asyncio.sleep(2)
        video_file = await asyncio.to_thread(
            client.files.get,
            name=video_file.name,
        )

    if video_file.state == "FAILED":
        raise RuntimeError(f"Video processing failed: {video_file.name}")

    # Get the appropriate prompt based on whether caption is provided
    prompt = get_video_review_prompt(caption)

    # Generate content with structured output
    response = await asyncio.to_thread(
        client.models.generate_content,
        model=settings.gemini_model,
        contents=[
            types.Content(
                parts=[
                    types.Part.from_uri(
                        file_uri=video_file.uri,
                        mime_type=video_file.mime_type,
                    ),
                    types.Part.from_text(text=prompt),
                ]
            )
        ],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=VideoReview,
        ),
    )

    # Clean up the uploaded file
    await asyncio.to_thread(
        client.files.delete,
        name=video_file.name,
    )

    # Parse and validate the structured response
    return VideoReview.model_validate_json(response.text)
