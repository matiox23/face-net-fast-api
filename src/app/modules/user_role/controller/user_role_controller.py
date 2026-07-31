from fastapi import APIRouter, Depends, HTTPException, status

from src.app.common.database.dependencies.get_async_session import AsyncSessionDep
from src.app.modules.auth.dependency.auth_dependencies import require_roles
from src.app.modules.user.service.user_exceptions import UserNotFoundError
from src.app.modules.user.service.user_service import UserService
from src.app.modules.user_role.dto.user_role_dto import (
    RoleAssignRequest,
    UserRolesResponse,
)
from src.app.modules.user_role.service.user_role_exceptions import (
    RoleAlreadyAssignedError,
    RoleNotAssignedError,
)
from src.app.modules.user_role.service.user_role_service import UserRoleService

router = APIRouter(
    prefix="/users/{user_id}/roles",
    tags=["user-roles"],
    dependencies=[Depends(require_roles("ADMIN"))],
)


async def _ensure_user_exists(user_id: int, session: AsyncSessionDep) -> None:
    try:
        await UserService(session).ensure_exists(user_id)
    except UserNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc


@router.get("")
async def list_user_roles(user_id: int, session: AsyncSessionDep) -> UserRolesResponse:
    await _ensure_user_exists(user_id, session)
    roles = await UserRoleService(session).list_role_codes(user_id)
    return UserRolesResponse(user_id=user_id, roles=roles)


@router.post("", status_code=status.HTTP_201_CREATED)
async def assign_user_role(
    user_id: int, data: RoleAssignRequest, session: AsyncSessionDep
) -> UserRolesResponse:
    await _ensure_user_exists(user_id, session)
    service = UserRoleService(session)
    try:
        await service.assign_role(user_id, data.role_code)
        await session.commit()
    except RoleAlreadyAssignedError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, str(exc)) from exc
    roles = await service.list_role_codes(user_id)
    return UserRolesResponse(user_id=user_id, roles=roles)


@router.delete("/{role_code}")
async def revoke_user_role(
    user_id: int, role_code: str, session: AsyncSessionDep
) -> UserRolesResponse:
    await _ensure_user_exists(user_id, session)
    service = UserRoleService(session)
    try:
        await service.revoke_role(user_id, role_code)
        await session.commit()
    except RoleNotAssignedError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc
    roles = await service.list_role_codes(user_id)
    return UserRolesResponse(user_id=user_id, roles=roles)
