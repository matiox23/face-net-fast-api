from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.modules.user_role.model.user_role_model import UserRole


class UserRoleRepository:
    """Data access for the `core.user_role` association table."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, user_id: int, role_id: int) -> UserRole:
        user_role = UserRole(user_id=user_id, role_id=role_id)
        self.session.add(user_role)
        await self.session.flush()
        return user_role

    async def remove(self, user_id: int, role_id: int) -> None:
        await self.session.execute(
            delete(UserRole).where(UserRole.user_id == user_id, UserRole.role_id == role_id)
        )

    async def list_role_ids_by_user(self, user_id: int) -> list[int]:
        result = await self.session.execute(select(UserRole.role_id).where(UserRole.user_id == user_id))
        return list(result.scalars().all())

    async def exists(self, user_id: int, role_id: int) -> bool:
        result = await self.session.execute(
            select(UserRole).where(UserRole.user_id == user_id, UserRole.role_id == role_id)
        )
        return result.scalar_one_or_none() is not None
