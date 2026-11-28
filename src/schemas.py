from __future__ import annotations

from uuid import UUID
from pydantic import BaseModel, Field

from datetime import datetime

from .models import RoleEnum


class StaffAdd(BaseModel):
    name: str
    age: int = Field(ge=18)
    role: RoleEnum
    monthly_wage: float = Field(ge=0)


class StaffUpdate(BaseModel):
    name: str | None = None
    age: int | None = Field(default=None, ge=18)
    role: RoleEnum | None = None
    monthly_wage: float | None = Field(default=None, ge=0)


class StaffPublic(BaseModel):
    id: UUID
    name: str
    age: int
    role: RoleEnum
    monthly_wage: float


class ItemPublic(BaseModel):
    id: UUID
    name: str
    tags: list[str]
    description: str
    price: float
    tax: float


class ItemAdd(BaseModel):
    name: str = Field(min_length=1,max_length=20)
    tags: list[str]
    description: str = Field(min_length=1, max_length=100)
    price: float = Field(ge=0)
    tax: float = Field(ge=0)


class ItemUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1,max_length=20)
    tags: list[str] | None = None
    description: str | None = Field(default=None, min_length=1, max_length=100)
    price: float | None = Field(default=None, ge=0)
    tax: float | None = Field(default=None, ge=0)


class Token(BaseModel):
    access_token: str
    token_type: str


class AdminPublic(BaseModel):
    id: int
    staff_id: UUID | None
    email: str = Field(min_length=1, max_length=25)
    name: str = Field(min_length=1, max_length=20)

class AdminForm(BaseModel):
    email: str
    name: str
    password: str


class AdminAdd(AdminForm):
    pass

class APIKeyPublic(BaseModel):
    expire_time: datetime
    admin_id: int

class APIKeyAdd(BaseModel):
    admin_id: int
