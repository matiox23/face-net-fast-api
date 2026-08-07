from sqlalchemy.ext.asyncio import AsyncSession

from src.app.common.security.jwt import create_access_token
from src.app.common.security.password_hasher import verify_password
from src.app.common.setting import base_config
from src.app.modules.auth.dto.auth_dto import (
    LogoutRequest,
    RefreshRequest,
    TokenResponse,
)
from src.app.modules.auth.service.auth_exceptions import InvalidCredentialsError
from src.app.modules.refresh_token.service.refresh_token_exceptions import (
    InvalidRefreshTokenError,
)
from src.app.modules.refresh_token.service.refresh_token_service import (
    RefreshTokenService,
)
from src.app.modules.user.model.user_model import UserStatus
from src.app.modules.user.service.user_service import UserService
from src.app.modules.user_role.service.user_role_service import UserRoleService

ACCESS_TOKEN_EXPIRES_SECONDS = base_config.jwt_access_token_expires_minutes * 60


class AuthService:
    """Business logic for login, token refresh, and logout."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.user_service = UserService(session)
        self.user_role_service = UserRoleService(session)
        self.refresh_token_service = RefreshTokenService(session)

    async def login(self, email: str, password: str) -> TokenResponse:
        user = await self.user_service.get_user_by_email_for_auth(email)
        if user is None or user.status in (UserStatus.BLOCKED, UserStatus.INACTIVE):
            raise InvalidCredentialsError("Invalid email or password")
        if not verify_password(password, user.password_hash):
            raise InvalidCredentialsError("Invalid email or password")

        roles = await self.user_role_service.list_role_codes(user.id)
        access_token = create_access_token(user.id, roles)
        refresh_token = await self.refresh_token_service.issue(user.id)
        await self.session.commit()

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=ACCESS_TOKEN_EXPIRES_SECONDS,
        )

    async def refresh(self, data: RefreshRequest) -> TokenResponse:
        try:
            token_row = await self.refresh_token_service.validate_and_get(
                data.refresh_token
            )
            new_refresh_token = await self.refresh_token_service.rotate(token_row)
        except InvalidRefreshTokenError:
            await self.session.rollback()
            raise

        roles = await self.user_role_service.list_role_codes(token_row.user_id)
        access_token = create_access_token(token_row.user_id, roles)
        await self.session.commit()

        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            expires_in=ACCESS_TOKEN_EXPIRES_SECONDS,
        )

    async def logout(self, data: LogoutRequest) -> None:
        try:
            token_row = await self.refresh_token_service.validate_and_get(
                data.refresh_token
            )
        except InvalidRefreshTokenError:
            await self.session.rollback()
            return
        await self.refresh_token_service.revoke(token_row)
        await self.session.commit()
