from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.modules.answer_option.model.answer_option_model import AnswerOption


class AnswerOptionRepository:
    """Data access for the `academic.answer_option` table."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self, question_id: int, text: str, is_correct: bool | None, order: int | None
    ) -> AnswerOption:
        option = AnswerOption(
            question_id=question_id,
            text=text,
            is_correct=is_correct,
            order=order,
            is_deleted=False,
        )
        self.session.add(option)
        await self.session.flush()
        return option

    async def get_by_id(self, option_id: int) -> AnswerOption | None:
        option = await self.session.get(AnswerOption, option_id)
        if option is None or option.is_deleted:
            return None
        return option

    async def list_by_question(self, question_id: int) -> list[AnswerOption]:
        result = await self.session.execute(
            select(AnswerOption)
            .where(AnswerOption.question_id == question_id, AnswerOption.is_deleted.is_(False))
            .order_by(AnswerOption.order, AnswerOption.id)
        )
        return list(result.scalars().all())

    async def update(
        self,
        option: AnswerOption,
        text: str | None,
        is_correct: bool | None,
        order: int | None,
        fields_set: set[str],
    ) -> AnswerOption:
        if "text" in fields_set:
            option.text = text
        if "is_correct" in fields_set:
            option.is_correct = is_correct
        if "order" in fields_set:
            option.order = order
        await self.session.flush()
        return option

    async def soft_delete(self, option: AnswerOption) -> None:
        option.is_deleted = True
        await self.session.flush()
