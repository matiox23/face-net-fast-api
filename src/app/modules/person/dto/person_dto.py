from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class PersonCreate(BaseModel):
    first_names: str = Field(max_length=120)
    paternal_surname: str = Field(max_length=80)
    maternal_surname: str | None = Field(default=None, max_length=80)
    document_type_id: int
    document_number: str = Field(max_length=20)
    birth_date: date | None = None
    sex: str | None = Field(default=None, max_length=1)
    phone: str | None = Field(default=None, max_length=20)


class PersonUpdate(BaseModel):
    first_names: str | None = Field(default=None, max_length=120)
    paternal_surname: str | None = Field(default=None, max_length=80)
    maternal_surname: str | None = Field(default=None, max_length=80)
    phone: str | None = Field(default=None, max_length=20)


class PersonResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    first_names: str
    paternal_surname: str
    maternal_surname: str | None
    document_type_id: int
    document_number: str
    birth_date: date | None
    sex: str | None
    phone: str | None
