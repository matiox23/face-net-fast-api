from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from src.app.modules.person.dto.person_dto import PersonResponse
from src.app.modules.user.model.user_model import UserStatus


class UserCreate(BaseModel):
    first_names: str = Field(max_length=120, examples=["Juan Carlos"])
    paternal_surname: str = Field(max_length=80, examples=["Pérez"])
    maternal_surname: str | None = Field(default=None, max_length=80, examples=["Gómez"])
    document_type_id: int = Field(examples=[1])
    document_number: str = Field(max_length=20, examples=["12345678"])
    birth_date: date | None = Field(default=None, examples=["2000-05-14"])
    sex: str | None = Field(default=None, max_length=1, examples=["M"])
    phone: str | None = Field(default=None, max_length=20, examples=["+56912345678"])

    email: EmailStr = Field(examples=["juan.perez@example.com"])
    password: str = Field(min_length=8, max_length=128, examples=["SuperSecret123"])
    institutional_code: str | None = Field(default=None, max_length=30, examples=["EST-2024-001"])


class UserUpdate(BaseModel):
    first_names: str | None = Field(default=None, max_length=120)
    paternal_surname: str | None = Field(default=None, max_length=80)
    maternal_surname: str | None = Field(default=None, max_length=80)
    phone: str | None = Field(default=None, max_length=20)
    institutional_code: str | None = Field(default=None, max_length=30)


class UserStatusUpdate(BaseModel):
    status: UserStatus


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    institutional_code: str | None
    status: UserStatus | None
    registration_date: datetime | None
    person: PersonResponse
    roles: list[str]


class UserListResponse(BaseModel):
    items: list[UserResponse]
    total: int
    page: int
    page_size: int
