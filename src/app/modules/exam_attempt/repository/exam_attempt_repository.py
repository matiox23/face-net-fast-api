from datetime import datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.modules.exam_attempt.model.exam_attempt_model import AttemptStatus, ExamAttempt


class ExamAttemptRepository:
    """Data access for the `academic.exam_attempt` table."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, exam_id: int, student_id: int, started_at: datetime) -> ExamAttempt:
        attempt = ExamAttempt(
            exam_id=exam_id,
            student_id=student_id,
            status=AttemptStatus.IN_PROGRESS,
            started_at=started_at,
        )
        self.session.add(attempt)
        await self.session.flush()
        return attempt

    async def get_by_id(self, attempt_id: int) -> ExamAttempt | None:
        return await self.session.get(ExamAttempt, attempt_id)

    async def get_by_exam_and_student(self, exam_id: int, student_id: int) -> ExamAttempt | None:
        result = await self.session.execute(
            select(ExamAttempt).where(
                ExamAttempt.exam_id == exam_id, ExamAttempt.student_id == student_id
            )
        )
        return result.scalar_one_or_none()

    async def mark_submitted(
        self, attempt: ExamAttempt, submitted_at: datetime, score_obtained: Decimal
    ) -> ExamAttempt:
        attempt.status = AttemptStatus.SUBMITTED
        attempt.submitted_at = submitted_at
        attempt.score_obtained = score_obtained
        await self.session.flush()
        return attempt
