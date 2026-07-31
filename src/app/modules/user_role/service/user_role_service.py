from sqlalchemy.ext.asyncio import AsyncSession

from src.app.modules.role.service.role_service import RoleService
from src.app.modules.user_role.repository.user_role_repository import UserRoleRepository
from src.app.modules.user_role.service.user_role_exceptions import (
    RoleAlreadyAssignedError,
    RoleNotAssignedError,
)


class UserRoleService:
    """Business logic for assigning and revoking roles for a user."""

    def __init__(self, session: AsyncSession) -> None:
        self.repository = UserRoleRepository(session)
        self.role_service = RoleService(session)

    async def assign_role(self, user_id: int, role_code: str) -> None:
        role = await self.role_service.get_by_code(role_code)
        if await self.repository.exists(user_id, role.id):
            raise RoleAlreadyAssignedError(f"User {user_id} already has role '{role_code}'")
        await self.repository.add(user_id, role.id)

    async def revoke_role(self, user_id: int, role_code: str) -> None:
        role = await self.role_service.get_by_code(role_code)
        if not await self.repository.exists(user_id, role.id):
            raise RoleNotAssignedError(f"User {user_id} does not have role '{role_code}'")
        await self.repository.remove(user_id, role.id)

    async def list_role_codes(self, user_id: int) -> list[str]:
        role_ids = await self.repository.list_role_ids_by_user(user_id)
        roles = [await self.role_service.get_by_id(role_id) for role_id in role_ids]
        return [role.code for role in roles if role.code is not None]
