from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.app.common.model.base_model import Base


class Evidence(Base):
    """Proctoring evidence (camera, screenshot or audio) captured during an attempt."""

    __tablename__ = "evidence"
    __table_args__ = {"schema": "academic"}

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    attempt_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("academic.exam_attempt.id"), nullable=False
    )
    question_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("academic.question.id"), nullable=True
    )
    type: Mapped[str] = mapped_column(
        String(30), nullable=False, comment="CAMERA, SCREENSHOT, AUDIO"
    )
    reason: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="PERIODIC, TAB_CHANGE, FULLSCREEN_EXIT, CAMERA_BLOCKED, etc.",
    )
    file_url: Mapped[str] = mapped_column(String(500), nullable=False)
    captured_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
