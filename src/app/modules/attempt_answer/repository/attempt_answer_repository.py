from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.modules.attempt_answer.model.attempt_answer_model import AttemptAnswer


class AttemptAnswerRepository:
    """Data access for the `academic.attempt_answer` table."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_attempt_and_question(
        self, attempt_id: int, question_id: int
    ) -> AttemptAnswer | None:
        result = await self.session.execute(
            select(AttemptAnswer).where(
                AttemptAnswer.attempt_id == attempt_id,
                AttemptAnswer.question_id == question_id,
            )
        )
        return result.scalar_one_or_none()

    async def upsert(
        self,
        attempt_id: int,
        question_id: int,
        option_id: int | None,
        answer_text: str | None,
    ) -> AttemptAnswer:
        answer = await self.get_by_attempt_and_question(attempt_id, question_id)
        if answer is None:
            answer = AttemptAnswer(
                attempt_id=attempt_id,
                question_id=question_id,
                option_id=option_id,
                answer_text=answer_text,
            )
            self.session.add(answer)
        else:
            answer.option_id = option_id
            answer.answer_text = answer_text
            answer.score_obtained = None
        await self.session.flush()
        return answer

    async def list_by_attempt(self, attempt_id: int) -> list[AttemptAnswer]:
        result = await self.session.execute(
            select(AttemptAnswer).where(AttemptAnswer.attempt_id == attempt_id)
        )
        return list(result.scalars().all())

    async def set_score(self, answer: AttemptAnswer, score: Decimal | None) -> AttemptAnswer:
        answer.score_obtained = score
        await self.session.flush()
        return answer
