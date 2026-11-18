from __future__ import annotations

from collections.abc import AsyncGenerator
from enum import IntEnum
from typing import Annotated, TypeAlias
from uuid import UUID

from fastapi import Depends
from pydantic import BaseModel
from sqlalchemy import delete, select
from sqlalchemy.exc import (
    IntegrityError,
)
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from .config import settings
from .models import Base

Model: TypeAlias = Base
Schema: TypeAlias = BaseModel

dsn = str(settings.db_dsn)

# Enable echo and echo_pool for debugging. Default to development mode
is_echo: bool = True
if settings.mode == "prod":
    is_echo = False

# See the documentation for available options
isolation = "READ COMMITTED"

# Per connection age. For pool_recycle
per_connection_age = 3600

engine = create_async_engine(
    dsn,
    echo=is_echo,
    echo_pool=is_echo,
    isolation_level=isolation,
    pool_pre_ping=True,
    pool_size=settings.db_pool_size,
    pool_recycle=per_connection_age,
    max_overflow=settings.db_burst_tolerance,
)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async_session = async_sessionmaker(bind=engine, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession]:
    async with async_session() as session:
        yield session


ASesDep = Annotated[AsyncSession, Depends(get_async_session)]


class factory_code(IntEnum):
    FACTORY_GENERIC_ERR = 0
    FACTORY_ATTR_ERR = 1
    FACTORY_CONFLICT_ERR = 2
    FACTORY_MISSING_COL_ERR = 3
    FACTORY_NOT_FOUND_ERR = 4
    FACTORY_PARAM_ERR = 5


class FactoryException(Exception):
    def __init__(self, message, code):
        self.code = code
        self.message = message
        super().__init__(self.message)


class AttributeException(FactoryException):
    def __init__(self, message, code=factory_code.FACTORY_ATTR_ERR):
        super().__init__(message, code)


class ConflictException(FactoryException):
    def __init__(
        self, message="Conflict occurred", code=factory_code.FACTORY_CONFLICT_ERR
    ):
        super().__init__(message, code)


class MissingColException(FactoryException):
    def __init__(
        self, message="Missing column", code=factory_code.FACTORY_MISSING_COL_ERR
    ):
        super().__init__(message, code)


class NotFoundException(FactoryException):
    def __init__(
        self, message="Data is not found", code=factory_code.FACTORY_NOT_FOUND_ERR
    ):
        super().__init__(message, code)


class ParamException(FactoryException):
    def __init__(
        self, message="Invalid parameter", code=factory_code.FACTORY_PARAM_ERR
    ):
        super().__init__(message, code)


