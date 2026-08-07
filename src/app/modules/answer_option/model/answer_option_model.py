from sqlalchemy import (
    BigInteger,
    Boolean,
    ForeignKey,
    SmallInteger,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from src.app.common.model.base_model import Base


class AnswerOption(Base):
    """Selectable option for a single-choice question."""

    __tablename__ = "answer_option"
    __table_args__ = (
        UniqueConstraint("question_id", "order", name="uq_option_order"),
        {"schema": "academic"},
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    question_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("academic.question.id"), nullable=False
    )
    text: Mapped[str] = mapped_column(Text, nullable=False)
    is_correct: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    order: Mapped[int | None] = mapped_column("order", SmallInteger, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
