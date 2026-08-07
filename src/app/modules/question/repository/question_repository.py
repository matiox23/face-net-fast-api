from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.modules.question.model.question_model import Question, QuestionType


class QuestionRepository:
    """Data access for the `academic.question` table."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        exam_id: int,
        statement: str,
        type: QuestionType | None,
        score: Decimal | None,
        order: int | None,
    ) -> Question:
        question = Question(
            exam_id=exam_id,
            statement=statement,
            type=type,
            score=score,
            order=order,
            is_deleted=False,
        )
        self.session.add(question)
        await self.session.flush()
        return question

    async def get_by_id(self, question_id: int) -> Question | None:
        question = await self.session.get(Question, question_id)
        if question is None or question.is_deleted:
            return None
        return question

    async def list_by_exam(self, exam_id: int) -> list[Question]:
        result = await self.session.execute(
            select(Question)
            .where(Question.exam_id == exam_id, Question.is_deleted.is_(False))
            .order_by(Question.order, Question.id)
        )
        return list(result.scalars().all())

    async def update(
        self,
        question: Question,
        statement: str | None,
        type: QuestionType | None,
        score: Decimal | None,
        order: int | None,
        fields_set: set[str],
    ) -> Question:
        if "statement" in fields_set:
            question.statement = statement
        if "type" in fields_set:
            question.type = type
        if "score" in fields_set:
            question.score = score
        if "order" in fields_set:
            question.order = order
        await self.session.flush()
        return question

    async def soft_delete(self, question: Question) -> None:
        question.is_deleted = True
        await self.session.flush()
