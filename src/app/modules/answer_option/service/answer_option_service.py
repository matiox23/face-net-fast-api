from sqlalchemy.ext.asyncio import AsyncSession

from src.app.modules.answer_option.dto.answer_option_dto import (
    AnswerOptionCreate,
    AnswerOptionListResponse,
    AnswerOptionResponse,
    AnswerOptionUpdate,
)
from src.app.modules.answer_option.model.answer_option_model import AnswerOption
from src.app.modules.answer_option.repository.answer_option_repository import (
    AnswerOptionRepository,
)
from src.app.modules.answer_option.service.answer_option_exceptions import (
    AnswerOptionNotFoundError,
)


class AnswerOptionService:
    """Business logic for managing answer options belonging to a question."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = AnswerOptionRepository(session)

    async def create_option(
        self, question_id: int, data: AnswerOptionCreate
    ) -> AnswerOptionResponse:
        option = await self.repository.create(
            question_id=question_id,
            text=data.text,
            is_correct=data.is_correct,
            order=data.order,
        )
        await self.session.commit()
        return AnswerOptionResponse.model_validate(option)

    async def get_option(self, option_id: int) -> AnswerOptionResponse:
        option = await self._get_option_or_raise(option_id)
        return AnswerOptionResponse.model_validate(option)

    async def get_option_entity(self, option_id: int) -> AnswerOption:
        """Return the raw ORM option. For use by controllers checking `question_id` ownership."""
        return await self._get_option_or_raise(option_id)

    async def list_options(self, question_id: int) -> AnswerOptionListResponse:
        options = await self.repository.list_by_question(question_id)
        items = [AnswerOptionResponse.model_validate(option) for option in options]
        return AnswerOptionListResponse(items=items, total=len(items))

    async def update_option(
        self, option_id: int, data: AnswerOptionUpdate
    ) -> AnswerOptionResponse:
        option = await self._get_option_or_raise(option_id)
        option = await self.repository.update(
            option,
            text=data.text,
            is_correct=data.is_correct,
            order=data.order,
            fields_set=data.model_fields_set,
        )
        await self.session.commit()
        return AnswerOptionResponse.model_validate(option)

    async def delete_option(self, option_id: int) -> None:
        option = await self._get_option_or_raise(option_id)
        await self.repository.soft_delete(option)
        await self.session.commit()

    async def _get_option_or_raise(self, option_id: int) -> AnswerOption:
        option = await self.repository.get_by_id(option_id)
        if option is None:
            raise AnswerOptionNotFoundError(f"Answer option with id {option_id} not found")
        return option
