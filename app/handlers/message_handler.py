"""Unified handler for all message events."""

import logging
import re

from app.core.slack import slack_app
from app.config import settings
from app.services import (
    analyze_video,
    download_file,
    cleanup_file,
    generate_engagement_comments,
)
from app.repositories import ApprovalRepository
from app.utils import markdown_to_slack

logger = logging.getLogger(__name__)

# Patterns to detect Instagram and TikTok links
# Instagram URLs can be:
#   instagram.com/p/CODE/ (post)
#   instagram.com/reel/CODE/ (direct reel)
#   instagram.com/USERNAME/reel/CODE/ (user reel)
INSTAGRAM_PATTERN = re.compile(
    r"https?://(?:www\.)?instagram\.com/(?:[\w.-]+/)?(?:p|reel|reels)/[\w-]+/?",
    re.IGNORECASE,
)
TIKTOK_PATTERN = re.compile(
    r"https?://(?:www\.)?(?:tiktok\.com/@[\w.-]+/video/\d+|vm\.tiktok\.com/[\w]+/?)",
    re.IGNORECASE,
)


def _is_video_file(file_info: dict) -> bool:
    """Check if the file is a video based on mimetype."""
    mimetype = file_info.get("mimetype", "")
    return mimetype.startswith("video/")


def _extract_caption(event: dict) -> str | None:
    """Extract the caption from the message text."""
    text = event.get("text", "").strip()
    return text if text else None


def _extract_links(text: str) -> dict[str, str | None]:
    """Extract Instagram and TikTok links from text."""
    instagram_match = INSTAGRAM_PATTERN.search(text)
    tiktok_match = TIKTOK_PATTERN.search(text)

    return {
        "instagram": instagram_match.group(0) if instagram_match else None,
        "tiktok": tiktok_match.group(0) if tiktok_match else None,
    }


def _create_video_summary(review_text: str) -> str:
    """Create a brief summary from the review for comment generation."""
    # Just use the first part of the review as context
    return review_text[:1500] if review_text else ""


@slack_app.event("message")
async def handle_message(event: dict, say, client) -> None:
    """Handle all incoming messages - video uploads and thread replies."""
    # Ignore bot messages
    if event.get("bot_id") or event.get("subtype") == "bot_message":
        return

    # Check if message is in the video review channel
    channel = event.get("channel")
    if channel != settings.video_review_channel:
        return

    thread_ts = event.get("thread_ts")

    # Route to appropriate handler
    if thread_ts:
        await _handle_thread_reply(event, say, client, thread_ts)
    else:
        await _handle_video_upload(event, say, client)


async def _handle_video_upload(event: dict, say, client) -> None:
    """Handle video uploads in the main channel."""
    # Check for file attachments
    files = event.get("files", [])
    video_files = [f for f in files if _is_video_file(f)]

    if not video_files:
        return

    # Process the first video file
    video_file = video_files[0]
    user_id = event.get("user")
    message_ts = event.get("ts")
    channel = event.get("channel")

    # Extract caption from message text
    caption = _extract_caption(event)

    logger.info(
        f"Processing video from user {user_id}: {video_file.get('name')}"
        f"{' (with caption)' if caption else ''}"
    )

    # Send initial processing message
    processing_msg = "Analyzing your video"
    if caption:
        processing_msg += " and caption"
    processing_msg += "... This may take a moment."

    await say(text=processing_msg, thread_ts=message_ts)

    try:
        # Download the video
        local_path = await download_file(
            url_private_download=video_file["url_private_download"],
            file_id=video_file["id"],
            filename=video_file["name"],
        )

        # Analyze with Gemini - returns structured VideoReview object
        review = await analyze_video(local_path, caption)

        # Format and post the review in the thread
        formatted_review = review.to_slack_message()
        await say(
            text=f"*Video Analysis Complete*\n\n{formatted_review}",
            thread_ts=message_ts,
        )

        # Check if approved based on score threshold
        is_approved = review.overall_score >= settings.score_threshold

        if is_approved:
            # Clean up the video immediately after analysis
            cleanup_file(local_path)

            # Store for later link collection
            await ApprovalRepository.save(
                thread_ts=message_ts,
                user_id=user_id,
                channel=channel,
                score=review.overall_score,
                review_text=formatted_review,
                virality_tier=review.virality_tier,
                caption=caption,
            )

            await say(
                text=(
                    f"Congratulations! Your video scored *{review.overall_score}/100* "
                    f"(Virality Tier: *{review.virality_tier}*) and has been approved for promotion.\n\n"
                    "Please reply to this thread with your Instagram and/or TikTok post links "
                    "so we can generate engagement comments for your content."
                ),
                thread_ts=message_ts,
            )

            logger.info(
                f"Video approved with score {review.overall_score}. Awaiting links from user {user_id}"
            )
        else:
            # Not approved - clean up the video
            cleanup_file(local_path)
            logger.info(
                f"Video not approved. Score: {review.overall_score}, Threshold: {settings.score_threshold}"
            )

    except Exception as e:
        logger.exception(f"Error processing video: {e}")
        # Clean up temp video on error
        if "local_path" in locals():
            cleanup_file(local_path)
        await say(
            text=f"Sorry, there was an error analyzing your video: {str(e)}",
            thread_ts=message_ts,
        )


