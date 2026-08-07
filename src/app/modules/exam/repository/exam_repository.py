from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.modules.exam.model.exam_model import Exam, ExamStatus


class ExamRepository:
    """Data access for the `academic.exam` table."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        teacher_id: int,
        title: str,
        description: str | None,
        duration_minutes: int | None,
    ) -> Exam:
        exam = Exam(
            teacher_id=teacher_id,
            title=title,
            description=description,
            duration_minutes=duration_minutes,
            status=ExamStatus.DRAFT,
        )
        self.session.add(exam)
        await self.session.flush()
        return exam

    async def get_by_id(self, exam_id: int) -> Exam | None:
        exam = await self.session.get(Exam, exam_id)
        if exam is None or exam.status == ExamStatus.DELETED:
            return None
        return exam

    async def list_paginated(
        self, page: int, page_size: int, teacher_id: int | None
    ) -> tuple[list[Exam], int]:
        query = select(Exam).where(Exam.status != ExamStatus.DELETED)
        count_query = select(func.count()).select_from(Exam).where(
            Exam.status != ExamStatus.DELETED
        )
        if teacher_id is not None:
            query = query.where(Exam.teacher_id == teacher_id)
            count_query = count_query.where(Exam.teacher_id == teacher_id)

        total = await self.session.scalar(count_query)
        result = await self.session.execute(
            query.order_by(Exam.id).offset((page - 1) * page_size).limit(page_size)
        )
        return list(result.scalars().all()), total or 0

    async def update(
        self,
        exam: Exam,
        title: str | None,
        description: str | None,
        duration_minutes: int | None,
        fields_set: set[str],
    ) -> Exam:
        if "title" in fields_set:
            exam.title = title
        if "description" in fields_set:
            exam.description = description
        if "duration_minutes" in fields_set:
            exam.duration_minutes = duration_minutes
        await self.session.flush()
        return exam

    async def update_status(self, exam: Exam, status: ExamStatus) -> Exam:
        exam.status = status
        await self.session.flush()
        return exam
