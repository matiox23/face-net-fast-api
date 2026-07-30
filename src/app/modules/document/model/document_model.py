from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from src.app.common.model.base_model import Base


class Document(Base):
    """Identity document type catalog (e.g. DNI, passport)."""

    __tablename__ = "Document"
    __table_args__ = {"schema": "academic"}

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    name: Mapped[str | None] = mapped_column(String(100), nullable=True)
