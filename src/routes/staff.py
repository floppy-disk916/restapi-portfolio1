from fastapi import (
    APIRouter,
    status,
    HTTPException,
)

from ..models import Staff, StaffPublic, StaffAdd, StaffUpdate
from ..db import ASesDep
from typing import Annotated

router = APIRouter(tags=["Staff Operation"], prefix="/staff")


@router.post("/")
async def add_staff(staff: StaffAdd, session: ASesDep) -> StaffPublic:
    session.add(staff)
    return item

@router.get("/")
async def get_staff(name: str, session: ASesDep) -> StaffPublic:
    staff_db = (await session.scalar(Staff).where(Staff.name == name))
    if staff_db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return staff_db

@router.patch("/")
async def partial_update_staff(staff: StaffUpdate, name: str, session: ASesDep) -> StaffPublic:
    staff_db = (await session.scalar(Staff).where(Staff.name == name))
    if staff_db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    staff_data = item.model_dump(exclude_unset=True, exclude_none=True)
    staff_db.sqlmodel_update(staff_data)
    session.add(staff_db)
    return staff_db

@router.put("/")
async def update_staff(staff: StaffUpdate, name: str, session: ASesDep) -> StaffPublic:
    staff_db = (await session.scalar(Staff).where(Staff.name == name))
    if staff_db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    staff_data = staff.model_dump()
    staff_db.sqlmodel_update(staff_data)
    session.add(staff_db)
    return staff_db


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_staff(name: str, session: ASesDep):
    staff_db = (await session.scalar(Staff).where(Staff.name == name))
    if staff_db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    session.delete(staff_db)

