from dataclasses import dataclass
from typing import Annotated, Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.app.common.database.dependencies.get_async_session import AsyncSessionDep
from src.app.common.security.jwt import ExpiredTokenError, InvalidTokenError, TokenType, decode_token
from src.app.modules.user.model.user_model import User, UserStatus
from src.app.modules.user.service.user_service import UserService

bearer_scheme = HTTPBearer(auto_error=False)


@dataclass
class AuthenticatedUser:
    """The authenticated user and the role codes carried by their access token."""

    user: User
    roles: list[str]


async def get_current_user(
    session: AsyncSessionDep,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> AuthenticatedUser:
    if credentials is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Missing bearer token")

    try:
        payload = decode_token(credentials.credentials, TokenType.ACCESS)
    except (ExpiredTokenError, InvalidTokenError) as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired token") from exc

    user = await UserService(session).get_user_by_id_for_auth(int(payload["sub"]))
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User not found")
    if user.status in (UserStatus.BLOCKED, UserStatus.INACTIVE):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "User account is not active")

    return AuthenticatedUser(user=user, roles=payload.get("roles", []))


CurrentUserDep = Annotated[AuthenticatedUser, Depends(get_current_user)]


def require_roles(*roles: str) -> Callable[[CurrentUserDep], AuthenticatedUser]:
    """Build a dependency that requires the current user to have at least one of `roles`."""

    async def _checker(current: CurrentUserDep) -> AuthenticatedUser:
        if not set(current.roles) & set(roles):
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Insufficient permissions")
        return current

    return _checker
