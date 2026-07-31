from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.modules.person.dto.person_dto import PersonCreate, PersonUpdate
from src.app.modules.person.model.person_model import Person


class PersonRepository:
    """Data access for the `core.person` table."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, data: PersonCreate) -> Person:
        person = Person(
            first_names=data.first_names,
            paternal_surname=data.paternal_surname,
            maternal_surname=data.maternal_surname,
            document_type_id=data.document_type_id,
            document_number=data.document_number,
            birth_date=data.birth_date,
            sex=data.sex,
            phone=data.phone,
        )
        self.session.add(person)
        await self.session.flush()
        return person

    async def get_by_id(self, person_id: int) -> Person | None:
        return await self.session.get(Person, person_id)

    async def get_by_document(self, document_type_id: int, document_number: str) -> Person | None:
        result = await self.session.execute(
            select(Person).where(
                Person.document_type_id == document_type_id,
                Person.document_number == document_number,
            )
        )
        return result.scalar_one_or_none()

    async def update(self, person: Person, data: PersonUpdate) -> Person:
        updates = data.model_dump(exclude_unset=True)
        for field, value in updates.items():
            setattr(person, field, value)
        await self.session.flush()
        return person
