from sqlalchemy.ext.asyncio import AsyncSession

from src.app.modules.role.model.role_model import Role
from src.app.modules.role.repository.role_repository import RoleRepository
from src.app.modules.role.service.role_exceptions import RoleNotFoundError


class RoleService:
    """Business logic for reading roles (roles are fixed, seeded via migration)."""

    def __init__(self, session: AsyncSession) -> None:
        self.repository = RoleRepository(session)

    async def get_by_code(self, code: str) -> Role:
        role = await self.repository.get_by_code(code)
        if role is None:
            raise RoleNotFoundError(f"Role with code '{code}' not found")
        return role

    async def get_by_id(self, role_id: int) -> Role:
        role = await self.repository.get_by_id(role_id)
        if role is None:
            raise RoleNotFoundError(f"Role with id {role_id} not found")
        return role
