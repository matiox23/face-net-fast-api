import enum

from sqlalchemy import BigInteger, Enum, ForeignKey, SmallInteger, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.app.common.model.base_model import Base


class ExamStatus(str, enum.Enum):
    """Lifecycle status of an exam."""

    DRAFT = "draft"
    PUBLISHED = "published"
    CLOSED = "closed"
    DELETED = "deleted"


class Exam(Base):
    """Exam created by a teacher."""

    __tablename__ = "exam"
    __table_args__ = {"schema": "academic"}

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    teacher_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("core.user.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    duration_minutes: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    status: Mapped[ExamStatus | None] = mapped_column(
        Enum(
            ExamStatus,
            name="exam_status",
            schema="academic",
            values_callable=lambda e: [m.value for m in e],
        ),
        nullable=True,
    )