def get_async_repo(model: Model):
    class AsyncRepo:
        model: Model

        @classmethod
        async def create_one(
            cls,
            session: AsyncSession,
            data: Schema,
        ) -> Model:
            try:
                db_model = model(**data.model_dump())
                session.add(db_model)
                await session.commit()
                await session.refresh(db_model)
                return db_model
            except IntegrityError as e:
                raise ConflictException(message=f"{e}")
            except Exception as e:
                raise FactoryException(
                    code=factory_code.FACTORY_GENERIC_ERR, message=f"{e}"
                ) from e

        @classmethod
        async def create_many(
            cls,
            session: AsyncSession,
            data_list: list[Schema],
            return_models: bool = False,
        ) -> list[Model] | bool:
            db_models = [model(**data.model_dump()) for data in data_list]
            try:
                session.add_all(db_models)
                await session.commit()

            except IntegrityError as e:
                raise ConflictException(message=f"{e}")
            except Exception as e:
                raise FactoryException(
                    code=factory_code.FACTORY_GENERIC_ERR,
                    message=f"Error occurred: {e}",
                ) from e

            if not return_models:
                return True

            for m in db_models:
                await session.refresh(m)

            return db_models

        @classmethod
        async def get_one_by_id(
            cls,
            session: AsyncSession,
            _id: str | UUID,
            col: str = "uuid",
            with_for_update: bool = False,
        ) -> Model:

            try:
                query = select(model).where(getattr(model, col) == _id)
            except AttributeError:
                raise AttributeException(
                    message=f"Column {col} not found in model {model.__tablename__}"
                )

            if with_for_update:
                query = query.with_for_update()

            results = await session.execute(query)
            return results.unique().scalar_one_or_none()

        @classmethod
        async def get_many_by_ids(
            cls,
            session: AsyncSession,
            ids: list[str | UUID],
            col: str = "uuid",
            with_for_update: bool = False,
        ) -> list[Model]:

            query = select(model)

            if ids:
                try:
                    query = query.where(getattr(model, col).in_(ids))
                except AttributeError:
                    raise AttributeException(
                        message=f"Column {col} not found in model {model.__tablename__}"
                    )

            if with_for_update:
                query = query.with_for_update()

            results = await session.execute(query)
            return results.unique().scalars().all()

        @classmethod
        async def update_one_by_id(
            cls,
            session: AsyncSession,
            data: Schema,
            _id: str | UUID,
            col: str = "uuid",
        ) -> Model:

            db_model = await cls.get_one_by_id(
                session, _id, col=col, with_for_update=True
            )

            if not db_model:
                raise NotFoundException(
                    message=f"{model.__tablename__} {col} = {_id} not found"
                )

            values = data.model_dump(exclude_unset=True)
            for k, v in values.items():
                setattr(db_model, k, v)

            try:
                await session.commit()
                await session.refresh(db_model)
                return db_model

            except IntegrityError:
                raise ConflictException(
                    message=f"{model.__tablename__} {col} = {_id} conflicts with existing data"
                )

        @classmethod
        async def update_many_by_id(
            cls,
            session: AsyncSession,
            updates: dict[str | UUID, Schema],
            col: str = "uuid",
            return_models: bool = False,
        ) -> list[Model] | bool:

            # dict comprehension
            updates = {str(id): update for id, update in updates.items() if update}

            ids = list(updates.keys())

            db_models = await cls.get_many_by_ids(
                session, ids=ids, col=col, with_for_update=True
            )

            for db_model in db_models:
                values = updates[str(getattr(db_model, col))].model_dump(
                    exclude_unset=True
                )
                for k, v in values.items():
                    setattr(db_model, k, v)
                session.add(db_model)

            try:
                await session.commit()
            except IntegrityError:
                raise ConflictException(
                    message=f"{model.__tablename__} conflict with existing data"
                )

            if not return_models:
                return True

            for db_model in db_models:
                await session.refresh(db_model)

            return db_models

        @classmethod
        async def remove_one_by_id(
            cls,
            session: AsyncSession,
            _id: str | UUID,
            col: str = "uuid",
        ) -> int:
            try:
                db_model = await session.scalar(
                    select(model).where(getattr(model, col) == _id)
                )
                if not db_model:
                    raise NotFoundException(
                        message=f"Item with id {_id} is not found",
                    )

                query = delete(model).where(getattr(model, col) == _id)
            except AttributeError:
                raise MissingColException(
                    message=f"Column {col} not found on {model.__tablename__}.",
                )

            rows = await session.execute(query)
            await session.commit()
            return rows.rowcount

        @classmethod
        async def remove_many_by_ids(
            cls,
            session: AsyncSession,
            ids: list[str | UUID],
            col: str = "uuid",
        ) -> int:

            if not ids:
                raise ParamException(
                    message="No ids provided",
                )

            try:
                query = delete(model).where(getattr(model, col).in_(ids))
            except AttributeError:
                raise AttributeException(
                    message=f"Column {col} not found on {model.__tablename__}.",
                )

            rows = await session.execute(query)
            await session.commit()
            return rows.rowcount

    AsyncRepo.model = model
    return AsyncRepo
