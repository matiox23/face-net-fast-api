from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.app.common.model.base_model import Base


class RefreshToken(Base):
    """Issued refresh token session, tracked to allow revocation (logout, password change)."""

    __tablename__ = "refresh_token"
    __table_args__ = {"schema": "core"}

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("core.user.id"), nullable=False)
    jti: Mapped[str] = mapped_column(String(36), unique=True, nullable=False)
    revoked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