async def _handle_thread_reply(event: dict, say, client, thread_ts: str) -> None:
    """Handle thread replies looking for social media links."""
    logger.info(f"Thread reply received. thread_ts={thread_ts}, user={event.get('user')}")

    # Check if this thread has a pending approval
    pending = await ApprovalRepository.get_by_thread(thread_ts)
    if not pending:
        logger.info(f"No pending approval for thread {thread_ts}")
        return

    logger.info(f"Found pending approval. Expected user: {pending.user_id}, actual: {event.get('user')}")

    # Only accept links from the original poster
    if event.get("user") != pending.user_id:
        logger.info("User mismatch - ignoring")
        return

    # Extract links from the message
    message_text = event.get("text", "")
    logger.info(f"Message text: {message_text[:200]}")
    links = _extract_links(message_text)
    logger.info(f"Extracted links: {links}")

    if not links["instagram"] and not links["tiktok"]:
        logger.info("No social links found in message")
        return

    logger.info(f"Found social links in thread {thread_ts}: {links}")

    # Get review summary for comment generation
    video_summary = _create_video_summary(pending.review_text)
    caption = pending.caption
    comments_sections = []

    for platform, url in links.items():
        if url:
            try:
                await say(
                    text=f"Generating engagement comments for {platform.capitalize()}...",
                    thread_ts=thread_ts,
                )

                comments = await generate_engagement_comments(
                    platform=platform,
                    post_url=url,
                    video_summary=video_summary,
                    caption=caption,
                )
                formatted_comments = markdown_to_slack(comments)
                comments_sections.append(
                    f"*{platform.upper()} Comments*\n{url}\n\n{formatted_comments}"
                )
            except Exception as e:
                logger.exception(f"Error generating {platform} comments: {e}")
                comments_sections.append(
                    f"*{platform.upper()}*\nError generating comments: {str(e)}"
                )

    # Post to approved content channel
    score = pending.score
    virality_tier = pending.virality_tier
    user_id = pending.user_id

    # Build caption section if available
    caption_section = ""
    if caption:
        caption_section = f"\n*Caption:*\n```{caption}```\n"

    approved_message = (
        f"*New Approved UGC Content*\n\n"
        f"Creator: <@{user_id}>\n"
        f"Score: *{score}/100*\n"
        f"Virality Tier: *{virality_tier}*\n"
        f"{caption_section}\n"
        f"{'—' * 30}\n\n"
        + "\n\n".join(comments_sections)
    )

    try:
        await client.chat_postMessage(
            channel=settings.approved_content_channel,
            text=approved_message,
        )

        # Confirm to the creator
        await say(
            text=(
                "Your content has been posted to the approved content channel "
                "with engagement comments. Great work!"
            ),
            thread_ts=thread_ts,
        )

        # Remove from pending approvals
        await ApprovalRepository.delete(thread_ts)

        logger.info(
            f"Posted approved content for user {user_id} to channel "
            f"{settings.approved_content_channel}"
        )

    except Exception as e:
        logger.exception(f"Error posting to approved channel: {e}")
        await say(
            text=f"Error posting to approved channel: {str(e)}",
            thread_ts=thread_ts,
        )
