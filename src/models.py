from sqlmodel import SQLModel, Field

from sqlalchemy.schema import Column
from sqlalchemy import CheckConstraint, MetaData
from sqlalchemy.types import ARRAY, String, Float
from pydantic import model_validator, BaseModel, ValidationError
from uuid import uuid4, UUID
from enum import Enum

from typing import Optional

NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}


SQLModel.metadata = MetaData(naming_convention=NAMING_CONVENTION)

class ItemBase(SQLModel):
    pass

class Item(ItemBase, table=True):

    __tablename__: str = "items"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(unique=True)
    tags: list[str] = Field(sa_column=Column("tags", ARRAY(String, dimensions=1, zero_indexes=True)))
    description: str
    price: float = Field(ge=0)
    tax: Optional[float] = Field(default=None, ge=0)

    __table_args__ = (
        CheckConstraint("tax >= 0", name="is_pos_tax"),
        CheckConstraint("price >= 0", name="is_pos_price"),
        CheckConstraint("tax < price", name="is_valid_tax"),
    )

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


class StaffBase(SQLModel):
    pass

class RoleEnum(Enum):
    admin = 1
    staff = 2

class Staff(StaffBase, table=True):

    __tablename__: str = "staffs"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(unique=True)
    age: int = Field(ge=18)
    role: RoleEnum
    avg_wage: float = Field(ge=0)

    __table_args__ = (
        CheckConstraint("age >= 18", name="is_valid_age"),
        CheckConstraint("avg_wage >= 0", name="is_avg_wage_valid"),
    )

class StaffPublic(StaffBase):
    id: UUID
    name: str
    age: int
    role: RoleEnum
    avg_wage: float

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
