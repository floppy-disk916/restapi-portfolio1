from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field

from .models import RoleEnum


class StaffAdd(BaseModel):
    name: str
    age: int = Field(ge=18)
    role: RoleEnum
    avg_wage: float = Field(ge=0)


class StaffUpdate(BaseModel):
    name: str | None = None
    age: int | None = None
    role: RoleEnum | None = None
    avg_wage: float | None = None


class StaffPublic(BaseModel):
    id: UUID
    name: str
    age: int
    role: RoleEnum
    avg_wage: float


class ItemPublic(BaseModel):
    id: UUID
    name: str
    tags: list[str]
    description: str
    price: float
    tax: float


class ItemAdd(BaseModel):
    name: str
    tags: list[str]
    description: str
    price: float = Field(ge=0)
    tax: float = Field(ge=0)


class ItemUpdate(BaseModel):
    name: str | None = None
    tags: list[str] | None = None
    description: str | None = None
    price: float | None = None
    tax: float | None = None


class Token(BaseModel):
    access_token: str
    token_type: str


class AdminPublic(BaseModel):
    id: int
    staff_id: UUID
    name: str = Field(min_length=10, max_length=20)


class AdminForm(BaseModel):
    email: str
    name: str
    password: str


class AdminAdd(AdminForm):
    pass
