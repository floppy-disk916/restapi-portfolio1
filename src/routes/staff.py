from typing import Annotated

from fastapi import APIRouter, Depends, status

from ..auth import check_api_key
from ..db import ASesDep, get_async_repo
from ..models import Staff
from ..schemas import StaffAdd, StaffPublic, StaffUpdate

router = APIRouter(tags=["Staff Operation"], prefix="/staff")

# Decide what type of model you want for the repository
Repo = get_async_repo(Staff)


@router.post("/")
async def add_staff(
    staff: StaffAdd, session: ASesDep, key: Annotated[str, Depends(check_api_key)]
) -> StaffPublic:
    return await Repo.create_one(session=session, data=staff)


@router.get("/")
async def get_staff(name: str, session: ASesDep) -> StaffPublic:
    return await Repo.get_one_by_id(session=session, _id=name, col="name")


@router.patch("/")
async def partial_update_staff(
    staff: StaffUpdate, name: str, session: ASesDep
) -> StaffPublic:
    return await Repo.update_one_by_id(
        session=session, data=staff, _id=name, col="name"
    )


@router.put("/")
async def update_staff(staff: StaffUpdate, name: str, session: ASesDep) -> StaffPublic:
    return await Repo.update_one_by_id(
        session=session, data=staff, _id=name, col="name"
    )


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_staff(name: str, session: ASesDep):
    return await Repo.remove_one_by_id(session=session, _id=name, col="name")
