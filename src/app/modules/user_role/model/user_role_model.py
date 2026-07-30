from sqlalchemy import BigInteger, ForeignKey, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column

from src.app.common.model.base_model import Base


class UserRole(Base):
    """Association between a user and a role (composite primary key)."""

    __tablename__ = "user_role"
    __table_args__ = {"schema": "core"}

    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("core.user.id"), primary_key=True)
    role_id: Mapped[int] = mapped_column(SmallInteger, ForeignKey("core.role.id"), primary_key=True)
