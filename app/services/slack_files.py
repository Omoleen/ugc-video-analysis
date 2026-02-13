"""Slack file operations service."""

import logging
import os
from pathlib import Path

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

# Temp directory for video downloads (deleted after analysis)
TEMP_DIR = Path("/tmp/ugc_videos")
TEMP_DIR.mkdir(parents=True, exist_ok=True)


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


