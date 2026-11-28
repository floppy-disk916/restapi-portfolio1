from abc import ABC, abstractmethod
from enum import IntEnum
from typing import TypeAlias
from uuid import UUID

from pydantic import (
    BaseModel,
    ValidationError,
)

from sqlalchemy import (
    delete,
    select,
    update,
)
from sqlalchemy.exc import (
    IntegrityError,
)
from sqlalchemy.ext.asyncio import (
    AsyncSession,
)
from sqlalchemy.orm import (
    selectinload,
)

from .models import SQLModel

Model: TypeAlias = SQLModel
Schema: TypeAlias = BaseModel


class repository_code(IntEnum):
    REPOSITORY_GENERIC_ERR = 0
    REPOSITORY_INTERNAL_ERR = 1
    REPOSITORY_CONFLICT_ERR = 2
    REPOSITORY_MISSING_COL_ERR = 3
    REPOSITORY_NOT_FOUND_ERR = 4
    REPOSITORY_PARAM_ERR = 5
    REPOSITORY_NOT_IMPLEMENTED_ERR = 6


class RepositoryException(Exception):
    def __init__(self, message, code):
        self.code = code
        self.message = message
        super().__init__(self.message)


class InternalException(RepositoryException):
    def __init__(self, message="Internal repository error", code=repository_code.REPOSITORY_INTERNAL_ERR):
        super().__init__(message, code)


class ConflictException(RepositoryException):
    def __init__(
        self, message="Conflict occurred", code=repository_code.REPOSITORY_CONFLICT_ERR
    ):
        super().__init__(message, code)


class MissingColException(RepositoryException):
    def __init__(
        self, message="Missing column", code=repository_code.REPOSITORY_MISSING_COL_ERR
    ):
        super().__init__(message, code)


class NotFoundException(RepositoryException):
    def __init__(
        self, message="Data is not found", code=repository_code.REPOSITORY_NOT_FOUND_ERR
    ):
        super().__init__(message, code)


class ParamException(RepositoryException):
    def __init__(
        self, message="Invalid parameter", code=repository_code.REPOSITORY_PARAM_ERR
    ):
        super().__init__(message, code)

class NotImplementedException(RepositoryException):
    def __init__(
        self, message="Not implemented yet",
        code=repository_code.REPOSITORY_NOT_IMPLEMENTED_ERR,
    ):
        super().__init__(message, code)


class BaseRepo(ABC):
    """
    Base class for database repository pattern

    It has :
    1. create_one
    2. create_many
    3. get_one_by_id
    4. get_many_by_ids
    5. update_one_by_id
    6. update_many_by_ids
    7. remove_one_by_id
    8. remove_many_by_ids
    """

    @property
    @abstractmethod
    def model(self) -> Model:
        ...
    
    @property
    @abstractmethod
    def public_schema(self) -> Schema:
        ...

    @classmethod
    @abstractmethod
    async def create_one(
        cls,
        session: AsyncSession,
        data: Schema
    ) -> Schema:
        ...

    @classmethod
    @abstractmethod
    async def create_many(
        cls,
        session: AsyncSession,
        data: list[Schema]
    ) -> list[Schema]:
        ...
    
    @classmethod
    @abstractmethod
    async def get_one_by_id(
        cls,
        session: AsyncSession,
        _id: str | UUID,
        col: str = "id",
        with_for_update: bool = False,
    ) -> Schema:
        ...

    @classmethod
    @abstractmethod
    async def get_many_by_ids(
        cls,
        session: AsyncSession,
        ids: list[str | UUID],
        col: str = "id",
        with_for_update: bool = False,
    ) -> list[Schema]:
        ...

    @classmethod
    @abstractmethod
    async def update_one_by_id(
        cls,
        session: AsyncSession,
        data: Schema,
        _id: str | UUID,
        col: str = "id",
        with_for_update: bool = False,
    ) -> Schema:
        ...

    @classmethod
    @abstractmethod
    async def update_many_by_ids(
        cls,
        session: AsyncSession,
        data: list[Schema],
    ) -> list[Schema]:
        ...

    @classmethod
    @abstractmethod
    async def remove_one_by_id(
        cls,
        session: AsyncSession,
        _id: str | UUID,
        col: str = "id",
    ) -> int:
        ...

    @classmethod
    @abstractmethod
    async def remove_many_by_ids(
        cls,
        session: AsyncSession,
        ids: list[str | UUID],
        col: str = "id",
    ) -> int:
        ...

