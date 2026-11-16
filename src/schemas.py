from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from .models import RoleEnum

class StaffAdd(BaseModel):
    name: str
    age: int = Field(ge=18)
    role: RoleEnum
    avg_wage: float = Field(ge=0)

class StaffUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    role: Optional[RoleEnum] = None
    avg_wage: Optional[float] = None

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
    name: Optional[str] = None
    tags: Optional[list[str]] = None
    description: Optional[str] = None
    price: Optional[float] = None
    tax: Optional[float] = None

class Token(BaseModel):
    access_token: str
    token_type: str
