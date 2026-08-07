import enum
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    Boolean,
    Enum,
    ForeignKey,
    Numeric,
    SmallInteger,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from src.app.common.model.base_model import Base


class QuestionType(str, enum.Enum):
    """Kind of answer a question expects."""

    SINGLE_CHOICE = "single_choice"
    OPEN_ENDED = "open_ended"


class Question(Base):
    """Question belonging to an exam."""

    __tablename__ = "question"
    __table_args__ = (
        UniqueConstraint("exam_id", "order", name="uq_question_order"),
        {"schema": "academic"},
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    exam_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("academic.exam.id"), nullable=False)
    statement: Mapped[str] = mapped_column(Text, nullable=False)
    type: Mapped[QuestionType | None] = mapped_column(
        Enum(QuestionType, name="question_type", schema="academic", values_callable=lambda e: [m.value for m in e]),
        nullable=True,
    )
    score: Mapped[Decimal | None] = mapped_column(Numeric(6, 2), nullable=True)
    order: Mapped[int | None] = mapped_column("order", SmallInteger, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
