from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from src.app.modules.exam.model.exam_model import ExamStatus


class ExamCreate(BaseModel):
    title: str = Field(max_length=200)
    description: str | None = None
    duration_minutes: int | None = Field(default=None, gt=0)


class ExamUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=200)
    description: str | None = None
    duration_minutes: int | None = Field(default=None, gt=0)


class ExamStatusUpdate(BaseModel):
    status: Literal[ExamStatus.DRAFT, ExamStatus.PUBLISHED, ExamStatus.CLOSED]


class ExamResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    teacher_id: int
    title: str
    description: str | None
    duration_minutes: int | None
    status: ExamStatus | None


class ExamListResponse(BaseModel):
    items: list[ExamResponse]
    total: int
    page: int
    page_size: int
