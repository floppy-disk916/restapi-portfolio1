from sqlmodel import SQLModel, Field, Relationship

from sqlalchemy.schema import Column
from sqlalchemy import CheckConstraint, MetaData
from sqlalchemy.types import ARRAY, String, Float
from pydantic import model_validator, BaseModel, ValidationError
from uuid import uuid4, UUID
from enum import Enum
from datetime import datetime

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

    admin: Admin | None = Relationship(back_populates="staff")

    __table_args__ = (
        CheckConstraint("age >= 18", name="is_valid_age"),
        CheckConstraint("avg_wage >= 0", name="is_avg_wage_valid"),
    )

class AdminBase(SQLModel):
    pass

class Admin(AdminBase, table=True):
    __tablename__ : str = "admins"

    id: int | None = Field(default = None, primary_key=True)
    staff_id: UUID | None = Field(default = None, unique=True, foreign_key="staffs.id")    
    email: str = Field(min_length=10, max_length=25)
    name: str = Field(min_length=10, max_length=20)
    password: str

    staff: Staff | None = Relationship(back_populates="admin")
    api_key: APIKey | None = Relationship(back_populates="admin")

class APIKeyBase(SQLModel):
    pass

class APIKey(APIKeyBase, table=True):
    __tablename__: str = "api_keys"

    id: int | None = Field(default = None, primary_key=True)
    admin_id: int | None = Field(default = None, foreign_key="admins.id")
    hashed_key: str = Field(unique=True)
    expire_date: datetime

    admin: list[Admin] | None = Relationship(back_populates="api_key")
