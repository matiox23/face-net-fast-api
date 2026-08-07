from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.modules.answer_option.service.answer_option_service import AnswerOptionService
from src.app.modules.attempt_answer.dto.attempt_answer_dto import (
    AnswerSubmit,
    AttemptAnswerListResponse,
    AttemptAnswerResponse,
)
from src.app.modules.attempt_answer.repository.attempt_answer_repository import (
    AttemptAnswerRepository,
)
from src.app.modules.attempt_answer.service.attempt_answer_exceptions import InvalidAnswerError
from src.app.modules.question.model.question_model import QuestionType
from src.app.modules.question.service.question_service import QuestionService


class AttemptAnswerService:
    """Business logic for submitting and grading answers within an exam attempt."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = AttemptAnswerRepository(session)
        self.question_service = QuestionService(session)
        self.answer_option_service = AnswerOptionService(session)

    async def submit_answer(
        self, attempt_id: int, question_id: int, data: AnswerSubmit
    ) -> AttemptAnswerResponse:
        question = await self.question_service.get_question_entity(question_id)

        if question.type == QuestionType.SINGLE_CHOICE:
            if data.option_id is None:
                raise InvalidAnswerError("This question requires an option_id")
            option = await self.answer_option_service.get_option_entity(data.option_id)
            if option.question_id != question_id:
                raise InvalidAnswerError("Option does not belong to this question")
            option_id = data.option_id
            answer_text = None
        else:
            if not data.answer_text:
                raise InvalidAnswerError("This question requires answer_text")
            option_id = None
            answer_text = data.answer_text

        answer = await self.repository.upsert(
            attempt_id=attempt_id,
            question_id=question_id,
            option_id=option_id,
            answer_text=answer_text,
        )
        await self.session.commit()
        return AttemptAnswerResponse.model_validate(answer)

    async def list_answers(self, attempt_id: int) -> AttemptAnswerListResponse:
        answers = await self.repository.list_by_attempt(attempt_id)
        items = [AttemptAnswerResponse.model_validate(answer) for answer in answers]
        return AttemptAnswerListResponse(items=items, total=len(items))

    async def grade_attempt(self, attempt_id: int) -> Decimal:
        """Auto-grade single_choice answers and return the total score. Commits per-answer scores."""
        total = Decimal(0)
        for answer in await self.repository.list_by_attempt(attempt_id):
            question = await self.question_service.get_question_entity(answer.question_id)
            if question.type != QuestionType.SINGLE_CHOICE or answer.option_id is None:
                continue
            option = await self.answer_option_service.get_option_entity(answer.option_id)
            score = (question.score or Decimal(0)) if option.is_correct else Decimal(0)
            await self.repository.set_score(answer, score)
            total += score
        return total
