from pydantic import BaseModel, Field


class RoleAssignRequest(BaseModel):
    role_code: str = Field(examples=["TEACHER"])


class UserRolesResponse(BaseModel):
    user_id: int
    roles: list[str]
