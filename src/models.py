
from datetime import datetime, UTC, timedelta
from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, MetaData, UniqueConstraint
from sqlalchemy.schema import Column
from sqlalchemy.types import JSON, String
from sqlalchemy.orm import Mapped
from sqlmodel import Field, Relationship, SQLModel

from typing import List, Optional

import string
import secrets

from .config import settings


NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


SQLModel.metadata = MetaData(naming_convention=NAMING_CONVENTION)

def generate_api_key(length: int = 32) -> str:
    alphabets = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabets) for _ in range(length))

def get_api_key_limit_time() -> datetime:
    expire_time = datetime.now(UTC) + timedelta(days=settings.api_key_expire_day)
    return expire_time



Base = SQLModel


class Item(SQLModel, table=True):
    __tablename__: str = "items"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(unique=True, min_length=1, max_length=20)
    tags: List[str] = Field(
        sa_column=Column("tags", JSON, default=list),
    )

    description: str | None = Field(default=None, min_length=1, max_length=100)
    price: float = Field(ge=0)
    tax: float | None = Field(default=None, ge=0)

    __table_args__ = (
        CheckConstraint("tax >= 0", name="is_pos_tax"),
        CheckConstraint("price >= 0", name="is_pos_price"),
        CheckConstraint("tax < price", name="is_valid_tax"),
    )


class RoleEnum(str, Enum):
    admin = "admin"
    staff = "staff"


class Staff(SQLModel, table=True):
    __tablename__: str = "staffs"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(unique=True)
    age: int = Field(ge=18)
    role: RoleEnum
    monthly_wage: float = Field(ge=0)

    admin_staff: Admin = Relationship(back_populates="staff", cascade_delete=True)

    __table_args__ = (
        CheckConstraint("age >= 18", name="is_valid_age"),
        CheckConstraint("monthly_wage >= 0", name="is_valid_monthly_wage"),
    )


class Admin(SQLModel, table=True):
    __tablename__: str = "admins"

    id: int | None = Field(default=None, primary_key=True)
    staff_id: UUID | None = Field(default=None, unique=True, foreign_key="staffs.id")
    
    email: str = Field(min_length=1, max_length=25)
    name: str = Field(min_length=1, max_length=20)
    password: str = Field(min_length=1)

    staff: Staff = Relationship(back_populates="admin_staff")
    api_keys: Optional[List["APIKey"]] = Relationship(back_populates="admin_api_key", cascade_delete=True)

    __table_args__ = (
        UniqueConstraint("email", name="unique_email"),
        UniqueConstraint("staff_id", name="unique_staff_id"),
    )

class APIKey(SQLModel, table=True):
    __tablename__: str = "api_keys"

    id: int | None = Field(default=None, primary_key=True)
    admin_id: int = Field(foreign_key="admins.id", ondelete="CASCADE")
    key: str = Field(default_factory=generate_api_key)
    expire_date: datetime = Field(default_factory=get_api_key_limit_time)

    admin_api_key: Admin = Relationship(back_populates="api_keys")