def get_async_repo(model: Model, public_schema: Schema, child_model: str | None = None):
    class AsyncRepo(BaseRepo):
        """
        Repository class in asynchronous style

        """
        model: Model = None
        public_schema: Schema = None
        child_model: str | None = None
        
        @classmethod
        async def create_one(
            cls,
            session: AsyncSession,
            data: Schema
        ) -> public_schema:
            """
            Creating a single new data into the database
            @param session:
                The ORM Session for the given request. Meant to be taken from Depends()
            @type session: AsyncSession
            
            @param data:
                The new data to be created
            @type data:
                Any schema related to the model
            
            @return: public_schema
            """
            try:
                db_data = model.model_validate(data.model_dump(exclude_unset=True))
                session.add(db_data)
                await session.commit()
            except IntegrityError as e:
                raise InternalException(f"{e.__cause__}") 
            
            return db_data

        @classmethod
        async def create_many(
            cls,
            session: AsyncSession,
            data: list[Schema]
        ) -> list[public_schema]:
            """
            Creating a single new data into the database
            @param session:
                The ORM Session for the given request. Meant to be taken from Depends()
            @type session: AsyncSession
            
            @param data:
                The new list of data to be created
            @type data:
                Any schema related to the model
            
            @return: a list of public_schema
            """           
            
            if not data:
                raise ParamException()

            db_data = []
            for d in data:
                db_data.append(model.model_validate(d.model_dump()))

            try:
                session.add_all(db_data)
                await session.commit()
            except IntegrityError as e:
                raise InternalException(f"{e.__cause__}")

            for d in db_data:
                await session.refresh(d)

            return db_data

        """
        @classmethod
        def _get(func):
            @wraps(func)
            def wrapper():
                where_filter = (getattr(model, col) == _id)
                query = select(model).where(where_filter)
                func(query)
        return wrapper
        """

        @classmethod
        async def get_one_by_id(
            cls,
            session: AsyncSession,
            _id: str | UUID,
            col: str = "id",
            with_for_update: bool = False,
        ) -> public_schema:
            """
            Getting one data by selected id
            
            @param session:
                The ORM Session for the given request. Meant to be taken from Depends()
            @type session: AsyncSession
            
            @param col:
                The column of the id identifier
            @type col: str

            @param _id:
                The identifier value of the data
            @type _id: str or UUID
            
            @param with_for_update: a parameter indicating whether to row lock
            the result or not
            @type with_for_update: bool

            @return: public_schema
            """
            try:
                where_filter = (getattr(model, col) == _id)
                query = select(model).where(where_filter)
                if child_model:
                    query = query.options(selectinload(getattr(model, child_model)))

                if with_for_update:
                    query = query.with_for_update()

            except AttributeError as e:
                raise InternalException(f"{e.__cause__}")
            
            db_data = await session.scalar(query)

            if db_data is None:
                raise NotFoundException()

            return db_data


        @classmethod
        async def get_many_by_ids(
            cls,
            session: AsyncSession,
            ids: list[str | UUID],
            col: str = "id",
            with_for_update: bool = False,
        ) -> list[public_schema]:
            """
            Getting many data by selected id
            
            @param session:
                The ORM Session for the given request. Meant to be taken from Depends()
            @type session: AsyncSession
            
            @param col:
                The column of the ids identifier
            @type col: str

            @param ids:
                The identifier value of the data
            @type ids: a list of str or UUID
            
            @param with_for_update: a parameter indicating whether to row lock
            the result or not
            @type with_for_update: bool

            @return: a list of public_schema
            """           

            try:
                where_filter = (getattr(model, col).in_(ids))
                query = select(model).where(where_filter)
                if child_model:
                    query = query.options(selectinload(getattr(model, child_model)))

            except AttributeError as e:
                raise InternalException(f"{e.__cause__}")

            if with_for_update:
                query = query.with_for_update()

            results = await session.execute(query)
            db_data = results.scalars().unique().all()
            if not db_data:
                raise NotFoundException(message="Not found any")

            return db_data
        
        @classmethod
        async def patch_one_by_id(
            cls,
            session: AsyncSession,
            _id: str | UUID,
            data: Schema,
            col: str = "id",
        ) -> public_schema:
            """
            Patching one data by id
            
            @param session:
                The ORM Session for the given request. Meant to be taken from Depends()
            @type session: AsyncSession
            
            @param data:
                The new data
            @type data: any Schema related to the model

            @param col:
                The column of the id identifier
            @type col: str

            @param _id:
                The identifier value of the data
            @type _id: str or UUID
            

            @return: public_schema
            """               
            
            db_data = await cls.get_one_by_id(
                session=session,
                col=col,
                _id=_id,
                with_for_update=True,
            )
            
            try:
                updates = data.model_dump(exclude_unset=True)
                for k, v in updates.items():
                    setattr(db_data, k, v)
            except AttributeError as e:
                raise InternalException(f"{e.__cause__}")

            session.add(db_data) 
            await session.commit()
            await session.refresh(db_data)
            return db_data


        @classmethod
        async def update_one_by_id(
            cls,
            session: AsyncSession,
            _id: str | UUID,
            data: Schema,
            col: str = "id",
        ) -> public_schema:
            """
            Updating one data by id
            
            @param session:
                The ORM Session for the given request. Meant to be taken from Depends()
            @type session: AsyncSession
            
            @param data:
                The new data
            @type data: any Schema related to the model

            @param col:
                The column of the id identifier
            @type col: str

            @param _id:
                The identifier value of the data
            @type _id: str or UUID
            

            @return: public_schema
            """               
            
            db_data = await cls.get_one_by_id(
                session=session,
                col=col,
                _id=_id,
                with_for_update=True,
            )
            
            try:
                updates = data.model_dump()
                for k, v in updates.items():
                    setattr(db_data, k, v)

            except (AttributeError, IntegrityError) as e:
                raise InternalException(f"{e.__cause__}")

            session.add(db_data) 
            await session.commit()
            await session.refresh(db_data)
            return db_data

        @classmethod
        async def update_many_by_ids(
            cls,
            session: AsyncSession,
            data: list[Schema],
        ) -> list[public_schema]:
            """
            Updating one data by id
            
            @param session:
                The ORM Session for the given request. Meant to be taken from Depends()
            @type session: AsyncSession
            
            @param data:
                All of the new data with id included each
            @type data: a list of any Schema related to the model
 

            @return: a list of public_schema
            """    
            
            raise NotImplementedException()

            if not data:
                raise ParamException()

            new_data = [d.model_dump() for d in data]

            results = await session.execute(
                update(model),
                data
            )
            
            await session.commit()
            return None
            
        @classmethod
        async def remove_one_by_id(
            cls,
            session: AsyncSession,
            _id: str | UUID,
            col: str = "id",
        ) -> int:
            """
            Removing one data by id
            
            @param session:
                The ORM Session for the given request. Meant to be taken from Depends()
            @type session: AsyncSession
            
            @param col:
                The column of the id identifier
            @type col: str

            @param _id:
                The identifier value of the data
            @type _id: str or UUID
 

            @return: deleted data rowcount in int
            """

            try:
                where_filter = (getattr(model, col) == _id)
                query = delete(model).where(where_filter)
            except AttributeError as e:
                raise InternalException(f"{e.__cause__}")

            result = await session.execute(query)
            
            await session.commit()

            if result.rowcount == 0:
                raise NotFoundException()
            
            return result.rowcount

        @classmethod
        async def remove_many_by_ids(
            cls,
            session: AsyncSession,
            ids: list[str | UUID],
            col: str = "id",
        ) -> int:
            """
            Removing many data by id
            
            @param session:
                The ORM Session for the given request. Meant to be taken from Depends()
            @type session: AsyncSession
            
            @param col:
                The column of the ids identifier
            @type col: str

            @param ids:
                The identifier value of the data
            @type ids: a list of str or UUID
 

            @return: deleted data rowcount in int
            """

            try:
                where_filter = (getattr(model, col).in_(ids))
                query = delete(model).where(where_filter)
            except AttributeError as e:
                raise InternalException(f"{e.__cause__}")
            
            result = await session.execute(query)
            
            await session.commit()
            
            if result.rowcount == 0:
                raise NotFoundException()
            
            return result.rowcount

    AsyncRepo.model = model
    AsyncRepo.public_schema = public_schema
    AsyncRepo.child_model = child_model
    return AsyncRepo

