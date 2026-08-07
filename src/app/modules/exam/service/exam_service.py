from sqlalchemy.ext.asyncio import AsyncSession

from src.app.modules.exam.dto.exam_dto import (
    ExamCreate,
    ExamListResponse,
    ExamResponse,
    ExamUpdate,
)
from src.app.modules.exam.model.exam_model import Exam, ExamStatus
from src.app.modules.exam.repository.exam_repository import ExamRepository
from src.app.modules.exam.service.exam_exceptions import ExamNotFoundError


class ExamService:
    """Business logic for managing exams."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = ExamRepository(session)

    async def create_exam(self, teacher_id: int, data: ExamCreate) -> ExamResponse:
        exam = await self.repository.create(
            teacher_id=teacher_id,
            title=data.title,
            description=data.description,
            duration_minutes=data.duration_minutes,
        )
        await self.session.commit()
        return ExamResponse.model_validate(exam)

    async def get_exam(self, exam_id: int) -> ExamResponse:
        exam = await self._get_exam_or_raise(exam_id)
        return ExamResponse.model_validate(exam)

    async def get_exam_entity(self, exam_id: int) -> Exam:
        """Return the raw ORM exam. For use by other modules that need `teacher_id`."""
        return await self._get_exam_or_raise(exam_id)

    async def list_exams(
        self, page: int, page_size: int, teacher_id: int | None
    ) -> ExamListResponse:
        exams, total = await self.repository.list_paginated(page, page_size, teacher_id)
        items = [ExamResponse.model_validate(exam) for exam in exams]
        return ExamListResponse(items=items, total=total, page=page, page_size=page_size)

    async def update_exam(self, exam_id: int, data: ExamUpdate) -> ExamResponse:
        exam = await self._get_exam_or_raise(exam_id)
        exam = await self.repository.update(
            exam,
            title=data.title,
            description=data.description,
            duration_minutes=data.duration_minutes,
            fields_set=data.model_fields_set,
        )
        await self.session.commit()
        return ExamResponse.model_validate(exam)

    async def update_status(self, exam_id: int, status: ExamStatus) -> ExamResponse:
        exam = await self._get_exam_or_raise(exam_id)
        exam = await self.repository.update_status(exam, status)
        await self.session.commit()
        return ExamResponse.model_validate(exam)

    async def delete_exam(self, exam_id: int) -> None:
        """Soft-delete: sets status to DELETED."""
        exam = await self._get_exam_or_raise(exam_id)
        await self.repository.update_status(exam, ExamStatus.DELETED)
        await self.session.commit()

    async def _get_exam_or_raise(self, exam_id: int) -> Exam:
        exam = await self.repository.get_by_id(exam_id)
        if exam is None:
            raise ExamNotFoundError(f"Exam with id {exam_id} not found")
        return exam
