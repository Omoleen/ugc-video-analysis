"""PendingApproval model for video reviews awaiting social links."""

from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class PendingApproval(SQLModel, table=True):
    """Model for pending video approvals awaiting social media links."""

    __tablename__ = "pending_approvals"

    thread_ts: str = Field(primary_key=True)
    user_id: str
    channel: str
    score: int | None = None
    review_text: str
    virality_tier: str | None = None
    caption: str | None = None
    video_path: str | None = None  # Path to temporarily stored video for comment generation
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
