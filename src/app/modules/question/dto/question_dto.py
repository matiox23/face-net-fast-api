from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from src.app.modules.question.model.question_model import QuestionType


class QuestionCreate(BaseModel):
    statement: str
    type: QuestionType | None = None
    score: Decimal | None = Field(default=None, gt=0)
    order: int | None = None


class QuestionUpdate(BaseModel):
    statement: str | None = None
    type: QuestionType | None = None
    score: Decimal | None = Field(default=None, gt=0)
    order: int | None = None


class QuestionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    exam_id: int
    statement: str
    type: QuestionType | None
    score: Decimal | None
    order: int | None


class QuestionListResponse(BaseModel):
    items: list[QuestionResponse]
    total: int
