from datetime import date

from sqlalchemy import CHAR, BigInteger, Date, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.app.common.model.base_model import Base


class Person(Base):
    """Natural person with identity document and personal data."""

    __tablename__ = "person"
    __table_args__ = (
        UniqueConstraint("document_type_id", "document_number", name="uq_person_document"),
        {"schema": "core"},
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    first_names: Mapped[str] = mapped_column(String(120), nullable=False)
    paternal_surname: Mapped[str] = mapped_column(String(80), nullable=False)
    maternal_surname: Mapped[str | None] = mapped_column(String(80), nullable=True)
    document_type_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("academic.Document.id"), nullable=False)
    document_number: Mapped[str] = mapped_column(String(20), nullable=False)
    birth_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    sex: Mapped[str | None] = mapped_column(CHAR(1), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
