from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.modules.role.model.role_model import Role


class RoleRepository:
    """Data access for the `core.role` table."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_code(self, code: str) -> Role | None:
        result = await self.session.execute(select(Role).where(Role.code == code))
        return result.scalar_one_or_none()

    async def get_by_id(self, role_id: int) -> Role | None:
        return await self.session.get(Role, role_id)
