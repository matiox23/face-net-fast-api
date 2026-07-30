from sqlalchemy import SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from src.app.common.model.base_model import Base


class Role(Base):
    """Role assignable to users (e.g. ADMIN, TEACHER, STUDENT)."""

    __tablename__ = "role"
    __table_args__ = {"schema": "core"}

    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True, autoincrement=True)
    code: Mapped[str | None] = mapped_column(String(30), unique=True, nullable=True)
    name: Mapped[str | None] = mapped_column(String(80), nullable=True)
