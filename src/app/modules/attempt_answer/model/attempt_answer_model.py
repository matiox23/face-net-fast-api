from decimal import Decimal

from sqlalchemy import BigInteger, ForeignKey, Numeric, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.app.common.model.base_model import Base


class AttemptAnswer(Base):
    """Answer given to a question within an exam attempt."""

    __tablename__ = "attempt_answer"
    __table_args__ = (
        UniqueConstraint("attempt_id", "question_id", name="uq_answer"),
        {"schema": "academic"},
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    attempt_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("academic.exam_attempt.id"), nullable=False
    )
    question_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("academic.question.id"), nullable=False
    )
    option_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("academic.answer_option.id"), nullable=True
    )
    answer_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    score_obtained: Mapped[Decimal | None] = mapped_column(Numeric(6, 2), nullable=True)
