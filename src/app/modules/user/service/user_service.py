from sqlalchemy.ext.asyncio import AsyncSession

from src.app.common.security.password_hasher import hash_password
from src.app.modules.person.dto.person_dto import PersonCreate, PersonUpdate
from src.app.modules.person.service.person_service import PersonService
from src.app.modules.user.dto.user_dto import (
    UserCreate,
    UserListResponse,
    UserResponse,
    UserUpdate,
)
from src.app.modules.user.model.user_model import User, UserStatus
from src.app.modules.user.repository.user_repository import UserRepository
from src.app.modules.user.service.user_exceptions import (
    EmailAlreadyExistsError,
    UserNotFoundError,
)
from src.app.modules.user_role.service.user_role_service import UserRoleService

DEFAULT_ROLE_CODE = "STUDENT"


class UserService:
    """Business logic for managing user accounts."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = UserRepository(session)
        self.person_service = PersonService(session)
        self.user_role_service = UserRoleService(session)

    async def register_user(self, data: UserCreate) -> UserResponse:
        """Create a Person and a User (with a default role) in a single transaction."""
        async with self.session.begin():
            if await self.repository.get_by_email(data.email) is not None:
                raise EmailAlreadyExistsError(
                    f"Email '{data.email}' is already registered"
                )

            person = await self.person_service.create_person(
                PersonCreate(
                    first_names=data.first_names,
                    paternal_surname=data.paternal_surname,
                    maternal_surname=data.maternal_surname,
                    document_type_id=data.document_type_id,
                    document_number=data.document_number,
                    birth_date=data.birth_date,
                    sex=data.sex,
                    phone=data.phone,
                )
            )
            user = await self.repository.create(
                person_id=person.id,
                email=data.email,
                password_hash=hash_password(data.password),
                institutional_code=data.institutional_code,
            )
            await self.user_role_service.assign_role(user.id, DEFAULT_ROLE_CODE)

        return await self._to_response(user)

    async def get_user(self, user_id: int) -> UserResponse:
        user = await self._get_user_or_raise(user_id)
        return await self._to_response(user)

    async def list_users(self, page: int, page_size: int) -> UserListResponse:
        users, total = await self.repository.list_paginated(page, page_size)
        items = [await self._to_response(user) for user in users]
        return UserListResponse(
            items=items, total=total, page=page, page_size=page_size
        )

    async def update_user(self, user_id: int, data: UserUpdate) -> UserResponse:
        user = await self._get_user_or_raise(user_id)

        person_updates = data.model_dump(
            include={"first_names", "paternal_surname", "maternal_surname", "phone"},
            exclude_unset=True,
        )
        if person_updates:
            await self.person_service.update_person(
                user.person_id, PersonUpdate(**person_updates)
            )

        if "institutional_code" in data.model_fields_set:
            await self.repository.update_institutional_code(
                user, data.institutional_code
            )

        await self.session.commit()
        return await self._to_response(user)

    async def update_status(self, user_id: int, status: UserStatus) -> UserResponse:
        user = await self._get_user_or_raise(user_id)
        await self.repository.update_status(user, status)
        await self.session.commit()
        return await self._to_response(user)

    async def ensure_exists(self, user_id: int) -> None:
        """Raise UserNotFoundError if no user has this id. For callers that only need existence."""
        await self._get_user_or_raise(user_id)

    async def get_user_by_email_for_auth(self, email: str) -> User | None:
        """Return the raw ORM user (with password_hash) for auth_service only."""
        return await self.repository.get_by_email(email)

    async def get_user_by_id_for_auth(self, user_id: int) -> User | None:
        """Return the raw ORM user for auth_service only."""
        return await self.repository.get_by_id(user_id)

    async def _get_user_or_raise(self, user_id: int) -> User:
        user = await self.repository.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError(f"User with id {user_id} not found")
        return user

    async def _to_response(self, user: User) -> UserResponse:
        person = await self.person_service.get_person(user.person_id)
        roles = await self.user_role_service.list_role_codes(user.id)
        return UserResponse(
            id=user.id,
            email=user.email,
            institutional_code=user.institutional_code,
            status=user.status,
            registration_date=user.registration_date,
            person=person,
            roles=roles,
        )
