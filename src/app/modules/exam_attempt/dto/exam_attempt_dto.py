from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from src.app.modules.exam_attempt.model.exam_attempt_model import AttemptStatus
from src.app.modules.question.model.question_model import QuestionType


class ExamAttemptResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    exam_id: int
    student_id: int
    status: AttemptStatus | None
    started_at: datetime | None
    submitted_at: datetime | None
    score_obtained: Decimal | None


class AttemptOptionResponse(BaseModel):
    """An answer option as seen by the student taking the exam (no `is_correct`)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    text: str
    order: int | None


class AttemptQuestionResponse(BaseModel):
    """A question as seen by the student taking the exam."""

    id: int
    statement: str
    type: QuestionType | None
    score: Decimal | None
    order: int | None
    options: list[AttemptOptionResponse]


class AttemptQuestionListResponse(BaseModel):
    items: list[AttemptQuestionResponse]
    total: int
