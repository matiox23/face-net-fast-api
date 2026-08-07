from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class AnswerSubmit(BaseModel):
    option_id: int | None = None
    answer_text: str | None = None


class AttemptAnswerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    attempt_id: int
    question_id: int
    option_id: int | None
    answer_text: str | None
    score_obtained: Decimal | None


class AttemptAnswerListResponse(BaseModel):
    items: list[AttemptAnswerResponse]
    total: int
