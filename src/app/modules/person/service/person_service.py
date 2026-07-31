from sqlalchemy.ext.asyncio import AsyncSession

from src.app.modules.person.dto.person_dto import PersonCreate, PersonUpdate
from src.app.modules.person.model.person_model import Person
from src.app.modules.person.repository.person_repository import PersonRepository
from src.app.modules.person.service.person_exceptions import (
    PersonDocumentAlreadyExistsError,
    PersonNotFoundError,
)


class PersonService:
    """Business logic for managing persons (identity data behind a user account)."""

    def __init__(self, session: AsyncSession) -> None:
        self.repository = PersonRepository(session)

    async def create_person(self, data: PersonCreate) -> Person:
        """Create a person. Flushes but does not commit — the caller controls the transaction."""
        existing = await self.repository.get_by_document(data.document_type_id, data.document_number)
        if existing is not None:
            raise PersonDocumentAlreadyExistsError(
                f"A person with document {data.document_number} already exists"
            )
        return await self.repository.create(data)

    async def get_person(self, person_id: int) -> Person:
        person = await self.repository.get_by_id(person_id)
        if person is None:
            raise PersonNotFoundError(f"Person with id {person_id} not found")
        return person

    async def update_person(self, person_id: int, data: PersonUpdate) -> Person:
        person = await self.get_person(person_id)
        return await self.repository.update(person, data)
