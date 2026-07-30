import enum
from datetime import datetime
from decimal import Decimal

from sqlalchemy import BigInteger, DateTime, Enum, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from src.app.common.model.base_model import Base


class AttemptStatus(str, enum.Enum):
    """Lifecycle status of an exam attempt."""

    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    GRADED = "graded"


class ExamAttempt(Base):
    """A student's attempt at an exam."""

    __tablename__ = "exam_attempt"
    __table_args__ = {"schema": "academic"}

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    exam_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("academic.exam.id"), nullable=False)
    student_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("core.user.id"), nullable=False)
    status: Mapped[AttemptStatus | None] = mapped_column(
        Enum(AttemptStatus, name="attempt_status", schema="academic", values_callable=lambda e: [m.value for m in e]),
        nullable=True,
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    score_obtained: Mapped[Decimal | None] = mapped_column(Numeric(6, 2), nullable=True)
