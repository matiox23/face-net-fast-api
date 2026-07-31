from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.modules.refresh_token.model.refresh_token_model import RefreshToken


class RefreshTokenRepository:
    """Data access for the `core.refresh_token` table."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, user_id: int, jti: str, expires_at: datetime) -> RefreshToken:
        token = RefreshToken(user_id=user_id, jti=jti, revoked=False, expires_at=expires_at)
        self.session.add(token)
        await self.session.flush()
        return token

    async def get_by_jti(self, jti: str) -> RefreshToken | None:
        result = await self.session.execute(select(RefreshToken).where(RefreshToken.jti == jti))
        return result.scalar_one_or_none()

    async def revoke(self, token: RefreshToken) -> None:
        token.revoked = True
        await self.session.flush()

    async def revoke_all_for_user(self, user_id: int) -> None:
        await self.session.execute(
            update(RefreshToken).where(RefreshToken.user_id == user_id).values(revoked=True)
        )
