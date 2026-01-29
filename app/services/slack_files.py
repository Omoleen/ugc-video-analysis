"""Slack file operations service."""

import logging
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

# Temp directory for video downloads (deleted after analysis)
TEMP_DIR = Path("/tmp/ugc_videos")
TEMP_DIR.mkdir(parents=True, exist_ok=True)

# Directory for approved videos awaiting comment generation (kept until links provided or 24h)
APPROVED_DIR = Path("/tmp/ugc_approved")
APPROVED_DIR.mkdir(parents=True, exist_ok=True)


async def download_file(url_private_download: str, file_id: str, filename: str) -> Path:
    """
    Download a file from Slack.

    Args:
        url_private_download: The private download URL from Slack
        file_id: The Slack file ID
        filename: Original filename

    Returns:
        Path to the downloaded file
    """
    # Create a unique filename to avoid collisions
    local_path = TEMP_DIR / f"{file_id}_{filename}"

    async with httpx.AsyncClient() as http_client:
        response = await http_client.get(
            url_private_download,
            headers={"Authorization": f"Bearer {settings.slack_bot_token}"},
            follow_redirects=True,
        )
        response.raise_for_status()

        # Write the file content
        local_path.write_bytes(response.content)

    return local_path


def cleanup_file(file_path: Path | str) -> None:
    """
    Remove a temporary file after processing.

    Args:
        file_path: Path to the file to remove
    """
    path = Path(file_path) if isinstance(file_path, str) else file_path
    if path.exists():
        os.remove(path)
        logger.info(f"Cleaned up file: {path}")


def move_to_approved(file_path: Path, thread_ts: str) -> Path:
    """
    Move a video to the approved directory for temporary storage.

    Args:
        file_path: Current path to the video file
        thread_ts: Thread timestamp (used as unique identifier)

    Returns:
        New path in the approved directory
    """
    # Use thread_ts in filename to ensure uniqueness and easy lookup
    suffix = file_path.suffix
    new_path = APPROVED_DIR / f"{thread_ts.replace('.', '_')}{suffix}"

    shutil.move(str(file_path), str(new_path))
    logger.info(f"Moved video to approved storage: {new_path}")

    return new_path


def cleanup_old_approved_videos(max_age_hours: int = 24) -> int:
    """
    Clean up approved videos older than max_age_hours.

    Args:
        max_age_hours: Maximum age in hours before deletion

    Returns:
        Number of files cleaned up
    """
    cleaned = 0
    now = datetime.now(timezone.utc)

    for file_path in APPROVED_DIR.iterdir():
        if file_path.is_file():
            # Get file modification time
            mtime = datetime.fromtimestamp(file_path.stat().st_mtime, tz=timezone.utc)
            age_hours = (now - mtime).total_seconds() / 3600

            if age_hours > max_age_hours:
                os.remove(file_path)
                logger.info(f"Cleaned up old approved video: {file_path} (age: {age_hours:.1f}h)")
                cleaned += 1

    return cleaned
