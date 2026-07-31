from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.modules.user.model.user_model import User, UserStatus


class UserRepository:
    """Data access for the `core.user` table."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        person_id: int,
        email: str,
        password_hash: str,
        institutional_code: str | None,
    ) -> User:
        user = User(
            person_id=person_id,
            email=email,
            password_hash=password_hash,
            institutional_code=institutional_code,
            status=UserStatus.ACTIVE,
        )
        self.session.add(user)
        await self.session.flush()
        return user

    async def get_by_id(self, user_id: int) -> User | None:
        return await self.session.get(User, user_id)

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def list_paginated(self, page: int, page_size: int) -> tuple[list[User], int]:
        total = await self.session.scalar(select(func.count()).select_from(User))
        result = await self.session.execute(
            select(User).order_by(User.id).offset((page - 1) * page_size).limit(page_size)
        )
        return list(result.scalars().all()), total or 0

    async def update_institutional_code(self, user: User, institutional_code: str | None) -> User:
        user.institutional_code = institutional_code
        await self.session.flush()
        return user

    async def update_status(self, user: User, status: UserStatus) -> User:
        user.status = status
        await self.session.flush()
        return user
