from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.modules.answer_option.service.answer_option_service import AnswerOptionService
from src.app.modules.attempt_answer.service.attempt_answer_service import AttemptAnswerService
from src.app.modules.exam.model.exam_model import ExamStatus
from src.app.modules.exam.service.exam_service import ExamService
from src.app.modules.exam_attempt.dto.exam_attempt_dto import (
    AttemptOptionResponse,
    AttemptQuestionListResponse,
    AttemptQuestionResponse,
    ExamAttemptResponse,
)
from src.app.modules.exam_attempt.model.exam_attempt_model import AttemptStatus, ExamAttempt
from src.app.modules.exam_attempt.repository.exam_attempt_repository import ExamAttemptRepository
from src.app.modules.exam_attempt.service.exam_attempt_exceptions import (
    AttemptAlreadyExistsError,
    AttemptNotInProgressError,
    ExamAttemptNotFoundError,
    ExamNotPublishedError,
)
from src.app.modules.question.service.question_service import QuestionService


class ExamAttemptService:
    """Business logic for a student taking an exam."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = ExamAttemptRepository(session)
        self.exam_service = ExamService(session)
        self.question_service = QuestionService(session)
        self.answer_option_service = AnswerOptionService(session)
        self.attempt_answer_service = AttemptAnswerService(session)

    async def start_attempt(self, exam_id: int, student_id: int) -> ExamAttemptResponse:
        exam = await self.exam_service.get_exam_entity(exam_id)
        if exam.status != ExamStatus.PUBLISHED:
            raise ExamNotPublishedError("Exam is not open for attempts")

        existing = await self.repository.get_by_exam_and_student(exam_id, student_id)
        if existing is not None:
            raise AttemptAlreadyExistsError("Student already has an attempt for this exam")

        attempt = await self.repository.create(exam_id, student_id, datetime.now(timezone.utc))
        await self.session.commit()
        return ExamAttemptResponse.model_validate(attempt)

    async def get_attempt(self, attempt_id: int) -> ExamAttemptResponse:
        attempt = await self._get_attempt_or_raise(attempt_id)
        return ExamAttemptResponse.model_validate(attempt)

    async def get_attempt_entity(self, attempt_id: int) -> ExamAttempt:
        """Return the raw ORM attempt. For use by other modules (e.g. attempt_answer controller)."""
        return await self._get_attempt_or_raise(attempt_id)

    async def get_questions_for_attempt(self, exam_id: int) -> AttemptQuestionListResponse:
        questions = await self.question_service.list_questions(exam_id)
        items = []
        for question in questions.items:
            options = await self.answer_option_service.list_options(question.id)
            items.append(
                AttemptQuestionResponse(
                    id=question.id,
                    statement=question.statement,
                    type=question.type,
                    score=question.score,
                    order=question.order,
                    options=[
                        AttemptOptionResponse(id=o.id, text=o.text, order=o.order)
                        for o in options.items
                    ],
                )
            )
        return AttemptQuestionListResponse(items=items, total=len(items))

    async def submit_attempt(self, attempt_id: int) -> ExamAttemptResponse:
        attempt = await self._get_attempt_or_raise(attempt_id)
        if attempt.status != AttemptStatus.IN_PROGRESS:
            raise AttemptNotInProgressError("Attempt is not in progress")

        total_score = await self.attempt_answer_service.grade_attempt(attempt_id)
        attempt = await self.repository.mark_submitted(attempt, datetime.now(timezone.utc), total_score)
        await self.session.commit()
        return ExamAttemptResponse.model_validate(attempt)

    async def _get_attempt_or_raise(self, attempt_id: int) -> ExamAttempt:
        attempt = await self.repository.get_by_id(attempt_id)
        if attempt is None:
            raise ExamAttemptNotFoundError(f"Attempt with id {attempt_id} not found")
        return attempt
