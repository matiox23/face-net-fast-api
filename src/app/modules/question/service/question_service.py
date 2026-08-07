from sqlalchemy.ext.asyncio import AsyncSession

from src.app.modules.question.dto.question_dto import (
    QuestionCreate,
    QuestionListResponse,
    QuestionResponse,
    QuestionUpdate,
)
from src.app.modules.question.model.question_model import Question
from src.app.modules.question.repository.question_repository import QuestionRepository
from src.app.modules.question.service.question_exceptions import QuestionNotFoundError


class QuestionService:
    """Business logic for managing questions belonging to an exam."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = QuestionRepository(session)

    async def create_question(self, exam_id: int, data: QuestionCreate) -> QuestionResponse:
        question = await self.repository.create(
            exam_id=exam_id,
            statement=data.statement,
            type=data.type,
            score=data.score,
            order=data.order,
        )
        await self.session.commit()
        return QuestionResponse.model_validate(question)

    async def get_question(self, question_id: int) -> QuestionResponse:
        question = await self._get_question_or_raise(question_id)
        return QuestionResponse.model_validate(question)

    async def get_question_entity(self, question_id: int) -> Question:
        """Return the raw ORM question. For use by other modules (e.g. answer_option)."""
        return await self._get_question_or_raise(question_id)

    async def list_questions(self, exam_id: int) -> QuestionListResponse:
        questions = await self.repository.list_by_exam(exam_id)
        items = [QuestionResponse.model_validate(question) for question in questions]
        return QuestionListResponse(items=items, total=len(items))

    async def update_question(self, question_id: int, data: QuestionUpdate) -> QuestionResponse:
        question = await self._get_question_or_raise(question_id)
        question = await self.repository.update(
            question,
            statement=data.statement,
            type=data.type,
            score=data.score,
            order=data.order,
            fields_set=data.model_fields_set,
        )
        await self.session.commit()
        return QuestionResponse.model_validate(question)

    async def delete_question(self, question_id: int) -> None:
        question = await self._get_question_or_raise(question_id)
        await self.repository.soft_delete(question)
        await self.session.commit()

    async def _get_question_or_raise(self, question_id: int) -> Question:
        question = await self.repository.get_by_id(question_id)
        if question is None:
            raise QuestionNotFoundError(f"Question with id {question_id} not found")
        return question
