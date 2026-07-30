import enum
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.app.common.model.base_model import Base


class UserStatus(str, enum.Enum):
    """Account status of a user."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    BLOCKED = "blocked"
    PENDING_VERIFICATION = "pending_verification"


class User(Base):
    """System account linked to a person, identified by email."""

    __tablename__ = "user"
    __table_args__ = {"schema": "core"}

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    person_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("core.person.id"), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    institutional_code: Mapped[str | None] = mapped_column(String(30), nullable=True)
    status: Mapped[UserStatus | None] = mapped_column(
        Enum(UserStatus, name="user_status", schema="core", values_callable=lambda e: [m.value for m in e]),
        nullable=True,
    )
    registration_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
