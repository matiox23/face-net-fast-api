from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.app.common.database.dependencies.get_async_session import AsyncSessionDep
from src.app.modules.auth.dependency.auth_dependencies import CurrentUserDep, require_roles
from src.app.modules.person.service.person_exceptions import PersonDocumentAlreadyExistsError
from src.app.modules.user.dto.user_dto import (
    UserCreate,
    UserListResponse,
    UserResponse,
    UserStatusUpdate,
    UserUpdate,
)
from src.app.modules.user.service.user_exceptions import EmailAlreadyExistsError, UserNotFoundError
from src.app.modules.user.service.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


def _ensure_self_or_admin(user_id: int, current: CurrentUserDep) -> None:
    if user_id != current.user.id and "ADMIN" not in current.roles:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Insufficient permissions")


@router.post("", status_code=status.HTTP_201_CREATED)
async def register_user(data: UserCreate, session: AsyncSessionDep) -> UserResponse:
    try:
        return await UserService(session).register_user(data)
    except EmailAlreadyExistsError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, str(exc)) from exc
    except PersonDocumentAlreadyExistsError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, str(exc)) from exc


@router.get("/{user_id}")
async def get_user(user_id: int, session: AsyncSessionDep, current: CurrentUserDep) -> UserResponse:
    _ensure_self_or_admin(user_id, current)
    try:
        return await UserService(session).get_user(user_id)
    except UserNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc


@router.get("", dependencies=[Depends(require_roles("ADMIN"))])
async def list_users(
    session: AsyncSessionDep,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> UserListResponse:
    return await UserService(session).list_users(page, page_size)


@router.patch("/{user_id}")
async def update_user(
    user_id: int, data: UserUpdate, session: AsyncSessionDep, current: CurrentUserDep
) -> UserResponse:
    _ensure_self_or_admin(user_id, current)
    try:
        return await UserService(session).update_user(user_id, data)
    except UserNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc


@router.patch("/{user_id}/status", dependencies=[Depends(require_roles("ADMIN"))])
async def update_user_status(
    user_id: int, data: UserStatusUpdate, session: AsyncSessionDep
) -> UserResponse:
    try:
        return await UserService(session).update_status(user_id, data.status)
    except UserNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc
