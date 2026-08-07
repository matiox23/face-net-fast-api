from pydantic import BaseModel, ConfigDict, Field


class AnswerOptionCreate(BaseModel):
    text: str
    is_correct: bool | None = None
    order: int | None = None


class AnswerOptionUpdate(BaseModel):
    text: str | None = None
    is_correct: bool | None = None
    order: int | None = None


class AnswerOptionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    question_id: int
    text: str
    is_correct: bool | None
    order: int | None


class AnswerOptionListResponse(BaseModel):
    items: list[AnswerOptionResponse]
    total: int
