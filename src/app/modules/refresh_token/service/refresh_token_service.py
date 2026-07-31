import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.common.security.jwt import ExpiredTokenError, InvalidTokenError, TokenType, create_refresh_token, decode_token
from src.app.common.setting import base_config
from src.app.modules.refresh_token.model.refresh_token_model import RefreshToken
from src.app.modules.refresh_token.repository.refresh_token_repository import RefreshTokenRepository
from src.app.modules.refresh_token.service.refresh_token_exceptions import InvalidRefreshTokenError


class RefreshTokenService:
    """Business logic for issuing, validating, rotating, and revoking refresh tokens."""

    def __init__(self, session: AsyncSession) -> None:
        self.repository = RefreshTokenRepository(session)

    async def issue(self, user_id: int) -> str:
        """Persist a new refresh token session and return its signed JWT."""
        jti = str(uuid.uuid4())
        expires_at = datetime.now(timezone.utc) + timedelta(days=base_config.jwt_refresh_token_expires_days)
        await self.repository.create(user_id=user_id, jti=jti, expires_at=expires_at)
        return create_refresh_token(user_id, jti, expires_at)

    async def validate_and_get(self, token: str) -> RefreshToken:
        """Decode and check that a refresh token is still an active, non-revoked session."""
        try:
            payload = decode_token(token, TokenType.REFRESH)
        except (ExpiredTokenError, InvalidTokenError) as exc:
            raise InvalidRefreshTokenError("Refresh token is invalid or expired") from exc

        token_row = await self.repository.get_by_jti(payload["jti"])
        if token_row is None or token_row.revoked or token_row.expires_at <= datetime.now(timezone.utc):
            raise InvalidRefreshTokenError("Refresh token is revoked, expired, or unknown")

        return token_row

    async def revoke(self, token_row: RefreshToken) -> None:
        await self.repository.revoke(token_row)

    async def revoke_all_for_user(self, user_id: int) -> None:
        await self.repository.revoke_all_for_user(user_id)

    async def rotate(self, old_token: RefreshToken) -> str:
        """Revoke the given session and issue a fresh refresh token for the same user."""
        await self.revoke(old_token)
        return await self.issue(old_token.user_id)
