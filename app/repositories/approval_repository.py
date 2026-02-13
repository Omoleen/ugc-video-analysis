"""Repository for PendingApproval CRUD operations."""

import logging

from sqlmodel import select

from app.core.database import get_session
from app.models.pending_approval import PendingApproval

logger = logging.getLogger(__name__)


class ApprovalRepository:
    """Data access layer for pending approvals."""

    @staticmethod
    async def save(
        thread_ts: str,
        user_id: str,
        channel: str,
        score: int | None,
        review_text: str,
        virality_tier: str | None,
        caption: str | None,
    ) -> PendingApproval:
        """Save or update a pending approval."""
        async with await get_session() as session:
            existing = await session.get(PendingApproval, thread_ts)

            if existing:
                existing.user_id = user_id
                existing.channel = channel
                existing.score = score
                existing.review_text = review_text
                existing.virality_tier = virality_tier
                existing.caption = caption
                session.add(existing)
                approval = existing
            else:
                approval = PendingApproval(
                    thread_ts=thread_ts,
                    user_id=user_id,
                    channel=channel,
                    score=score,
                    review_text=review_text,
                    virality_tier=virality_tier,
                    caption=caption,
                )
                session.add(approval)

            await session.commit()
            await session.refresh(approval)
            logger.info(f"Saved pending approval for thread {thread_ts}")
            return approval

    @staticmethod
    async def get_by_thread(thread_ts: str) -> PendingApproval | None:
        """Get a pending approval by thread timestamp."""
        async with await get_session() as session:
            return await session.get(PendingApproval, thread_ts)

    @staticmethod
    async def delete(thread_ts: str) -> bool:
        """Delete a pending approval. Returns True if deleted."""
        async with await get_session() as session:
            approval = await session.get(PendingApproval, thread_ts)

            if approval:
                await session.delete(approval)
                await session.commit()
                logger.info(f"Deleted pending approval for thread {thread_ts}")
                return True
            return False

    @staticmethod
    async def get_all() -> list[PendingApproval]:
        """Get all pending approvals."""
        async with await get_session() as session:
            result = await session.exec(select(PendingApproval))
            return list(result.all())
