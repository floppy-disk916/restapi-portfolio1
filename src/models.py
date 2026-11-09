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
    price: float 
    tax: Optional[float] = Field(default=None)

    __table_args__ = (
        CheckConstraint("tax < price", name="is_valid_tax"),
    )

class ItemPublic(BaseModel):
    id: UUID
    name: str
    tags: list[str]
    description: str
    price: float
    tax: float

    @model_validator(mode="after")
    def is_valid_tax(self):
        if self.tax >= self.price:
            raise ValidationError("tax must be below price")

class StaffBase(SQLModel):
    pass

class RoleEnum(Enum):
    admin = 1
    staff = 2

class Staff(StaffBase, table=True):

    __tablename__: str = "staffs"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(unique=True)
    age: int
    role: RoleEnum
    avg_wage: float = Field(ge=0)

    __table_args__ = (
        CheckConstraint("avg_wage >= 0", name="is_avg_wage_valid"),
    )
